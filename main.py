from telegram.ext import Updater, CommandHandler, MessageHandler, filters
from pytube import YouTube

# This function handles the /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a YouTube downloader bot. Send me a YouTube video link and I'll send you a download link.")

# This function handles all other messages
def echo(update, context):
    url = update.message.text

    # Check if the message contains a valid YouTube URL
    if "youtube.com" in url:
        try:
            yt = YouTube(url)
            video_url = yt.streams.get_highest_resolution().url
            context.bot.send_message(chat_id=update.effective_chat.id, text=video_url)
        except Exception:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid YouTube URL.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Send me a YouTube video link.")

# Create the bot and add the handlers
updater = Updater(token='5542310588:AAHg4m7EzQzB7j5cSllnf7qZUpkwqpwyWl4', use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

# Start the bot
updater.start_polling()
