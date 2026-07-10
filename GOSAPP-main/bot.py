# -*- coding: utf-8 -*-
"""
Telegram-бот «Куда обратиться?»
Установка: pip install python-telegram-bot==21.*
Запуск:    TELEGRAM_TOKEN=ваш_токен python bot.py
Токен получить у @BotFather
"""
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

from matcher import classify, format_response
from app import init_db, log_request  # переиспользуем БД статистики

logging.basicConfig(level=logging.INFO)

WELCOME = (
    "👋 Здравствуйте! Я помогу определить, в какой государственный орган обратиться.\n\n"
    "Просто опишите вашу проблему, например:\n"
    "• «Не выплачивают алименты»\n"
    "• «Соседи шумят ночью»\n"
    "• «Не убирают мусор во дворе»\n"
    "• «Работодатель не выплачивает зарплату»"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    cat = classify(user_text)[0]
    log_request(user_text, cat)
    await update.message.reply_text(format_response(cat))


def main():
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise SystemExit("Установите переменную окружения TELEGRAM_TOKEN")

    init_db()
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    application.run_polling()


if name == "__main__":
    main()