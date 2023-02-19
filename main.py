import os
import tempfile
import telebot
from pytube import YouTube

# Initialize the Telegram bot
bot = telebot.TeleBot("5542310588:AAHg4m7EzQzB7j5cSllnf7qZUpkwqpwyWl4")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome to the video downloader bot! Send me the YouTube video URL and the desired format (mp4 or mp3) separated by a space.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    # Parse the user's message for the video URL and desired format
    try:
        url, file_type = message.text.split()
    except ValueError:
        bot.reply_to(message, "Please send the video URL and the desired format (mp4 or mp3) separated by a space.")
        return
    
    # Try converting a url to a downloadable video
    try:
        yt = YouTube(url)
    except Exception:
        bot.reply_to(message, "Video URL is not valid.")
        return
    
    # Assign the file type and donwloads path
    downloads_path = tempfile.gettempdir()
    file_type = file_type.lower()
    if file_type not in ["mp4", "mp3"]:
        bot.reply_to(message, "Invalid file format. Please choose mp4 or mp3.")
        return
    
    # Try downloading the converted video
    try:
        video = yt.streams.filter(file_extension=file_type).order_by('resolution').desc().first()
        file_path = os.path.join(downloads_path, video.default_filename) 
        video.download(downloads_path)
    except Exception:
        bot.reply_to(message, "Video could not be downloaded.")
        return
    
    # Send the video file to the user
    with open(file_path, "rb") as file:
        bot.send_video(message.chat.id, file)

# Start the bot
bot.polling()
