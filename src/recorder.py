import os
import time
import wave
import threading

import cv2

import ffmpeg
from utils import Mutex
import settings

if settings.RECORD_AUDIO:
    import pyaudio


class Recorder:
    def __init__(self, camera):
        self.video = VideoRecorder(camera, self.video_frame_written)
        self.audio = AudioRecorder()

        self.full_video_name = None

        self.combining_threads = []

        self.frame_count = 0

    def start_recording(self):
        self.video.start_recording()
        self.audio.start_recording()

        self.frame_count = 0

    def stop_recording(self):
        video_filename = self.video.stop_recording()
        audio_filename = self.audio.stop_recording()
        self.combine_video_audio_background(video_filename, audio_filename)

    def video_frame_written(self):
        if settings.RECORDINGS_FRAMES_PER_FILE > 0:
            self.frame_count += 1

            if self.frame_count >= settings.RECORDINGS_FRAMES_PER_FILE:
                self.stop_recording()
                self.start_recording()

    def release(self):
        self.video.release()
        self.audio.release()

    def combine_video_audio_background(self, video_filename, audio_filename):
        def func():
            try:
                out_filename = combined_filename_from_video_filename(video_filename)
                if not ffmpeg.combine_video_audio(video_filename, audio_filename, out_filename):
                    return

                if not settings.RECORDINGS_KEEP_PARTS:
                    os.remove(video_filename)
                    os.remove(audio_filename)

                if self.full_video_name is None:
                    self.full_video_name = out_filename
                else:
                    if ffmpeg.append_videos(self.full_video_name, out_filename):
                        os.remove(out_filename)
            finally:
                self.combining_threads.remove(thread)
            
        thread = threading.Thread(target=func, daemon=True)
        self.combining_threads.append(thread)

        thread.start()

VIDEO_FORMAT = "MJPG"
VIDEO_SUFFIX = "-video"

class VideoRecorder:
    def __init__(self, camera, frame_written_callback=None):
        self.out_file = Mutex(None)
        self.filename = ""
        self.size = (camera.width, camera.height)
        self.camera = camera

        self.frame_written_callback = frame_written_callback

        self._background_reader_running = True
        self.background_thread = threading.Thread(target=self._write_in_background, daemon=True)

    def start_recording(self):
        with self.out_file.acquire() as lock:
            self._start_recording(lock)

    def _start_recording(self, lock):
        if not self.background_thread.is_alive():
            self.background_thread.start()

        self._stop_recording(lock)

        fourcc = cv2.VideoWriter_fourcc(*VIDEO_FORMAT)
        fps = self._determine_fps()
        self.filename = parts_filename(VIDEO_SUFFIX, settings.RECORDINGS_FILENAME_VIDEO_EXTENSION)
        lock.value = cv2.VideoWriter(self.filename, fourcc, fps, self.size)

    def stop_recording(self):
        with self.out_file.acquire() as lock:
            return self._stop_recording(lock)
    
    def _stop_recording(self, lock):
        filename = ""

        if lock.value is not None:
            filename = self.filename
            self.filename = ""
            lock.value.release()
            lock.value = None

        return filename

    def write_frame(self, frame):
        with self.out_file.acquire() as lock:
            if lock.value is None:
                return

            lock.value.write(frame)

    def release(self):
        self.stop_recording()
        self._background_reader_running = False
        self.background_thread.join()

    def _determine_fps(self):
        return settings.CAMERA_FPS

    def _write_in_background(self):
        start_time = time.time()
        seconds_per_frame = 1 / settings.CAMERA_FPS

        while self._background_reader_running:
            frame = self.camera.current_frame
            if frame is not None:
                self.write_frame(frame)
                if self.frame_written_callback is not None:
                    self.frame_written_callback()
            
            current_time = time.time()
            time_since_start = current_time - start_time
            sleep_time = seconds_per_frame - (time_since_start % seconds_per_frame)
            if sleep_time > 0:
                time.sleep(sleep_time)

WIDTH = 2
CHANNELS = 1
RATE = 44100
AUDIO_FORMAT = pyaudio.paInt16 if settings.RECORD_AUDIO else 0
AUDIO_SUFFIX = "-audio"

class AudioRecorder:
    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.outfile = Mutex(None)
        
        self.stream = self.pyaudio.open(
            format=self.pyaudio.get_format_from_width(WIDTH),
            channels=CHANNELS,
            rate=RATE,
            input=True,
            output=False,
            stream_callback=self.audio_callback
        )
        self.stream.start_stream()

    def start_recording(self):
        f = wave.open(parts_filename(AUDIO_SUFFIX, settings.RECORDINGS_FILENAME_AUDIO_EXTENSION), "wb")
        f.setnchannels(CHANNELS)
        f.setsampwidth(self.pyaudio.get_sample_size(AUDIO_FORMAT))
        f.setframerate(RATE)

        with self.outfile.acquire() as lock:
            lock.value = f

    def stop_recording(self):
        with self.outfile.acquire() as lock:
            if lock.value is None:
                return ""
            
            filename = lock.value._file.name
            lock.value.close()
            lock.value = None

            return filename

    def release(self):
        self.stop_recording()

        self.stream.stop_stream()
        self.stream.close()
        self.stream = None

        self.pyaudio.terminate()
        self.pyaudio = None

    def audio_callback(self, in_data, frame_count, time_info, status):
        with self.outfile.acquire() as lock:
            if lock.value is not None:
                lock.value.writeframes(in_data)

        return (None, pyaudio.paContinue)

def parts_filename(suffix, extension):
    return os.path.join(
        settings.RECORDINGS_DIRECTORY,
        settings.RECORDINGS_PARTS_SUBDIR_NAME,
        time.strftime(settings.RECORDINGS_FILENAME_FORMAT) + suffix + extension)

def combined_filename_from_video_filename(filename):
    (path, ext) = os.path.splitext(filename)
    filename = os.path.split(path)[1].replace(VIDEO_SUFFIX, "")

    return os.path.join(
        settings.RECORDINGS_DIRECTORY,
        filename + ext
    )
