import socket
import sys
from PIL import Image
import pickle, time
from objectdata import ObjectData

class Client:
    MESSAGE = "GCCAPSTONE CLASSIFIER"

    BROADCAST_ADDRESS = '255.255.255.255'

    MSG_ENCODING = 'utf-8'
    PORT = 50000
    D_PORT = 49999

    RECV_BUFFER_SIZE = 1024

    def __init__(self):
        self.setup_sockets()
        self.discover_server()
        self.connect_to_server()

    def setup_sockets(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)

            # Set up broadcast socket
            self.d_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.d_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.d_socket.settimeout(5)
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def discover_server(self):
        self.SERVER_ADDRESS = ""
        try:
            while self.SERVER_ADDRESS == "":
                self.d_socket.sendto(Client.MESSAGE.encode(Client.MSG_ENCODING), (Client.BROADCAST_ADDRESS, Client.D_PORT))
                try:
                    recvd_bytes, address = self.d_socket.recvfrom(1024)
                    if recvd_bytes.decode(Client.MSG_ENCODING) == Client.MESSAGE:
                        print("Server found at {}".format(address))
                        self.SERVER_ADDRESS = address[0]
                        return self.SERVER_ADDRESS
                except socket.timeout:
                    pass
                except KeyboardInterrupt:
                    print()
                    self.socket.close()
                    self.d_socket.close()
                    sys.exit(1)

                time.sleep(2)
                print("Broadcast timed out, trying again ...")

        except Exception as msg:
            print(msg)

    def connect_to_server(self):
        try:
            # Connect to the server using its socket address tuple.
            self.socket.connect((self.SERVER_ADDRESS, Client.PORT))
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
                self.d_socket.close()
                sys.exit(1)

            objdatas = pickle.loads(recvd_bytes)
            return objdatas

        except Exception as msg:
            print(msg)
            sys.exit(1)

    def __del__(self):
        self.socket.close()
        self.d_socket.close()


