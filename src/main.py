import os

import camera_manager
import webserver

# Ensure the current directory is the file path of the main file - helps make code simpler
os.chdir(os.path.dirname(os.path.realpath(__file__)))

camera_manager.start_background_reader()

webserver.setup()
webserver.start_listening()

print("Stopping")
camera_manager.stop_background_reader()
if camera_manager.is_recording():
    camera_manager.stop_recording()

camera_manager.release_cameras()
