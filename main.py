import sys, time

sys.path.insert(0, 'hardware')
from controller import Controller

sys.path.insert(0, 'software')
import classiflier

LEFT = 0 # Counter Clockwise
RIGHT = 1 # Clockwise

def sensor_hit_object(controller):
	distance = abs(controller.get_distance())
	print(distance)
	return distance < 35

def get_distance(controller):
	return abs(controller.get_distance())

def main():
	c = Controller()

	while 1:
		# Camera to identify object direction (left/right) and object classification
		# Classifier API returns object type and object coordinates
		direction = LEFT

		# Sensor to identify distance to object by turning the rover towards left/right
		l = 13
		running_distances = []
		while 1: # can even use classifier here to check object coord
			distance = get_distance(c)
			print(distance)
			running_distances.append(distance)
			if len(running_distances) > l:
				running_distances.pop(0)
			if len(running_distances) == l and sum(running_distances) / l < 35:
				break

			c.turn(direction = direction)
			time.sleep(0.01)
			c.stop()

		# Classifier to see whether object is in center of image

		# Go straight because object in front of rover
		c.move(direction = 0);
		time.sleep(0.5)
		c.stop()
		return

main()