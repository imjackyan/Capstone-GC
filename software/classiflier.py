import numpy as np
import os
import sys
import tensorflow as tf
import time
import glob

from PIL import Image

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
		
		return [([-1,-1], OBJECT_NONE)]

	def process_ditch(self, img):
		# takes in image of certain format
		# returns the type of ditch that is perpendicular to rover
		# return OBJECT_NONE if no ditch is perpendicular

		return OBJECT_NONE