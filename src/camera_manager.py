import base64
import time
import os
import logging

import cv2

from camera import Camera, MockCamera, GridCamera, CurrentTimeCamera
from recorder import Recorder

import settings


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

    return _merge_cameras(cameras)


def _merge_cameras(cameras):
    return CurrentTimeCamera(GridCamera(cameras))


camera = _create_cameras()


def _camera_reader(pipe):
    running = True
    start_time = time.time()
    seconds_per_frame = 1 / settings.CAMERA_FPS

    while running:
        camera.update_frame()

        current_time = time.time()
        time_since_start = current_time - start_time
        sleep_time = seconds_per_frame - (time_since_start % seconds_per_frame)
        if sleep_time > 0:
            time.sleep(sleep_time)

        if pipe.poll():
            msg = pipe.recv()
            if isinstance(msg, str) and msg == "terminate":
                running = False


def start_reader(pipe):
    logging.info("Starting cameras")
    try:
        _camera_reader(pipe)  # Blocks until shutdown
    except KeyboardInterrupt:
        pass
    logging.info("Cameras stopping, cleaning up")

    release_cameras()
    logging.info("Cameras cleaned up")


_recorder = None


def start_recording():
    global _recorder

    if not os.path.exists(settings.RECORDINGS_DIRECTORY):
        os.mkdir(settings.RECORDINGS_DIRECTORY)
    parts_dir = os.path.join(settings.RECORDINGS_DIRECTORY, settings.RECORDINGS_PARTS_SUBDIR_NAME)
    if not os.path.exists(parts_dir):
        os.mkdir(parts_dir)

    _recorder = Recorder(camera)
    _recorder.start_recording()
    logging.info("Recording started")


def stop_recording():
    global _recorder
    _recorder.stop_recording()
    _recorder.release()
    _recorder = None
    logging.info("Recording ended")


def is_recording():
    return _recorder is not None


def current_frame_base64(format):
    frame = camera.current_frame
    if frame is None:
        return None

    success, buf = cv2.imencode(format, frame)
    if not success:
        return None

    return base64.b64encode(buf).decode("utf-8")


def release_cameras():
    if is_recording():
        stop_recording()

    global camera
    camera.release()
    camera = None


# This only needs to be called if release_cameras is called prior - a camera will be created initially on module load
def create_cameras():
    global camera
    camera = _create_cameras()
