import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from instagram_downloader import download_instagram_content
import shutil
from flask import Flask
from threading import Thread

# 1. تنظیمات وب‌سرور برای بیدار نگه داشتن ربات در Render
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    # Render پورت را در متغیر محیطی PORT قرار می‌دهد
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. تنظیمات ربات
TOKEN = os.environ.get("7705251196:AAF_FrSB3316Nti4_BNgFnnf4TJqNZp5iKI")
if not TOKEN:
    print("Error: No Token Found")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context) -> None:
    await update.message.reply_text('👋 سلام! من ربات دانلودر اینستاگرام هستم. لینک بفرستید!')

async def handle_instagram_link(update: Update, context) -> None:
    url = update.message.text
    chat_id = update.message.chat_id
    
    if "instagram.com" not in url:
        await update.message.reply_text("لطفاً لینک صحیح اینستاگرام بفرستید.")
        return

    msg = await update.message.reply_text("⏳ در حال دانلود...")
    downloaded_files = download_instagram_content(url, chat_id)
    await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)

    if downloaded_files and not downloaded_files[0].startswith(("متاسفانه", "لطفاً")):
        for file_path in downloaded_files:
            try:
                if file_path.endswith(('.jpg', '.png')):
                    await update.message.reply_photo(open(file_path, 'rb'))
                elif file_path.endswith('.mp4'):
                    await update.message.reply_video(open(file_path, 'rb'))
            except Exception as e:
                logger.error(e)
        await update.message.reply_text("✅ تمام شد.")
    else:
        await update.message.reply_text(f"❌ خطا: {downloaded_files[0] if downloaded_files else 'ناشناخته'}")

    # پاکسازی
    if os.path.exists(f"downloads/{chat_id}"):
        shutil.rmtree(f"downloads/{chat_id}")

def main() -> None:
    keep_alive() # اجرای سرور وب در پس‌زمینه
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'instagram\.com'), handle_instagram_link))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    if not os.path.exists("downloads"): os.makedirs("downloads")
    main()