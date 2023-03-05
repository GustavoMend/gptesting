import os
import mutagen
from moviepy.editor import AudioFileClip
import yt_dlp

def download_and_convert(url):
    # Extract audio stream information from YouTube
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'forcejson': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
    audio_file_path = f"{info_dict['title']}.mp3"

    # Download audio stream to MP3 file using yt_dlp
    ydl_opts['outtmpl'] = audio_file_path
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Update metadata of MP3 file
    title = info_dict['title']
    artist = info_dict.get('artist', '')
    album = info_dict.get('album', '')
    update_metadata(audio_file_path, title, artist, album)

    print(f"Download complete. Audio saved as {audio_file_path}.")

def update_metadata(file_path: str, title: str, artist: str, album: str="") -> None:
    # Update the file metadata according to YouTube video details
    with open(file_path, 'r+b') as file:
        media_file = mutagen.File(file, easy=True)
        media_file["TIT2"] = title  # Title
        media_file["TPE1"] = artist  # Artist
        media_file["TALB"] = album  # Album
        media_file.save(file)

url = input("Enter YouTube video URL: ")
download_and_convert(url)
