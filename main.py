import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# Инициализация Flask
app = Flask(__name__)

# Конфигурация
TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

# URL для файлов
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

# Глобальная переменная для приложения Telegram
telegram_app = None

# Состояния
NAME = range(1)

# ===== Handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_photo(
            photo=FILE_URLS["smile"],
            caption="Привет! 👋 Я чат-бот «Не Усложняй». Как тебя зовут?"
        )
        return NAME
    except Exception as e:
        print(f"Error in start handler: {e}")
        return -1

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await show_main_menu(update, context)
    return -1

async def show_main_menu(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("О нас ✴️", callback_data='about'), 
         InlineKeyboardButton("Меню 📋", callback_data='menu')],
        [InlineKeyboardButton("Забронировать стол 📞", callback_data='book')],
        [InlineKeyboardButton("Бонусная программа 💰🎁", callback_data='bonus')],
        [InlineKeyboardButton("Помоги нам стать лучше 🙏", callback_data='feedback')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    caption = f"{context.user_data.get('name', 'Друг')}, я могу быть очень полезным! Что тебя интересует? 😉"

    try:
        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_photo(
                photo=FILE_URLS["help"],
                caption=caption,
                reply_markup=reply_markup
            )
        else:
            await update_or_query.edit_message_media(
                media=InputMediaPhoto(FILE_URLS["help"])
            )
            await update_or_query.edit_message_caption(
                caption=caption,
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Error showing main menu: {e}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data == 'about':
            await query.message.reply_photo(
                photo=FILE_URLS["about"],
                caption="Мы рады видеть тебя в нашем уютном заведении! 🌟",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Яндекс Карты 🗺️", url="https://yandex.ru/maps/-/CHFWQPPa")],
                    [InlineKeyboardButton("2ГИС Карты 🏙️", url="https://2gis.ru/irkutsk/geo/70000001039853425")],
                    [InlineKeyboardButton("Instagram 📸", url="https://www.instagram.com/nu_irk1")],
                    [InlineKeyboardButton("Назад ↩️", callback_data='back')],
                ])
            )
        elif query.data == 'book':
            await query.message.reply_photo(
                photo=FILE_URLS["bron"],
                caption="Для брони, пожалуйста, позвоните: +79148985744",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Назад ↩️", callback_data='back')]
                ])
            )
        elif query.data == 'menu':
            await query.message.reply_text(
                "Нажмите на кнопку ниже, чтобы открыть меню:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Открыть меню в браузере 🌐", url=FILE_URLS["menu"])],
                    [InlineKeyboardButton("Назад ↩️", callback_data='back')],
                ])
            )
        elif query.data == 'bonus':
            await query.message.reply_photo(
                photo=FILE_URLS["bonus"],
                caption="Бонусы! 🎁",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Регистрация бонусной карты 📝", url="https://iiko.biz/L/075535")],
                    [InlineKeyboardButton("Назад ↩️", callback_data='back')],
                ])
            )
        elif query.data == 'feedback':
            await query.message.reply_photo(
                photo=FILE_URLS["anketa"],
                caption="Заполни анкету и получи бонусы! 💰",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Заполнить анкету 📝", url="https://docs.google.com/forms/...")],
                    [InlineKeyboardButton("Назад ↩️", callback_data='back')],
                ])
            )
        elif query.data == 'back':
            await show_main_menu(query, context)
    except Exception as e:
        print(f"Error in button handler: {e}")

# ===== Webhook Endpoint =====
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return 'Use POST for Telegram updates', 200
    
    try:
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        asyncio.run(telegram_app.process_update(update))
        return 'OK', 200
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return str(e), 500

# ===== Health Check =====
@app.route('/')
def health_check():
    return "Bot is running", 200

# ===== Error Handler =====
@app.errorhandler(500)
def internal_error(e):
    print(f"Server error: {e}")
    return "Internal server error", 500

# ===== Startup =====
async def setup_application():
    global telegram_app
    
    telegram_app = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    telegram_app.add_handler(CommandHandler('start', start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_name))
    telegram_app.add_handler(CallbackQueryHandler(button_handler))
    
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    print(f"Webhook установлен: {WEBHOOK_URL}/webhook")

# ===== Run Application =====
if __name__ == '__main__':
    # Настройка и запуск приложения Telegram
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_application())
    
    # Запуск Flask
    from waitress import serve
    serve(app, host="0.0.0.0", port=PORT)
