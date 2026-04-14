import phonenumbers
from phonenumbers import geocoder, carrier
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ⚠️ YAHAN APNA TOKEN DAAL (temporary testing)
TOKEN = "8639441803:AAEXuJS9lLZb2GIvyC8CpclT1lALccgOhCs"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send number like +919876543210")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text

    try:
        parsed = phonenumbers.parse(number)
        valid = phonenumbers.is_valid_number(parsed)
        country = geocoder.description_for_number(parsed, "en")
        sim = carrier.name_for_number(parsed, "en")

        msg = f"""
📞 {number}
✅ Valid: {valid}
🌍 Country: {country}
📡 Carrier: {sim}
"""
        await update.message.reply_text(msg)

    except:
        await update.message.reply_text("Invalid number!")

app = ApplicationBuilder().token(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).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, check))

print("BOT RUNNING...")
app.run_polling()
