import sys
from PIL import Image

sys.path.insert(0,"/home/pi/Capstone-GC/hardware")
from controller import Controller

sys.path.insert(0,"/home/pi/Capstone-GC/software")
from client import Client
from objectdata import ObjectData


controller = Controller()
c = Client()
print("Client initialzed");

controller.capture("image.jpg")

img = Image.open("image.jpg")
img = img.rotate(180)

c.send_PIL(img)
objs = c.connection_receive()
print("NUMBER OF DETECTED OBJECTS: {}".format(len(objs)))
for o in objs:
	print("width: {}, height: {}".format(o.width, o.height))
	print("Bounding box: ", o.x1, o.y1, o.x2, o.y2)
	print("x: {}, y: {}".format(o.x, o.y))
	print("*"*10)