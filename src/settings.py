import os

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 10

RECORD_AUDIO = True

RECORDINGS_DIRECTORY = os.path.expanduser("~/Desktop/recordings")
RECORDINGS_PARTS_SUBDIR_NAME = "parts"
RECORDINGS_FILENAME_FORMAT = "%Y-%m-%d-%H-%M-%S"
RECORDINGS_FILENAME_VIDEO_EXTENSION = ".mp4"
RECORDINGS_FILENAME_AUDIO_EXTENSION = ".wav"
RECORDINGS_FRAMES_PER_FILE = 2 * CAMERA_FPS
RECORDINGS_KEEP_PARTS = True

USE_MOCK_CAMERAS = False
MOCK_CAMERA_COUNT = 4

RUN_CAMERAS = True
RUN_WEBSERVER = True

WEBSERVER_PORT = 8080

# -- Interprocess communication data -- #
# The IP for the socket in the camera process to connect to
CONNECT_TO_IP = "localhost"
# The IP for the server socket to listen on
BIND_IP = "0.0.0.0"
# The port for the server socket to listen on and the camera socket to connect to
PORT = 26349
