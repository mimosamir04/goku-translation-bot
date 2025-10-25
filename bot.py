import os
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from functools import wraps

import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatAction, ParseMode

# ========== LOGGING CONFIGURATION ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== ENVIRONMENT VARIABLES ==========
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("❌ Missing TELEGRAM_BOT_TOKEN in .env file")
if not GOOGLE_API_KEY:
    raise RuntimeError("❌ Missing GOOGLE_API_KEY in .env file")

# ========== BOT CONFIGURATION ==========
# Bot is now available for all users (no topic restrictions)

# ========== GEMINI AI CONFIGURATION ==========
genai.configure(api_key=GOOGLE_API_KEY)

# Main translation model
translation_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config={
        "temperature": 0.3,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
)

# ========== BOT NAME VARIATIONS ==========
BOT_NAMES = [
    'goku', 'جوكو', 'ڨوكو', 'غوكو', 'قوكو',
    'gokou', 'غوكـو', 'جـوكو', 'ڤوكو'
]

# ========== USER STATISTICS ==========
user_stats: Dict[int, Dict[str, Any]] = {}

def update_user_stats(user_id: int, chars_translated: int = 0):
    """Track user translation statistics"""
    if user_id not in user_stats:
        user_stats[user_id] = {
            "translations": 0,
            "chars_translated": 0,
            "first_use": datetime.now(),
            "last_use": datetime.now()
        }
    
    user_stats[user_id]["translations"] += 1
    user_stats[user_id]["chars_translated"] += chars_translated
    user_stats[user_id]["last_use"] = datetime.now()

# ========== RATE LIMITING DECORATOR ==========
def rate_limit(max_per_minute: int = 20):
    """Simple rate limiting decorator"""
    user_requests = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            now = datetime.now()
            
            if user_id in user_requests:
                requests, last_reset = user_requests[user_id]
                if (now - last_reset).seconds >= 60:
                    user_requests[user_id] = ([now], now)
                elif len(requests) >= max_per_minute:
                    await update.message.reply_text(
                        "⏳ انتظر قليلاً! لقد أرسلت الكثير من الطلبات.\n"
                        "جرب مرة أخرى بعد دقيقة."
                    )
                    return
                else:
                    requests.append(now)
            else:
                user_requests[user_id] = ([now], now)
            
            return await func(update, context)
        return wrapper
    return decorator

# ========== HELPER FUNCTIONS ==========
def contains_bot_name(text: str) -> bool:
    """Check if text contains bot name"""
    text_lower = text.lower()
    for name in BOT_NAMES:
        if name in text_lower:
            return True
    return False

def remove_bot_name(text: str) -> str:
    """Remove bot name from text"""
    result = text
    for name in BOT_NAMES:
        # Case-insensitive removal
        pattern = re.compile(re.escape(name), re.IGNORECASE)
        result = pattern.sub('', result)
    return result.strip()

# ========== LANGUAGE DETECTION ==========
async def detect_language_advanced(text: str) -> str:
    """Advanced language detection with AI"""
    try:
        prompt = f"""Analyze this text and determine its PRIMARY language.
Reply with ONLY ONE WORD from these options:
- "arabic" if the text is primarily in Arabic (any dialect)
- "french" if the text is primarily in French
- "english" if the text is primarily in English
- "mixed" if multiple languages are mixed
- "other" for any other language

Text to analyze: {text[:300]}

Your answer (one word only):"""
        
        response = translation_model.generate_content(prompt)
        detected = response.text.strip().lower()
        
        # Clean up response
        if 'arabic' in detected or 'عربي' in detected:
            return 'arabic'
        elif 'french' in detected or 'français' in detected or 'francais' in detected:
            return 'french'
        elif 'english' in detected or 'anglais' in detected:
            return 'english'
        elif 'mixed' in detected:
            return 'mixed'
        else:
            return 'other'
            
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        
        # Fallback: Simple heuristic
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        latin_chars = len(re.findall(r'[a-zA-ZÀ-ÿ]', text))
        
        if arabic_chars > latin_chars:
            return 'arabic'
        elif latin_chars > arabic_chars:
            return 'french'
        else:
            return 'unknown'

