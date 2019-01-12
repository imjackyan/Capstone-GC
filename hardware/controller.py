from multiprocessing.connection import Listener
from nanpy import (ArduinoApi, SerialManager)
from picamera import PiCamera
from time import sleep
import sys
import camera_config
import numpy as np
import cv2

class Controller():
	'''
	Controller set up functions
	'''
	def __init__(self):
		self.arduino = self.setup_arduino()
		self.camera = self.setup_camera()


	def setup_arduino(self):
		arduino = self.establish_connection()
		# set up pin modes on arduino
		self.LOW = arduino.LOW
		self.HIGH = arduino.HIGH
		arduino.pinMode(8, arduino.OUTPUT) # example
		return arduino

	def establish_connection(self):
		# establish connection to the Arduino
		try:
			conn = SerialManager()
			return ArduinoApi(connection = conn)
		except:
			sys.exit("Failed to establish connection with the Arduino")

	def setup_camera(self):
		try:
			camera = PiCamera()
			self.resolution = (camera_config.resolution_width, camera_config.resolution_height)
			camera.resolution = self.resolution
			return camera
		except:
			sys.exit("Failed to set up camera")


	'''
	Public functions for pictures / rover movements etc.
	'''

	# **************** Camera ****************
	def capture(self, output = 'image', format = 'jpeg'):
		self.camera.capture(output, format = format)
	def capture_continuous(self, output = 'image', format = 'jpeg'):
		# returns an infinite iterator with output names = images + "-{counter}" 
		return self.camera.capture_continuous(output + "-{counter}", format = format)

	def capture_opencv(self):
		image = np.empty((self.resolution[1] * self.resolution[0] * 3,), dtype=np.uint8)
		self.camera.capture(image, 'bgr')
		image = image.reshape((self.resolution[1], self.resolution[0], 3))
		return image
	
	# **************** Rover ****************
	def move(self, direction):
		self.arduino.digitalWrite(8, self.LOW)

	def turn(self, angle):
		self.arduino.digitalWrite(8, self.HIGH)

	'''
	Destructor
	'''
	def __del__(self):
		self.camera.close()