'''
Using command line
 - use this method if computer vision is not done with Python, else see importing.py
'''


import subprocess
from time import sleep

def run(cmd, async=0):
	print(cmd)
	if async == 1:
		p = subprocess.Popen(cmd.split(' '))
	else:
		subprocess.call(cmd.split(' '))
# starting the server
cmd = 'python3 ../manager.py --start'
run(cmd, 1)

sleep(2)

# capture images and store into images folder
for i in range(5):
	cmd = 'python3 ../manager.py --capture image.jpg' + str(i+1)
	run(cmd)

# close the server
cmd = 'python3 ../manager.py --close'
run(cmd)