from pitopcommon.ptdm_message import Message
import zmq
import atexit


class PTDMRequestClient:
    def __init__(self):
        self.zmq_socket = None

    def __enter__(self):
        self.initialise()

    def __exit__(self):
        self.cleanup()

    def initialise(self):
        atexit.register(self.cleanup)
        self.connect_to_socket()

    def connect_to_socket(self):
        zmq_context_send = zmq.Context()
        self.zmq_socket = zmq_context_send.socket(zmq.REQ)
        self.zmq_socket.sndtimeo = 1000
        self.zmq_socket.rcvtimeo = 1000
        self.zmq_socket.connect("tcp://127.0.0.1:3782")

    def send_request(self, message_request_id, parameters=list(), verbose=False):
        message = Message.from_parts(message_request_id, parameters)
        self.send_message(message, verbose)

    def send_message(self, message, verbose=False):
        self._zmq_socket.send_string(message.to_string())

        response_string = self._zmq_socket.recv_string()
        response_object = Message.from_string(response_string)

        if verbose:
            print(f"RESP:\t{response_object.message_friendly_string()}")

        return response_object

    def cleanup(self):
        if self.zmq_socket is not None:
            self.zmq_socket.close(0)
        atexit.unregister(self.cleanup)
