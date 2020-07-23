import time
import os
import logging

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
    global _recorder

    logging.info("Starting cameras")
    try:
        _camera_reader(pipe)  # Blocks until shutdown
    except KeyboardInterrupt:
        pass
    logging.info("Cameras stopping, cleaning up")

    release_cameras()
    logging.info("Cameras cleaned up")

    _recorder.release()
    _recorder = None


def _create_recorder():
    if not os.path.exists(settings.RECORDINGS_DIRECTORY):
        os.mkdir(settings.RECORDINGS_DIRECTORY)

    parts_dir = os.path.join(settings.RECORDINGS_DIRECTORY, settings.RECORDINGS_PARTS_SUBDIR_NAME)
    if not os.path.exists(parts_dir):
        os.mkdir(parts_dir)

    return Recorder(camera)


_recorder = _create_recorder()


def start_recording():
    global _recorder

    _recorder.start_recording()
    logging.info("Recording started")


def stop_recording():
    global _recorder

    _recorder.stop_recording()
    logging.info("Recording ended")


def is_recording():
    return _recorder.is_recording()


def segment(last_received):
    if len(_recorder.all_combined_segments) == 0:
        logging.info("No segments exist, returning empty byte string")
        return ("", b"")

    segments_to_check = [get_filename(i) for i in _recorder.all_combined_segments[-10:]]

    if last_received == segments_to_check[-1]:
        logging.info("Last received segment is most recent segment, returning empty byte string")
        return ("", b"")

    if last_received in segments_to_check:
        idx_offset = len(_recorder.all_combined_segments) - len(segments_to_check)
        index_to_serve = segments_to_check.index(last_received) + 1 + idx_offset
        logging.info("Serving index %s", index_to_serve)
    else:
        index_to_serve = max(len(_recorder.all_combined_segments) - 2, 0)
        logging.info("last_segment cannot be found '%s' - serving index %s", last_received, index_to_serve)

    filename = _recorder.all_combined_segments[index_to_serve]
    with open(filename, "rb") as f:
        buf = f.read()

    return (get_filename(filename), buf)


def get_filename(s):
    return os.path.split(s)[1]


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
