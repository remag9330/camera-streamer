import os
import time

import cv2

import settings

FORMAT = "MJPG"

class Recorder:
    def __init__(self, camera):
        if camera is None: raise Exception("No camera supplied to the recorder")

        self.filename = filename()
        self.camera = camera

        self.recorder = None
        self.size = (camera.width, camera.height)

        self.recorded_frames = 0

    def start_recording(self):
        fourcc = cv2.VideoWriter_fourcc(*FORMAT)
        fps = self._determine_fps()
        self.recorder = cv2.VideoWriter(self.filename, fourcc, fps, self.size)
        self.recorded_frames = 0
    
    def stop_recording(self):
        if self.recorder is not None:
            self.recorder.release()
            self.recorder = None

    def write_frames(self):
        if self.recorder is None:
            return
        
        self.recorder.write(self.camera.current_frame)

        self.recorded_frames += 1

        if self.recorded_frames >= settings.RECORDINGS_FRAMES_PER_FILE:
            self.stop_recording()
            self.filename = filename()
            self.start_recording()

    def _determine_fps(self):
        return settings.CAMERA_FPS

def filename():
    return os.path.join(
        settings.RECORDINGS_DIRECTORY,
        time.strftime(settings.RECORDINGS_FILENAME_FORMAT))
