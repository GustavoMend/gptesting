import os
import mutagen
import subprocess
import requests
import tempfile
from moviepy.editor import AudioFileClip
from pyrogram import Client, filters

app = Client("my_bot", bot_token="6054512042:AAE-WQ5IdL18KhVZkSLO1e_zECKG3XKztck", api_id=11169140, api_hash="4b185d543b0d1a84bed3a462ade1498f")

@app.on_message(filters.command('start'))
def start_handler(client, message):
    message.reply_text("Hello! Send me a YouTube video URL and I'll convert it to MP3 for you.")

# Register a command handler for the /download command
@app.on_message(filters.command("download"))
async def download_video(client, message):
    # Get the URL of the video to download from the message text
    url = message.text.split(" ")[1]

    # Download the video using yt-dlp
    with tempfile.TemporaryDirectory() as tempdir:
        output_file = os.path.join(tempdir, "audio.mp4")
        subprocess.run(["yt-dlp", "-f", "bestaudio", "--merge-output-format", "mp4", "-o", output_file, url], check=True)

        # Convert the MP4 file to an MP3 file using moviepy
        audio_clip = AudioFileClip(output_file)
        output_mp3 = os.path.join(tempdir, "audio.mp3")
        audio_clip.write_audiofile(output_mp3)
        audio_clip.close()

        # Get the video details from yt-dlp
        result = subprocess.run(["yt-dlp", "-e", url], stdout=subprocess.PIPE)
        title = result.stdout.strip().decode("utf-8")
        artist = ""
        album = ""

        # Update metadata of MP3 file
        update_metadata(output_mp3, title, artist, album)

        # Send the MP3 file to the user through Telegram
        with open(output_mp3, "rb") as f:
            await client.send_audio(chat_id=message.chat.id, audio=f, title=title)

        # Delete the temporary files
        os.remove(output_file)
        os.remove(output_mp3)

# Update the file metadata according to video details
def update_metadata(file_path, title, artist, album=""):
    with open(file_path, 'r+b') as file:
        media_file = mutagen.File(file, easy=True)
        media_file["title"] = title
        if album:
            media_file["album"] = album
        media_file["artist"] = artist
        media_file.save(file)

# Start the client and wait for commands
app.run()
