'''
Using imports.
 - for when using Python for computer visions
'''

import sys
sys.path.insert(0, '/home/pi/Capstone-GC/hardware/')

from controller import Controller
import numpy as np
import cv2
from time import sleep


# Initialize controller object
controller = Controller()

# Taking Images
img = controller.capture("image.jpg")

cv2_img = controller.capture_opencv()
cv2.imwrite('image-opencv.jpg', cv2_img)

# Rover movements
controller.move()
sleep(0.5)
controller.stop()

# Discretized scan by turning
speed = 200
for i in range(10):	
	controller.turn(speed = speed)
	sleep(0.025)
	controller.stop()
	sleep(0.1)

sleep(0.5)

for i in range(10):	
	controller.turn(direction = 0, speed = speed)
	sleep(0.021)
	controller.stop()
	sleep(0.1)
