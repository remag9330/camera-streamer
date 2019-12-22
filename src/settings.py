import os

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 10

RECORDINGS_DIRECTORY = os.path.expanduser("~/Desktop/recordings")
RECORDINGS_FILENAME_FORMAT = "%Y-%m-%d-%H-%M-%S.avi"

USE_MOCK_CAMERAS = False
MOCK_CAMERA_COUNT = 10