'''
Using imports.
 - for when using Python for computer visions
'''

from time import sleep
import sys
sys.path.insert(0, '/home/pi/Capstone-GC/hardware/')

from controller import Controller
import numpy as np
import cv2


controller = Controller()

# img = controller.capture("image.jpg")

# cv2_img = controller.capture_opencv()
# cv2.imwrite('image-opencv.jpg', cv2_img)

# controller.move()
# sleep(2)
# controller.stop()
speed = 255
# for i in range(10):	
# 	controller.turn(speed = speed)
# 	sleep(0.025)
# 	controller.stop()
# 	sleep(0.1)
controller.move(speed = speed)
sleep(0.5)
controller.stop()
sleep(0.5)
controller.move(speed = speed, direction = 0)
sleep(0.5)
controller.stop()

controller.turn(speed = speed)
sleep(0.5)
controller.stop()
sleep(0.5)
controller.turn(speed = speed, direction = 0)
sleep(0.5)
controller.stop()

sleep

# sleep(0.5)

# for i in range(10):	
# 	controller.turn(direction = 0, speed = speed)
# 	sleep(0.021)
# 	controller.stop()
# 	sleep(0.1)
# controller.turn(direction = 0, speed = speed)
# sleep(1)
# controller.stop()