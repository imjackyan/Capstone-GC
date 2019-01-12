
# Hardware API
See **command_line.py** and **importing.py** in the examples folder for examples.

## Using the API as a module
Import the controller module and initialize a controller object, this will command the hardware aspects of the rover, ie snapping a picture with camera, moving forward with motors.
```python
from controller import Controller

con = Controller()
```
Snap a picture and save to location
```python
con.capture('/home/pi/Capstone-GC/image.jpg')
```
Snap a picture and return as an OpenCV image object
```python
image = con.capture_opencv()
```

## Command through server/client
With **manager.py** start the server with
```shell
python3 manager.py --start
```
Give it 2 seconds for the server and controller to initialize.


Command the controller with other arguments
```shell
python3 manager.py --capture image.jpg
```

When finished, close the server
```shell
python3 manager.py --close
```
