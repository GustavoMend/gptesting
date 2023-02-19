import os
import tempfile
import telebot
import subprocess

# Initialize the Telegram bot
bot = telebot.TeleBot("5542310588:AAHg4m7EzQzB7j5cSllnf7qZUpkwqpwyWl4")

# Assign the downloads path
downloads_path = tempfile.mkdtemp()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome to the YouTube audio downloader bot! Send me the YouTube video URL.")

@bot.message_handler(func=lambda message: True)
def download_audio(message):
    # Parse the user's message for the video URL
    try:
        url = message.text
    except ValueError:
        bot.reply_to(message, "Please send the video URL.")
        return

    # Use youtube-dl to download the audio from the video
    try:
        output_file = os.path.join(downloads_path, "%(title)s.%(ext)s")
        command = ["youtube-dl", "-x", "--audio-format", "mp3", "-o", output_file, url]
        subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"Error downloading audio: {e.output.decode('utf-8')}")
        return

    # Send the audio file to the user
    try:
        audio_file_path = output_file.replace("%(title)s.%(ext)s", "*.mp3")
        with open(audio_file_path, "rb") as file:
            bot.send_audio(message.chat.id, file)
    except Exception as e:
        bot.reply_to(message, f"Error sending file: {str(e)}")
    finally:
        # Clean up the downloaded files
        for file in os.listdir(downloads_path):
            if file.endswith(".mp3"):
                os.remove(os.path.join(downloads_path, file))

# Start the bot
bot.polling()
