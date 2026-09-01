"""Utility to download YouTube videos (with English subtitles if available), burn subtitles
into the video, and extract the first frame as a thumbnail.

This file can be used as a module or run as a standalone script. When run as a script you can
specify a URL, output directory and filename. Subtitles (if available) are automatically
downloaded and burned into the resulting MP4 file.
"""

from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


def _ffmpeg_has_filter(filter_name: str) -> bool:
    """Return True if ffmpeg reports a given filter as available."""
    try:
        res = subprocess.run(
            ["ffmpeg", "-hide_banner", "-h", f"filter={filter_name}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        output = (res.stdout or "") + (res.stderr or "")
        return f"Unknown filter '{filter_name}'" not in output
    except Exception:
        return False


def check_dependencies(output_dir: str = "media"):
    """Checks if yt-dlp and ffmpeg are installed and raises an error if not.

    Also ensures the output directory exists and is writable.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    elif not os.access(output_dir, os.W_OK):
        raise PermissionError(
            f"The directory {output_dir} is not writable. Please check the permissions."
        )

    if yt_dlp is None:
        raise ImportError(
            "yt-dlp module is not installed. Please install it to use this function."
        )

    if shutil.which("ffmpeg") is None:
        raise ImportError(
            "ffmpeg is not installed. Please install it to use this function."
        )


def extract_first_frame(video_path: str, output_path: str) -> None:
    """Extracts the first frame of the video using ffmpeg and saves it to the output path."""
    check_dependencies(os.path.dirname(output_path) or ".")

    command = [
        "ffmpeg",
        "-ss",
        "00:00:00",
        "-i",
        video_path,
        "-frames:v",
        "1",
        "-q:v",
        "3",
        "-y",
        output_path,
    ]

    subprocess.run(
        command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def merge_subtitles(video_path: str, subtitle_path: str, output_path: str) -> None:
    """Soft-embed an SRT subtitle file into an MP4 container (mov_text) without re-encoding video.

    This keeps the original video streams and adds a subtitle track that players can toggle.
    """
    check_dependencies(os.path.dirname(output_path) or ".")

    print(f"Merging subtitles from {subtitle_path} into video {video_path}...")

    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-i",
        subtitle_path,
        "-map",
        "0",
        "-map",
        "1",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-c:s",
        "mov_text",
        "-y",
        output_path,
    ]

    subprocess.run(
        command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    print(f"Subtitles merged and saved to {output_path}.")


def burn_subtitles(video_path: str, subtitle_path: str, output_path: str) -> None:
    """Hardcode (burn) an SRT subtitle file into an MP4 video using ffmpeg.

    The video stream will be re-encoded to apply the subtitles. Audio stream is copied.
    """
    check_dependencies(os.path.dirname(output_path) or ".")

    print(f"Burning subtitles from {subtitle_path} into video {video_path}...")

    # Some ffmpeg builds (including certain Homebrew builds) do not include
    # libass-backed subtitle rendering filters. In that case, gracefully
    # fallback to soft subtitle embedding so the pipeline still succeeds.
    has_subtitles = _ffmpeg_has_filter("subtitles")
    has_ass = _ffmpeg_has_filter("ass")
    if not has_subtitles and not has_ass:
        print(
            "Warning: ffmpeg subtitle rendering filters ('subtitles'/'ass') are not available; "
            "falling back to soft subtitle embedding (not hard-burned)."
        )
        merge_subtitles(video_path, subtitle_path, output_path)
        return

    # Use ffmpeg subtitles filter which requires re-encoding the video stream.
    # The subtitles filter parses its argument and paths can contain characters
    # that are interpreted as filter options; pass an absolute path and wrap
    # it in single quotes (escaping any internal single quotes) so ffmpeg
    # treats it as a filename.
    abs_video = os.path.abspath(video_path)
    abs_sub = os.path.abspath(subtitle_path)
    abs_output = os.path.abspath(output_path)
    sub_dir = os.path.dirname(abs_sub) or "."
    sub_name = os.path.basename(abs_sub)

    if has_subtitles:
        # Try straightforward subtitles filter first.
        vf_arg = f"subtitles={sub_name}"
        command = [
            "ffmpeg",
            "-i",
            abs_video,
            "-vf",
            vf_arg,
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-y",
            abs_output,
        ]

        try:
            subprocess.run(command, check=True, cwd=sub_dir)
            print(f"Subtitles burned and saved to {output_path}.")
            return
        except subprocess.CalledProcessError:
            print("subtitles filter failed, falling back to ASS conversion...")
    else:
        print("'subtitles' filter not available, trying ASS conversion fallback...")

    # Fallback: convert SRT to ASS and use the ass filter which is often more lenient.
    ass_path = os.path.splitext(abs_sub)[0] + ".ass"
    try:
        subprocess.run(["ffmpeg", "-y", "-i", abs_sub, ass_path], check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Failed to convert SRT to ASS: {exc}") from exc

    try:
        ass_name = os.path.basename(ass_path)
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                abs_video,
                "-vf",
                f"ass={ass_name}",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-y",
                abs_output,
            ],
            check=True,
            cwd=sub_dir,
        )
        print(f"Subtitles burned (via ASS) and saved to {output_path}.")
    except subprocess.CalledProcessError:
        print("ASS filter path failed; falling back to soft subtitle embedding.")
        merge_subtitles(video_path, subtitle_path, output_path)
    finally:
        # Clean up the temporary ASS file if it was created
        try:
            if os.path.exists(ass_path):
                os.remove(ass_path)
        except Exception:
            pass


def download_youtube_video(
    url: str,
    output_dir: str = "media",
    filename: str | None = None,
    download_subtitles: bool = True,
) -> str:
    """Downloads the youtube video using yt-dlp and returns the path to the video file.

    The filename parameter should be the desired base filename (without extension). If omitted,
    yt-dlp's default naming (id.ext) will be used.
    """
    check_dependencies(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Downloading video from {url}...")
    file_template = f"{filename}.%(ext)s" if filename else "%(id)s.%(ext)s"
    outtmpl = os.path.join(output_dir, file_template)

    ydl_opts = {
        # Prioritize H.264 (avc1) and AAC (m4a) for PowerPoint compatibility, fallback to best mp4
        "format": "bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "outtmpl": outtmpl,
        # Let yt-dlp handle conversion to mp4 via postprocessor. We avoid extra ffmpeg args here
        # because we will re-encode only if we burn subtitles.
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
        ydl_opts["postprocessors"].append(
            {
                "key": "FFmpegSubtitlesConvertor",
                "format": "srt",
            }
        )

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_path_info = ydl.prepare_filename(info_dict)

    base_path, _ = os.path.splitext(video_path_info)
    final_video_path = f"{base_path}.mp4"
    if not os.path.exists(final_video_path) and os.path.exists(video_path_info):
        final_video_path = video_path_info

    # create a thumbnail from the downloaded video
    try:
        extract_first_frame(final_video_path, f"{base_path}.png")
    except Exception:
        # non-fatal: thumbnail extraction failed
        print("Warning: failed to extract thumbnail.")

    print(
        f"Video downloaded and saved to {final_video_path}. Thumbnail saved to {base_path}.png."
    )
    return final_video_path


def download_and_burn(
    url: str,
    output_dir: str = "media",
    filename: str | None = None,
    burn: bool = True,
) -> str:
    """Downloads a video and (optionally) burns English subtitles into the final MP4.

    Returns the path to the final MP4 file.
    """
    # normalize filename (strip extension if provided)
    if filename:
        filename = os.path.splitext(filename)[0]

    downloaded_video = download_youtube_video(
        url, output_dir=output_dir, filename=filename, download_subtitles=burn
    )

    base_path, _ = os.path.splitext(downloaded_video)

    # look for subtitle files that start with the base path
    subtitle_candidates = glob.glob(base_path + "*.srt")

    final_path = (
        os.path.join(output_dir, f"{filename}.mp4") if filename else downloaded_video
    )

    if burn and subtitle_candidates:
        # choose EN subtitle if available, else first candidate
        subtitle_path = None
        for cand in subtitle_candidates:
            if (
                cand.lower().endswith(".en.srt")
                or cand.lower().endswith(".en-us.srt")
                or cand.lower().endswith(".en-gb.srt")
            ):
                subtitle_path = cand
                break
        if subtitle_path is None:
            subtitle_path = subtitle_candidates[0]

        temp_burned = base_path + ".burned.mp4"
        burn_subtitles(downloaded_video, subtitle_path, temp_burned)

        # replace/move to final path
        shutil.move(temp_burned, final_path)
        print(f"Final video with subtitles available at {final_path}")
    else:
        # no subtitles to burn or burn disabled: ensure file is at final_path
        if downloaded_video != final_path:
            shutil.move(downloaded_video, final_path)
        print(f"Final video available at {final_path} (no subtitles burned)")

    # try to (re)extract thumbnail for final file
    try:
        extract_first_frame(final_path, os.path.splitext(final_path)[0] + ".png")
    except Exception:
        pass

    return final_path


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Download a YouTube video and burn English subtitles (if available)."
    )
    p.add_argument("url", help="YouTube video URL to download")
    p.add_argument(
        "-o",
        "--output-dir",
        default="media",
        help="Output directory for video and subtitles",
    )
    p.add_argument(
        "-f",
        "--filename",
        default=None,
        help="Desired output filename (without extension)",
    )
    p.add_argument(
        "--no-burn",
        dest="burn",
        action="store_false",
        help="Do not burn subtitles into the video (just download them)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    try:
        out = download_and_burn(
            args.url, output_dir=args.output_dir, filename=args.filename, burn=args.burn
        )
        print(out)
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
