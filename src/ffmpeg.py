import os
import subprocess
import logging
import tempfile

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
        out_filename
    ]

    pipes = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = pipes.communicate()

    success = pipes.returncode == 0

    if success:
        logging.info("combine completed successfully")
    else:
        logging.error(f"combine failed - status code: {pipes.returncode} - stdout: '{stdout}' - stderr: '{stderr}'")

    return success

def append_videos(full, end):
    logging.info(f"appending video {end} to {full}")

    (full_path, full_name) = os.path.split(full)
    start = os.path.join(full_path, "t-" + full_name)
    os.rename(full, start)

    with tempfile.NamedTemporaryFile(delete=False) as files_to_combine_file:
        files_to_combine_file.write("\n".join([
            f"file '{start}'",
            f"file '{end}'"
        ]).encode("utf-8"))

        temp_file_name = files_to_combine_file.name

    args = [FFMPEG_EXE,
        "-hide_banner",
        # "-loglevel", "panic",
        "-nostats",
        "-f", "concat",
        "-safe", "0",
        "-i", temp_file_name,
        "-c", "copy",
        full
    ]

    try:
        pipes = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = pipes.communicate()
    finally:
        try:
            os.remove(temp_file_name)
        except ex:
            logging.warn("Could not delete temp file %s", temp_file_name)

    os.remove(start)
    success = pipes.returncode == 0

    if success:
        logging.info("append completed successfully")
    else:
        logging.error(f"append failed - status code: {pipes.returncode} - stdout: '{stdout}' - stderr: '{stderr}'")

    return success
