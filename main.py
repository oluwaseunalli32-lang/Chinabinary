import os
import logging
import asyncio  # Added to handle the sleep delays
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
# Get token from environment variable (set in Render)
TOKEN = os.environ.get("BOT_TOKEN")

# The exact name of the image file you uploaded to GitHub
IMAGE_FILE = "poster.jpg" 

# The Telegram link for the button
CHANNEL_LINK = "https://t.me/chinabinarysession"

# The bilingual message
MESSAGE_TEXT = (
    "Lost $1,000+ on IQ Option, Binolla, or ExpertOption? I use my own capital to attempt loss recovery for your account.\n\n"
    "خسرت أكثر من 1000 دولار في آي كيو أوبشن أو بينولا أو إكسبرت أوبشن؟ أحاول تعويض خسائرك باستخدام مالي الخاص. تواصل معي"
)

# --- BOT FUNCTIONS ---

async def send_advertisement(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Sends the sequence: Text -> (10s wait) -> Image -> (5s wait) -> Button."""
    try:
        # 1. Send the text message first
        await context.bot.send_message(chat_id=chat_id, text=MESSAGE_TEXT)
        logger.info(f"Step 1: Text sent to {chat_id}")

        # 2. Wait 10 seconds
        await asyncio.sleep(10)

        # 3. Send the image
        with open(IMAGE_FILE, "rb") as photo_file:
            await context.bot.send_photo(chat_id=chat_id, photo=photo_file)
        logger.info(f"Step 2: Image sent to {chat_id}")

        # 4. Wait 5 seconds
        await asyncio.sleep(5)

        # 5. Send the link/button message
        keyboard = [[InlineKeyboardButton("Join China Binary Session", url=CHANNEL_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=chat_id, 
            text="👇 Click below to join the channel 👇", 
            reply_markup=reply_markup
        )
        logger.info(f"Step 3: Button sent to {chat_id}")

    except FileNotFoundError:
         logger.error(f"ERROR: Could not find '{IMAGE_FILE}'. Make sure it is uploaded to GitHub.")
    except Exception as e:
        logger.error(f"Failed to send sequence to {chat_id}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command."""
    chat_id = update.effective_chat.id
    
    # 1. Trigger the sequence immediately
    await send_advertisement(chat_id, context)

    # 2. Set up a reminder every 2 hours
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
    # Send the advertisement sequence again as a reminder
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

    # Run the bot (polling mode)
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
