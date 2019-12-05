import os
import base64

from bottle import route, view, static_file, request, run

import cv2

import camera_manager

# Ensure the current directory is the file path of the main file - helps make code simpler
os.chdir(os.path.dirname(os.path.realpath(__file__)))

@route("/")
@view("main")
def main():
    class CameraModel:
        def __init__(self, id):
            self.id = id

    return {
        "cameras": [CameraModel(id) for id in camera_manager.cameras.keys()],
        "isRecording": camera_manager.is_recording()
    }

@route("/frame/<id:int>")
def frame(id):
    format = request.query.format or ".jpg"
    if format[0] != ".":
        format = "." + format
    
    mime_types = {
        ".jpg": "image/jpeg",
        ".png": "image/png"
    }

    if format not in mime_types:
        format = ".jpg"

    frame = camera_manager.cameras[id].current_frame
    if frame is not None:
        success, buf = cv2.imencode(format, frame)
        if success:
            return {
                "image": "data:" + mime_types[format] + ";base64, " + base64.b64encode(buf).decode("utf-8")
            }
    return {
        "image": None
    }

@route("/recording/start")
def start_recording():
    camera_manager.start_recording()

@route("/recording/stop")
def stop_recording():
    camera_manager.stop_recording()

@route("/static/<name>")
def static(name):
    return static_file(name, root="./static")

camera_manager.start_background_reader()

run(host="localhost", port=8080, debug=True, quiet=True)

print("Stopping")
camera_manager.stop_background_reader()
if camera_manager.is_recording():
    camera_manager.stop_recording()

camera_manager.release_cameras()
