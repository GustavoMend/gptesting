from pyrogram import Client, filters
from moviepy.editor import AudioFileClip
import pytube
import os
import mutagen

app = Client("my_bot", bot_token="6054512042:AAE-WQ5IdL18KhVZkSLO1e_zECKG3XKztck")

@app.on_message(filters.command('start'))
def start_handler(client, message):
    message.reply_text("Hello! Send me a YouTube video URL and I'll convert it to MP3 for you.")

@app.on_message(~filters.command & filters.text)
def echo(client, message):
    message.reply_text(message.text)
app.run()
def youtube_handler(client, message):
    url = message.text.strip()
    if not url.startswith('https://www.youtube.com/watch?v='):
        message.reply_text("Invalid URL. Please send a valid YouTube video URL.")
        return

    try:
        download_and_convert(url)
    except Exception as e:
        message.reply_text(f"Error: {str(e)}")
        return

    # Send the MP3 file
    title = pytube.YouTube(url).title
    mp3_file = f"{title}.mp3"
    message.reply_audio(audio=mp3_file)

def download_and_convert(url):
    # Create YouTube object and extract audio stream
    yt = pytube.YouTube(url)
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

    print(f"Download complete. Audio saved as {output_mp3}.")

def update_metadata(file_path: str, title: str, artist: str, album: str="") -> None:
    # Update the file metadata according to YouTube video details
    with open(file_path, 'r+b') as file:
        media_file = mutagen.File(file, easy=True)
        media_file["title"] = title
        if album:
            media_file["album"] = album
        media_file["artist"] = artist
        media_file.save(file)

app.run()
