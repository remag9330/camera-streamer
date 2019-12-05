import time
import threading
import os

import cv2

from camera import Camera, MockCamera
from recorder import Recorder

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 10

RECORDINGS_DIRECTORY = os.path.expanduser("~/Desktop/recordings")
RECORDINGS_FILENAME_FORMAT = "%Y-%m-%d-%H-%M-%S.avi"

USE_MOCK_CAMERAS = False
MOCK_CAMERA_COUNT = 10

cameras = {}

def _create_cameras():
    cameras = {}

    if USE_MOCK_CAMERAS:
        for i in range(MOCK_CAMERA_COUNT):
            cameras[i] = MockCamera(i, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS)

    else:
        for i in range(10):
            test = Camera(i, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS)

            if test.current_frame is not None:
                cameras[i] = test
            else:
                test.release()

    return cameras

_background_reader_running = True
_background_reader_thread = None

def _camera_background_reader():
    while _background_reader_running:
        start = time.time()

        for camera in cameras.values():
            camera.update_frame()
        
        if _recorder is not None:
            _recorder.write_frames()
        
        end = time.time()
        total = end - start
        sleep_time = (1 / CAMERA_FPS) - total
        if sleep_time > 0:
            time.sleep(sleep_time)


cameras = _create_cameras()

def start_background_reader():
    global _background_reader_thread
    _background_reader_thread = threading.Thread(target=_camera_background_reader, daemon=True)
    _background_reader_thread.start()

def stop_background_reader():
    global _background_reader_running
    _background_reader_running = False
    if _background_reader_thread is not None:
        _background_reader_thread.join()

_recorder = None

def start_recording():
    global _recorder

    if not os.path.exists(RECORDINGS_DIRECTORY):
        os.mkdir(RECORDINGS_DIRECTORY)

    filename = os.path.join(
        RECORDINGS_DIRECTORY,
        time.strftime(RECORDINGS_FILENAME_FORMAT))

    _recorder = Recorder(filename, *list(cameras.values()))
    _recorder.start_recording()

def stop_recording():
    global _recorder
    _recorder.stop_recording()
    _recorder = None

def is_recording():
    return _recorder is not None

def release_cameras():
    global cameras
    for camera in cameras.values():
        camera.release()
    cameras = {}
