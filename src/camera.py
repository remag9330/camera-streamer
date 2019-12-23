import random
import math
import time

import cv2
import numpy as np

class Camera:
    def __init__(self, camera_id, width, height):
        self.camera_id = camera_id
        self.width = width
        self.height = height

        self.camera = cv2.VideoCapture(self.camera_id)

        if self.width > 0:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)

        if self.height > 0:
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        print(f"camera {self.camera_id} - width: {self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)}, height: {self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)}, fps: {self.camera.get(cv2.CAP_PROP_FPS)}")

        self.update_frame()
    
    def update_frame(self):
        success, data = self.camera.read()
        self.current_frame = data if success else None

    def release(self):
        self.camera.release()

class MockCamera:
    def __init__(self, camera_id, width, height):
        self.camera_id = camera_id
        self.width = width
        self.height = height

        self.blank_frame = np.full((height, width, 3), random.randint(0, 255), np.uint8)
        self.frame_count = 0

        self.update_frame()

    def update_frame(self):
        new_frame = np.array(self.blank_frame)
        self.frame_count += 1
        
        cv2.putText(
            new_frame,
            str(self.camera_id) + " - " + str(self.frame_count),
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255, 255),
            3
        )

        self.current_frame = new_frame

    def release(self):
        pass

class CurrentTimeCamera:
    _id = 0

    def __init__(self, camera):
        if camera is None: raise Exception("No camera supplied")

        self.camera_id = "CurrentTime-" + str(CurrentTimeCamera._id)
        CurrentTimeCamera._id += 1

        self.camera = camera
        self.width = camera.width
        self.height = camera.height

        self.update_frame()

    def update_frame(self):
        self.camera.update_frame()

        time = self._create_status_image(self.camera.current_frame.shape[1])
        # import pdb; pdb.set_trace()
        self.current_frame = cv2.vconcat([time, self.camera.current_frame])

    def release(self):
        self.camera.release()

    @staticmethod
    def _create_status_image(width):
        height = CurrentTimeCamera._determine_status_bar_height()
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

    @staticmethod
    def _determine_status_bar_height():
        return 50 # TODO Make better?

class GridCamera:
    _id = 0

    def __init__(self, cameras):
        if len(cameras) == 0: raise Exception("Must be at least 1 camera to record from")

        self.camera_id = "GridCamera-" + str(GridCamera._id)
        GridCamera._id += 1

        self.cameras = cameras

        self.camera_grid = self._generate_camera_grid(self.cameras)
        self.width, self.height = self._determine_size()

        self.update_frame()

    def update_frame(self):
        for camera in self.cameras:
            camera.update_frame()

        fullImage = self._row_image(self.camera_grid[0])

        for row in self.camera_grid[1:]:
            rowImage = self._row_image(row, fullImage.shape[1])
            fullImage = cv2.vconcat([fullImage, rowImage])

        self.current_frame = fullImage

    def release(self):
        for camera in self.cameras:
            camera.release()

    def _row_image(self, row, fullWidth=None):
        # Create the row image by concatenating the images horizontally
        rowImage = row[0].current_frame
        for cam in row[1:]:
            rowImage = cv2.hconcat([rowImage, cam.current_frame])
        
        # Ensure the row is as wide as the whole image by adding some black space on the right
        if fullWidth is not None and rowImage.shape[1] != fullWidth:
            blank_space = np.zeros((rowImage.shape[0], fullWidth - rowImage.shape[1], 3), np.uint8)
            rowImage = cv2.hconcat([rowImage, blank_space])

        return rowImage

    @staticmethod
    def _generate_camera_grid(cameras):
        grid = []

        cameras = list(cameras)
        columns = math.ceil(math.sqrt(len(cameras)))

        row = []
        while len(cameras) > 0:
            row.append(cameras.pop(0))

            if len(row) == columns:
                grid.append(row)
                row = []

        if len(row) > 0:
            grid.append(row)
        
        return grid

    def _determine_size(self):
        width = 0
        height = 0

        for row in self.camera_grid:
            rowWidth, rowHeight = self._determine_row_size(row)
            width = max(width, rowWidth)
            height += rowHeight
        
        return (width, height)

    @staticmethod
    def _determine_row_size(row):
        rowWidth = sum(cam.width for cam in row)
        rowHeight = max(cam.height for cam in row)

        return (rowWidth, rowHeight)
