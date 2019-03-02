import sys, time

sys.path.insert(0, 'hardware')
from controller import Controller
import camera_config

sys.path.insert(0, 'software')
import classiflier as clr

LEFT = 0 # Counter Clockwise
RIGHT = 1 # Clockwise
FORWARD = 2

STATE_SEARCH = 0
STATE_DITCH = 1

class MainLogic():
	def __init__(self):
		self.controller = Controller()
		self.classifier = clr.Classifier()
		self.state = STATE_SEARCH
		self.aura = 35 # objects within 35 units will be approached by rover
		self.resolution_width = camera_config.resolution_width,
		self.resolution_height = camera_config.resolution_height

	def get_distance(self):
		return abs(self.controller.get_distance())

	# ************ loop methods ************
	def loop(self):
		if self.state == STATE_SEARCH:
			self.search_object()
		elif self.state == STATE_DITCH:
			self.search_ditch()

	def search_object(self):
		# Step 1: Camera to identify object direction (left/right) and object classification
		# Classifier API returns object type and object coordinates
		objects = self.classifier.process(self.controller.capture_opencv())
		direction = LEFT
		object_type = clr.OBJECT_NONE
		for obj in objects:
			if obj[1] != clr.OBJECT_NONE:
				if obj[0][0] < self.resolution_width / 2:
					direction = LEFT
				elif obj[0][0] > self.resolution_width / 2:
					direction = RIGHT
				else:
					direction = FORWARD
				object_type = obj[1]



		# Step 2: Sweep with rover to identify objects (needs refinement)
		# Sensor to identify distance to object by turning the rover towards left/right
		l = 5
		running_distances = [999] * l
		while direction != FORWARD:
			distance = self.get_distance()
			print(distance)
			running_distances.append(distance)

			if len(running_distances) > l:
				running_distances.pop(0)

			if self.object_ahead(running_distances):
				break

			self.turn(direction = direction, delay = 0.01)


		# Step 3: Go straight because object in front of rover
		# Move forward at small intervals until object is within grasp of rover
		while distance > 5:
			self.move(direction = 0, speed = self.get_speed_from_distance(distance), delay = 0.1)
			distance = self.get_distance()

	def search_ditch(self):
		# TODO
		return 0


	# ************ supporting methods ************
	def turn(self, direction = 0, speed = 255, delay = 0.1):
		self.controller.turn(direction = direction, speed = speed)
		time.sleep(delay)
		self.controller.stop()

	def move(self, direction = 0, speed = 255, delay = 0.1):
		self.controller.move(direction = direction, speed = speed)
		time.sleep(delay)
		self.controller.stop()

	def object_ahead(self, running_distances):
		# Use Classifier to identify object coordinate, 
		# if object in center and sensor returns some resonable value then object is ahead
		return sum(running_distances) / len(running_distances) < self.aura
	def get_speed_from_distance(self, distance):
		# Calculate rover moving speed based on distance from object
		sMax = 255
		sMin = 1
		factor = 2 # higher it is slower the movement
		speed = (sMax-sMin) * distance / (factor * self.aura)
		return speed if speed < sMax else sMax

def main():
	m = MainLogic()
	while 1:
		m.loop()		
		return

main()