import sys, time
from PIL import Image

sys.path.insert(0, 'hardware')
from controller import Controller
import camera_config

sys.path.insert(0, 'software')
from client import Client

LEFT = 0 # Counter Clockwise
RIGHT = 1 # Clockwise
FORWARD = 2

STATE_SEARCH = 0
STATE_DITCH = 1

OBJECT_NONE = -1
OBJECT_CANS = 0
OBJECT_PAPER = 2
OBJECT_DITCH = 1

## cam config
FOCAL_LENGTH = 3.6 #mm
CAN_HEIGHT = 121 #mm
CAN_WIDTH = 63 #mm
DITCH_HEIGHT = 210
DITCH_WIDTH = 190
SENSOR_HEIGHT = 2.74
SENSOR_WIDTH = 3.76

OBJ_DIM = {OBJECT_CANS:(CAN_HEIGHT, CAN_WIDTH), OBJECT_DITCH:(DITCH_HEIGHT, DITCH_WIDTH)}

DELAY_CAM_SHAKE = 0.3
REACHED_DISTANCE = 5 #

INF = 100000

class MainLogic():
    def __init__(self):
        self.controller = Controller()
        self.client = Client()
        self.state = STATE_SEARCH
        self.aura = 35 # objects within 35 units will be approached by rover
        self.resolution_width = camera_config.resolution_width
        self.resolution_height = camera_config.resolution_height

    def get_distance(self):
        # use sensor to detect dist to cans
        # camera to detect dist to ditch
        if self.cur_obj_type == OBJECT_CANS:
            sum = 0
            NUM_AVG = 5
            for i in range(NUM_AVG):
                sum = sum + abs(self.controller.get_distance())
            return sum/NUM_AVG
        elif self.cur_obj_type == OBJECT_DITCH:
            time.sleep(DELAY_CAM_SHAKE)
            objs = self.capture_and_process()
            return self.dist_from_img(objs)

    def capture_and_process(self):
        imgname = "image.jpg"
        self.controller.capture(imgname)
        img = Image.open(imgname)
        img = img.rotate(180)
        self.client.send_PIL(img)
        return self.client.connection_receive()

    # ************ loop methods ************
    def loop(self):
        if self.state == STATE_SEARCH:
            self.search_object()
        elif self.state == STATE_DITCH:
            self.search_ditch()
            
    def object_direction(self, objects):
        min = INF
        direction = INF
        self.coarse_threshold = 30#2000/self.get_distance() ## threshold to center is relativce to the distance
        self.fine_threshold = 10#200/self.get_distance()
        self.curobj = None
        for obj in objects:
            print("detected object type : ",obj.object_type)
            if obj.object_type == self.cur_obj_type:
                print(obj.x, abs(obj.x - self.resolution_width / 2), min)
                if abs(obj.x - self.resolution_width / 2) < min: # obj closest to center
                    min = abs(obj.x - self.resolution_width / 2)
                    if obj.x  < self.resolution_width / 2 - self.fine_threshold :
                        direction = LEFT
                    elif obj.x  > self.resolution_width / 2 + self.fine_threshold:
                        direction = RIGHT
                    else:
                        direction = FORWARD
                    self.curobj = obj
                    self.object_type = obj.object_type
        print("object is on {}".format(direction))
        if (direction == INF):
            print("# obj{} no target found".format(len(objects)))
        else:
            print("cur_obj x1{} x2{} y1{} y2{} x{} y{}".format(obj.x1, obj.x2, obj.y1, obj.y2, obj.x, obj.y))
        return (direction, min)
        
    def dist_from_img(self, objs): ## for center obj only
        # For ditch only
        obj_pixel_height = INF
        obj_pixel_width = INF
        min = INF
        distance = INF
        for obj in objs:
            if obj.object_type == self.cur_obj_type:
                if abs(obj.x - self.resolution_width / 2) < min: # obj closest to center
                    min = abs(obj.x - self.resolution_width / 2)
                    obj_pixel_height = obj.y2-obj.y1
                    obj_pixel_width = obj.x2-obj.x1
        Dist_from_h = FOCAL_LENGTH * OBJ_DIM[self.cur_obj_type][0] * self.resolution_height /(obj_pixel_height * SENSOR_HEIGHT)
        Dist_from_w = FOCAL_LENGTH * OBJ_DIM[self.cur_obj_type][1] * self.resolution_width /(obj_pixel_width * SENSOR_WIDTH)
        if (obj_pixel_height > 0.9 * self.resolution_height):## too close use width instead
            print("###use width###")
            distance = Dist_from_w
        else:
            distance = (Dist_from_h + Dist_from_w)/2
        print("using average : ", distance)
        #print("Using height : ", Dist_from_h)
        #print("Using width : ", Dist_from_w)
        return distance
                    
    def search_object(self):
        state = 1
        self.coarse_threshold = INF
        self.fine_threshold = INF
        self.direction = INF
        self.distance = INF
        self.object_type = OBJECT_NONE
        self.cur_obj_type = OBJECT_CANS # start with cans
        END_State = 5
        
        while state != END_State:
            # Step 0: Sweep with camera to find objects
            if state == 1:
                print("state {}".format(state))
                ratio = 0.01 # second per degree
                objs = []
                self.direction = INF
                while self.direction == INF:
                    print("capturing...")
                    objs = self.capture_and_process()
                    print(len(objs))
                    if len(objs) > 0:
                        self.direction, self.dist2cen = self.object_direction(objs)
                        if self.direction != INF: # if target objs found
                            print("read direction {}".format(self.direction))
                            if (self.direction == FORWARD):
                                self.distance = self.get_distance()
                                if self.distance < REACHED_DISTANCE:
                                    if self.cur_obj_type == OBJECT_CANS:
                                        state = 1
                                        self.cur_obj_type = OBJECT_DITCH
                                        print("reached cans")
                                    elif self.cur_obj_type == OBJECT_CANS:
                                        state = 5
                                        print("reached ditch")
                                else:
                                    state = 4 ## go move forward
                                    print("got to state {}".format(state))
                            else:
                                if abs(self.dist2cen) < self.coarse_threshold: # small turn
                                    state = 3 ## use dist2cen to do small turn
                                    print("got to state {}".format(state))
                                else:
                                    state = 2 ## big turn 
                                    print("got to state {}".format(state))
                        else:
                            self.turn(direction = LEFT, delay = ratio * 30)
                    else:
                        self.turn(direction = LEFT, delay = ratio * 30)

            # Step 2: Sweep with rover to identify objects (needs refinement)
            # Sensor to identify distance to object by turning the rover towards left/right
            if state == 2: # in camera but not center forward (coarse adjust
                time.sleep(DELAY_CAM_SHAKE)# avoid image blur
                self.turn(direction = self.direction, delay = self.dist2cen / 1000)
                # Use img info to identify turn params
                state = 1 # check with camera again
                
            # Step 3: verify if center fine adjust
            # 
            if state == 3:
                print("state {}".format(state))
                time.sleep(DELAY_CAM_SHAKE)# avoid image blur
                self.turn(direction = self.direction, delay = 0.02)
                
                state = 1
                
            # Step 4: Go straight because object in front of rover
            # Move forward at small intervals until object is within grasp of rover
            # if object type is can, use sensor
            # else use img to determine distance
            if state == 4:
                print("state {}".format(state))
                dist_log = []
                count = 0
                SENSOR_MISSED_TOLERANCE = 5
                
                self.distance = self.get_distance() ##****** for ditch need to seperate the img capture in this********
                if self.distance > REACHED_DISTANCE*2:
                    Max_movement = self.distance/2 ## move halfway then go state to verify if center
                else:
                    Max_movement = REACHED_DISTANCE ## should be good moving straight in close range
                while self.distance > Max_movement:
                    self.move(direction = 1, speed = self.get_speed_from_distance(self.distance), delay = 0.1)
                    self.distance = self.get_distance()
                    dist_log.append(self.distance)
                    print("get distance : ", self.distance)
                    ## for sensor only
                    if(self.distance > sum(dist_log)/len(dist_log)):
                        count += 1
                    if(count == SENSOR_MISSED_TOLERANCE):
                        print("object out of center")
                        break
                if self.distance <= REACHED_DISTANCE:
                    if self.cur_obj_type == OBJECT_CANS:
                        state = 1
                        self.cur_obj_type = OBJECT_DITCH
                        print("reached cans")
                    else: 
                        state = 5
                        print("reached ditch")
                else:
                    print("Moved straight, now adjust angle")
                    state = 1

    def search_ditch(self):
        state = 0
        objs = []

        while True:
            if state == 0:
                objs = self.capture_and_process()

            if state == 1:
                print(self.dist_from_img(objs))

            if state == 10:
                self.state = STATE_SEARCH


    # ************ supporting methods ************
    def turn(self, direction = 0, speed = 255, delay = 0.1):
        print("Turning in dir {}".format(direction))
        self.controller.turn(direction = direction, speed = speed)
        time.sleep(delay)
        self.controller.stop()

    def move(self, direction = 0, speed = 255, delay = 0.1):
        self.controller.move(direction = direction, speed = speed)
        time.sleep(delay)
        self.controller.stop()

    def object_ahead(self, running_distances):
        # Use Classifier to identify object coordinate, 
        # if object in center and sensor returns some resonable value then object is ahead
        return sum(running_distances) / len(running_distances) < self.aura
    def get_speed_from_distance(self, distance):
        # Calculate rover moving speed based on distance from object
        sMax = 255
        sMin = 1
        factor = 2 # higher it is slower the movement
        speed = (sMax-sMin) * distance / (factor * self.aura)
        return speed if speed < sMax else sMax

def main():
    m = MainLogic()
    while 1:
        m.loop()        
        return

main()