#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

try:
    from google.cloud import translate_v2
except ImportError:
    print("Error: google-cloud-translate not installed. Run: pip install -r requirements.txt")
    exit(1)

import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ChatAction

# ==================== الإعداد ====================

load_dotenv()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== Google Translate ==========
translate_client = None
try:
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path and os.path.exists(creds_path):
        translate_client = translate_v2.Client()
        logger.info("✅ Google Cloud Translate initialized successfully")
    else:
        logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS not set or file not found")
except Exception as e:
    logger.error(f"❌ Google Translate init failed: {e}")

# ========== Gemini ==========
gemini_model = None
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel("gemini-2.5-flash-lite")
        logger.info("✅ Gemini AI initialized successfully")
    else:
        logger.warning("⚠️ GOOGLE_API_KEY not set")
except Exception as e:
    logger.error(f"❌ Gemini init failed: {e}")

user_stats: Dict[int, Dict[str, Any]] = {}

# ==================== الأدوات ====================

def detect_language(text: str) -> str:
    """Detect Arabic or French"""
    return "ar" if re.search(r"[\u0600-\u06FF]", text) else "fr"


def is_ai_question(text: str) -> tuple[bool, str]:
    """Detect if message starts with Goku/Gukou prefixes"""
    prefixes = ["قوكو", "غوكو", "ڨوكو", "غوغو", "goku", "gukou", "gogo", "gougou"]
    txt = text.strip()
    for p in prefixes:
        if txt.lower().startswith(p.lower()):
            return True, txt[len(p):].strip()
    return False, ""


def is_creator_question(text: str) -> bool:
    """Detect if question is asking 'who created you'"""
    t = re.sub(r"[؟?!.…,:;]+", "", text.strip().lower())
    patterns = [
        "من الذي صنعك", "من صنعك", "من خالقك", "من مبرمجك", "من انشأك",
        "من طورك", "من الذي طورك", "من الذي انشأك", "من برمجك",
        "qui t'a créé", "qui t a créé", "qui t'a fait",
        "qui est ton créateur", "qui est ton programmeur",
        "qui t'a développé", "qui t'a programmé"
    ]
    return any(p in t for p in patterns)


def get_creator_response(_: str) -> str:
    """Return the creator answer only"""
    return "صنعني المبرمج anes_miiih19@"


async def ask_gemini(question: str) -> Optional[str]:
    """Ask Gemini and return plain text only"""
    try:
        if not gemini_model:
            return None
        response = gemini_model.generate_content(question)
        if getattr(response, "text", None):
            # تنظيف أي ترميز HTML مثل &#39;
            clean = response.text.replace("&#39;", "'").strip()
            return clean
        return None
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return None


async def translate_text(text: str, source: str, target: str, user_id: int) -> str:
    """Translate with Google Cloud"""
    try:
        result = translate_client.translate(text, source_language=source, target_language=target)
        translated = result["translatedText"].replace("&#39;", "'")
        user_stats.setdefault(user_id, {"translations": 0, "chars": 0})
        user_stats[user_id]["translations"] += 1
        user_stats[user_id]["chars"] += len(text)
        return translated
    except Exception as e:
        logger.error(e)
        return f"❌ خطأ في الترجمة: {str(e)}"


# ==================== المعالجة ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (update.message.text or "").strip()
    user_id = user.id
    await update.message.chat.send_action(ChatAction.TYPING)

    # --- أسئلة ذكاء اصطناعي ---
    is_ai, q = is_ai_question(text)
    if is_ai and q:
        if is_creator_question(q):
            await update.message.reply_text(get_creator_response(q))
        else:
            answer = await ask_gemini(q)
            await update.message.reply_text(answer or "❌ لم أتمكن من الإجابة حالياً.")
        return

    # --- سؤال بعلامة استفهام ---
    if text.endswith(("?", "؟")):
        if is_creator_question(text):
            await update.message.reply_text(get_creator_response(text))
        else:
            answer = await ask_gemini(text)
            await update.message.reply_text(answer or "❌ لم أتمكن من الإجابة حالياً.")
        return

    # --- ترجمة تلقائية ---
    src = detect_language(text)
    tgt = "fr" if src == "ar" else "ar"
    translated = await translate_text(text, src, tgt, user_id)
    await update.message.reply_text(translated)


# ==================== الأوامر ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 أهلاً! أرسل نصاً لأترجمه أو سؤالاً للإجابة عليه.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل نصاً بالعربية أو الفرنسية لأترجمه مباشرة.\n"
                                    "ابدأ الرسالة بـ 'قوكو' لطرح سؤال ذكاء اصطناعي.")


# ==================== التشغيل ====================

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN مفقود.")
        return

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Goku bot started.")
    app.run_polling()

if __name__ == "__main__":
    main()
