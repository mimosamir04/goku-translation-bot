import os
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

try:
    from google.cloud import translate_v2
    from google.oauth2 import service_account
except ImportError:
    print("Error: google-cloud-translate not installed. Run: pip install -r requirements.txt")
    exit(1)
# single-instance lock to avoid duplicate polling in same container
import sys
try:
    import fcntl
    _lock_fh = open('.goku_bot.lock', 'w')
    fcntl.lockf(_lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
except Exception:
    print("Another instance is already running. Exiting.")
    sys.exit(1)

import google.generativeai as genai

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatAction

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

translate_client = None
try:
    # Check if credentials file exists
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if creds_path and os.path.exists(creds_path):
        logger.info(f"Using Google Cloud credentials from: {creds_path}")
        translate_client = translate_v2.Client()
        logger.info("✅ Google Cloud Translate initialized successfully")
    else:
        logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS not set or file not found")
        logger.warning("Translation service will not be available")
        logger.info("To set up Google Cloud Translate:")
        logger.info("1. Create a service account in Google Cloud Console")
        logger.info("2. Download the JSON credentials file")
        logger.info("3. Set GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json")
        
except Exception as e:
    logger.error(f"❌ Failed to initialize Google Cloud Translate: {e}")
    logger.error(f"Error type: {type(e).__name__}")
    translate_client = None

gemini_model = None
try:
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        logger.warning("⚠️ GOOGLE_API_KEY not set")
    else:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel('gemini-pro')
        logger.info("✅ Gemini AI initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Gemini AI: {e}")
    gemini_model = None

# User statistics storage
user_stats: Dict[int, Dict[str, Any]] = {}

# ========== UTILITY FUNCTIONS ==========

def update_user_stats(user_id: int, text_length: int) -> None:
    """Update user translation statistics"""
    if user_id not in user_stats:
        user_stats[user_id] = {
            'translations': 0,
            'characters': 0,
            'first_use': datetime.now()
        }
    user_stats[user_id]['translations'] += 1
    user_stats[user_id]['characters'] += text_length


def detect_language(text: str) -> str:
    """Detect if text is French or Arabic"""
    # Arabic detection
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    if arabic_pattern.search(text):
        return 'ar'
    
    # Default to French
    return 'fr'


# ========== TRANSLATION FUNCTION ==========

async def translate_text(text: str, source_lang: str, target_lang: str, user_id: int) -> str:
    """Translate text using Google Cloud Translate"""
    try:
        if not translate_client:
            logger.error("Translation client not initialized")
            return "❌ خطأ: خدمة الترجمة غير متاحة حالياً.\n\nيرجى التحقق من:\n1. تثبيت مفتاح Google Cloud\n2. تفعيل Translate API\n3. تعيين GOOGLE_APPLICATION_CREDENTIALS"
        
        logger.info(f"Translating {source_lang}→{target_lang} for user {user_id}: {text[:50]}...")
        
        result = translate_client.translate(
            text,
            source_language=source_lang,
            target_language=target_lang
        )
        
        translated_text = result['translatedText']
        logger.info(f"Translation successful: {translated_text[:50]}...")
        
        # Update statistics
        update_user_stats(user_id, len(text))
        
        return translated_text
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return f"❌ خطأ في الترجمة: {str(e)[:100]}"


# ========== GEMINI AI FUNCTION ==========

async def ask_gemini(question: str) -> Optional[str]:
    """Ask Gemini AI a question"""
    try:
        if not gemini_model:
            logger.warning("Gemini model not initialized")
            return None
        
        logger.info(f"Asking Gemini: {question[:50]}...")
        
        response = gemini_model.generate_content(question)
        
        if response.text:
            logger.info(f"Gemini response: {response.text[:50]}...")
            return response.text
        
        return None
        
    except Exception as e:
        logger.error(f"Gemini error: {str(e)}")
        return None


# ========== LANGUAGE DETECTION ==========

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages"""
    user = update.effective_user
    text = update.message.text
    user_id = user.id
    
    logger.info(f"Message from {user.id}: {text}")
    
    # Show typing indicator
    await update.message.chat.send_action(ChatAction.TYPING)
    
    is_question = text.strip().endswith('?')
    
    if is_question:
        # Use Gemini AI for questions
        gemini_response = await ask_gemini(text)
        
        if gemini_response:
            response = f"""
🤖 إجابة من الذكاء الاصطناعي:

📝 سؤالك:
{text}

💬 الإجابة:
{gemini_response}
"""
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("❌ عذراً، لم أتمكن من الإجابة على سؤالك. حاول لاحقاً.")
        return
    
    # Default behavior: translate the text
    # Detect language
    detected_lang = detect_language(text)
    
    # Determine target language
    if detected_lang == 'ar':
        target_lang = 'fr'
        target_lang_name = 'الفرنسية'
        source_lang_name = 'العربية'
    else:
        target_lang = 'ar'
        target_lang_name = 'العربية'
        source_lang_name = 'الفرنسية'
    
    # Try translation first
    translated = await translate_text(text, detected_lang, target_lang, user_id)
    
    # If translation looks good, send it
    if not translated.startswith('❌'):
        response = f"""
🔄 الترجمة:

📌 اللغة الأصلية: {source_lang_name}
🎯 اللغة المستهدفة: {target_lang_name}

📝 النص الأصلي:
{text}

✅ النص المترجم:
{translated}
"""
        await update.message.reply_text(response)
    else:
        # If translation fails, try Gemini AI
        gemini_response = await ask_gemini(text)
        
        if gemini_response:
            response = f"""
🤖 إجابة من الذكاء الاصطناعي:

📝 سؤالك:
{text}

💬 الإجابة:
{gemini_response}
"""
            await update.message.reply_text(response)
        else:
            await update.message.reply_text(translated)


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ask command for AI questions"""
    user = update.effective_user
    
    # Get the question from command arguments
    if not context.args:
        await update.message.reply_text(
            "استخدام: /ask السؤال\n\n"
            "مثال: /ask ما هي عاصمة فرنسا؟"
        )
        return
    
    question = ' '.join(context.args)
    
    logger.info(f"User {user.id} asking: {question}")
    
    # Show typing indicator
    await update.message.chat.send_action(ChatAction.TYPING)
    
    # Ask Gemini AI
    gemini_response = await ask_gemini(question)
    
    if gemini_response:
        response = f"""
🤖 إجابة من الذكاء الاصطناعي:

📝 سؤالك:
{question}

💬 الإجابة:
{gemini_response}
"""
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ عذراً، لم أتمكن من الإجابة على سؤالك. حاول لاحقاً.")


# ========== TELEGRAM HANDLERS ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    welcome_message = f"""
مرحباً {user.first_name}! 👋

أنا بوت الترجمة الذكي! 🤖

يمكنني مساعدتك في:
✅ ترجمة النصوص من الفرنسية إلى العربية
✅ ترجمة النصوص من العربية إلى الفرنسية
✅ الإجابة على أسئلتك باستخدام الذكاء الاصطناعي

طرق الاستخدام:
1️⃣ أرسل نصاً عادياً → سأترجمه
2️⃣ أرسل سؤالاً ينتهي بـ (؟) → سأجيب عليه بالذكاء الاصطناعي
3️⃣ استخدم /ask السؤال → للأسئلة المباشرة

الأوامر المتاحة:
/start - عرض هذه الرسالة
/help - الحصول على المساعدة
/ask - اسأل سؤالاً
/stats - عرض إحصائياتك
"""
    await update.message.reply_text(welcome_message)
    logger.info(f"User {user.id} started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_message = """
📖 دليل الاستخدام:

1️⃣ **الترجمة من الفرنسية إلى العربية:**
   أرسل النص الفرنسي وسأترجمه للعربية تلقائياً

2️⃣ **الترجمة من العربية إلى الفرنسية:**
   أرسل النص العربي وسأترجمه للفرنسية تلقائياً

3️⃣ **الأسئلة العامة - الطريقة الأولى:**
   أرسل سؤالك ينتهي بـ (؟) وسأجيب عليه بالذكاء الاصطناعي
   مثال: ما هي عاصمة فرنسا؟

4️⃣ **الأسئلة العامة - الطريقة الثانية:**
   استخدم /ask متبوعاً بسؤالك
   مثال: /ask ما هي عاصمة فرنسا

📊 الأوامر:
/ask - اسأل سؤالاً
/stats - عرض عدد الترجمات والأحرف المترجمة
/help - عرض هذه الرسالة

💡 نصيحة: كلما أرسلت نصاً أطول، كانت الترجمة أدق!
"""
    await update.message.reply_text(help_message)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command"""
    user_id = update.effective_user.id
    
    if user_id not in user_stats:
        await update.message.reply_text("لم تقم بأي ترجمة حتى الآن! 📊")
        return
    
    stats = user_stats[user_id]
    stats_message = f"""
📊 إحصائياتك:

✅ عدد الترجمات: {stats['translations']}
📝 عدد الأحرف المترجمة: {stats['characters']}
📅 تاريخ الاستخدام الأول: {stats['first_use'].strftime('%Y-%m-%d %H:%M:%S')}
"""
    await update.message.reply_text(stats_message)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


# ========== MAIN APPLICATION ==========

def main() -> None:
    """Start the bot"""
    # Get token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    logger.info("=" * 50)
    logger.info("🚀 Starting Goku Translation Bot")
    logger.info("=" * 50)
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("✅ Bot started successfully!")
    logger.info("=" * 50)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
