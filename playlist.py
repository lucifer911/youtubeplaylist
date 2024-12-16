import yt_dlp
import re
import os
from pathlib import Path
import subprocess

def check_ffmpeg_installed():
    try:
        # Check if ffmpeg is installed
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def clean_title(title):
    # Clean the title to make it a valid filename and limit the length to avoid OS issues
    title = re.sub(r'[\\/*?:"<>|]', "", title)
    return title[:100]  # Truncate title to 100 characters if it's too long

def is_playlist(url):
    # Check if the provided URL is a playlist based on typical YouTube URL structure
    return "playlist" in url

def download_audio_playlist(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'cookies-from-browser': 'brave',  # Use Brave browser to extract cookies
            'noplaylist': False,  # Ensure it's not blocking playlists
            'ignoreerrors': True,  # Skip over videos that cause errors
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(url, download=False)

            # Check if it's a playlist
            if not playlist_info.get('_type') == 'playlist':
                print("The provided URL is not a playlist.")
                return

            playlist_title = clean_title(playlist_info.get('title', 'Unnamed Playlist'))
            folder_path = Path(playlist_title)
            folder_path.mkdir(parents=True, exist_ok=True)

            # Update the output template to save in the playlist folder
            ydl_opts['outtmpl'] = str(folder_path / '%(title)s.%(ext)s')

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            print(f"Audio playlist downloaded successfully and saved in {folder_path}.")
    except yt_dlp.utils.DownloadError as e:
        print(f"Error downloading playlist: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def download_youtube_short(url):
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'quiet': True,
            'merge_output_format': 'mp4',
            'outtmpl': '%(title)s.%(ext)s',
            'cookies-from-browser': 'brave',  # Use Brave browser to extract cookies
            'ignoreerrors': True,  # Skip over unavailable videos
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', None)
            description = info_dict.get('description', '')
            hashtags = ' '.join([tag for tag in re.findall(r'#[\w]+', description)])

            if not title:
                print("Failed to retrieve video title.")
                return

            title = clean_title(title)

            # Create a new folder with the title name
            folder_path = Path(title)
            folder_path.mkdir(parents=True, exist_ok=True)

            save_path = folder_path / f"{title}.mp4"
            ydl_opts['outtmpl'] = str(save_path)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"Video downloaded successfully and saved as {save_path}.")

            # Save description and hashtags to a text file
            text_file_path = folder_path / f"{title}.txt"
            with text_file_path.open('w', encoding='utf-8') as text_file:
                text_file.write(f"Title: {title}\n")
                text_file.write(f"Description: {description}\n")
                if hashtags:
                    text_file.write(f"Hashtags: {hashtags}\n")
                else:
                    text_file.write("Hashtags: None\n")
            print(f"Description and hashtags saved as {text_file_path}.")
    except yt_dlp.utils.DownloadError as e:
        print(f"Error downloading video: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function to handle user input
if __name__ == "__main__":
    # Check if ffmpeg is installed
    if not check_ffmpeg_installed():
        print("ffmpeg is not installed. Please install ffmpeg to proceed.")
    else:
        youtube_url = input("Enter YouTube video or playlist URL: ")

        if is_playlist(youtube_url):
            print("Downloading playlist audio...")
            download_audio_playlist(youtube_url)
        else:
            print("Downloading YouTube Short...")
            download_youtube_short(youtube_url)
