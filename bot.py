import os
import gdown
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import asyncio

# Настройки
TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # будет использоваться ниже
PORT = int(os.environ.get('PORT', 10000))

# Flask приложение
app = Flask(__name__)

# Telegram Application
telegram_app = Application.builder().token(TOKEN).build()

# Прямые ссылки на файлы на Google Диске
FILE_URLS = {
    "smile_pic.jpg": "https://drive.google.com/uc?id=1vH_McsvkRbUU5LWY307NO0pB-cAF_Ble",
    "help_pic.jpg": "https://drive.google.com/uc?id=1isSktQGhQxmvydIwpGJ8K_8oRGMK-0vB",
    "about_pic.jpg": "https://drive.google.com/uc?id=18ac1Lxs0YdFF0Jg-Zl1XRc4_AARRyP7C",
    "bron_pic.jpg": "https://drive.google.com/uc?id=1TrH4GCkFVAwEzf_vJ5FcqjlmrMxIl_u3",
    "bonus_pic.jpg": "https://drive.google.com/uc?id=1o-x6e2meNsmQyKIQGUEUsO1RtC4spTSC",
    "anketa_pic.jpg": "https://drive.google.com/uc?id=12lx9dDl7WuaG1he6GDWAdENLvUGyiCBO",
}
MENU_PDF_URL = "https://raw.githubusercontent.com/your_username/your_repository/main/menu.pdf"

async def download_file_if_needed(filename, url):
    if not os.path.exists(filename):
        gdown.download(url, filename, quiet=True)

NAME = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await download_file_if_needed('smile_pic.jpg', FILE_URLS["smile_pic.jpg"])
    with open('smile_pic.jpg', 'rb') as photo:
        await update.message.reply_photo(photo=photo, caption="Привет! 👋 Я чат-бот «Не Усложняй». Как тебя зовут?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await show_main_menu(update, context)
    return -1

async def show_main_menu(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    await download_file_if_needed('help_pic.jpg', FILE_URLS["help_pic.jpg"])
    keyboard = [
        [InlineKeyboardButton("О нас ✴️", callback_data='about'), InlineKeyboardButton("Меню 📋", callback_data='menu')],
        [InlineKeyboardButton("Забронировать стол 📞", callback_data='book')],
        [InlineKeyboardButton("Бонусная программа 💰🎁", callback_data='bonus')],
        [InlineKeyboardButton("Помоги нам стать лучше 🙏", callback_data='feedback')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    with open('help_pic.jpg', 'rb') as photo:
        caption = f"{context.user_data.get('name', 'Друг')}, я могу быть очень полезным! Что тебя интересует? 😉"
        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_photo(photo=photo, caption=caption, reply_markup=reply_markup)
        else:
            await update_or_query.message.reply_photo(photo=photo, caption=caption, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'about':
        await download_file_if_needed('about_pic.jpg', FILE_URLS["about_pic.jpg"])
        keyboard = [
            [InlineKeyboardButton("Яндекс Карты 🗺️", url="https://yandex.ru/maps/-/CHFWQPPa")],
            [InlineKeyboardButton("2ГИС Карты 🏙️", url="https://2gis.ru/irkutsk/geo/70000001039853425")],
            [InlineKeyboardButton("Instagram 📸", url="https://www.instagram.com/nu_irk1?igsh=MW15OWU5NGJ6ZDVnMw==")],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        with open('about_pic.jpg', 'rb') as photo:
            await query.message.reply_photo(
                photo=photo,
                caption="Мы рады видеть тебя в нашем уютном заведении! 🌟",
                reply_markup=reply_markup
            )

    elif data == 'book':
        await download_file_if_needed('bron_pic.jpg', FILE_URLS["bron_pic.jpg"])
        keyboard = [[InlineKeyboardButton("Назад ↩️", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        with open('bron_pic.jpg', 'rb') as photo:
            await query.message.reply_photo(
                photo=photo,
                caption="Для брони, пожалуйста, позвоните: +79148985744",
                reply_markup=reply_markup
            )

    elif data == 'menu':
        keyboard = [
            [InlineKeyboardButton("Открыть меню в браузере 🌐", url=MENU_PDF_URL)],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        await query.message.reply_text("Нажмите на кнопку ниже, чтобы открыть меню:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'bonus':
        await download_file_if_needed('bonus_pic.jpg', FILE_URLS["bonus_pic.jpg"])
        keyboard = [
            [InlineKeyboardButton("Регистрация бонусной карты 📝", url="https://iiko.biz/L/075535")],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        with open('bonus_pic.jpg', 'rb') as photo:
            await query.message.reply_photo(photo=photo, caption="Бонусы! 🎁", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'feedback':
        await download_file_if_needed('anketa_pic.jpg', FILE_URLS["anketa_pic.jpg"])
        keyboard = [
            [InlineKeyboardButton("Заполнить анкету 📝", url="https://docs.google.com/forms/d/e/1FAIpQLSeiTU3ouHFEyhRMCRh_cpVpD_Dn5laaLdtFzP8Nx8uni8c1Rw/viewform")],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        with open('anketa_pic.jpg', 'rb') as photo:
            await query.message.reply_photo(photo=photo, caption="Заполни анкету и получи бонусы! 💰", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'back':
        await show_main_menu(query, context)

# Webhook endpoint
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return "ok", 200

# Установка Webhook при запуске
@app.before_first_request
def set_webhook():
    url = f"{WEBHOOK_URL}/{TOKEN}"
    asyncio.run(telegram_app.bot.set_webhook(url))

# Регистрация хендлеров
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_name))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

# Запуск Flask-сервера
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
