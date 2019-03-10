import sys
sys.path.insert(0,"/home/pi/Capstone-GC/hardware")
from controller import Controller
from PIL import Image

c = Controller()

name = "images/ditch"
num = 60

while True:
	input("take pic {}".format(num))
	_name = name + str(num) + ".jpg"
	c.capture(_name)
	img = Image.open(_name)
	img = img.rotate(180)
	img.save(_name)
	num += 1