import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
# Get token from environment variable (for Render)
TOKEN = os.environ.get("BOT_TOKEN")
# Replace with the direct URL of your uploaded image
IMAGE_URL = "YOUR_IMAGE_DIRECT_URL_HERE" 
# The Telegram link for the button
CHANNEL_LINK = "https://t.me/chinabinarysession"

# The bilingual message
MESSAGE_TEXT = (
    "Lost $1,000+ on IQ Option, Binolla, or ExpertOption? I use my own capital to attempt loss recovery for your account.\n\n"
    "خسرت أكثر من 1000 دولار في آي كيو أوبشن أو بينولا أو إكسبرت أوبشن؟ أحاول تعويض خسائرك باستخدام مالي الخاص. تواصل معي"
)

# --- BOT FUNCTIONS ---

async def send_advertisement(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Sends the image, caption, and inline button."""
    # Create the inline button
    keyboard = [[InlineKeyboardButton("Join China Binary Session", url=CHANNEL_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        # Send the photo with caption and button
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=IMAGE_URL,
            caption=MESSAGE_TEXT,
            reply_markup=reply_markup
        )
        logger.info(f"Message sent to chat_id: {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command."""
    chat_id = update.effective_chat.id
    
    # 1. Send the initial message immediately
    await send_advertisement(chat_id, context)

    # 2. Set up a reminder every 2 hours
    # Check if a job already exists for this chat to avoid duplicates
    job_name = f"reminder_{chat_id}"
    current_jobs = context.job_queue.get_jobs_by_name(job_name)
    if not current_jobs:
        # Run the job every 2 hours (7200 seconds)
        context.job_queue.run_repeating(
            callback=reminder_callback,
            interval=7200,  # 2 hours in seconds
            first=7200,     # First reminder after 2 hours
            chat_id=chat_id,
            name=job_name
        )
        logger.info(f"Reminder job scheduled for chat_id: {chat_id}")
    else:
        logger.info(f"Reminder job already exists for chat_id: {chat_id}")

async def reminder_callback(context: ContextTypes.DEFAULT_TYPE):
    """Callback function for the recurring job."""
    job = context.job
    # Send the advertisement again as a reminder
    await send_advertisement(job.chat_id, context)

# --- MAIN APPLICATION ---

def main():
    """Start the bot."""
    if not TOKEN:
        logger.error("BOT_TOKEN environment variable not set!")
        return

    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Register the /start command handler
    application.add_handler(CommandHandler("start", start))

    # Run the bot (polling mode - suitable for Background Workers)
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
