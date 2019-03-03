from importing import *
from PIL import Image
import sys, time

sys.path.insert(0, '/home/pi/Capstone-GC/software/')
import from_project_dir_object_detection_runner_simple
print("Classifier initialized.")

controller.capture("image.jpg")
img = Image.open("image.jpg")
img = img.rotate(180)
print("PIL image taken.")

start = time.time()
print("Analysis result:\n" + ("*"*10))
print(from_project_dir_object_detection_runner_simple.process(img))
print(("*"*10) + "\nRun time: {}".format(time.time() - start))