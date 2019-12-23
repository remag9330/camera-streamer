import os

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 10

RECORD_AUDIO = True

RECORDINGS_DIRECTORY = os.path.expanduser("~/Desktop/recordings")
RECORDINGS_FILENAME_FORMAT = "%Y-%m-%d-%H-%M-%S"
RECORDINGS_FILENAME_VIDEO_EXTENSION = ".avi"
RECORDINGS_FILENAME_AUDIO_EXTENSION = ".wav"
RECORDINGS_FRAMES_PER_FILE = 60 * 60 * CAMERA_FPS

USE_MOCK_CAMERAS = False
MOCK_CAMERA_COUNT = 10
