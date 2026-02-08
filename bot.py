import os
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---------- СОСТОЯНИЯ ----------
users = {}

STEP_NAME = 1
STEP_FEELING = 2
STEP_FREE_TEXT = 3
STEP_RHYTHM = 4
STEP_DONE = 5

# ---------- НИЖНИЕ КНОПКИ ----------
BOTTOM_BUTTONS = [
    ["1️⃣ Наша история", "2️⃣ Секрет листьев", "3️⃣ Магазин"],
    ["4️⃣ Косметика", "5️⃣ Добавки", "6️⃣ Коллаген"],
    ["7️⃣ Контроль веса", "8️⃣ YouTube", "9️⃣ Детокс"]
]

BOTTOM_LINKS = {
    "1️⃣ Наша история": "https://www.evergreenlife.it/ru_ru/nasha-istorija",
    "2️⃣ Секрет листьев": "https://www.evergreenlife.it/ru_ru/olivkovyye-listya#secret",
    "3️⃣ Магазин": "https://www.evergreenlife.it/ru_ru/magazin.html",
    "4️⃣ Косметика": "https://www.evergreenlife.it/ru_ru/magazin/kosmetika.html",
    "5️⃣ Добавки": "https://www.evergreenlife.it/ru_ru/magazin/bad.html",
    "6️⃣ Коллаген": "https://www.evergreenlife.it/ru_ru/magazin/bad/collagene.html",
    "7️⃣ Контроль веса": "https://www.evergreenlife.it/ru_ru/magazin/bad/controllo-del-peso.html",
    "8️⃣ YouTube": "https://www.youtube.com/@EvergreenLifeProducts",
    "9️⃣ Детокс": "https://www.evergreenlife.it/ru_ru/magazin/bad/detoks.html"
}

def build_bottom_keyboard():
    return ReplyKeyboardMarkup(BOTTOM_BUTTONS, resize_keyboard=True)

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users[uid] = {"step": STEP_NAME}

    await update.message.reply_text(
        "Добрый день 🌿\n\n"
        "Меня зовут Оксана — я ваш персональный консультант Olife.\n\n"
        "Как я могу к вам обращаться?",
        reply_markup=build_bottom_keyboard()
    )

# ---------- ТЕКСТ ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()

    if uid not in users:
        return

    step = users[uid]["step"]

    # ----- Нижние кнопки -----
    if text in BOTTOM_LINKS:
        await update.message.reply_text(f"🌿 {BOTTOM_LINKS[text]}")
        return

    # ----- Ввод имени -----
    if step == STEP_NAME:
        users[uid]["name"] = text
        users[uid]["step"] = STEP_FEELING

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("😊 В целом комфортно", callback_data="feel_good")],
            [InlineKeyboardButton("😴 К вечеру нет сил", callback_data="feel_tired")],
            [InlineKeyboardButton("✍️ Свой вариант", callback_data="feel_free")]
        ])

        await update.message.reply_text(
            f"Приятно познакомиться, {text} 🌸\n\n"
            "Как вы себя чувствуете в течение дня?",
            reply_markup=keyboard
        )
        return

    # ----- Свой вариант (текст) -----
    if step == STEP_FREE_TEXT:
        users[uid]["free_text"] = text
        users[uid]["step"] = STEP_RHYTHM

        reply = (
            "🌸 Понимаю вас.\n\n"
            "Когда тело подсказывает, что ему тяжело или испытываются неприятные ощущения, "
            "важно это услышать и уделить себе немного заботы. "
            "Попробуйте дать себе паузу: сделать глубокий вдох, немного размяться, выпить воды или спокойно побыть наедине с собой.\n\n"
            "Даже маленькие шаги к заботе о себе помогают восстановить баланс 💚. "
            "Мне помогает продукция Olife — натуральные ингредиенты мягко поддерживают организм и помогают вернуть энергию и гармонию 🌸, "
            "даже если есть чувствительность или аллергия.\n\n"
            "Познакомиться с нашей продукцией можно здесь:\n"
            "https://www.evergreenlife.it/ru_ru/magazin/bad.html"
        )

        await update.message.reply_text(reply)
        await ask_rhythm(update.message)
        return

# ---------- INLINE КНОПКИ ----------
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # обязательно отвечаем на callback_query

    uid = query.from_user.id
    data = query.data

    if uid not in users:
        return

    # ----- Самочувствие -----
    if data == "feel_good":
        users[uid]["step"] = STEP_RHYTHM
        await query.message.reply_text(
            "🌿 Замечательно 🌸. Рад(а), что вы чувствуете себя в целом хорошо.\n\n"
            "Скажите, пожалуйста, ваш ритм жизни сейчас — скорее активный или спокойный?"
        )
        await ask_rhythm(query.message)
        return

    if data == "feel_tired":
        users[uid]["step"] = STEP_RHYTHM
        await query.message.reply_text(
            "🌿 Понимаю вас…\n"
            "Когда к вечеру нет сил — это очень знакомо. "
            "У меня самой бывали периоды, когда организм словно шепчет: «мне нужна поддержка».\n\n"
            "Какой у вас ритм жизни сейчас — активный или спокойный?"
        )
        await ask_rhythm(query.message)
        return

    if data == "feel_free":
        users[uid]["step"] = STEP_FREE_TEXT
        await query.message.reply_text(
            "Напишите, пожалуйста, своими словами 🌿\n"
            "Я внимательно прочитаю ваш ответ."
        )
        return

    # ----- РИТМ -----
    if data in ("active", "calm"):
        users[uid]["step"] = STEP_DONE
        await query.message.reply_text(
            "🌿 Спасибо, что поделились 🌸\n\n"
            "Я сама заметила: когда начинаешь бережно относиться к себе и поддерживать организм, "
            "он очень быстро откликается.\n\n"
            "Мне в этом помогает продукция Olife — мягко, натурально, без давления. "
            "Это не про «лечить», а про заботу и баланс 💚\n\n"
            "Познакомиться с нашей продукцией можно здесь:\n"
            "https://www.evergreenlife.it/ru_ru/magazin.html"
        )

# ---------- ВОПРОС ПРО РИТМ ----------
async def ask_rhythm(message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Активный", callback_data="active")],
        [InlineKeyboardButton("🌿 Спокойный", callback_data="calm")]
    ])
    await message.reply_text(
        "Ваш ритм жизни сейчас:",
        reply_markup=keyboard
    )

# ---------- ЗАПУСК ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Olife bot запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
