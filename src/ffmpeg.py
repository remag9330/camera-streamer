import os
import subprocess
import logging
import tempfile

FFMPEG_EXE = "./ffmpeg.exe"


def combine_video_audio(video_filename, audio_filename, out_filename):
    logging.debug(f"combining {video_filename} {audio_filename} into {out_filename}")
    args = [FFMPEG_EXE,
            "-hide_banner",
            "-loglevel", "panic",
            "-nostats",
            "-i", video_filename,
            "-i", audio_filename,
            "-c:v", "h264",
            "-c:a", "aac",
            "-movflags", "empty_moov+default_base_moof+frag_keyframe",
            "-profile:v", "baseline",
            out_filename
            ]

    pipes = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = pipes.communicate()

    success = pipes.returncode == 0

    if success:
        logging.debug("combine completed successfully")
    else:
        logging.error(f"combine failed - status code: {pipes.returncode} - stdout: '{stdout}' - stderr: '{stderr}'")

    return success


def append_videos(output_file, filenames):
    logging.info(f"appending video files '{', '.join(filenames)}' to '{output_file}'")

    file_content = "\n".join([f"file '{f}'" for f in filenames])
    with tempfile.NamedTemporaryFile(delete=False) as files_to_combine_file:
        files_to_combine_file.write(file_content.encode("utf-8"))

        temp_file_name = files_to_combine_file.name

    args = [FFMPEG_EXE,
            "-hide_banner",
            # "-loglevel", "panic",
            "-nostats",
            "-f", "concat",
            "-safe", "0",
            "-i", temp_file_name,
            "-c", "copy",
            output_file
            ]

    try:
        pipes = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = pipes.communicate()
    finally:
        try:
            os.remove(temp_file_name)
        except Exception:
            logging.warn("Could not delete temp file %s", temp_file_name)

    success = pipes.returncode == 0

    if success:
        logging.info("append completed successfully")
    else:
        logging.error(f"append failed - status code: {pipes.returncode} - stdout: '{stdout}' - stderr: '{stderr}'")

    return success
