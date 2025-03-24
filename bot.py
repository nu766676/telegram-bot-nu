import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# Telegram токен и Webhook URL из переменных окружения
TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Пример: https://your-app-name.onrender.com
PORT = int(os.environ.get('PORT', 10000))

# GitHub RAW-ссылки на изображения и PDF
RAW_BASE = "https://raw.githubusercontent.com/your_username/your_repository/main"
FILE_URLS = {
    "smile": f"{RAW_BASE}/smile_pic.jpg",
    "help": f"{RAW_BASE}/help_pic.jpg",
    "about": f"{RAW_BASE}/about_pic.jpg",
    "bron": f"{RAW_BASE}/bron_pic.jpg",
    "bonus": f"{RAW_BASE}/bonus_pic.jpg",
    "anketa": f"{RAW_BASE}/anketa_pic.jpg",
    "menu": f"{RAW_BASE}/menu.pdf",
}

# Flask-приложение
app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()
NAME = range(1)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(photo=FILE_URLS["smile"], caption="Привет! 👋 Я чат-бот «Не Усложняй». Как тебя зовут?")
    return NAME

# Обработка имени
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await show_main_menu(update, context)
    return -1

# Главное меню
async def show_main_menu(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("О нас ✴️", callback_data='about'), InlineKeyboardButton("Меню 📋", callback_data='menu')],
        [InlineKeyboardButton("Забронировать стол 📞", callback_data='book')],
        [InlineKeyboardButton("Бонусная программа 💰🎁", callback_data='bonus')],
        [InlineKeyboardButton("Помоги нам стать лучше 🙏", callback_data='feedback')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    caption = f"{context.user_data.get('name', 'Друг')}, я могу быть очень полезным! Что тебя интересует? 😉"

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_photo(photo=FILE_URLS["help"], caption=caption, reply_markup=reply_markup)
    else:
        await update_or_query.message.reply_photo(photo=FILE_URLS["help"], caption=caption, reply_markup=reply_markup)

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'about':
        keyboard = [
            [InlineKeyboardButton("Яндекс Карты 🗺️", url="https://yandex.ru/maps/-/CHFWQPPa")],
            [InlineKeyboardButton("2ГИС Карты 🏙️", url="https://2gis.ru/irkutsk/geo/70000001039853425")],
            [InlineKeyboardButton("Instagram 📸", url="https://www.instagram.com/nu_irk1?igsh=MW15OWU5NGJ6ZDVnMw==")],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        await query.message.reply_photo(photo=FILE_URLS["about"],
                                        caption="Мы рады видеть тебя в нашем уютном заведении! 🌟",
                                        reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'book':
        keyboard = [[InlineKeyboardButton("Назад ↩️", callback_data='back')]]
        await query.message.reply_photo(photo=FILE_URLS["bron"],
                                        caption="Для брони, пожалуйста, позвоните: +79148985744",
                                        reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'menu':
        keyboard = [
            [InlineKeyboardButton("Открыть меню в браузере 🌐", url=FILE_URLS["menu"])],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        await query.message.reply_text("Нажмите на кнопку ниже, чтобы открыть меню:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'bonus':
        keyboard = [
            [InlineKeyboardButton("Регистрация бонусной карты 📝", url="https://iiko.biz/L/075535")],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        await query.message.reply_photo(photo=FILE_URLS["bonus"], caption="Бонусы! 🎁", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'feedback':
        keyboard = [
            [InlineKeyboardButton("Заполнить анкету 📝", url="https://docs.google.com/forms/d/e/1FAIpQLSeiTU3ouHFEyhRMCRh_cpVpD_Dn5laaLdtFzP8Nx8uni8c1Rw/viewform")],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        await query.message.reply_photo(photo=FILE_URLS["anketa"], caption="Заполни анкету и получи бонусы! 💰", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'back':
        await show_main_menu(query, context)

# Обработка Webhook-запросов от Telegram
@app.route(f'/{TOKEN}', methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return "ok", 200

# Установка Webhook при запуске
@app.before_first_request
def setup():
    webhook_url = f"{WEBHOOK_URL}/{TOKEN}"
    asyncio.run(telegram_app.bot.set_webhook(webhook_url))

# Регистрация обработчиков
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_name))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

# Запуск Flask-сервера
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
