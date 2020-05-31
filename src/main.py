import os
import time
import multiprocessing
import logging

import settings
import interprocess_communication as ipc


# Ensure the current directory is the file path of the main file - helps make code simpler
os.chdir(os.path.dirname(os.path.realpath(__file__)))

format = "%(levelname)s:%(processName)s:%(process)d:%(threadName)s:%(thread)d:%(name)s:%(asctime)s\n\t%(message)s"
level = logging.DEBUG
logging.basicConfig(format=format, level=level)

def start_cameras(pipe):
    import camera_manager

    logging.info("Starting camera process...")
    logging.info("Setting up camera IPC...")
    comm = ipc.CameraClientSide(camera_manager, settings.CONNECT_TO_IP, settings.PORT)
    logging.info("Camera IPC set up")
    logging.info("Starting reader")
    camera_manager.start_reader(pipe)
    logging.info("Reader stopped")
    logging.info("Stopping camera IPC")
    comm.stop()
    logging.info("Camera process finished successfully")

def start_webserver(pipe):
    import webserver

    logging.info("Starting webserver process...")
    logging.info("Setting up webserver IPC...")
    comm = ipc.WebServerSide(settings.BIND_IP, settings.PORT)
    logging.info("Webserver IPC set up")
    logging.info("Starting server")
    webserver.start_server(pipe, comm)
    logging.info("Server stopped")
    logging.info("Stopping webserver IPC")
    comm.stop()
    logging.info("Webserver process finished successfully")


def start_process(func, name):
    (p_conn, c_conn) = multiprocessing.Pipe()
    p = multiprocessing.Process(target=func, args=(c_conn,), name=name)
    p.start()
    return [p, p_conn]

def main():
    processes = []

    if settings.RUN_CAMERAS:
        processes.append(start_process(start_cameras, "cameras"))
        logging.info("Camera process started")

    if settings.RUN_WEBSERVER:
        processes.append(start_process(start_webserver, "webserver"))
        logging.info("Camera webserver started")

    if len(processes) == 0:
        logging.error("No processes started - ensure at least one of the RUN_* settings is True")
        return

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Ctrl-C caught - stopping")
    except Exception:
        logging.exception("Unexpected error - stopping")

    for [_, conn] in processes:
        conn.send("terminate")

    logging.info("Waiting for processes to exit...")
    for [p, _] in processes:
        p.join()
    logging.info("Processes exited - Application shutdown successful")

if __name__ == "__main__":
    main()
