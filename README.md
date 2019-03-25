# Capstone-GC
## Description
4OI6 Capstone project. A garbage collecting rover.
## Installation
### Getting GPU Tensorflow on Server system
```
conda install tensorflow-gpu
```
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
## Usage
### Server
To run the ML model on a CUDA capable machine, navitage to software/ folder and run
```
python server.py
```
### Pi
To start the project, SSH/Putty into the Raspberry Pi and run
```
python main.py
```
## Documentation
See API within subfolders (hardware)
