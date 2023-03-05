from moviepy.editor import AudioFileClip
import os
import mutagen
import youtube_dl

def download_and_convert(url):
    # Set ytdl options
    ytdl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    # Create YouTube object and extract audio stream
    try:
        with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            output_mp3 = ydl.prepare_filename(info_dict)
    except youtube_dl.utils.DownloadError:
        print("The provided URL is not supported.")
        return

    # Get video details from YouTube
    title = info_dict.get('title', '')
    artist = info_dict.get('uploader', '')
    album = ''

    # Update metadata of MP3 file
    update_metadata(output_mp3, title, artist, album)

    print(f"Download complete. Audio saved as {output_mp3}.")

def update_metadata(file_path: str, title: str, artist: str, album: str='') -> None:
    # Update the file metadata according to YouTube video details
    with open(file_path, 'r+b') as file:
        media_file = mutagen.File(file, easy=True)
        media_file['title'] = title
        if album:
            media_file['album'] = album
        media_file['artist'] = artist
        media_file.save()

url = input("Enter YouTube video URL: ")
download_and_convert(url)
