import io
import telegram
from pytube import YouTube
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a YouTube downloader bot. Send me a YouTube video link and I'll send you a download link.")

def download_video(url, file_type, downloads_path):
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    if file_type == "mp3":
        stream = stream.streams.filter(only_audio=True).first()
    return stream.download(downloads_path)

def send_video(update, context):
    try:
        video_url = update.message.text
        file_type = "mp4"  # or "mp3"
        downloads_path = os.path.join(os.getcwd(), "temp")
        video_path = download_video(video_url, file_type, downloads_path)
        with open(video_path, 'rb') as f:
            if file_type == "mp4":
                context.bot.send_video(chat_id=update.message.chat_id, video=f)
            elif file_type == "mp3":
                context.bot.send_audio(chat_id=update.message.chat_id, audio=f)
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Error: {e}")

updater = Updater(token="your_token_here", use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

video_handler = MessageHandler(Filters.regex(r'https?://.*'), send_video)
dispatcher.add_handler(video_handler)

updater.start_polling()
