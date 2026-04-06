"""Utility to download youtube videos (with english subtitles if available) and extract the first frame of the video."""

import os
import shutil
import subprocess

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

def check_dependencies(output_dir: str = "media"):
    """Checks if yt-dlp and ffmpeg are installed and raises an error if not."""

    # check if the output directory exists and is writable
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    elif not os.access(output_dir, os.W_OK):
        raise PermissionError(f"The directory {output_dir} is not writable. Please check the permissions.")
    
    if yt_dlp is None:
        raise ImportError("yt-dlp module is not installed. Please install it to use this function.")

    if shutil.which("ffmpeg") is None:
        raise ImportError("ffmpeg is not installed. Please install it to use this function.")
    

def extract_first_frame(video_path: str, output_path: str) -> None:
    """Extracts the first frame of the video using ffmpeg and saves it to the output path."""
    check_dependencies(os.path.dirname(output_path) or ".")

    command = [
        "ffmpeg",
        "-ss", "00:00:00",
        "-i", video_path,
        "-frames:v", "1",
        "-q:v", "3",
        "-y",
        output_path,
    ]

    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def merge_subtitles(video_path: str, subtitle_path: str, output_path: str) -> None:
    """Embeds an SRT subtitle file into an MP4 video using ffmpeg soft-coding."""
    check_dependencies(os.path.dirname(output_path) or ".")

    print(f"Merging subtitles from {subtitle_path} into video {video_path}...")

    command = [
        "ffmpeg",
        "-i", video_path,
        "-i", subtitle_path,
        "-map", "0",
        "-map", "1",
        "-c:v", "copy",
        "-c:a", "copy",
        "-c:s", "mov_text",
        "-y",
        output_path,
    ]

    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 
    print(f"Subtitles merged and saved to {output_path}.")

def burn_subtitles(video_path: str, subtitle_path: str, output_path: str) -> None:
    """Hardcodes (burns) an SRT subtitle file into an MP4 video using ffmpeg."""
    check_dependencies(os.path.dirname(output_path) or ".")

    print(f"Burning subtitles from {subtitle_path} into video {video_path}...")
    
    # Escape path characters for ffmpeg's subtitles filter
    escaped_sub = str(subtitle_path).replace("\\", "/").replace(":", "\\:")
    
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles={escaped_sub}",
        "-c:a", "copy",
        "-y",
        output_path,
    ]

    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 
    print(f"Subtitles burned and saved to {output_path}.")

def download_youtube_video(
    url: str, 
    output_dir: str = "media", 
    filename: str | None = None, 
    download_subtitles: bool = True
) -> str:
    """Downloads the youtube video using yt-dlp and returns the path to the video file."""
    check_dependencies(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Downloading video from {url}...")
    file_template = f"{filename}.%(ext)s" if filename else "%(id)s.%(ext)s"
    outtmpl = os.path.join(output_dir, file_template)

    ydl_opts = {
        "format": "bv+ba/b",
        "merge_output_format": "mp4",
        "outtmpl": outtmpl,
        "postprocessor_args": {
            "ffmpeg": [
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                "-movflags", "+faststart"
            ]
        },
        "writethumbnail": False,
        "writesubtitles": download_subtitles,
        "subtitleslangs": ["en", "en-US", "en-GB"] if download_subtitles else [],
        "remote_components": ["ejs:github"],
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
        "quiet": True,
    }
    
    if download_subtitles:
        ydl_opts["postprocessors"].append({
            "key": "FFmpegSubtitlesConvertor",
            "format": "srt",
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_path_info = ydl.prepare_filename(info_dict)
        
    base_path, _ = os.path.splitext(video_path_info)
    final_video_path = f"{base_path}.mp4"
    if not os.path.exists(final_video_path) and os.path.exists(video_path_info):
        final_video_path = video_path_info

    extract_first_frame(final_video_path, f"{base_path}.png")
    print(f"Video downloaded and saved to {final_video_path}. Thumbnail saved to {base_path}.png.")
    return final_video_path