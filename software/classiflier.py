import from_project_dir_object_detection_runner_simple
from objectdata import *

OBJECT_NONE = -1
OBJECT_CANS = 0
OBJECT_PAPER = 1

class Classifier():
	def __init__(self):
		self.dummy = 0

	def process(self, img):
		# takes in image in certain format (please advise)
		# return a list of coordinates of objects. (-1,-1) if no object found
		# also returns classification of the objects

		boxes_list = from_project_dir_object_detection_runner_simple.process(img)
		objs = []
		for box in boxes_list:
			o = ObjectData()
			o.x1 = box[0]
			o.y1 = box[1]
			o.x2 = box[2]
			o.y2 = box[3]
			o.width = abs(o.x2 - o.x1)
			o.height = abs(o.y2 - o.y1)

			objs.append(o)

		return objs

	def process_ditch(self, img):
		# takes in image of certain format
		# returns the type of ditch that is perpendicular to rover
		# return OBJECT_NONE if no ditch is perpendicular

		return OBJECT_NONE