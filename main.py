from pyrogram import Client, filters
import pytube
import os
import mutagen
from moviepy.editor import AudioFileClip

bot = Client("my_bot", bot_token="6054512042:AAE-WQ5IdL18KhVZkSLO1e_zECKG3XKztck", api_id=11169140, api_hash="4b185d543b0d1a84bed3a462ade1498f")

@app.on_message(filters.command('start'))
def start_handler(client, message):
    message.reply_text("Hello! Send me a YouTube video URL and I'll convert it to MP3 for you.")

# filter function to check if the message contains a valid YouTube URL
@bot.on_message(filters.private & filters.regex(r"(http|https)://(www\.)?youtube\.com/watch\?v=\w+"))
async def download_and_send_audio(client, message):
    # extract the YouTube URL from the message
    url = message.text.strip()

    # download and convert the video to audio
    try:
        yt = pytube.YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        output_mp4 = f"{yt.title}.mp4"
        audio_stream.download(output_path=os.getcwd(), filename=output_mp4)
        audio_clip = AudioFileClip(output_mp4)
        output_mp3 = f"{yt.title}.mp3"
        audio_clip.write_audiofile(output_mp3)
        audio_clip.close()
        os.remove(output_mp4)
        title = yt.title
        artist = yt.author
        album = ""
        update_metadata(output_mp3, title, artist, album)
    except Exception as e:
        await message.reply_text(f"An error occurred while downloading the video: {str(e)}")
        return

    # send the audio file to the user
    try:
        await message.reply_audio(audio=output_mp3, title=title, performer=artist, caption=url)
        os.remove(output_mp3)
    except Exception as e:
        await message.reply_text(f"An error occurred while sending the audio file: {str(e)}")

# function to update the metadata of an audio file
def update_metadata(file_path: str, title: str, artist: str, album: str="") -> None:
    with open(file_path, 'r+b') as file:
        media_file = mutagen.File(file, easy=True)
        media_file["title"] = title
        if album:
            media_file["album"] = album
        media_file["artist"] = artist
        media_file.save(file)

# start the bot
bot.run()
