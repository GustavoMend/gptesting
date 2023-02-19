import os
import mutagen
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pytube import YouTube
from moviepy.editor import AudioFileClip


## Functions
def convert_to_mp3_with_metadata(file_path: str) -> str:
    # Use moviepy to convert an mp4 to an mp3 with metadata support. Delete mp4 afterwards
    audio_clip = AudioFileClip(file_path)
    file_path = file_path.replace("mp4", "mp3")
    audio_clip.write_audiofile(file_path)
    audio_clip.close()
    os.remove(file_path.replace("mp3", "mp4"))
    return file_path

def update_metadata(file_path: str, title: str, artist: str, album: str="") -> None:
    # Update the file metadata according to YouTube video details
    with open(file_path, 'r+b') as file:
        media_file = mutagen.File(file, easy=True)
        media_file["title"] = title
        if album: media_file["album"] = album
        media_file["artist"] = artist
        media_file.save(file)

def download_video(yt: YouTube, file_type: str, downloads_path: str, debug: bool=False):
    # Download a video and debug progress
    if file_type == "mp4":
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    else:
        video = yt.streams.filter(only_audio=True).get_audio_only()

    if debug:
        debug_video_progress(yt, video, file_type)

    video.download(downloads_path)
    return video

def debug_video_progress(yt: YouTube, video, file_type: str, extra_info: str=""):
    highest_res = f", Highest Resolution: {video.resolution}" if file_type == "mp4" else ""
    print(f"Fetching {extra_info}\"{video.title}\"")
    print(f"[File size: {round(video.filesize * 0.000001, 2)} MB{highest_res}, Author: {yt.author}]\n")


## Main function
def main():
    updater = Updater("5542310588:AAHg4m7EzQzB7j5cSllnf7qZUpkwqpwyWl4", use_context=True)
    dispatcher = updater.dispatcher

    # Define the start command handler
    def start(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the YouTube downloader bot! Please send me the URL of the YouTube video you want to download.")

    # Define the download command handler
    def download(update, context):
        url = update.message.text
        convert = context.user_data.get('convert')
        file_type = "mp4" if convert == "mp4" else "mp3"
        downloads_path = os.path.join(os.getcwd(), "temp")

        # Try converting a url to a downloadable video
        try:
            yt = YouTube(url)
        except Exception:
            if "playlist?" in url:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Playlists can only be converted on the playlist page.")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Video URL is not valid.")
            return

        # Try downloading the converted video
        try:
            video = download_video(yt, file_type, downloads_path, True)
        except Exception:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Video could not be downloaded.")
            return

        file_path = os.path.join(downloads_path, video.default_filename)

        # Convert to mp3
        try:
            if file_type == "mp3":
                file_path_mp3 = file_path.replace("mp4", "mp3")
                if os.path.exists(file_path_mp3):
                    os.remove(file_path_mp3)
                
                file_path = convert_to_mp3_with_metadata(file_path)
        except Exception:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Video could not be converted to an MP3 format successfully. File cannot be found or already exists.")
            return
        
        # Update file metadata
        update_metadata(file_path, yt.title, yt.author)

        # Send the converted file to the user
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_path, 'rb'))


    # Define the convert command handler
    def convert(update, context):
        convert = update.message.text.lower()
        context.user_data['convert'] = convert
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"File type set to {convert.upper()}.")

    # Register the handlers
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    download_handler = MessageHandler(Filters.regex(r'^https?://.*'), download)
    dispatcher.add_handler(download_handler)

    convert_handler = MessageHandler(Filters.regex(r'^(mp3|mp4)$'), convert)
    dispatcher.add_handler(convert_handler)

    # Start the bot
bot.polling()
