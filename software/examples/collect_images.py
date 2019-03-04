import sys
sys.path.insert(0,"/home/pi/Capstone-GC/hardware")
from controller import Controller

c = Controller()

name = "images/positive-"
num = 0

while True:
	input("take pic")
	c.capture(name + str(num) + ".jpg")
	num += 1