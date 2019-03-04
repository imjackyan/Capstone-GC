import socket
import sys
from PIL import Image
import pickle
from objectdata import ObjectData

class Client:
    # Set the server hostname to connect to. If the server and client
    # are running on the same machine, we can use the current
    # hostname.
    # SERVER_HOSTNAME = socket.gethostname()
    SERVER_HOSTNAME = '192.168.0.107'
    MSG_ENCODING = 'utf-8'
    PORT = 50000

    RECV_BUFFER_SIZE = 1024

    def __init__(self):
        self.get_socket()
        self.connect_to_server()

    def get_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connect_to_server(self):
        try:
            # Connect to the server using its socket address tuple.
            self.socket.connect((Client.SERVER_HOSTNAME, Client.PORT))
            self.socket.settimeout(None)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def send_PIL(self, PIL_image):
        try:
            d = pickle.dumps(PIL_image)
            d = (len(d)).to_bytes(4, 'big') + d
            self.socket.sendall(d)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def connection_receive(self):
        try:
            recvd_bytes = self.socket.recv(Client.RECV_BUFFER_SIZE)

            if len(recvd_bytes) == 0:
                print("Closing server connection ... ")
                self.socket.close()
                sys.exit(1)

            objdatas = pickle.loads(recvd_bytes)
            return objdatas

        except Exception as msg:
            print(msg)
            sys.exit(1)


