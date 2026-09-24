"""Simple Telegram bot powered by python-telegram-bot.

Required environment variable:
    BOT_TOKEN  Token provided by @BotFather

Install:
    pip install python-telegram-bot

Run:
    python main.py
"""

from __future__ import annotations

import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome a user and show the available commands."""
    if update.message:
        await update.message.reply_text(
            "👋 Hello!\n\n"
            "🤖 Bot Online ✅\n\n"
            "Commands:\n"
            "/help\n"
            "/ping\n"
            "/id\n"
            "/rules"
        )


async def help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Show the bot command reference."""
    if update.message:
        await update.message.reply_text(
            "🛠 Bot Commands\n\n"
            "/start - Start Bot\n"
            "/help - Help\n"
            "/ping - Check Bot\n"
            "/id - Get ID\n"
            "/rules - Group Rules"
        )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check whether the bot is responding."""
    if update.message:
        await update.message.reply_text("🏓 Pong! Bot is working ✅")


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return the current user's Telegram ID."""
    if update.message and update.effective_user:
        await update.message.reply_text(
            f"🆔 Your ID: {update.effective_user.id}"
        )


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the group rules."""
    if update.message:
        await update.message.reply_text(
            "📜 GROUP RULES\n\n"
            "1️⃣ Respect everyone.\n"
            "2️⃣ No spam.\n"
            "3️⃣ No unnecessary fights.\n"
            "4️⃣ Follow admin instructions.\n"
            "5️⃣ Keep the group clean. 💚"
        )


def main() -> None:
    """Build the application and start long polling."""
    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is missing. Add your BotFather token as a secret."
        )

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("id", get_id))
    application.add_handler(CommandHandler("rules", rules))

    logging.info("Bot started successfully.")
    application.run_polling()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    main()