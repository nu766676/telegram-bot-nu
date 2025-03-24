import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# Логи
logging.basicConfig(level=logging.INFO)

# Конфигурация
TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

RAW_BASE = "https://raw.githubusercontent.com/nu766676/telegram-bot-nu/main"
FILE_URLS = {
    "smile": f"{RAW_BASE}/smile_pic.jpg",
    "help": f"{RAW_BASE}/help_pic.jpg",
    "about": f"{RAW_BASE}/about_pic.jpg",
    "bron": f"{RAW_BASE}/bron_pic.jpg",
    "bonus": f"{RAW_BASE}/bonus_pic.jpg",
    "anketa": f"{RAW_BASE}/anketa_pic.jpg",
    "menu": f"{RAW_BASE}/menu.pdf",
}

# Flask
app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

NAME = range(1)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=FILE_URLS["smile"],
        caption="Привет! 👋 Я чат-бот «Не Усложняй». Как тебя зовут?"
    )
    return NAME

# Имя
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await show_main_menu(update, context)
    return -1

# Главное меню
async def show_main_menu(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("О нас ✴️", callback_data='about'),
         InlineKeyboardButton("Меню 📋", callback_data='menu')],
        [InlineKeyboardButton("Забронировать стол 📞", callback_data='book')],
        [InlineKeyboardButton("Бонусная программа 💰🎁", callback_data='bonus')],
        [InlineKeyboardButton("Помоги нам стать лучше 🙏", callback_data='feedback')],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    caption = f"{context.user_data.get('name', 'Друг')}, я могу быть полезным! Что тебя интересует? 😉"

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_photo(FILE_URLS["help"], caption=caption, reply_markup=markup)
    else:
        await update_or_query.message.reply_photo(FILE_URLS["help"], caption=caption, reply_markup=markup)

# Кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'about':
        kb = [
            [InlineKeyboardButton("Яндекс Карты 🗺️", url="https://yandex.ru/maps/-/CHFWQPPa")],
            [InlineKeyboardButton("2ГИС 🏙️", url="https://2gis.ru/irkutsk/geo/70000001039853425")],
            [InlineKeyboardButton("Instagram 📸", url="https://www.instagram.com/nu_irk1")],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        await query.message.reply_photo(FILE_URLS["about"], caption="Мы рады видеть тебя! 🌟", reply_markup=InlineKeyboardMarkup(kb))

    elif data == 'book':
        await query.message.reply_photo(FILE_URLS["bron"], caption="Для брони: +79148985744", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Назад ↩️", callback_data='back')]]))

    elif data == 'menu':
        await query.message.reply_text("Нажмите кнопку ниже для просмотра меню:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Открыть меню 🌐", url=FILE_URLS["menu"])],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]))

    elif data == 'bonus':
        await query.message.reply_photo(FILE_URLS["bonus"], caption="Бонусы! 🎁", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Зарегистрировать карту 📝", url="https://iiko.biz/L/075535")],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]))

    elif data == 'feedback':
        await query.message.reply_photo(FILE_URLS["anketa"], caption="Заполни анкету и получи бонус! 💰", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Заполнить анкету 📝", url="https://docs.google.com/forms/...")],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]))

    elif data == 'back':
        await show_main_menu(query, context)

# Webhook endpoint
@app.route(f'/{TOKEN}', methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        loop.create_task(telegram_app.process_update(update))
    except Exception as e:
        logging.exception("Ошибка в webhook:")
        return "Internal Server Error", 500
    return "OK", 200

# Инициализация
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")
    logging.info("Webhook установлен!")

# Хендлеры
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_name))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

# Запуск
if __name__ == '__main__':
    loop.run_until_complete(startup())
    app.run(host='0.0.0.0', port=PORT)
