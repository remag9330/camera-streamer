import threading
import socket
import time
import uuid
import json
import logging

BYTES_PER_PACKET_SIZE = 4
PACKET_SIZE_ENDIANNESS = "big"

ID_BYTES_LEN = len(uuid.uuid4().bytes)

REQUEST_KEY = "request"

REQUEST_RESPONSE_TIMEOUT = 30 # seconds


class BaseConnection:
    def __init__(self, ip, port):
        self.messages_to_send = []
        self.received_messages = []
        self.unfinished_read_buffer = b""

        self.running = True
        self.thread = self._start_background_thread(ip, port)

    def stop(self):
        self._stop_background_thread()

    def _send_request_receive_response(self, data, data_type="bytes"):
        if data_type == "json":
            data = json.dumps(data).encode("utf-8")

        id = self._generate_id_and_send(data)
        
        start = time.time()
        while time.time() - start <= REQUEST_RESPONSE_TIMEOUT:
            response = self._recv_by_id(id)
            if response is not None:
                break
            time.sleep(0.1)

        if response is None:
            raise TimeoutError("request response timeout reached")

        if data_type == "json":
            response = json.loads(response.decode("utf-8"))

        return response

    def _generate_id_and_send(self, data):
        id = self._generate_id()
        self._send(id + data)
        return id

    def _send(self, data):
        self.messages_to_send.append(data)

    def _recv_by_id(self, id):
        for (i, v) in enumerate(self.received_messages):
            if v.startswith(id):
                result = v[len(id):]
                del self.received_messages[i]
                return result

        return None
    
    def _recv(self):
        if len(self.received_messages) > 0:
            return self.received_messages.pop()

        return None

    def _generate_id(self):
        return uuid.uuid4().bytes

    def _start_background_thread(self, ip, port):
        t = threading.Thread(target=self._mainloop, args=(ip, port))
        t.start()
        return t

    def _stop_background_thread(self):
        self.running = False
        self.thread.join()

    def _mainloop(self, ip, port):
        while self.running:
            self._connect_or_accept(ip, port)

            while self.running:
                try:
                    self._try_send_data()
                    self._try_receive_data()
                    time.sleep(0.1)
                except ConnectionError:
                    logging.warning("Connection error occurred - reconnecting...")
                    break

    def _connect_or_accept(self, ip, port):
        raise NotImplementedError("Must be overridden!")

    def _try_send_data(self):
        if len(self.messages_to_send) > 0:
            try:
                data = self.messages_to_send[0]
                data_len_bytes = len(data).to_bytes(BYTES_PER_PACKET_SIZE, PACKET_SIZE_ENDIANNESS)
                self.socket.sendall(data_len_bytes + data)
                # Only if the send successfully completes do we remove the data from messages_to_send
                self.messages_to_send.pop()
            except Exception:
                logging.exception("Error in WebServerSide!")

    def _try_receive_data(self):
        try:
            raw = self.socket.recv(4096)
            if len(raw) == 0:
                logging.debug("Recieved 0 data")
                raise ConnectionAbortedError("Connection was closed")

            self.unfinished_read_buffer += raw
            while len(self.unfinished_read_buffer) > 0:
                if len(self.unfinished_read_buffer) < BYTES_PER_PACKET_SIZE:
                    return

                packet_size = int.from_bytes(self.unfinished_read_buffer[:BYTES_PER_PACKET_SIZE], PACKET_SIZE_ENDIANNESS)
                raw_packet_size = packet_size + BYTES_PER_PACKET_SIZE
                if len(self.unfinished_read_buffer) < raw_packet_size:
                    return

                raw_msg = self.unfinished_read_buffer[:raw_packet_size]
                self.unfinished_read_buffer = self.unfinished_read_buffer[raw_packet_size:]
                message = raw_msg[BYTES_PER_PACKET_SIZE:]

                if not self._process_message_on_receive(message):
                    self.received_messages.append(message)
            
        except (BlockingIOError, socket.timeout):
            return

    def _process_message_on_receive(self, msg_bytes):
        return False


class WebServerSide(BaseConnection):
    def __init__(self, ip, port):
        self.srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv_socket.bind((ip, port))
        self.srv_socket.listen()
        
        super().__init__(ip, port)

    def is_recording(self):
        request = { REQUEST_KEY: "is_recording" }
        response = self._send_request_receive_response(request, "json")
        return response["value"]

    def start_recording(self):
        request = { REQUEST_KEY: "start_recording" }
        response = self._send_request_receive_response(request, "json")
        return response["value"]
        
    def stop_recording(self):
        request = { REQUEST_KEY: "stop_recording" }
        response = self._send_request_receive_response(request, "json")
        return response["value"]

    def current_frame_base64(self, format):
        request = { REQUEST_KEY: "current_frame_base64", "format": format }
        response = self._send_request_receive_response(request, "json")
        return response["value"]

        
    def _connect_or_accept(self, ip, port):
        logging.info("Waiting for connection...")
        self.srv_socket.settimeout(1)
        while self.running:
            try:
                [self.socket, self.clnt_ip] = self.srv_socket.accept()
                logging.info("Connection received.")
                self.socket.setblocking(False)
                break
            except socket.timeout:
                logging.debug("No connection accepted before timeout - retrying")
                pass
        

class CameraClientSide(BaseConnection):
    def __init__(self, camera_manager, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camera_manager = camera_manager
        
        super().__init__(ip, port)

    def _connect_or_accept(self, ip, port):
        while self.running:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((ip, port))
                logging.info("Socket connected")
                break
            except ConnectionError:
                logging.warn("Could not connect to server - re-attempting...")
                time.sleep(1)

        self.socket.setblocking(False)

    def _process_message_on_receive(self, msg_bytes):
        [msg_id, msg_bytes] = [msg_bytes[:ID_BYTES_LEN], msg_bytes[ID_BYTES_LEN:]]

        try:
            msg = json.loads(msg_bytes.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            return False

        if REQUEST_KEY in msg:
            response = self._process_message(msg)
            if response is not None:
                res_bytes = json.dumps(response).encode("utf-8")
                self._send(msg_id + res_bytes)
                return True

        return False

    def _process_message(self, message):
        req = message[REQUEST_KEY]
        # logging.debug("Recieved: " + req)

        if req == "is_recording":
            return { "value": self.camera_manager.is_recording() }
        elif req == "start_recording":
            self.camera_manager.start_recording()
            return { "value": True }
        elif req == "stop_recording":
            self.camera_manager.stop_recording()
            return { "value": True }
        elif req == "current_frame_base64":
            format = message["format"]
            return { "value": self.camera_manager.current_frame_base64(format) }
