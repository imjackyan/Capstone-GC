import socket
import argparse, glob
import sys, os, time
import pickle
from PIL import Image
from objectdata import *
import classiflier as clr
from window import Window

LOGGING = False
LOG_DIRECTORY = "log_images"

class Server:
    MESSAGE = "GCCAPSTONE CLASSIFIER"

    HOSTNAME = "0.0.0.0"

    # Set the server port to bind the listen socket to.
    PORT = 50000
    D_PORT = 49999 # for discovery

    RECV_BUFFER_SIZE = 1024*1024
    MAX_CONNECTION_BACKLOG = 10
    
    MSG_ENCODING = "utf-8"

    def __init__(self):
        self.classifier = clr.Classifier()
        self.create_listen_socket()
        self.process_connections_forever()

    def create_listen_socket(self):
        try:
            # Set up TCP socket for classification
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((Server.HOSTNAME, Server.PORT))
            self.socket.listen(Server.MAX_CONNECTION_BACKLOG)
            print("Listening on port {} ...".format(Server.PORT))

            # Set up UDP discovery service socket
            self.d_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.d_socket.bind((Server.HOSTNAME, Server.D_PORT))
            print("Broadcast port {}".format(Server.D_PORT))
        except Exception as msg:
            print(msg)
            sys.exit(1)

    def process_connections_forever(self):
        try:
            self.socket.setblocking(False)
            self.d_socket.setblocking(False)

            while True:
                # Check UDP for broadcast requests
                try:
                    data, address = self.d_socket.recvfrom(Server.RECV_BUFFER_SIZE)
                    data = data.decode(Server.MSG_ENCODING)
                    print("Broadcast received: {}".format(address))
                    print("Key received: {}".format(data))
                    if data == Server.MESSAGE:
                        self.d_socket.sendto(Server.MESSAGE.encode(Server.MSG_ENCODING), address)
                except socket.error:
                    pass

                # Process TCP connection, only allow 1 client
                try:
                    client = self.socket.accept()
                    self.connection_handler(client)
                except socket.error:
                    pass

        except Exception as msg:
            print(msg)
        except KeyboardInterrupt:
            print()
        finally:
            self.socket.close()
            self.d_socket.close()
            sys.exit(1)
        
    def connection_handler(self, client):
        connection, address_port = client
        print("-" * 72)
        print("Connection received from {}.".format(address_port))
        connection.setblocking(False)
        _window = Window()
        
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
                while recvd_size < msg_length:
                    try:
                        recvd = connection.recv(Server.RECV_BUFFER_SIZE)
                        if len(recvd) == 0:
                            print("Closing client connection ... ")
                            connection.close()
                            break
                        recvd_size = recvd_size + len(recvd)
                        recvd_bytes = recvd_bytes + recvd

                        if recvd_size == msg_length:
                            print("receive ", len(recvd_bytes), "expected ", msg_length)

                            recvd_img = pickle.loads(recvd_bytes) ## load pil image

                            print("Image received, classifying..")
                            objs = self.classifier.process(recvd_img)
                            send_bytes = pickle.dumps(objs)
                            print("Sending data object back to client..")
                            connection.sendall(send_bytes)

                            print("Displaying new image")
                            for obj in objs:
                                _window.rectangle(recvd_img, ((obj.x1, obj.y1), (obj.x2, obj.y2)), obj.object_type)
                            _window.display(recvd_img)
                            if args.log:
                                recvd_img.save(os.path.join(LOG_DIRECTORY, "{}.jpg").format(time.strftime("%m%d-%H%M%S")))
                                logged_images = glob.glob(os.path.join(LOG_DIRECTORY, "*.jpg"))
                                if len(logged_images) > args.max_backlog:
                                    logged_images.sort()
                                    for im in logged_images[:len(logged_images) - args.max_backlog]:
                                        os.remove(im)

                    except KeyboardInterrupt:
                        print("Closing client connection ... ")
                        connection.close()
                        break
                    except socket.error:
                        pass
                    except Exception as msg:
                        print(msg)

            except KeyboardInterrupt:
                print("Closing client connection ... ")
                connection.close()
                break
            except socket.error:
                pass

            try:
                _window.update()
            except:
                pass

        try:
            _window.destroy()
        except:
            pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', action="store_true", default=False, help="Log the pictures")
    parser.add_argument('--max_backlog', default=100, help="Store maximum log")
    args = parser.parse_args()
    if args.log:
        print("Logging enabled.")
        LOGGING = True
        if not os.path.exists(LOG_DIRECTORY):
            os.mkdir(LOG_DIRECTORY)

    Server()






