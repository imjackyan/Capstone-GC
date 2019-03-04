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
for o in objs:
	print(o.width, o.height)
	print(o.x1, o.y1, o.x2, o.y2)
	print("_"*10)