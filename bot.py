from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

df = pd.read_excel("filiallar.xlsx")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🔍 Филиалларни қидириш"],
        ["ℹ️ Ёрдам"]
    ]

    context.user_data.clear()

    await update.message.reply_text(
        "🏥 ВАКСИНА МЕД АХБОРОТ БОТИ\n\nКеракли бўлимни танланг:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def search_filial(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    # Асосий меню
    if text == "🔍 Филиалларни қидириш":

        keyboard = [
            ["🔍 Номи бўйича қидириш"],
            ["🔢 Рақами бўйича қидириш"],
            ["🏢 Район бўйича қидириш"],
            ["📄 Excel файлни олиш"],
            ["⬅️ Орқага"]
        ]

        await update.message.reply_text(
            "Қидириш турини танланг:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )
        return

    # Орқага
    if text == "⬅️ Орқага":
        await start(update, context)
        return

    # Ёрдам
    if text == "ℹ️ Ёрдам":
        await update.message.reply_text(
            "Филиалларни номи, рақами ёки райони бўйича қидириш мумкин."
        )
        return

    # Excel файл
    if text == "📄 Excel файлни олиш":
        await update.message.reply_document(
            document=open("filiallar.xlsx", "rb")
        )
        return

    # Номи бўйича қидириш
    if text == "🔍 Номи бўйича қидириш":
        context.user_data["mode"] = "name"

        await update.message.reply_text(
            "Филиал номини киритинг.\n\nМасалан: ТАШМИ ёки ДАРХОН"
        )
        return

    # Рақами бўйича қидириш
    if text == "🔢 Рақами бўйича қидириш":
        context.user_data["mode"] = "number"

        await update.message.reply_text(
            "Филиал рақамини киритинг.\n\nМасалан: 6 ёки 6-ФИЛИАЛ"
        )
        return

    # Район бўйича қидириш
    if text == "🏢 Район бўйича қидириш":
        context.user_data["mode"] = "district"

        await update.message.reply_text(
            "Район номини киритинг."
        )
        return

    mode = context.user_data.get("mode")

    if not mode:
        await update.message.reply_text(
            "Аввал қидириш турини танланг."
        )
        return

    text_upper = text.upper()

    # Агар филиал номи тугмасини босса
    selected = df[
        df["Филиал номи"].astype(str).str.upper() == text_upper
    ]

    if not selected.empty:

        row = selected.iloc[0]

        msg = (
            f"🏪 {row['Филиал рақами']}\n\n"
            f"📛 Номи: {row['Филиал номи']}\n"
            f"🏢 Район: {row['Район']}\n"
            f"📍 Манзил: {row['Манзил']}\n"
            f"📞 Телефон: {row['Телефон']}"
        )

        await update.message.reply_text(msg)
        return

    # Номи бўйича
    if mode == "name":

        result = df[
            df["Филиал номи"]
            .astype(str)
            .str.upper()
            .str.contains(text_upper, na=False)
        ]

        if result.empty:
            await update.message.reply_text(
                "❌ Филиал топилмади."
            )
            return

        # Бир нечта топилса тугмалар чиқарамиз
        if len(result) > 1:

            keyboard = []

            for _, row in result.iterrows():
                keyboard.append([str(row["Филиал номи"])])

            keyboard.append(["⬅️ Орқага"])

            await update.message.reply_text(
                "Қуйидаги филиаллар топилди:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard,
                    resize_keyboard=True
                )
            )
            return

    # Рақами бўйича
    elif mode == "number":

        if text.isdigit():
            text_upper = f"{text}-ФИЛИАЛ"

        result = df[
            df["Филиал рақами"]
            .astype(str)
            .str.upper()
            == text_upper
        ]

    # Район бўйича
    elif mode == "district":

        result = df[
            df["Район"]
            .astype(str)
            .str.upper()
            .str.contains(text_upper, na=False)
        ]

    else:
        result = pd.DataFrame()

    if result.empty:
        await update.message.reply_text(
            "❌ Филиал топилмади."
        )
        return

    for _, row in result.iterrows():

        msg = (
            f"🏪 {row['Филиал рақами']}\n\n"
            f"📛 Номи: {row['Филиал номи']}\n"
            f"🏢 Район: {row['Район']}\n"
            f"📍 Манзил: {row['Манзил']}\n"
            f"📞 Телефон: {row['Телефон']}"
        )

        await update.message.reply_text(msg)


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        search_filial
    )
)

print("Bot ishga tushdi...")

app.run_polling()