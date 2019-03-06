#!/usr/bin/python3

"""
Echo Client and Server Classes

T. D. Todd
McMaster University

to create a Client: "python EchoClientServer.py -r client" 
to create a Server: "python EchoClientServer.py -r server" 

or you can import the module into another file, e.g., 
import EchoClientServer

"""

########################################################################

import socket
import argparse
import sys
import pickle
from PIL import Image
from objectdata import *
import classiflier as clr
from window import Window

class Server:
    HOSTNAME = "0.0.0.0"

    # Set the server port to bind the listen socket to.
    PORT = 50000

    RECV_BUFFER_SIZE = 1024*1024
    MAX_CONNECTION_BACKLOG = 10
    
    MSG_ENCODING = "utf-8"

    # Create server socket address. It is a tuple containing
    # address/hostname and port.
    SOCKET_ADDRESS = (HOSTNAME, PORT)

    def __init__(self):
        self.classifier = clr.Classifier()
        self.window = Window()
        self.create_listen_socket()
        self.process_connections_forever()

    def create_listen_socket(self):
        try:
            # Create an IPv4 TCP socket.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Set socket layer socket options. This allows us to reuse
            # the socket without waiting for any timeouts.
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind socket to socket address, i.e., IP address and port.
            self.socket.bind(Server.SOCKET_ADDRESS)

            # Set socket to listen state.
            self.socket.listen(Server.MAX_CONNECTION_BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            while True:
                # Block while waiting for accepting incoming
                # connections. When one is accepted, pass the new
                # (cloned) socket reference to the connection handler
                # function.
                self.connection_handler(self.socket.accept())
        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            self.socket.close()
            sys.exit(1)
            
    def connection_handler(self, client):
        connection, address_port = client
        print("-" * 72)
        print("Connection received from {}.".format(address_port))
        
        while True:
            try:
                recvd_bytes = connection.recv(4)
            
                if len(recvd_bytes) == 0:
                    print("Closing client connection ... ")
                    connection.close()
                    break
                    
                msg_length = int.from_bytes(recvd_bytes, 'big')## first 4 bytes = size

                recvd_size = 0
                recvd_bytes = b''
                try:
                    while recvd_size < msg_length:
                        recvd = connection.recv(Server.RECV_BUFFER_SIZE)
                        if len(recvd) == 0:
                            print("Closing client connection ... ")
                            connection.close()
                            break
                        recvd_size = recvd_size + len(recvd)
                        recvd_bytes = recvd_bytes + recvd
                    print("receive ", len(recvd_bytes), "expected ", msg_length)

                    recvd_img = pickle.loads(recvd_bytes) ## load pil image

                    print("Image received, classifying..")
                    objs = self.classifier.process(recvd_img)
                    send_bytes = pickle.dumps(objs)
                    print("Sending data object back to client..")
                    connection.sendall(send_bytes)

                    print("Displaying new image")
                    for obj in objs:
                        self.window.rectangle(recvd_img, ((obj.x1, obj.y1), (obj.x2, obj.y2)))
                    self.window.display(recvd_img)

                except Exception as msg:
                    print(msg)
            except KeyboardInterrupt:
                print()
                print("Closing client connection ... ")
                connection.close()
                break

Server()