# ========== SPECIAL COMMANDS HANDLER ==========
async def handle_special_command(text: str, user_name: str) -> Optional[str]:
    """Handle special commands that require bot name"""
    text_lower = text.lower()
    
    # Must contain bot name for special commands
    if not contains_bot_name(text):
        return None
    
    # Remove bot name to check the actual question
    clean_text = remove_bot_name(text).strip()
    
    # Creator questions
    creator_keywords = [
        'من صنعك', 'من صانعك', 'من طورك', 'من المطور', 'من مطورك',
        'who created you', 'who made you', 'who is your creator',
        'qui t\'a créé', 'qui t\'a fait', 'qui est ton créateur',
        'من انشأك', 'من بناك', 'صانعك من', 'مين صنعك'
    ]
    
    for keyword in creator_keywords:
        if keyword in text_lower:
            return (
                f"👨‍💻 مرحباً {user_name}!\n\n"
                "صانعي ومطوري هو: @anes_miiih19 ✨\n\n"
                "🐉 أنا Goku، بوت ترجمة ذكي صُنعت بواسطة أنس لمساعدتكم في الترجمة!"
            )
    
    # Greeting responses
    greeting_responses = {
        'مرحبا': f'مرحباً {user_name}! 🐉 أنا Goku، بوت الترجمة الذكي! أرسل لي أي نص وسأترجمه لك!',
        'مرحبا بك': f'أهلاً وسهلاً {user_name}! 🐉 جاهز للترجمة!',
        'سلام': f'وعليكم السلام {user_name}! 🐉 كيف أساعدك اليوم؟',
        'السلام عليكم': f'وعليكم السلام ورحمة الله {user_name}! 🐉',
        'hello': f'Hello {user_name}! 🐉 I\'m Goku, your smart translation bot! Send me any text!',
        'hi': f'Hi there {user_name}! 🐉 Ready to translate!',
        'bonjour': f'Bonjour {user_name}! 🐉 Je suis Goku, votre bot de traduction! Envoyez-moi un texte!',
        'salut': f'Salut {user_name}! 🐉 Prêt à traduire!',
        'hey': f'Hey {user_name}! 🐉 What can I translate for you?',
    }
    
    for greeting, response in greeting_responses.items():
        if greeting in clean_text.lower():
            return response
    
    # Help/question about capabilities
    help_keywords = ['كيف', 'ماذا تفعل', 'what can you do', 'que peux-tu faire', 'help', 'مساعدة']
    for keyword in help_keywords:
        if keyword in clean_text.lower():
            return (
                f"🐉 مرحباً {user_name}!\n\n"
                "أنا بوت ترجمة ذكي، أستطيع:\n"
                "✅ الترجمة من الفرنسية → العربية\n"
                "✅ الترجمة من العربية → الفرنسية\n"
                "✅ تصحيح الأخطاء الإملائية تلقائياً\n"
                "✅ فهم النصوص المختلطة\n\n"
                "📝 فقط أرسل النص وأنا أترجمه!"
            )
    
    return None

