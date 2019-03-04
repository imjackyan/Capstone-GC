import numpy as np
import os
import sys
import tensorflow as tf
import time
import glob

from PIL import Image
from objectdata import ObjectData

class Classifier():

	OBJECT_NONE = -1
	OBJECT_CANS = 0
	OBJECT_PAPER = 1

	# Path to frozen detection graph. This is the actual model that is used for the object detection.
	MODEL_NAME = 'output_inference_graph'
	PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
	PATH_TO_LABELS = 'annotations/label_map.pbtxt'

	# useless for pi
	PATH_TO_TEST_IMAGES_DIR = 'test_images'
	TEST_IMAGE_PATHS = glob.glob(os.path.join(PATH_TO_TEST_IMAGES_DIR, '*.jpg'))

	def __init__(self, minimum_confidence=0.9):
		self.minimum_confidence = minimum_confidence

		print('Initializing model...')
		self.detection_graph = tf.Graph()
		with self.detection_graph.as_default():
			od_graph_def = tf.GraphDef()
			with tf.gfile.GFile(Classifier.PATH_TO_CKPT, 'rb') as fid:
				serialized_graph = fid.read()
				od_graph_def.ParseFromString(serialized_graph)
				tf.import_graph_def(od_graph_def, name='')

			self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
			self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
			self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
			self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
			self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

			print('Getting detection tensors...')
			with tf.Session(graph=self.detection_graph) as sess:
				self.sess = sess

		print('Done initialization.')

	def process(self, img):
		# We can currently call detect_objects() directly without invoking this function.
		# However, leave it here if processing adds more steps in future.

		# takes in image in certain format (please advise)
		# return a list of coordinates of objects. (-1,-1) if no object found
		# also returns classification of the objects

		start_time = time.time()
		boxes_list = self.detect_objects(img)
		boxObj_list = []
		for box in boxes_list:
			o = ObjectData()
			o.x1 = box[0]
			o.y1 = box[1]
			o.x2 = box[2]
			o.y2 = box[3]
			o.width = abs(o.x2 - o.x1)
			o.height = abs(o.y2 - o.y1)

			boxObj_list.append(o)
		elapsed_time = time.time() - start_time
		print('Elapsed time (s):', elapsed_time)
		
		return boxObj_list

	def process_ditch(self, img):
		# takes in image of certain format
		# returns the type of ditch that is perpendicular to rover
		# return OBJECT_NONE if no ditch is perpendicular

		return Classifier.OBJECT_NONE

	def load_image_into_numpy_array(self, image):
		(im_width, im_height) = image.size
		try:
			return np.array(image.getdata()).reshape(
			(im_height, im_width, 3)).astype(np.uint8)
		except ValueError:
			grayimage = np.array(image.getdata()).reshape(
			(im_height, im_width)).astype(np.uint8)
			return np.dstack((grayimage, grayimage, grayimage))

	def detect_objects(self, image, image_path=None):
		if image is None:
			image = Image.open(image_path)
		
		image_np = self.load_image_into_numpy_array(image)
		image_np_expanded = np.expand_dims(image_np, axis=0)

		(boxes, scores, classes, num) = \
			self.sess.run([self.detection_boxes, self.detection_scores, 
				      	   self.detection_classes, self.num_detections], 
					  	   feed_dict={self.image_tensor: image_np_expanded})
		
		# print('Boxes:', boxes)
		# print('Scores:', scores)
		# print('Classes:', classes)
		# print('Num:', num)
		# print()
		np_scores = np.squeeze(scores)
		np_boxes = np.squeeze(boxes)
		print('Number of boxes:', np_boxes.shape[0])
		width, height = image.size

		boxes_list = []

		for i in range(np_boxes.shape[0]):
			if np_scores is None or np_scores[i] > self.minimum_confidence:
				box = list(np_boxes[i].tolist())
				box[0] = int(box[0] * width)
				box[2] = int(box[2] * width)
				box[1] = int(box[1] * height)
				box[3] = int(box[3] * height)
				print('Box i', i, box)
				boxes_list.append(box)

		return boxes_list

if __name__ == '__main__':
	clf = Classifier()

	for image_path in Classifier.TEST_IMAGE_PATHS:
		print('Detecing for image:', image_path)
		start_time = time.time()
		# If using from pi, call clf.process(image) with image instead of filepath
		boxes_list = clf.detect_objects(None, image_path=image_path)
		elapsed_time = time.time() - start_time
		print('elapsed time:', elapsed_time)

		# print('Boxes:')
		# for box in boxes_list:
		# 	print(box)