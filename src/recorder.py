import math

import cv2
import numpy as np

FORMAT = "MJPG"

class Recorder:
    def __init__(self, filename, *cameras):
        if len(cameras) == 0: raise Exception("Must be at least 1 camera to record from")

        self.filename = filename
        self.cameras = cameras
        self.camera_grid = _generate_camera_grid(cameras)

        self.recorder = None

    def start_recording(self):
        fourcc = cv2.VideoWriter_fourcc(*FORMAT)
        fps = self._determine_fps()
        size = self._determine_size()
        self.recorder = cv2.VideoWriter(self.filename, fourcc, fps, size)
    
    def stop_recording(self):
        if self.recorder is not None:
            self.recorder.release()

    def write_frames(self):
        if self.recorder is None:
            return
        
        fullImage = None
        for row in self.camera_grid:
            # Create the row image by concatenating the images horizontally
            rowImage = row[0].current_frame
            for cam in row[1:]:
                rowImage = cv2.hconcat([rowImage, cam.current_frame])
            
            # Then add these row images vertically
            if fullImage is None:
                fullImage = rowImage
            else:
                # Ensure the row is as wide as the whole image by adding some black space on the right
                if rowImage.shape[1] != fullImage.shape[1]:
                    blank_space = np.zeros((rowImage.shape[0], fullImage.shape[1] - rowImage.shape[1], 3), np.uint8)
                    rowImage = cv2.hconcat([rowImage, blank_space])

                fullImage = cv2.vconcat([fullImage, rowImage])        
        
        self.recorder.write(fullImage)

    def _determine_fps(self):
        return self.cameras[0].fps

    def _determine_size(self):
        width = 0
        height = 0

        for row in self.camera_grid:
            rowHeight = 0
            rowWidth = 0

            for camera in row:
                rowHeight = max(rowHeight, camera.height)
                rowWidth += camera.width

            width = max(width, rowWidth)
            height += rowHeight
        
        return (width, height)


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
