import os
import time
import wave

import cv2

import settings

if settings.RECORD_AUDIO:
    import pyaudio


FORMAT = "MJPG"

class Recorder:
    def __init__(self, camera):
        if camera is None: raise Exception("No camera supplied to the recorder")

        self.filename = filename(settings.RECORDINGS_FILENAME_VIDEO_EXTENSION)
        self.camera = camera

        self.recorder = None
        self.size = (camera.width, camera.height)

        self.audio_recorder = None

        self.recorded_frames = 0

    def start_recording(self):
        fourcc = cv2.VideoWriter_fourcc(*FORMAT)
        fps = self._determine_fps()
        self.recorder = cv2.VideoWriter(self.filename, fourcc, fps, self.size)
        self.recorded_frames = 0

        if settings.RECORD_AUDIO:
            self.audio_recorder = AudioRecorder()
            self.audio_recorder.start_recording()
    
    def stop_recording(self):
        if self.recorder is not None:
            self.recorder.release()
            self.recorder = None

        if self.audio_recorder is not None:
            self.audio_recorder.stop_recording()
            self.audio_recorder = None

    def write_frames(self):
        if self.recorder is None:
            return
        
        self.recorder.write(self.camera.current_frame)

        self.recorded_frames += 1

        if self.recorded_frames >= settings.RECORDINGS_FRAMES_PER_FILE:
            self.stop_recording()
            self.filename = filename(settings.RECORDINGS_FILENAME_VIDEO_EXTENSION)
            self.start_recording()

    def _determine_fps(self):
        return settings.CAMERA_FPS

WIDTH = 2
CHANNELS = 2
RATE = 44100
AUDIO_FORMAT = pyaudio.paInt16

class AudioRecorder:
    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.stream = None
        self.outfile = None

    def start_recording(self):
        p = self.pyaudio
        self.stream = p.open(
            format=p.get_format_from_width(WIDTH),
            channels=CHANNELS,
            rate=RATE,
            input=True,
            output=False,
            stream_callback=self.callback
        )

        self.outfile = wave.open(filename(settings.RECORDINGS_FILENAME_AUDIO_EXTENSION), "wb")
        self.outfile.setnchannels(CHANNELS)
        self.outfile.setsampwidth(p.get_sample_size(AUDIO_FORMAT))
        self.outfile.setframerate(RATE)

        self.stream.start_stream()

    def stop_recording(self):
        self.outfile.close()
        self.outfile = None

        self.stream.stop_stream()
        self.stream.close()
        self.stream = None

    def release():
        self.pyaudio.terminate()

    def callback(self, in_data, frame_count, time_info, status):
        self.outfile.writeframes(in_data)
        return (None, pyaudio.paContinue)

def filename(extension):
    return os.path.join(
        settings.RECORDINGS_DIRECTORY,
        time.strftime(settings.RECORDINGS_FILENAME_FORMAT) + extension)
