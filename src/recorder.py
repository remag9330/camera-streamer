import math
import time

import cv2
import numpy as np

import settings

FORMAT = "MJPG"

class Recorder:
    def __init__(self, filename, *cameras):
        if len(cameras) == 0: raise Exception("Must be at least 1 camera to record from")

        self.filename = filename
        self.cameras = cameras
        self.camera_grid = _generate_camera_grid(cameras)

        self.recorder = None
        self.size = self._determine_size()

    def start_recording(self):
        fourcc = cv2.VideoWriter_fourcc(*FORMAT)
        fps = self._determine_fps()
        self.recorder = cv2.VideoWriter(self.filename, fourcc, fps, self.size)
    
    def stop_recording(self):
        if self.recorder is not None:
            self.recorder.release()

    def write_frames(self):
        if self.recorder is None:
            return
        
        fullImage = _create_status_image(self.size[0])

        for row in self.camera_grid:
            # Create the row image by concatenating the images horizontally
            rowImage = row[0].current_frame
            for cam in row[1:]:
                rowImage = cv2.hconcat([rowImage, cam.current_frame])
            
            # Then add these row images vertically
            # Ensure the row is as wide as the whole image by adding some black space on the right
            if rowImage.shape[1] != fullImage.shape[1]:
                blank_space = np.zeros((rowImage.shape[0], fullImage.shape[1] - rowImage.shape[1], 3), np.uint8)
                rowImage = cv2.hconcat([rowImage, blank_space])

            fullImage = cv2.vconcat([fullImage, rowImage])
        
        self.recorder.write(fullImage)

    def _determine_fps(self):
        return settings.CAMERA_FPS

    def _determine_size(self):
        width = 0
        height = _determine_status_bar_height()

        for row in self.camera_grid:
            rowWidth, rowHeight = _determine_row_size(row)
            width = max(width, rowWidth)
            height += rowHeight
        
        return (width, height)

def _determine_row_size(row):
    rowWidth = sum(cam.width for cam in row)
    rowHeight = max(cam.height for cam in row)

    return (rowWidth, rowHeight)

def _determine_status_bar_height():
    return 50 # TODO Make better?

def _create_status_image(width):
    height = _determine_status_bar_height()
    result = np.zeros((height, width, 3), np.uint8)
    cv2.putText(
        result,
        time.strftime("%Y-%m-%d %H:%M:%S"),
        (0, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255, 255),
        3
    )

    return result

def _generate_camera_grid(cameras):
    grid = []

    columns = math.ceil(math.sqrt(len(cameras)))
    cameras = list(cameras)

    row = []
    while len(cameras) > 0:
        row.append(cameras.pop(0))

        if len(row) == columns:
            grid.append(row)
            row = []

    if len(row) > 0:
        grid.append(row)
    
    return grid
