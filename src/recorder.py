import cv2

import settings

FORMAT = "MJPG"

class Recorder:
    def __init__(self, filename, camera):
        if camera is None: raise Exception("No camera supplied to the recorder")

        self.filename = filename
        self.camera = camera

        self.recorder = None
        self.size = self._determine_size()

    def start_recording(self):
        fourcc = cv2.VideoWriter_fourcc(*FORMAT)
        fps = self._determine_fps()
        self.recorder = cv2.VideoWriter(self.filename, fourcc, fps, self.size)
    
    def stop_recording(self):
        if self.recorder is not None:
            self.recorder.release()
            self.recorder = None

    def write_frames(self):
        if self.recorder is None:
            return
        
        self.recorder.write(self.camera.current_frame)

    def _determine_fps(self):
        return settings.CAMERA_FPS
