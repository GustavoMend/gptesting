import os
import tempfile
import telebot
from pytube import YouTube
from moviepy.editor import *
from mutagen.easyid3 import EasyID3

# Initialize the Telegram bot
bot = telebot.TeleBot("5542310588:AAHg4m7EzQzB7j5cSllnf7qZUpkwqpwyWl4")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome to the video downloader bot! Send me the YouTube video URL and the desired format (video or audio) separated by a space.")

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
    
    # Assign the file type and downloads path
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

    # Update file metadata
    if file_type == "audio":
        try:
            audio_file = AudioFileClip(file_path)
            audio_file_tags = EasyID3(file_path)
            audio_file_tags['title'] = yt.title
            audio_file_tags['artist'] = yt.author
            audio_file_tags['album'] = "YouTube Audio"
            audio_file_tags['date'] = str(yt.publish_date)
            audio_file_tags.save()
        except Exception:
            pass
    
        # Send the video file to the user
    try:
        if file_type == "mp4":
            with open(file_path, "rb") as file:
                bot.send_video(message.chat.id, file)
        elif file_type == "mp3":
            audio_file_path = os.path.splitext(file_path)[0] + ".mp3"
            audio = AudioFileClip(file_path)
            audio.write_audiofile(audio_file_path)
            with open(audio_file_path, "rb") as file:
                bot.send_audio(message.chat.id, file, title=yt.title, performer=yt.author)
    except Exception as e:
        bot.reply_to(message, f"Error sending file: {str(e)}")
    finally:
        os.remove(file_path) # Delete the temporary file after sending it
        if file_type == "mp3":
            os.remove(audio_file_path) # Delete the temporary audio file
# Start the bot
bot.polling()
