import os

from bottle import route, view, static_file, run

import cv2

# Ensure the current directory is the file path of the main file - helps make code simpler
os.chdir(os.path.dirname(os.path.realpath(__file__)))

@route("/")
@view("main")
def main():
    return { "cameras": [{"id": 0}, {"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}] }

@route("/static/<name>")
def static(name):
    return static_file(name, root="./static")

run(host="localhost", port=8080, debug=True)
