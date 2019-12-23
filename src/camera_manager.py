import time
import threading
import os

import cv2

from camera import Camera, MockCamera, GridCamera, CurrentTimeCamera
from recorder import Recorder

import settings

cameras = []

def _create_cameras():
    cameras = []

    if settings.USE_MOCK_CAMERAS:
        for i in range(settings.MOCK_CAMERA_COUNT):
            cameras.append(MockCamera(i, settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT))

    else:
        for i in range(10):
            test = Camera(i, settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)

            if test.current_frame is not None:
                cameras.append(test)
            else:
                test.release()

    return [_merge_cameras(cameras)]

def _merge_cameras(cameras):
    return CurrentTimeCamera(GridCamera(cameras))

_background_reader_running = True
_background_reader_thread = None

def _camera_background_reader():
    while _background_reader_running:
        start = time.time()

        for camera in cameras:
            camera.update_frame()
        
        if _recorder is not None:
            _recorder.write_frames()
        
        end = time.time()
        total = end - start
        sleep_time = (1 / settings.CAMERA_FPS) - total
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

    if not os.path.exists(settings.RECORDINGS_DIRECTORY):
        os.mkdir(settings.RECORDINGS_DIRECTORY)

    filename = os.path.join(
        settings.RECORDINGS_DIRECTORY,
        time.strftime(settings.RECORDINGS_FILENAME_FORMAT))

    _recorder = Recorder(filename, cameras[0])
    _recorder.start_recording()

def stop_recording():
    global _recorder
    _recorder.stop_recording()
    _recorder = None

def is_recording():
    return _recorder is not None

def release_cameras():
    global cameras
    for camera in cameras:
        camera.release()
    cameras = []
