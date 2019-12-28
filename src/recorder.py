import os
import time
import wave

import cv2

from utils import Mutex
import settings

if settings.RECORD_AUDIO:
    import pyaudio


class Recorder:
    def __init__(self, camera_width, camera_height):
        self.video = VideoRecorder(camera_width, camera_height)
        self.audio = AudioRecorder()

        self.frame_count = 0

    def start_recording(self):
        self.video.start_recording()
        self.audio.start_recording()

        self.frame_count = 0

    def stop_recording(self):
        self.video.stop_recording()
        self.audio.stop_recording()

    def write_video_frame(self, frame):
        self.video.write_frame(frame)

        if settings.RECORDINGS_FRAMES_PER_FILE > 0:
            self.frame_count += 1

            if self.frame_count >= settings.RECORDINGS_FRAMES_PER_FILE:
                self.stop_recording()
                self.start_recording()

VIDEO_FORMAT = "MJPG"

class VideoRecorder:
    def __init__(self, camera_width, camera_height):
        self.out_file = Mutex(None)
        self.size = (camera_width, camera_height)

    def start_recording(self):
        with self.out_file.acquire() as lock:
            self._start_recording(lock)

    def _start_recording(self, lock):
        self._stop_recording(lock)

        fourcc = cv2.VideoWriter_fourcc(*VIDEO_FORMAT)
        fps = self._determine_fps()
        lock.value = cv2.VideoWriter(filename(settings.RECORDINGS_FILENAME_VIDEO_EXTENSION), fourcc, fps, self.size)

    def stop_recording(self):
        with self.out_file.acquire() as lock:
            self._stop_recording(lock)
    
    def _stop_recording(self, lock):
        if lock.value is not None:
            lock.value.release()
            lock.value = None

    def write_frame(self, frame):
        with self.out_file.acquire() as lock:
            if lock.value is None:
                return
            
            lock.value.write(frame)

    def _determine_fps(self):
        return settings.CAMERA_FPS

WIDTH = 2
CHANNELS = 2
RATE = 44100
AUDIO_FORMAT = pyaudio.paInt16 if settings.RECORD_AUDIO else 0

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
        f = wave.open(filename(settings.RECORDINGS_FILENAME_AUDIO_EXTENSION), "wb")
        f.setnchannels(CHANNELS)
        f.setsampwidth(self.pyaudio.get_sample_size(AUDIO_FORMAT))
        f.setframerate(RATE)

        with self.outfile.acquire() as lock:
            lock.value = f

    def stop_recording(self):
        with self.outfile.acquire() as lock:
            if lock.value is None:
                return
            
            lock.value.close()
            lock.value = None

    def release():
        self.stop_recording()

        self.stream.stop_stream()
        self.stream.close()
        self.stream = None

        self.pyaudio.terminate()

    def audio_callback(self, in_data, frame_count, time_info, status):
        with self.outfile.acquire() as lock:
            if lock.value is not None:
                lock.value.writeframes(in_data)

        return (None, pyaudio.paContinue)

def filename(extension):
    return os.path.join(
        settings.RECORDINGS_DIRECTORY,
        time.strftime(settings.RECORDINGS_FILENAME_FORMAT) + extension)
