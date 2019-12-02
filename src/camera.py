import time
import threading

import cv2

CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
CAMERA_FPS = 10

cameras = {}

def _create_cameras():
    cameras = {}

    for i in range(10):
        test = cv2.VideoCapture(i)
        success, _ = test.read()
        test.release()

        if success:
            cameras[i] = Camera(i, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS)

    return cameras

_background_reader_running = True
def _camera_background_reader():
    while _background_reader_running:
        start = time.time()

        for camera in cameras.values():
            camera.update_frame()
        
        end = time.time()
        total = end - start
        sleep_time = (1 / CAMERA_FPS) - total
        if sleep_time > 0:
            time.sleep(sleep_time)

_background_reader_thread = threading.Thread(target=_camera_background_reader, daemon=True)
_background_reader_thread.start()

def stop_background_reader():
    _background_reader_running = False
    _background_reader_thread.join()

class Camera:
    def __init__(self, camera_id, width, height, fps):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps

        self.camera = cv2.VideoCapture(self.camera_id)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.camera.set(cv2.CAP_PROP_FPS, self.fps)

        self.update_frame()
    
    def update_frame(self):
        success, data = self.camera.read()
        self.current_frame = data if success else None


cameras = _create_cameras()