# ========== TRANSLATION FUNCTION ==========
async def translate_with_correction(text: str, from_lang: str, to_lang: str, user_id: int) -> str:
    """Advanced translation with automatic spelling correction"""
    try:
        logger.info(f"Translating {from_lang}→{to_lang} for user {user_id}")
        
        # Build comprehensive prompt
        if from_lang == 'french' and to_lang == 'arabic':
            prompt = f"""You are a professional French-to-Arabic translator with advanced capabilities.

INSTRUCTIONS:
1. First, analyze the input text and correct any spelling/grammar mistakes
2. Then translate the CORRECTED text from French to Modern Standard Arabic
3. Preserve proper names, numbers, dates, and brand names
4. Maintain the original tone and style
5. Return ONLY the Arabic translation (no explanations, no source text)
6. If the text is not French, still attempt translation if possible

Input text to translate:
{text}

Your Arabic translation:"""

        elif from_lang == 'arabic' and to_lang == 'french':
            prompt = f"""You are a professional Arabic-to-French translator with advanced capabilities.

INSTRUCTIONS:
1. First, analyze the input text and correct any spelling/grammar mistakes
2. Then translate the CORRECTED text from Arabic to French
3. Preserve proper names, numbers, dates, and brand names
4. Maintain the original tone and style
5. Return ONLY the French translation (no explanations, no source text)
6. Handle both Modern Standard Arabic and dialects

Input text to translate:
{text}

Your French translation:"""

        else:
            return f"❌ اتجاه الترجمة غير مدعوم: {from_lang} → {to_lang}"
        
        # Generate translation
        response = translation_model.generate_content(prompt)
        
        # Extract translation
        if hasattr(response, 'text') and response.text:
            translated = response.text.strip()
        elif hasattr(response, 'candidates') and response.candidates:
            translated = ""
            for candidate in response.candidates:
                if hasattr(candidate, 'content'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'text'):
                            translated += part.text
            translated = translated.strip()
        else:
            return "❌ لم أتمكن من الترجمة. حاول مرة أخرى."
        
        if not translated:
            return "❌ الترجمة فارغة. يرجى المحاولة مرة أخرى."
        
        # Update statistics
        update_user_stats(user_id, len(text))
        
        return translated
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return f"❌ حدث خطأ في الترجمة: {str(e)[:100]}\n\nحاول مرة أخرى أو تواصل مع @anes_miih19"

# ========== SMART LANGUAGE DETECTION AND TRANSLATION ==========
async def smart_translate(text: str, user_id: int) -> tuple[str, str]:
    """Detect language and translate smartly"""
    
    # Detect language
    detected_lang = await detect_language_advanced(text)
    logger.info(f"Detected language: {detected_lang}")
    
    # Handle based on detection
    if detected_lang == 'french':
        translated = await translate_with_correction(text, 'french', 'arabic', user_id)
        direction = "🇫🇷 → 🇸🇦"
        
    elif detected_lang == 'arabic':
        translated = await translate_with_correction(text, 'arabic', 'french', user_id)
        direction = "🇸🇦 → 🇫🇷"
        
    elif detected_lang == 'english':
        # Try to translate English as French
        translated = await translate_with_correction(text, 'french', 'arabic', user_id)
        direction = "🇬🇧→🇫🇷 → 🇸🇦"
        
    elif detected_lang == 'mixed':
        # Try French to Arabic first
        translated = await translate_with_correction(text, 'french', 'arabic', user_id)
        direction = "🔀 → 🇸🇦"
        
    else:
        return (
            "⚠️ لم أتمكن من تحديد اللغة.\n\n"
            "الرجاء إرسال نص بالفرنسية 🇫🇷 أو العربية 🇸🇦",
            "❌"
        )
    
    return translated, direction

