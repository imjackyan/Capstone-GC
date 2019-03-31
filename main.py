import sys, time
from PIL import Image
from datetime import datetime

sys.path.insert(0, 'hardware')
from controller import Controller
import camera_config

sys.path.insert(0, 'software')
from client import Client
import math

LEFT = 0 # Counter Clockwise
RIGHT = 1 # Clockwise
FORWARD = 2

STATE_NONE = 0
STATE_LOST_OBJECT = 1
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
DITCH_HEIGHT = 190
DITCH_WIDTH = 190
SENSOR_HEIGHT = 2.74
SENSOR_WIDTH = 3.76

OBJ_DIM = {OBJECT_CANS:(CAN_HEIGHT, CAN_WIDTH), OBJECT_DITCH:(DITCH_HEIGHT, DITCH_WIDTH)}

DELAY_CAM_SHAKE = 0.3
REACHED_DISTANCE = 5 #
REACHED_DISTANCE_DITCH = 35 ## experimental for ditch
OBJ_LOST_THR = 15

INF = 100000

class MainLogic():
    def __init__(self):
        printf("\n____________________________________________\n");
        self.controller = Controller()
        self.client = Client()
        self.aura = 35 # objects within 35 units will be approached by rover
        self.resolution_width = camera_config.resolution_width
        self.resolution_height = camera_config.resolution_height
        self.motion_log_en = 0
        self.log = []
        self.amt_turned = 0
        self.amt_moved = 0

    def get_distance(self, objs = None, force_type = None, num_avg = 5):
        # use sensor to detect dist to cans
        # camera to detect dist to ditch
        if self.cur_obj_type == OBJECT_CANS or force_type == OBJECT_CANS:
            _sum = 0
            for i in range(num_avg):
                _sum = _sum + abs(self.controller.get_distance())
            return _sum/num_avg
        elif self.cur_obj_type == OBJECT_DITCH or force_type == OBJECT_DITCH:
            if objs == None:
                time.sleep(DELAY_CAM_SHAKE)
                objs = self.capture_and_process()
            return self.dist_from_img(objs = objs, obj_type = OBJECT_DITCH)

    def capture_and_process(self):
        printf("Capturing and processing ...")
        imgname = "image.jpg"
        self.controller.capture(imgname)
        img = Image.open(imgname)
        img = img.rotate(180)
        self.client.send_PIL(img)
        return self.client.connection_receive()

    # ************ loop methods ************
    def loop(self):
        self.search_object()
            
    def object_direction(self, objects):
        min = INF
        direction = INF
        self.coarse_threshold = 30 #2000/self.get_distance() ## threshold to center is relativce to the distance
        self.fine_threshold = 10 #200/self.get_distance()
        self.curobj = None
        for obj in objects:
            printf("Detected object type : ", obj_to_str(obj.object_type))
            if obj.object_type == self.cur_obj_type:
                printf(obj.x, abs(obj.x - self.resolution_width / 2), min)
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

            if obj.object_type == OBJECT_DITCH:
                #d = dist_from_img(objs = objs, obj_type = OBJECT_DITCH)
                self.motion_log_en = 1
                self.log = []
                self.amt_turned = 0
                self.amt_moved = 0

        printf("Target object is on {}".format(direction))
        if (direction == INF):
            printf("# obj{} no target found".format(len(objects)))
        else:
            printf("cur_obj x1{} x2{} y1{} y2{} x{} y{}".format(obj.x1, obj.x2, obj.y1, obj.y2, obj.x, obj.y))
        return (direction, min)

        
    def dist_from_img(self, objs, obj_type):
        # For ditch only
        obj_pixel_height = INF
        obj_pixel_width = INF
        offset2center = INF
        min = INF
        distance = INF
        for obj in objs:
            if obj.object_type == obj_type:
                if abs(obj.x - self.resolution_width / 2) < min: # obj closest to center
                    min = abs(obj.x - self.resolution_width / 2)
                    obj_pixel_height = obj.y2-obj.y1
                    obj_pixel_width = obj.x2-obj.x1
                    offset2center = abs(obj.x - self.resolution_width / 2) - obj_pixel_width/2 #(pixel)
        offset2center = offset2center * SENSOR_WIDTH/self.resolution_width #
        Dist_from_h = FOCAL_LENGTH * OBJ_DIM[obj_type][0] * self.resolution_height /(obj_pixel_height * SENSOR_HEIGHT)
        Dist_from_w = FOCAL_LENGTH * OBJ_DIM[obj_type][1] * self.resolution_width /(obj_pixel_width * SENSOR_WIDTH)
        
        dist_h_v2 = math.sqrt(Dist_from_h * Dist_from_h + (offset2center*Dist_from_h/FOCAL_LENGTH+OBJ_DIM[obj_type][0])*(offset2center*Dist_from_h/FOCAL_LENGTH+OBJ_DIM[obj_type][0]))
        dist_w_v2 = math.sqrt(Dist_from_w * Dist_from_w + (offset2center*Dist_from_w/FOCAL_LENGTH+OBJ_DIM[obj_type][1])*(offset2center*Dist_from_w/FOCAL_LENGTH+OBJ_DIM[obj_type][1]))
        
        #print("In testing h:{} w:{} v2:h:{} w:{}".format(Dist_from_h, Dist_from_w, dist_h_v2, dist_w_v2))
        if (obj_pixel_height > 0.9 * self.resolution_height):## too close use width instead
            printf("###use width###")
            distance = dist_w_v2 
        else:
            distance = dist_h_v2
        printf("Dist from image : ", distance)
        return distance/10 # tocm    
    def is_object_lost(self, objs):
        self.obj_distance = self.get_distance(force_type = OBJECT_CANS)
        if self.obj_distance > OBJ_LOST_THR:
            print("sensor read {}".format(self.obj_distance))
            printf("Object sensor distance is greater than {}".format(OBJ_LOST_THR))

            for o in objs:
                if o.object_type != OBJECT_DITCH:
                    p = self.resolution_width * 0.13
                    if o.y2 > (self.resolution_height * 0.95) and\
                    o.x1 > p and o.x2 < self.resolution_width - p:
                        return False

            return True
        return False

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
                printf("[STATE] {} | Searching for {}".format(state_to_str(state), obj_to_str(self.cur_obj_type)))
                ratio = 0.01 # second per degree
                objs = []
                self.direction = INF
                if True:
                    time.sleep(DELAY_CAM_SHAKE)# avoid image blur
                    objs = self.capture_and_process()
                    if self.cur_obj_type == OBJECT_DITCH: ## for now
                        print("sel amt turned {}".format(self.amt_turned))
                        if self.is_object_lost(objs):
                            state = STATE_LOST_OBJECT

                    if len(objs) > 0 and state != STATE_LOST_OBJECT:
                        self.direction, self.dist2cen = self.object_direction(objs)
                        if self.direction != INF: # if target objs found
                            printf("Read direction {}".format(self.direction))
                            if (self.direction == FORWARD):
                                self.distance = self.get_distance(objs = objs)
                                if self.distance < REACHED_DISTANCE:
                                    if self.cur_obj_type == OBJECT_CANS:
                                        state = STATE_MAIN
                                        self.cur_obj_type = OBJECT_DITCH
                                        printf("Reached cans")
                                else:
                                    state = STATE_STRAIGHT ## go move forward
                            else:
                                if abs(self.dist2cen) < self.coarse_threshold: # small turn
                                    state = STATE_TURN_ADJUST ## use dist2cen to do small turn
                                else:
                                    # Object is far from center, turn larger
                                    state = STATE_TURN_ATTEMPT
                        else:
                            state = STATE_SWEEP
                    elif state != STATE_LOST_OBJECT:
                        state = STATE_SWEEP

            # Step 0.1: Object is lost while trying to find ditch
            # Attempt to relocate object by moving back 
            if state == STATE_LOST_OBJECT:
                printf("[STATE] {}".format(state_to_str(state)))
                if self.obj_distance > OBJ_LOST_THR + 5:
                    self.cur_obj_type = OBJECT_CANS
                    printf(" LOST TRACK OF OBJECT")
                    self.move(direction = 0, delay = 0.08)
                else:
                    self.move(direction = 1, delay = 0.03)
                state = STATE_MAIN

            # Step 2: Sweep with rover to identify objects (needs refinement)
            if state == STATE_SWEEP:
                printf("[STATE] {}".format(state_to_str(state)))
                if self.cur_obj_type == OBJECT_DITCH:
                    print("turn 45 -> {}".format(self.amt_turned))
                    direc = LEFT
                    if self.amt_turned is not 0:
                        if self.amt_turned < 0:
                            direc = RIGHT
                        else:
                            direc = LEFT
                    self.turn(direction = direc, delay = ratio * 30, speed = 160)
                    self.move(direction = 1, delay = 0.06, speed = 180)
                else:
                    # self.turn(direction = LEFT, delay = ratio * 30)
                    start = time.time()
                    self.turn(direction = LEFT, speed = 140, delay = 0)
                    slope_buffer = []
                    l = 0
                    last_dis = 0
                    while 1:
                        cur_dis = self.get_distance(num_avg = 2)
                        slope = cur_dis - last_dis
                        last_dis = cur_dis
                        if (slope < -10 or slope > 10 or l > 50) and l > 8:
                            break
                        l += 1
                    end = time.time()
                    self.stop(motion_type = 1, direction = LEFT, speed = 165, duration = end-start)

                state = STATE_MAIN # check with camera again
                
            # Step 3.1: Use big turn to attemp to center object faster
            if state == STATE_TURN_ATTEMPT:
                printf("[STATE] {}".format(state_to_str(state)))
                l1 = self.dist2cen
                last_dir = self.direction
                t1 = 10 * ratio
                speed = 150
                self.turn(direction = self.direction, speed = speed, delay = t1)

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
                printf("[STATE] {}".format(state_to_str(state)))
                self.turn(direction = self.direction, delay = 0.02)
                
                state = STATE_MAIN
                
            # Step 4: Go straight because object in front of rover
            # Move forward at small intervals until object is within grasp of rover
            # if object type is can, use sensor
            # else use img to determine distance
            if state == STATE_STRAIGHT:
                printf("[STATE] {}".format(state_to_str(state)))
                dist_log = []
                count = 0
                hit_count = 0 ## to stop the car from hitting obs
                SENSOR_MISSED_TOLERANCE = 3
                
                self.distance = self.get_distance(objs = objs) ##****** for ditch need to seperate the img capture in this********
                
                if self.cur_obj_type == OBJECT_CANS:
                    REACHED = REACHED_DISTANCE
                    if self.distance > REACHED * 4:
                        Max_movement = self.distance/2 ## move halfway then go state to verify if center
                    else:
                        Max_movement = REACHED ## should be good moving straight in close range
                    self.motion_log_en = 0
                    self.amt_moved = self.distance## relative ang, dist to ditch stored
                else:
                    REACHED = REACHED_DISTANCE_DITCH
                    if self.distance > REACHED*2:
                        Max_movement = self.distance*3/4 ## move halfway then go state to verify if center
                    else:
                        Max_movement = REACHED ## should be good moving straight in close range
                
                # With set_speed method, we can change speed as the rover moves
                # Instead of stopping it per interval, this way it seems more natural
                printf("Moving towards {}".format(obj_to_str(self.cur_obj_type)))  
                start = time.time()
                while self.distance > Max_movement:        
                    self.move(direction = 1, speed = self.get_speed_from_distance(self.distance), delay = 0)
                    if self.cur_obj_type == OBJECT_DITCH:
                        sleep_duration = 0.008*self.distance
                        if sleep_duration < 0.1:
                            sleep_duration = 0.1
                        printf("sleep duration is "+str(sleep_duration))
                        time.sleep(sleep_duration)
                        end = time.time()     
                        self.stop(motion_type = 0, direction = 1, speed = self.get_speed_from_distance(self.distance), duration = end-start)   
                        start = time.time()
                        
                    self.distance = self.get_distance()
                    end = time.time()
                    self.set_speed(motion_type = 0, direction = 1, speed = self.get_speed_from_distance(self.distance), duration = end-start)  
                    if self.cur_obj_type == OBJECT_CANS:
                        if self.distance < 30:
                            self.set_speed(motion_type = 0, direction = 1, speed = 80, duration = end-start) 
                            
                    start = time.time()
                    
                    dist_log.append(self.distance)
                    printf("get distance : ", self.distance)
                    
                    ## for sensor only
                    if(self.distance > sum(dist_log)/len(dist_log)):
                        count += 1
                    else:
                        count = 0
                    if abs(self.distance - sum(dist_log)/len(dist_log)) < 1:
                        hit_count+=1
                    else:
                        hit_count = 0
                    
                    if(hit_count == SENSOR_MISSED_TOLERANCE):
                        printf("Cant go forward")
                        break
                        
                    if(count == SENSOR_MISSED_TOLERANCE):
                        printf("object out of center")
                        break
                end = time.time()
                self.stop(motion_type = 0, direction = 1, speed = self.get_speed_from_distance(self.distance), duration = end-start)

                """
                while self.distance > Max_movement:
                    self.move(direction = 1, speed = self.get_speed_from_distance(self.distance), delay = 0.1)
                    self.distance = self.get_distance()
                    dist_log.append(self.distance)
                    printf("get distance : ", self.distance)
                    ## for sensor only
                    if(self.distance > sum(dist_log)/len(dist_log)):
                        count += 1
                    if(count == SENSOR_MISSED_TOLERANCE):
                        printf("object out of center")
                        break
                """
                if self.distance <= REACHED:
                    if self.cur_obj_type == OBJECT_CANS:
                        state = STATE_MAIN
                        self.cur_obj_type = OBJECT_DITCH
                        printf("Reached cans")
                        # self.controller.speed_factor = 0.4
                    else:
                        state = STATE_DUMMY
                        printf("Reached ditch")
                        self.cur_obj_type = OBJECT_CANS
                        self.move(direction = 1, delay = 0.6) ## push through ditch
                        time.sleep(0.07)
                        self.move(direction = 0, delay = 1) ## backoff to center
                        # self.controller.speed_factor = 0.5
                        printf("Scanning for new cans")
                        state = STATE_MAIN
                else:
                    printf("Moved straight, now adjusting angle")
                    state = STATE_MAIN


    # ************ supporting methods ************
    def turn(self, direction = 0, speed = 255, delay = 0.1):
        printf("Turning in dir {}".format(direction))
        self.controller.turn(direction = direction, speed = speed)
        if delay > 0:
            time.sleep(delay)
            self.stop(1, direction, speed, delay)
    
    def move(self, direction = 0, speed = 255, delay = 0.1):
        self.controller.move(direction = direction, speed = speed)
        if delay > 0:
            time.sleep(delay)
            self.stop(0, direction, speed, delay)

    def stop(self, motion_type, direction, speed, duration):
        self.controller.stop()
        if self.motion_log_en == 1:
            self.motion_log(motion_type, direction, speed, duration)
            
    def set_speed(self, motion_type, direction, speed, duration):
        self.controller.set_speed(speed)
        if self.motion_log_en == 1:
            self.motion_log(motion_type, direction, speed, duration)
            
    def motion_log(self, motion_type, direction, speed, duration):
        self.log.append([motion_type, direction, speed, duration])
        if motion_type == 1:
            self.amt_turned = self.amt_turned + (direction-0.5)/0.5 * speed * duration

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

def state_to_str(s):
    if s == STATE_NONE:
        return "None"
    elif s == STATE_MAIN:
        return "Main"
    elif s == STATE_LOST_OBJECT:
        return "Lost Object"
    elif s == STATE_SWEEP:
        return "Sweep"
    elif s == STATE_TURN_ATTEMPT:
        return "Wide Turn"
    elif s == STATE_TURN_ADJUST:
        return "Small Turn"
    elif s == STATE_STRAIGHT:
        return "Straight"
    elif s == STATE_DUMMY:
        return "Dummy"
    return ""
def obj_to_str(o):
    if o == OBJECT_CANS:
        return "Cans"
    elif o == OBJECT_PAPER:
        return "Paper"
    elif o == OBJECT_DITCH:
        return "Ditch"
    return ""

def printf(*args):
    args = [str(i) for i in args]
    s = " ".join(args)
    print(s)
    with open("log.txt", "a") as f:
        f.write("[{}] {}\n".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S:%f"), s))

def main():
    m = MainLogic()
    while 1:
        m.loop()        
        return

if __name__ == '__main__':
    main()