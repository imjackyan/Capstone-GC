import argparse
from multiprocessing.connection import Listener, Client
from controller import Controller


PORT = 6000
address = ('localhost', PORT)
passwd = b'AUTHKEY-CAPSTONE'

parser = argparse.ArgumentParser()
parser.add_argument('--start', help="Start a listening server and Controller object", default=False, action="store_true")
parser.add_argument('--close', help="Close the server", default=False, action="store_true")
parser.add_argument('--capture', help="Capture an image, specify location", type=str, default="")
args = parser.parse_args()


if args.start:
	listener = Listener(address, authkey = passwd)
	con = Controller()
	while 1:
		print('Listening..')
		client = listener.accept()
		msg = client.recv()

		if msg[0] == 'capture':
			con.capture(msg[1])

		if msg[0] == 'close':
			client.close()
			break

	listener.close()

else:
	conn = Client(address, authkey = passwd)
	if args.capture:
		conn.send(['capture', args.capture])
	if args.close:
		conn.send(['close'])
	conn.close()