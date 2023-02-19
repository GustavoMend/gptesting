import io
import telegram
from pytube import YouTube
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a YouTube downloader bot. Send me a YouTube video link and I'll send you a download link.")

def download_video(url):
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    return stream

def send_video(update, context):
    try:
        video_url = update.message.text
        video = download_video(video_url)
        with io.BytesIO() as video_buffer:
            video.stream_to_buffer(video_buffer)
            video_buffer.seek(0)
            context.bot.send_video(chat_id=update.message.chat_id, video=video_buffer)
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Error: {e}")

updater = Updater(token="your_token_here", use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

video_handler = MessageHandler(Filters.regex(r'https?://.*'), send_video)
dispatcher.add_handler(video_handler)

updater.start_polling()
