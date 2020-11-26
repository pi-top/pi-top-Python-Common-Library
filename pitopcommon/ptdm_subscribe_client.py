from pitopcommon.logger import PTLogger
from pitopcommon.ptdm_message import Message
from threading import Thread
from time import sleep
import traceback
import zmq


class PTDMSubscribeClient:
    __thread = Thread()

    def __init__(self):
        self.__thread = Thread(target=self.__thread_method)
        self.__thread.setDaemon(True)

        self.__message_dict = None

        self.__zmq_context = zmq.Context()

        self.__zmq_socket = self.__zmq_context.socket(zmq.SUB)
        self.__zmq_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        self.__continue = False

    def initialise(self, message_dict):
        self.__message_dict = message_dict

    def start_listening(self):
        PTLogger.debug("Opening request socket...")

        try:
            self.__zmq_socket.connect("tcp://127.0.0.1:3781")
            PTLogger.info("Request client ready.")

        except zmq.error.ZMQError as e:
            PTLogger.error("Error starting the request client: " + str(e))
            PTLogger.info(traceback.format_exc())

            return False

        sleep(0.5)

        self.__continue = True
        self.__thread.start()

        return True

    def stop_listening(self):
        PTLogger.info("Closing responder socket...")

        self.__continue = False
        if self.__thread.is_alive():
            self.__thread.join()

        self.__zmq_socket.close()
        self.__zmq_context.destroy()

        PTLogger.debug("Closed responder socket.")

    def __thread_method(self):
        PTLogger.info("Listening for requests...")

        poller = zmq.Poller()
        poller.register(self.__zmq_socket, zmq.POLLIN)
        while self.__continue:
            events = poller.poll(500)

            for i in range(len(events)):
                message_string = self.__zmq_socket.recv_string()
                message = Message.from_string(message_string)

                id = message.message_id()
                if id in self.__message_dict:
                    message.validate_parameters([])
                    function_to_run = self.__message_dict[id]
                    function_to_run()
