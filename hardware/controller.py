from multiprocessing.connection import Listener
from nanpy import (ArduinoApi, SerialManager)
from picamera import PiCamera
from time import sleep
import sys
import camera_config
import numpy as np

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

		self.outpins = {
			"enA": 10,
			"in1": 2,
			"in2": 3,
			"enB": 11,
			"in3": 4,
			"in4": 5
		}
		self.inpins = {

		}

		arduino.pinMode(self.outpins["enA"], arduino.OUTPUT)
		arduino.pinMode(self.outpins["in1"], arduino.OUTPUT)
		arduino.pinMode(self.outpins["in2"], arduino.OUTPUT)
		arduino.pinMode(self.outpins["enB"], arduino.OUTPUT)
		arduino.pinMode(self.outpins["in3"], arduino.OUTPUT)
		arduino.pinMode(self.outpins["in4"], arduino.OUTPUT)

		# Not sure why below doens't work - TODO: fix later
		# for k, p in enumerate(self.outpins.items()):
		# 	arduino.pinMode(p, arduino.OUTPUT)
		# for k, p in enumerate(self.inpins.items()):
		# 	arduino.pinMode(p, arduino.INPUT)

		return arduino

	def establish_connection(self):
		# establish connection to the Arduino
		try:
			conn = SerialManager()
			return ArduinoApi(connection = conn)
		except:
			print("Failed to establish connection with the Arduino")
			sys.exit("Failed to establish connection with the Arduino")

	def setup_camera(self):
		try:
			camera = PiCamera()
			self.resolution = (camera_config.resolution_width, camera_config.resolution_height)
			camera.resolution = self.resolution
			return camera
		except:
			print("Failed to set up camera")
			sys.exit("Failed to set up camera")


	'''
	Public functions for pictures / rover movements etc.
	'''

	# **************** Camera ****************
	def capture(self, output = 'image', format = 'jpeg'):
		if self.camera != None:
			self.camera.capture(output, format = format)
		else:
			print("Controller has no camera.")
	def capture_continuous(self, output = 'image', format = 'jpeg'):
		# returns an infinite iterator with output names = images + "-{counter}" 
		if self.camera != None:
			return self.camera.capture_continuous(output + "-{counter}", format = format)
		else:
			print("Controller has no camera.")
	def capture_opencv(self):
		if self.camera != None:
			image = np.empty((self.resolution[1] * self.resolution[0] * 3,), dtype=np.uint8)
			self.camera.capture(image, 'bgr')
			image = image.reshape((self.resolution[1], self.resolution[0], 3))
			return image
		else:
			print("Controller has no camera.")
		
	# **************** Rover ****************
	def move_l_wheel(self, direction = 1):
		if(direction == 1): #Move forward
			self.arduino.digitalWrite(self.outpins["in1"], self.HIGH)
			self.arduino.digitalWrite(self.outpins["in2"], self.LOW)

		else: #Move backwards
			self.arduino.digitalWrite(self.outpins["in1"], self.LOW)
			self.arduino.digitalWrite(self.outpins["in2"], self.HIGH)

	def move_r_wheel(self, direction = 1):
		if(direction == 1): #Move forward
			self.arduino.digitalWrite(self.outpins["in3"], self.HIGH)
			self.arduino.digitalWrite(self.outpins["in4"], self.LOW)

		else: #Move backwards
			self.arduino.digitalWrite(self.outpins["in3"], self.LOW)
			self.arduino.digitalWrite(self.outpins["in4"], self.HIGH)


	def move(self, direction = 1, speed = 255):
		self.move_l_wheel(direction)
		self.move_r_wheel(direction)

		self.arduino.analogWrite(self.outpins["enA"], speed)
		self.arduino.analogWrite(self.outpins["enB"], speed)

	def turn(self, direction = 1, speed = 255):
		#direction can either be 0 or 1
		#0 : turn counter clockwise
		#1 : turn clockwise
		self.move_l_wheel(direction) #crappy implementation, either 0 or 1
		self.move_r_wheel(direction+1) #crappy implementation, either 1 or 2

		self.arduino.analogWrite(self.outpins["enA"], speed)
		self.arduino.analogWrite(self.outpins["enB"], speed)


	def stop(self):
		self.arduino.digitalWrite(self.outpins["in1"], self.LOW)
		self.arduino.digitalWrite(self.outpins["in2"], self.LOW)

		self.arduino.digitalWrite(self.outpins["in3"], self.LOW)
		self.arduino.digitalWrite(self.outpins["in4"], self.LOW)

		self.arduino.analogWrite(self.outpins["enA"], 0)
		self.arduino.analogWrite(self.outpins["enB"], 0)

	'''
	Destructor
	'''
	def __del__(self):
		if self.camera != None:
			self.camera.close()