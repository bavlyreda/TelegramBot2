import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from telegram.error import TelegramError

# Enable logging to file
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log")]
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Configuration
BOT_TOKEN = "7640023244:AAGuggNq8T6xD6kjb837pldRXh-ikG2HUro"
CHANNEL_USERNAME = "@vlyftblcourseteasers"
FILE_LINK = "https://mega.nz/file/uREGhLaQ#ThbiQhpltsPQ5CR7bhFpT2kuqLt6Hu8a4Mb0VkTUHkg"

# Initialize bot application
application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        is_member = await check_membership(context, user.id)
        if is_member:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Here's your file link! Thanks for joining:\n{FILE_LINK}"
            )
        else:
            keyboard = [[
                InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
                InlineKeyboardButton("Check Membership", callback_data="check_membership"),
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Please join {CHANNEL_USERNAME} to get the file link.\nClick 'Check Membership' after joining.",
                reply_markup=reply_markup,
            )
    except Exception as e:
        logger.error(f"Error in /start for user {user.id}: {e}")

async def check_membership(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """Check if user is in the channel."""
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramError as e:
        logger.error(f"Membership check error for user {user_id}: {e}")
        return False

async def check_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 'Check Membership' button."""
    try:
        query = update.callback_query
        await query.answer()
        user = query.from_user
        chat_id = query.message.chat_id
        is_member = await check_membership(context, user.id)
        if is_member:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Welcome! Here's your file link:\n{FILE_LINK}"
            )
            await query.message.delete()
        else:
            await query.message.reply_text(f"You're not in {CHANNEL_USERNAME}. Join and try again.")
    except Exception as e:
        logger.error(f"Error in check_button for user {query.from_user.id}: {e}")

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /check command."""
    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        is_member = await check_membership(context, user.id)
        if is_member:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"You're a member! Here's your file link:\n{FILE_LINK}"
            )
        else:
            keyboard = [[
                InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"),
                InlineKeyboardButton("Check Membership", callback_data="check_membership"),
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"You're not in {CHANNEL_USERNAME}. Join and click 'Check Membership'.",
                reply_markup=reply_markup,
            )
    except Exception as e:
        logger.error(f"Error in /check for user {user.id}: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error(f"Update {update} caused error {context.error}")

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    global application
    update = Update.de_json(request.get_json(), application.bot)
    await application.process_update(update)
    return "OK"

def create_application():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check_command))
    application.add_handler(CallbackQueryHandler(check_button, pattern="check_membership"))
    application.add_error_handler(error_handler)
    return application

if __name__ == "__main__":
    application = create_application()
    app.run(host="0.0.0.0", port=5000)