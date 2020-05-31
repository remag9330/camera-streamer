import subprocess
import logging

FFMPEG_EXE = "./ffmpeg.exe"

def combine_video_audio(video_filename, audio_filename, out_filename):
    logging.info(f"combining {video_filename} {audio_filename} into {out_filename}")
    args = [FFMPEG_EXE,
        "-hide_banner",
        "-loglevel", "panic",
        "-nostats",
        "-i", video_filename,
        "-i", audio_filename,
        "-c:v", "copy",
        "-c:a", "aac",
        out_filename]

    result = subprocess.call(args)

    if result == 0:
        logging.info("combine completed successfully")
    else:
        logging.error(f"combine failed - status code: {result}")
