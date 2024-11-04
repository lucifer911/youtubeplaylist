import yt_dlp
import re
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

def is_playlist(url):
    # Check if the provided URL is a playlist based on typical YouTube URL structure
    return "playlist" in url

def download_audio_playlist(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': False,  # Set to False to see warning messages
            'verbose': True,  # Enable verbose logging for debugging
            'retries': 5,  # Increase retries
            'fragment_retries': 5,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'cookies-from-browser': 'brave',  # Use Brave browser to extract cookies
            'noplaylist': False  # Ensure it treats the input as a playlist
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print("Audio playlist downloaded successfully.")
    except yt_dlp.utils.DownloadError as e:
        print(f"Error downloading playlist: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def download_audio(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'retries': 5,
            'fragment_retries': 5,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'cookies-from-browser': 'brave',  # Use Brave browser to extract cookies
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Audio downloaded successfully.")
    except yt_dlp.utils.DownloadError as e:
        print(f"Error downloading audio: {e}")
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
            print("Downloading audio...")
            download_audio(youtube_url)
