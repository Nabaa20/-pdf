import os
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from PIL import Image

TOKEN = os.getenv("BOT_TOKEN")
TEMP_FOLDER = "images"
os.makedirs(TEMP_FOLDER, exist_ok=True)
user_photos = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text("أرسل لي مجموعة صور، وبعدها أرسل كلمة 'تحويل' حتى أحولهم PDF.")

def handle_photo(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1]
    file = context.bot.get_file(photo.file_id)
    file_path = f"{TEMP_FOLDER}/{user_id}_{len(user_photos.get(user_id, []))}.jpg"
    file.download(file_path)
    user_photos.setdefault(user_id, []).append(file_path)
    update.message.reply_text("تم حفظ الصورة. أرسل المزيد أو أكتب 'تحويل'.")

def convert_to_pdf(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    images = user_photos.get(user_id)
    if not images:
        update.message.reply_text("ما عندي صور حتى أحوّلها.")
        return
    pdf_path = f"{TEMP_FOLDER}/{user_id}.pdf"
    image_list = [Image.open(img).convert("RGB") for img in images]
    image_list[0].save(pdf_path, save_all=True, append_images=image_list[1:])
    with open(pdf_path, 'rb') as pdf_file:
        context.bot.send_document(chat_id=update.effective_chat.id, document=pdf_file)
    for img in images:
        os.remove(img)
    os.remove(pdf_path)
    user_photos[user_id] = []
    update.message.reply_text("تم التحويل إلى PDF!")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.command, start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^تحويل$'), convert_to_pdf))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()