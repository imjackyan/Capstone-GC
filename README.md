# Capstone-GC
## Description
4OI6 Capstone project. A garbage collecting rover.
## Installation
### Getting OpenCV
```
pip3 install numpy
pip3 install opencv-contrib-python-headless
```
Now try importing cv2 in a Python console, you will likely get some import errors on missing dependencies. Follow [this link for solution](https://blog.piwheels.org/how-to-work-out-the-missing-dependencies-for-a-python-package/).

### Getting Nanpy
[Video tutorial](https://www.youtube.com/watch?v=QumIhvYtRKQ)
```
sudo apt-get install arduino -y

cd $workspace_directory

git clone https://github.com/nanpy/nanpy
git clone https://github.com/nanpy/nanpy-firmware
```
Under nanpy-firmware/Nanpy/, edit cfg.h to enable desired features. We will enable Ultrasonic by setting it to 1.
```
// GW Robotics Classes
#define USE_Ultrasonic                                          1
```
Then copy to Arduino sketchbook.
```
cp -avr nanpy-firmware/ ~/sketchbook/libraries

sudo python3 nanpy/setup.py install
```
Upload the firmware onto the Arduino

## Documentation
See API within subfolders (hardware)
