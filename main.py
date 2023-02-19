import os
import tempfile
import telebot
from pytube import YouTube
from moviepy.editor import *
from mutagen.easyid3 import EasyID3

# Initialize the Telegram bot
bot = telebot.TeleBot("5542310588:AAHg4m7EzQzB7j5cSllnf7qZUpkwqpwyWl4")

# Assign the file type and downloads path
file_type = "mp3"  # Set the default file type to mp3
downloads_path = tempfile.mkdtemp()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome to the video downloader bot! Send me the YouTube video URL.")

@bot.message_handler(commands=['settings'])
def settings(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Video', 'Audio')
    bot.send_message(message.chat.id, "Choose your preferred file format:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Video' or message.text == 'Audio')
def set_format(message):
    global file_type  # Set file_type as a global variable so that it can be modified
    file_type = message.text.lower()
    bot.send_message(message.chat.id, f"Your preferred file format is {file_type}.")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    # Parse the user's message for the video URL and use the user's preferred format, or default to mp3
    try:
        url = message.text
    except ValueError:
        bot.reply_to(message, "Please send the video URL.")
        return

    # Try converting a url to a downloadable video
    try:
        yt = YouTube(url)
    except Exception:
        bot.reply_to(message, "Video URL is not valid.")
        return

    # Try downloading the converted video
    try:
        video = yt.streams.filter(file_extension=file_type).order_by('resolution').desc().first()
        file_path = os.path.join(downloads_path, video.default_filename)
        video.download(downloads_path)
    except Exception:
        bot.reply_to(message, "Video could not be downloaded.")
        return

    # Update file metadata and convert to mp3 if desired
    if file_type == "mp3":
        try:
            audio_file = AudioFileClip(file_path)
            audio_file_tags = EasyID3(file_path)
            audio_file_tags['title'] = yt.title
            audio_file_tags['artist'] = yt.author
            audio_file_tags['album'] = "YouTube Audio"
            audio_file_tags['date'] = str(yt.publish_date)
            audio_file_tags.save()
            audio_file_path = os.path.splitext(file_path)[0] + ".mp3"
            audio_file.write_audiofile(audio_file_path)
            os.remove(file_path)
            file_path = audio_file_path
        except Exception:
            bot.reply_to(message, "Video could not be converted to an MP3 format successfully.")
            return

    # Send the video file to the user
    try:
        if file_type == "mp4":
            with open(file_path, "rb") as file:
                bot.send_video(message.chat.id, file)
        elif file_type == "mp3":
            with open(file_path, "rb") as file:
                bot.send_audio(message.chat.id, file, title=yt.title, performer=yt.author)
    except Exception as e:
        bot.reply_to(message, f"Error sending file: {str(e)}")
    finally:
        os.remove(file_path)  # Delete the temporary file after sending it

# Start the bot
bot.polling()
