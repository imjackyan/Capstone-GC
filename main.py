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

STATE_NONE = 0
STATE_MAIN = 2
STATE_SWEEP = 3
STATE_TURN_ATTEMPT = 4
STATE_TURN_ADJUST = 5
STATE_STRAIGHT = 6
STATE_DUMMY = 7

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

DELAY_CAM_SHAKE = 0.5
REACHED_DISTANCE = 5 #
REACHED_DISTANCE_DITCH = 35 ## experimental for ditch
CAN_LOST_THR = 15

INF = 100000

class MainLogic():
    def __init__(self):
        self.controller = Controller()
        self.client = Client()
        self.state = STATE_SEARCH
        self.aura = 35 # objects within 35 units will be approached by rover
        self.resolution_width = camera_config.resolution_width
        self.resolution_height = camera_config.resolution_height

    def get_distance(self, objs = None):
        # use sensor to detect dist to cans
        # camera to detect dist to ditch
        if self.cur_obj_type == OBJECT_CANS:
            sum = 0
            NUM_AVG = 5
            for i in range(NUM_AVG):
                sum = sum + abs(self.controller.get_distance())
            return sum/NUM_AVG
        elif self.cur_obj_type == OBJECT_DITCH:
            if objs == None:
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
        self.coarse_threshold = 30 #2000/self.get_distance() ## threshold to center is relativce to the distance
        self.fine_threshold = 10 #200/self.get_distance()
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
        return distance/10 # tocm
                    
    def search_object(self):
        state = STATE_MAIN
        self.coarse_threshold = INF
        self.fine_threshold = INF
        self.direction = INF
        self.distance = INF
        self.object_type = OBJECT_NONE
        self.cur_obj_type = OBJECT_CANS # start with cans

        END_State = STATE_DUMMY
        
        while state != END_State:
            # Step 0: Sweep with camera to find objects
            if state == STATE_MAIN:
                print("> Current state: {}".format(state))
                ratio = 0.01 # second per degree
                objs = []
                self.direction = INF
                # while self.direction == INF:
                if True:
                    print("capturing...")
                    time.sleep(DELAY_CAM_SHAKE)# avoid image blur
                    objs = self.capture_and_process()
                    print(len(objs))
                    
                    if 1:
                        if self.cur_obj_type == OBJECT_DITCH: ## for now
                            self.cur_obj_type = OBJECT_CANS ##to use sensor
                            x = self.get_distance()
                            if x > CAN_LOST_THR:
                                if x > 20:
                                    self.cur_obj_type = OBJECT_CANS
                                    print("****** LOST TRACK OF CAN *****")
                                else:
                                    self.move(direction = 1, delay = 0.02)
                                    objs = self.capture_and_process()
                                    print("feedforward adjust")
                                    self.cur_obj_type = OBJECT_DITCH
                            else:
                                self.cur_obj_type = OBJECT_DITCH
                    if len(objs) > 0:
                        self.direction, self.dist2cen = self.object_direction(objs)
                        if self.direction != INF: # if target objs found
                            print("read direction {}".format(self.direction))
                            if (self.direction == FORWARD):
                                self.distance = self.get_distance(objs)
                                if self.distance < REACHED_DISTANCE:
                                    if self.cur_obj_type == OBJECT_CANS:
                                        state = STATE_MAIN
                                        self.cur_obj_type = OBJECT_DITCH
                                        print("reached cans")
                                    # elif self.cur_obj_type == OBJECT_DITCH:
                                    #     state = STATE_DUMMY
                                    #     print("reached ditch")
                                else:
                                    state = STATE_STRAIGHT ## go move forward
                                    print("got to state {}".format(state))
                            else:
                                if abs(self.dist2cen) < self.coarse_threshold: # small turn
                                    state = STATE_TURN_ADJUST ## use dist2cen to do small turn
                                    print("got to state {}".format(state))
                                else:
                                    # Object is far from center, turn larger
                                    # state = STATE_TURN_ADJUST
                                    state = STATE_TURN_ATTEMPT
                                    print("got to state {}".format(state))
                        else:
                            state = STATE_SWEEP
                    else:
                        state = STATE_SWEEP

            # Step 2: Sweep with rover to identify objects (needs refinement)
            if state == STATE_SWEEP:
                print("> Current state: {}".format(state))
                if self.cur_obj_type == OBJECT_DITCH:
                    # target_delay = ratio * 45
                    # current_delay = 0
                    # self.controller.turn(direction = LEFT, speed = 80)
                    # while current_delay < target_delay:
                    #     time.sleep(0.05)
                    #     current_delay += 0.05
                    #     self.controller.set_speed(int(80 + (current_delay * (120/target_delay))))
                    # self.controller.stop()
                    self.turn(direction = LEFT, delay = ratio * 30, speed = 180)

                else:
                    self.turn(direction = LEFT, delay = ratio * 30)

                state = STATE_MAIN # check with camera again
                
            # Step 3.1: Use big turn to attemp to center object faster
            if state == STATE_TURN_ATTEMPT:
                print("> Current state: {}".format(state))
                l1 = self.dist2cen
                last_dir = self.direction
                t1 = 10 * ratio
                self.turn(direction = self.direction, delay = t1)

                time.sleep(DELAY_CAM_SHAKE)
                objs = self.capture_and_process()
                self.direction, self.dist2cen = self.object_direction(objs)

                if self.direction == last_dir:
                    new_delay = self.dist2cen / l1 * t1
                else:
                    new_delay = self.dist2cen / (self.dist2cen + l1) * t1
                self.turn(direction = self.direction, delay = new_delay)

                state = STATE_MAIN

            # Step 3.2: verify if center fine adjust
            if state == STATE_TURN_ADJUST:
                print("> Current state: {}".format(state))
                self.turn(direction = self.direction, delay = 0.02)
                
                state = STATE_MAIN
                
            # Step 4: Go straight because object in front of rover
            # Move forward at small intervals until object is within grasp of rover
            # if object type is can, use sensor
            # else use img to determine distance
            if state == STATE_STRAIGHT:
                print("> Current state: {}".format(state))
                dist_log = []
                count = 0
                SENSOR_MISSED_TOLERANCE = 5
                
                self.distance = self.get_distance(objs) ##****** for ditch need to seperate the img capture in this********
                
                if self.cur_obj_type == OBJECT_CANS:
                    REACHED = REACHED_DISTANCE
                    Max_movement = REACHED
                else:
                    REACHED = REACHED_DISTANCE_DITCH
                    if self.distance > REACHED*2:
                        Max_movement = self.distance/2 ## move halfway then go state to verify if center
                    else:
                        Max_movement = REACHED ## should be good moving straight in close range
                
                # With set_speed method, we can change speed as the rover moves
                # Instead of stopping it per interval, this way it seems more natural
                while self.distance > Max_movement:          
                    self.controller.move(direction = 1, speed = self.get_speed_from_distance(self.distance))
                    if self.cur_obj_type == OBJECT_DITCH:
                        sleep_duration = 0.008*self.distance
                        if sleep_duration < 0.1:
                            sleep_duration = 0.1
                        print("sleep duration is "+str(sleep_duration))
                        time.sleep(sleep_duration)
                        self.controller.stop()
                    self.distance = self.get_distance()
                    self.controller.set_speed(self.get_speed_from_distance(self.distance))
                    dist_log.append(self.distance)
                    print("get distance : ", self.distance)
                    
                    ## for sensor only
                    if(self.distance > sum(dist_log)/len(dist_log)):
                        count += 1
                    if(count == SENSOR_MISSED_TOLERANCE):
                        print("object out of center")
                        break
                self.controller.stop()

                """
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
                """
                if self.distance <= REACHED:
                    if self.cur_obj_type == OBJECT_CANS:
                        state = STATE_MAIN
                        self.cur_obj_type = OBJECT_DITCH
                        print("reached cans")
                        # self.controller.speed_factor = 0.4
                    else:
                        state = STATE_DUMMY
                        print("reached ditch")
                        self.cur_obj_type = OBJECT_CANS
                        self.move(direction = 1, delay = 0.6) ## push through holes
                        time.sleep(0.07)
                        self.move(direction = 0, delay = 0.8) ## backoff to center
                        # self.controller.speed_factor = 0.5
                        print("scan new cans")
                        state = STATE_MAIN
                else:
                    print("Moved straight, now adjust angle")
                    state = STATE_MAIN

    def search_ditch(self):
        state = STATE_NONE
        objs = []

        while True:
            if state == STATE_NONE:
                objs = self.capture_and_process()

            if state == STATE_MAIN:
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