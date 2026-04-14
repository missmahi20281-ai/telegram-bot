import os
import sqlite3
import phonenumbers
import re
import speech_recognition as sr

from phonenumbers import geocoder, carrier
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

TOKEN = os.getenv("8639441803:AAEXuJS9lLZb2GIvyC8CpclT1lALccgOhCs")

# ===== DATABASE =====
conn = sqlite3.connect("ultimate.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS reports (number TEXT PRIMARY KEY, count INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS history (user_id INTEGER, number TEXT)")
conn.commit()

# ===== AI ANALYSIS =====
def ai_score(number, spam):
    score = spam * 2

    if re.search(r'(.)\1{5,}', number):
        score += 3

    if score >= 8:
        return score, "🚨 HIGH RISK"
    elif score >= 4:
        return score, "⚠️ SUSPICIOUS"
    else:
        return score, "✅ SAFE"

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Ultimate AI Bot Ready!\nSend number or voice")

# ===== NUMBER CHECK =====
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    user = update.effective_user

    try:
        parsed = phonenumbers.parse(number)

        valid = phonenumbers.is_valid_number(parsed)
        country = geocoder.description_for_number(parsed, "en")
        sim = carrier.name_for_number(parsed, "en")

        cursor.execute("INSERT INTO history VALUES (?, ?)", (user.id, number))
        conn.commit()

        cursor.execute("SELECT count FROM reports WHERE number=?", (number,))
        res = cursor.fetchone()
        spam = res[0] if res else 0

        score, result = ai_score(number, spam)

        keyboard = [[InlineKeyboardButton("🚨 Report Spam", callback_data=f"report|{number}")]]

        msg = f"""
📞 {number}
✅ Valid: {valid}
🌍 {country}
📡 {sim}

🚨 Reports: {spam}
🧠 AI Score: {score}/10
{result}
"""

        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    except:
        await update.message.reply_text("❌ Invalid number")

# ===== VOICE =====
async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    await file.download_to_drive("voice.ogg")

    r = sr.Recognizer()

    try:
        with sr.AudioFile("voice.ogg") as source:
            audio = r.record(source)
            text = r.recognize_google(audio)

        await update.message.reply_text(f"🧠 Text:\n{text}")

    except:
        await update.message.reply_text("❌ Voice error")

# ===== REPORT =====
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    number = query.data.split("|")[1]

    cursor.execute("SELECT count FROM reports WHERE number=?", (number,))
    res = cursor.fetchone()

    if res:
        cursor.execute("UPDATE reports SET count=? WHERE number=?", (res[0]+1, number))
    else:
        cursor.execute("INSERT INTO reports VALUES (?, ?)", (number, 1))

    conn.commit()
    await query.edit_message_text("🚨 Reported!")

# ===== MAIN =====
app = ApplicationBuilder().token(8639441803:AAEXuJS9lLZb2GIvyC8CpclT1lALccgOhCs).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check))
app.add_handler(MessageHandler(filters.VOICE, voice))
app.add_handler(CallbackQueryHandler(report, pattern="report\\|"))

print("🔥 ULTIMATE BOT RUNNING...")
app.run_polling()
