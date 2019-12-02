import os
import base64

from bottle import route, view, static_file, request, run

import cv2

import camera

# Ensure the current directory is the file path of the main file - helps make code simpler
os.chdir(os.path.dirname(os.path.realpath(__file__)))

@route("/")
@view("main")
def main():
    class CameraModel:
        def __init__(self, id):
            self.id = id

    return { "cameras": [CameraModel(id) for id in camera.cameras.keys()] }

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

    frame = camera.cameras[id].current_frame
    if frame is not None:
        success, buf = cv2.imencode(format, frame)
        if success:
            return {
                "image": "data:" + mime_types[format] + ";base64, " + base64.b64encode(buf).decode("utf-8")
            }
    return {
        "image": None
    }

@route("/static/<name>")
def static(name):
    return static_file(name, root="./static")

run(host="localhost", port=8080, debug=True)
