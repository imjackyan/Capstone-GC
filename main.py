import sys, time

sys.path.insert(0, 'hardware')
from controller import Controller

sys.path.insert(0, 'software')
import classiflier

LEFT = 0 # Counter Clockwise
RIGHT = 1 # Clockwise

def sensor_hit_object(controller, i):
	distance = controller.get_distance()
	return i > 10

def main():
	c = Controller()

	while 1:
		# Camera to identify object direction (left/right)
		direction = LEFT

		# Sensor to identify distance to object by turning the rover towards left/right
		i = 0
		while not sensor_hit_object(c, i):
			c.turn(direction = direction, speed = 200)
			time.sleep(0.1)
			c.stop()
			i+=1

		# Go straight because object in front of rover
		c.move(direction = 1, speed = 200);
		time.sleep(2)
		c.stop()

main()