'''
Using imports.
 - for when using Python for computer visions
'''


import sys
sys.path.insert(0, '/home/pi/Capstone-GC/hardware/')

from controller import Controller
import numpy as np
import cv2


controller = Controller()

img = controller.capture("image.jpg")

cv2_img = controller.capture_opencv()
cv2.imwrite('image-opencv.jpg', cv2_img)