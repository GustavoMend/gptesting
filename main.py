import os
import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pytube import YouTube

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Define command handlers
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! Send me a YouTube video link and I'll download the audio for you.")

def download_audio(update, context):
    url = update.message.text
    try:
        # Get the YouTube video object
        yt = YouTube(url)
        # Get the audio stream
        stream = yt.streams.filter(only_audio=True).first()
        # Download the audio
        filename = f"{yt.title}.mp3"
        stream.download(filename=filename)
        # Send the audio file to the user
        context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(filename, 'rb'))
        # Delete the downloaded file
        os.remove(filename)
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, there was an error downloading the audio. Please try again.")

def error(update, context):
    logger.warning(f"Update {update} caused error {context.error}")

# Set up the Telegram bot
token = '5542310588:AAHg4m7EzQzB7j5cSllnf7qZUpkwqpwyWl4'
updater = Updater(token, use_context=True)

# Set up command handlers
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'^https?:\/\/(www.youtube.com|youtu.be)\/'), download_audio))

# Set up error handler
updater.dispatcher.add_error_handler(error)

# Start the bot
updater.start_polling()
updater.idle()
