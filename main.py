import os
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
            # Assign the file type and downloads path
            file_type = "mp4"
            downloads_path = os.path.join(os.getcwd(), "temp")
            # Try downloading the converted video
            video = yt.streams.get_highest_resolution().download(output_path=downloads_path, filename="video")
            file_path = os.path.join(downloads_path, f"{video.title}.{video.mime_type.split('/')[-1]}")
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_path, 'rb'))
        except Exception as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Video could not be downloaded.")
            print(e)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Send me a YouTube video link.")

# Create the bot and add the handlers
updater = Updater(token="5542310588:AAHg4m7EzQzB7j5cSllnf7qZUpkwqpwyWl4", use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(filters.Filters.text & (~filters.Filters.command), echo)

dispatcher.add_handler(echo_handler)

# Start the bot
updater.start_polling()
