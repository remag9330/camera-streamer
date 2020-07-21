import base64
import threading
import logging

from bottle import route, view, static_file, run, ServerAdapter, response

import settings


def start_server(pipe, cam_comm):
    setup(cam_comm)
    t = start_stopper_listener(pipe)
    logging.info("Starting web server...")
    start_listening()
    logging.info("Web server stopped!")
    t.join()
    logging.info("Server terminated.")


def start_listening():
    run(server=server)


def start_stopper_listener(pipe):
    t = threading.Thread(target=_stopper_listener, args=(pipe,), name="Webserver Stopper Listener")
    t.start()
    return t


def _stopper_listener(pipe):
    while True:
        msg = pipe.recv()
        if isinstance(msg, str) and msg == "terminate":
            logging.info("Received terminate command - stopping")
            server.stop()
            break


def setup(cam_comm):
    @route("/")
    @view("main")
    def main():
        return {
            "isRecording": cam_comm.is_recording(),
            "segmentLengthSeconds": settings.RECORDINGS_FRAMES_PER_FILE / settings.CAMERA_FPS
        }

    @route("/segment")
    def segment():
        (filename, enc_segment) = cam_comm.segment()
        segment = base64.b64decode(enc_segment.encode("utf-8"))
        response.set_header("X-segment-name", filename)
        return segment

    @route("/recording/start")
    def start_recording():
        cam_comm.start_recording()

    @route("/recording/stop")
    def stop_recording():
        cam_comm.stop_recording()

    @route("/static/<name>")
    def static(name):
        return static_file(name, root="./static")


class MyWSGIRefServer(ServerAdapter):
    def run(self, app):  # pragma: no cover
        from wsgiref.simple_server import WSGIRequestHandler, WSGIServer
        from wsgiref.simple_server import make_server
        import socket

        class FixedHandler(WSGIRequestHandler):
            def address_string(self):  # Prevent reverse DNS lookups please.
                return self.client_address[0]

            def log_request(*args, **kw):
                if not self.quiet:
                    return WSGIRequestHandler.log_request(*args, **kw)

        handler_cls = self.options.get('handler_class', FixedHandler)
        server_cls = self.options.get('server_class', WSGIServer)

        if ':' in self.host:  # Fix wsgiref for IPv6 addresses.
            if getattr(server_cls, 'address_family') == socket.AF_INET:
                class server_cls(server_cls):
                    address_family = socket.AF_INET6

        self.server = make_server(self.host, self.port, app, server_cls, handler_cls)
        self.server.serve_forever()

    def stop(self):
        # self.server.server_close() <--- alternative but causes bad fd exception
        self.server.shutdown()


server = MyWSGIRefServer(host="0.0.0.0", port=settings.WEBSERVER_PORT)
server.quiet = True
server.debug = True
