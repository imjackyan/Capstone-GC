import sys
import time
from PIL import Image

sys.path.insert(0,"/home/pi/Capstone-GC/hardware")
from controller import Controller
from camera_config import *

sys.path.insert(0,"/home/pi/Capstone-GC/software")
from client import Client
from objectdata import ObjectData

controller = Controller()
c = Client()
print("Client initialzed");
LEFT = 0
RIGHT = 1


def capture_and_process():
	controller.capture("image.jpg")

	img = Image.open("image.jpg")
	img = img.rotate(180)

	c.send_PIL(img)
	objs = c.connection_receive()
	return objs




def turn(direction = 0, speed = 255, delay = 0.1):
		controller.turn(direction = direction, speed = speed)
		time.sleep(delay)
		controller.stop()

def main():
	ratio = 0.01 # second per degree
	objs = []
	while len(objs) == 0:
		objs = capture_and_process()
		print(len(objs))
		if len(objs) > 0:
			break
		turn(LEFT, delay = ratio * 45)


	# found object
	print("found object")
	o = objs[0]
	d1 = resolution_width / 2 - ((o.x1 + o.x2) / 2)
	print(d1)
	t = 30 * ratio
	if d1 > 0:
		# obj is on the left
		turn(LEFT, delay = t)
	elif d1 < 0:
		# obj is on the right
		turn(RIGHT, delay = t)


	objs = capture_and_process()
	print("rescan obj length " + str(len(objs)))
	if len(objs) > 0:
		o = objs[0]
		d2 = resolution_width / 2 - ((o.x1 + o.x2) / 2)
		print(d2)
		if d2 > 0:
			turn(LEFT, delay = t * (d2 / (d1 + d2)))
		elif d2 < 0:
			turn(RIGHT, delay = t * (d2 / (d1 + d2)))




# objs = capture_and_process()
# for o in objs:
# 	print(o.width, o.height)
# 	print(o.x1, o.y1, o.x2, o.y2)
# 	print("*" * 10)

main()