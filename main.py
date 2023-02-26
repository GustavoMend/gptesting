from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from moviepy.editor import AudioFileClip
import pytube
import os
import mutagen

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! Please send me a YouTube video URL to download the audio.")

def download_and_convert(url):
    # Create YouTube object and extract audio stream
    try:
        yt = pytube.YouTube(url)
    except pytube.exceptions.RegexMatchError:
        return "The provided URL is not supported."
    audio_stream = yt.streams.filter(only_audio=True).first()
    # Set output file names
    output_mp4 = f"{yt.title}.mp4"

    # Download audio stream to MP4 file
    audio_stream.download(output_path=os.getcwd(), filename=output_mp4)

    # Use moviepy to convert the MP4 file to an MP3 file with metadata support, then delete the MP4 file
    audio_clip = AudioFileClip(output_mp4)
    output_mp3 = f"{yt.title}.mp3"
    audio_clip.write_audiofile(output_mp3)
    audio_clip.close()
    os.remove(output_mp4)

    # Get video details from YouTube
    title = yt.title
    artist = yt.author
    album = ""

    # Update metadata of MP3 file
    update_metadata(output_mp3, title, artist, album)

    return output_mp3

def update_metadata(file_path: str, title: str, artist: str, album: str="") -> None:
    # Update the file metadata according to YouTube video details
    with open(file_path, 'r+b') as file:
        media_file = mutagen.File(file, easy=True)
        media_file["title"] = title
        if album:
            media_file["album"] = album
        media_file["artist"] = artist
        media_file.save(file)

def handle_message(update, context):
    text = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Processing...")

    try:
        output_mp3 = download_and_convert(text)
        if output_mp3:
            context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(output_mp3, 'rb'))
            os.remove(output_mp3)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Download complete.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I couldn't extract audio from this link.")
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Sorry, an error occurred: {str(e)}")


def main():
    updater = Updater(token="6054512042:AAF_4lsVxJbwFk0qacpe0NqvBRauW-zEdnU", use_context=True)

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(Filters.text, handle_message)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(message_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

