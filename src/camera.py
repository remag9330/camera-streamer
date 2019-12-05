import random

import cv2
import numpy as np

class Camera:
    def __init__(self, camera_id, width, height, fps):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps

        self.camera = cv2.VideoCapture(self.camera_id)

        if self.fps > 0:
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)

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
    def __init__(self, camera_id, width, height, fps):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps

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