# ========== COMMAND HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with comprehensive instructions"""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    keyboard = [
        [
            InlineKeyboardButton("📖 المساعدة", callback_data="help"),
            InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")
        ],
        [
            InlineKeyboardButton("🌐 اللغات المدعومة", callback_data="languages"),
            InlineKeyboardButton("ℹ️ حول", callback_data="about")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_msg = (
        f"🐉 <b>مرحباً {user.first_name}!</b>\n\n"
        "أنا <b>Goku</b> - بوت ترجمة ذكي ثنائي الاتجاه! 🤖\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ <b>المميزات:</b>\n"
        "✅ ترجمة فرنسي ↔️ عربي\n"
        "✅ تصحيح الأخطاء الإملائية تلقائياً\n"
        "✅ كشف اللغة الذكي\n"
        "✅ معالجة النصوص الطويلة\n"
        "✅ الحفاظ على الأسماء والأرقام\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📝 <b>كيفية الاستخدام:</b>\n\n"
        "🔹 <b>للترجمة فقط:</b>\n"
        "   فقط أرسل النص مباشرة وسأترجمه!\n\n"
        "🔹 <b>للأسئلة الخاصة:</b>\n"
        "   اكتب اسمي أولاً ثم سؤالك:\n"
        "   <code>ڨوكو من صنعك؟</code>\n"
        "   <code>Goku مرحباً!</code>\n"
        "   <code>Goku كيف حالك؟</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <b>أمثلة:</b>\n"
        "📤 <code>Bonjour comment ça va?</code>\n"
        "📥 مرحباً كيف حالك؟\n\n"
        "📤 <code>أنا بخير شكراً</code>\n"
        "📥 Je vais bien merci\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "👨‍💻 <b>المطور:</b> @anes_miiih19\n"
        "🆔 <b>جرب:</b> اكتب <code>ڨوكو من صنعك؟</code>"
    )
    
    await update.message.reply_text(
        welcome_msg,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = (
        "📚 <b>دليل الاستخدام الكامل</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 <b>الأوامر المتاحة:</b>\n"
        "/start - بدء المحادثة\n"
        "/help - عرض المساعدة\n"
        "/stats - إحصائيات الاستخدام\n"
        "/language - اللغات المدعومة\n"
        "/about - حول البوت\n"
        "/ping - اختبار البوت\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📝 <b>طريقتان للاستخدام:</b>\n\n"
        "1️⃣ <b>الترجمة المباشرة:</b>\n"
        "   أرسل النص فقط دون اسم البوت\n"
        "   سيتم الكشف التلقائي والترجمة\n\n"
        "2️⃣ <b>الأسئلة والمحادثة:</b>\n"
        "   اكتب اسمي أولاً: ڨوكو / Goku\n"
        "   مثال: <code>ڨوكو من صنعك؟</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ <b>المميزات الذكية:</b>\n"
        "✅ تصحيح الأخطاء الإملائية\n"
        "✅ فهم النصوص المختلطة\n"
        "✅ الحفاظ على التنسيق\n"
        "✅ معالجة حتى 8000 حرف\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🎓 <b>نصائح:</b>\n"
        "• لا تقلق من الأخطاء - سأصححها!\n"
        "• الأسماء الخاصة تبقى كما هي\n"
        "• الأرقام لا تُترجم\n"
        "• يمكنك إرسال فقرات كاملة\n\n"
        "👨‍💻 صُنعت بواسطة: @anes_miih19"
    )
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics"""
    user_id = update.effective_user.id
    
    if user_id not in user_stats:
        await update.message.reply_text(
            "📊 <b>إحصائياتك</b>\n\n"
            "لم تقم بأي ترجمات بعد.\n"
            "أرسل نصاً وابدأ الآن! 🚀",
            parse_mode=ParseMode.HTML
        )
        return
    
    stats = user_stats[user_id]
    usage_days = max((datetime.now() - stats["first_use"]).days, 1)
    avg_per_day = stats['translations'] / usage_days
    
    stats_text = (
        "📊 <b>إحصائياتك الشخصية</b>\n\n"
        f"🔢 <b>عدد الترجمات:</b> {stats['translations']:,}\n"
        f"📝 <b>الأحرف المترجمة:</b> {stats['chars_translated']:,}\n"
        f"📅 <b>عضو منذ:</b> {usage_days} يوم\n"
        f"📈 <b>متوسط يومي:</b> {avg_per_day:.1f} ترجمة\n"
        f"🕒 <b>آخر استخدام:</b> {stats['last_use'].strftime('%Y-%m-%d %H:%M')}\n\n"
        f"⭐ <b>متوسط الأحرف:</b> {stats['chars_translated'] // max(stats['translations'], 1):,} حرف/ترجمة\n\n"
        "🐉 استمر في الترجمة! أنت رائع!"
    )
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)

async def language_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show supported languages"""
    lang_text = (
        "🌐 <b>اللغات المدعومة</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "<b>الترجمة الثنائية الكاملة:</b>\n\n"
        "🇫🇷 <b>الفرنسية</b> ↔️ <b>العربية</b> 🇸🇦\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ <b>المميزات اللغوية:</b>\n\n"
        "✅ الفرنسية الفصحى والعامية\n"
        "✅ العربية الفصحى\n"
        "✅ اللهجات العربية المختلفة\n"
        "✅ تصحيح الأخطاء الإملائية\n"
        "✅ فهم النصوص المختلطة\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔜 <b>قريباً:</b>\n"
        "• الإنجليزية\n"
        "• الإسبانية\n"
        "• المزيد من اللغات!\n\n"
        "💡 اقتراحات؟ راسل @anes_miih19"
    )
    
    await update.message.reply_text(lang_text, parse_mode=ParseMode.HTML)

async def about_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """About the bot"""
    about_text = (
        "ℹ️ <b>حول Goku Translation Bot</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🐉 <b>من أنا؟</b>\n"
        "أنا بوت ترجمة ذكي يستخدم أحدث\n"
        "تقنيات الذكاء الاصطناعي لتقديم\n"
        "ترجمات دقيقة وسريعة!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔧 <b>التقنيات:</b>\n"
        "• Google Gemini 2.0 Flash\n"
        "• Python Telegram Bot API\n"
        "• معالجة اللغات الطبيعية\n"
        "• خوارزميات تصحيح ذكية\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ <b>القدرات الخاصة:</b>\n"
        "🎯 ترجمة ثنائية الاتجاه\n"
        "🔍 كشف اللغة التلقائي\n"
        "✏️ تصحيح الأخطاء الإملائية\n"
        "📊 تتبع الإحصائيات\n"
        "🛡️ حماية من الإفراط\n"
        "🎨 واجهة تفاعلية\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "👨‍💻 <b>المطور:</b>\n"
        "@anes_miih19 ✨\n\n"
        "📅 <b>النسخة:</b> 3.0 Final\n"
        "📍 <b>التوبيك:</b> #473\n\n"
        "💬 <b>للتواصل والاقتراحات:</b>\n"
        "راسل @anes_miih19"
    )
    
    await update.message.reply_text(about_text, parse_mode=ParseMode.HTML)

async def ping_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test command to check bot status"""
    try:
        await update.message.reply_text(
            "✅ <b>اختبار البوت ناجح!</b>\n\n"
            "🐉 <b>Goku Bot</b> يعمل بشكل طبيعي\n"
            "📡 الحالة: نشط ومستعد للترجمة!\n\n"
            "👨‍💻 المطور: @anes_miih19",
            parse_mode=ParseMode.HTML
        )
        logger.info(f"Ping successful by user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Ping failed: {e}")
        await update.message.reply_text(
            f"❌ <b>فشل الاختبار</b>\n\n"
            f"الخطأ: <code>{str(e)[:200]}</code>\n\n"
            "تواصل مع @anes_miiih19",
            parse_mode=ParseMode.HTML
        )

# ========== CALLBACK QUERY HANDLER ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses"""
    query = update.callback_query
    await query.answer()
    
    class TempUpdate:
        def __init__(self, msg):
            self.message = msg
            self.effective_user = msg.from_user
            self.effective_chat = msg.chat
    
    temp_update = TempUpdate(query.message)
    
    handlers = {
        "help": help_cmd,
        "stats": stats_cmd,
        "languages": language_cmd,
        "about": about_cmd
    }
    
    if query.data in handlers:
        await handlers[query.data](temp_update, context)

# ========== MAIN MESSAGE HANDLER ==========
@rate_limit(max_per_minute=20)
async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main message handler - Available for all users"""
    msg = update.message
    chat = update.effective_chat
    
    # Basic validation
    if not (chat and msg):
        return
    
    user = update.effective_user
    user_text = (msg.text or "").strip()
    
    if not user_text:
        await msg.reply_text("⚠️ أرسل نصاً للترجمة.")
        return
    
    # Check for special commands (requires bot name)
    special_response = await handle_special_command(user_text, user.first_name)
    if special_response:
        await msg.reply_text(special_response, parse_mode=ParseMode.HTML)
        return
    
    # Check text length
    if len(user_text) > 8000:
        await msg.reply_text(
            f"⚠️ <b>النص طويل جداً!</b>\n\n"
            f"الحد الأقصى: 8000 حرف\n"
            f"نصك: {len(user_text):,} حرف\n\n"
            f"قسّم النص إلى أجزاء أصغر.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=chat.id,
        action=ChatAction.TYPING
    )
    
    # Translate
    translated, direction = await smart_translate(user_text, user.id)
    
    # Format and send response
    if direction == "❌":
        # Error case
        await msg.reply_text(translated)
        return
    
    # Success case - split if needed
    MAX_LEN = 4000
    
    if len(translated) <= MAX_LEN:
        final_text = f"{direction}\n\n{translated}"
        await msg.reply_text(final_text)
    else:
        # Smart splitting
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs first
        paragraphs = translated.split('\n\n')
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= MAX_LEN:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If single paragraph is too long, split by sentences
                if len(para) > MAX_LEN:
                    sentences = para.split('. ')
                    temp_chunk = ""
                    for sent in sentences:
                        if len(temp_chunk) + len(sent) + 2 <= MAX_LEN:
                            temp_chunk += sent + ". "
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            temp_chunk = sent + ". "
                    if temp_chunk:
                        current_chunk = temp_chunk
                    else:
                        current_chunk = ""
                else:
                    current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Send chunks
        for i, chunk in enumerate(chunks, 1):
            if i == 1:
                header = f"{direction} <b>[الجزء {i}/{len(chunks)}]</b>\n\n"
            else:
                header = f"<b>[الجزء {i}/{len(chunks)}]</b>\n\n"
            
            await msg.reply_text(
                header + chunk,
                parse_mode=ParseMode.HTML
            )
            
            # Show typing for next chunk
            if i < len(chunks):
                await context.bot.send_chat_action(
                    chat_id=chat.id,
                    action=ChatAction.TYPING
                )

# ========== ERROR HANDLER ==========
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and notify user"""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ <b>حدث خطأ!</b>\n\n"
            "تم تسجيل الخطأ وسيتم إصلاحه.\n"
            "حاول مرة أخرى أو تواصل مع @anes_miiih19",
            parse_mode=ParseMode.HTML
        )

# ========== MAIN FUNCTION ==========
def main():
    """Start the bot"""
    logger.info("🚀 Starting Goku Translation Bot v3.0 Final...")
    
    # Build application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("language", language_cmd))
    app.add_handler(CommandHandler("about", about_cmd))
    app.add_handler(CommandHandler("ping", ping_bot))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Start bot
    logger.info("✅ Bot is running!")
    print("\n" + "="*70)
    print("🐉 GOKU TRANSLATION BOT v3.0 FINAL")
    print("="*70)
    print("✅ Status: ONLINE & READY")
    print("🔧 Mode: Polling")
    print("📊 Logging: Enabled (bot.log)")
    print("🌐 Languages: French ↔️ Arabic")
    print("🎯 Scope: Available for all users")
    print("✨ Features: Auto-correction, Smart detection")
    print("👨‍💻 Developer: @anes_miih19")
    print("="*70 + "\n")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
