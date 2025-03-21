import os
import gdown
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import TimedOut

# Получаем токен из переменных окружения
TOKEN = os.environ.get("TOKEN")

# Прямые ссылки на файлы на Google Диске
FILE_URLS = {
    "smile_pic.jpg": "https://drive.google.com/uc?id=1vH_McsvkRbUU5LWY307NO0pB-cAF_Ble",
    "help_pic.jpg": "https://drive.google.com/uc?id=1isSktQGhQxmvydIwpGJ8K_8oRGMK-0vB",
    "about_pic.jpg": "https://drive.google.com/uc?id=18ac1Lxs0YdFF0Jg-Zl1XRc4_AARRyP7C",
    "bron_pic.jpg": "https://drive.google.com/uc?id=1TrH4GCkFVAwEzf_vJ5FcqjlmrMxIl_u3",
    "bonus_pic.jpg": "https://drive.google.com/uc?id=1o-x6e2meNsmQyKIQGUEUsO1RtC4spTSC",
    "anketa_pic.jpg": "https://drive.google.com/uc?id=12lx9dDl7WuaG1he6GDWAdENLvUGyiCBO",
    "menu.pdf": "https://drive.google.com/uc?id=1xOz_D8Su0rBVeP5w_c1XeioqEHFdnmNe",
}

# Функция для скачивания файла при необходимости
async def download_file_if_needed(filename, url):
    if not os.path.exists(filename):
        gdown.download(url, filename, quiet=True)

# Состояние для запроса имени
NAME = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await download_file_if_needed('smile_pic.jpg', FILE_URLS["smile_pic.jpg"])

    with open('smile_pic.jpg', 'rb') as photo:
        await update.message.reply_photo(photo=photo, caption="Привет! 👋 Я чат-бот «Не Усложняй». Как тебя зовут?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.text
    context.user_data['name'] = user_name
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
                caption="Мы рады видеть тебя в нашем уютном заведении! 🌟 Подписывайся на соцсети и оставляй отзывы! 💬",
                reply_markup=reply_markup
            )

    elif data == 'book':
        keyboard = [
            [InlineKeyboardButton("Скопировать номер 📋", callback_data='copy_number')],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            text="Для брони, пожалуйста, позвоните: +79148985744",
            reply_markup=reply_markup
        )

    elif data == 'copy_number':
        await query.message.reply_text("Скопируйте номер: +79148985744")

    elif data == 'menu':
        keyboard = [
            [InlineKeyboardButton("Открыть меню в браузере 🌐", url=FILE_URLS["menu.pdf"])],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Нажмите на кнопку ниже, чтобы открыть меню:", reply_markup=reply_markup)

    elif data == 'bonus':
        await download_file_if_needed('bonus_pic.jpg', FILE_URLS["bonus_pic.jpg"])
        keyboard = [
            [InlineKeyboardButton("Регистрация бонусной карты 📝", url="https://iiko.biz/L/075535")],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        with open('bonus_pic.jpg', 'rb') as photo:
            await query.message.reply_photo(
                photo=photo,
                caption="Бонусы: 🎁 15% скидка именинникам, 5% кэшбек, 600 бонусов при регистрации, 150 за анкету!",
                reply_markup=reply_markup
            )

    elif data == 'feedback':
        await download_file_if_needed('anketa_pic.jpg', FILE_URLS["anketa_pic.jpg"])
        keyboard = [
            [InlineKeyboardButton("Заполнить анкету 📝", url="https://docs.google.com/forms/d/e/1FAIpQLSeiTU3ouHFEyhRMCRh_cpVpD_Dn5laaLdtFzP8Nx8uni8c1Rw/viewform")],
            [InlineKeyboardButton("Назад ↩️", callback_data='back')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        with open('anketa_pic.jpg', 'rb') as photo:
            await query.message.reply_photo(
                photo=photo,
                caption="Заполни анкету и получи бонусы! 💰",
                reply_markup=reply_markup
            )

    elif data == 'back':
        await show_main_menu(query, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Произошла ошибка: {context.error}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_name))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
