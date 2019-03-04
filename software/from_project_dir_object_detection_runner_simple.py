import numpy as np
import os
import sys
import tensorflow as tf
import time
import glob

from PIL import Image


MINIMUM_CONFIDENCE = 0.9

# Path to frozen detection graph. This is the actual model that is used for the object detection.
MODEL_NAME = 'output_inference_graph'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABELS = 'annotations/label_map.pbtxt'

# useless for pi
PATH_TO_TEST_IMAGES_DIR = 'test_images'
TEST_IMAGE_PATHS = glob.glob(os.path.join(PATH_TO_TEST_IMAGES_DIR, '*.jpg'))

def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    try:
        return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)
    except ValueError:
        temp = np.array(image.getdata()).reshape(
        (im_height, im_width)).astype(np.uint8)
        return np.dstack((temp, temp, temp))

def detect_objects(image, image_path=None, min_score_thresh=MINIMUM_CONFIDENCE):
    if image is None:
        image = Image.open(image_path)
    
    image_np = load_image_into_numpy_array(image)
    image_np_expanded = np.expand_dims(image_np, axis=0)

    (boxes, scores, classes, num) = sess.run([detection_boxes, detection_scores, detection_classes, num_detections], feed_dict={image_tensor: image_np_expanded})
    
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
        if np_scores is None or np_scores[i] > min_score_thresh:
            box = list(np_boxes[i].tolist())
            box[0] = int(box[0] * width)
            box[2] = int(box[2] * width)
            box[1] = int(box[1] * height)
            box[3] = int(box[3] * height)
            print('Box i', i, box)
            boxes_list.append(box)

    return boxes_list

def process(image):
    # Load model into memory (TODO: Try to avoid having to do this every time?)
    print('Loading model...')
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    print('detecting...')
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')
    
    # print('Detecing for image:', image_path)
    start_time = time.time()
    boxes = detect_objects(image)
    elapsed_time = time.time() - start_time
    print('elapsed time:', elapsed_time)

    return boxes

if __name__ == '__main__':

    # Load model into memory
    print('Loading model...')
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    print('detecting...')
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')

            for image_path in TEST_IMAGE_PATHS:
                print('Detecing for image:', image_path)
                start_time = time.time()
                detect_objects(None, image_path=image_path)
                elapsed_time = time.time() - start_time
                print('elapsed time:', elapsed_time)