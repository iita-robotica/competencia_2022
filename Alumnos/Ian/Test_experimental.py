from controller import Robot
from controller import Motor
from controller import GPS
from controller import PositionSensor
from controller import DistanceSensor
import math
import pandas as pd


# Start robot & sensors

timeStep = 32

robot = Robot()
robot.step(timeStep)

gps = robot.getDevice("gps")
gps.enable(timeStep)

wheel_left = robot.getDevice("wheel_1 motor")
wheel_left.setPosition(float('inf'))
wheel_right = robot.getDevice("wheel_2 motor")
wheel_right.setPosition(float('inf'))

encoder_left = wheel_left.getPositionSensor()
encoder_left.enable(timeStep)
encoder_right = wheel_right.getPositionSensor()
encoder_right.enable(timeStep)

distance_right = robot.getDevice("distance_sensor_1")
distance_right.enable(timeStep)
distance_front = robot.getDevice("distance_sensor_2")
distance_front.enable(timeStep)
distance_left = robot.getDevice("distance_sensor_3")
distance_left.enable(timeStep)

color_sensor = robot.getDevice("colour_sensor")
color_sensor.enable(timeStep)


# State variables

condition_block = 0

tilesize = 0.06
tilesize_front = 0.05
tilesize_side = 0.07

x0 = 0
y0 = 0
xr = 0
yr = 0
x = 0
y = 0
x1 = 0
y1 = 0

row = 0
column = 0

cardinal = "north"

is_tilecenter = False
is_wall = False

error_margin = 0.01
encoder = 2.215
encoder_goal = encoder 

angle = 0
angle_permit = [0, 45, 90]
angle_prox = 0

start = (0,0)
original_tile = (0,0)
next_tile = (0,0)
trajectory = []

stage_state = "linear"
robot_state = "follow"
movement_state = "advance"
object_state = "tile"


# Define functions

def advance(vx, vy):
    wheel_left.setVelocity(vx)
    wheel_right.setVelocity(vy)

def turn(vel):
    wheel_left.setVelocity(-vel)
    wheel_right.setVelocity(vel)
    
def ang():
    global angle
    if x != x1 and y != y1:
        angle = math.atan2(abs(y-y1),abs(x-x1)) * 180/math.pi
        angle_norm = angle/90
        if angle_norm > 1:
            angle -= 90
    else:
        angle = 0
    return angle

def coord():
    global x1
    global y1
    if (x0 >= 2) or (x0 <= -2):
        x1 = 0
    elif (-2 <= x0 <= 0):
        x1 = -1
    elif (0 <= x0 <= 2):
        x1 = 1  
    if (y0 >= 2) or (y0 <= -2):
        y1 = 0
    elif (-2 <= y0 <= 0):
        y1 = -1
    elif (0 <= y0 <= 2):
        y1 = 1 

def position():
    global x1
    global y1
    global row
    global column
    global cardinal
    if abs(x - xr) > abs(y - yr):
        if x1 < x:
            cardinal = "east"
            if x - x1 >= 2:
                row += 1
                x1 = x
        elif x < x1:
            cardinal = "west"
            if x1 - x >= 2:
                row -= 1
                x1 = x
    elif abs(y - yr) > abs(x - xr):
        if y1 < y:
            cardinal = "south"
            if y - y1 >= 2:
                column -= 1
                y1 = y
        elif y < y1:
            cardinal = "north"
            if y1 - y >= 2:
                column += 1
                y1 = y

def tilecenter():
    global is_tilecenter
    if cardinal == "north" or cardinal == "south":
        if (y%1 == 0) and (y1 == y):
            is_tilecenter = True
        else:
            is_tilecenter = False
    elif cardinal == "west" or cardinal == "east":
        if (x%1 == 0) and (x1 == x):
            is_tilecenter = True
        else:
            is_tilecenter = False

def wall():
    global is_wall
    if (dis_front < tilesize_front):
        is_wall = True
    else:
        is_wall = False

def object(image):
    global object_state
    r = color_sensor.imageGetRed(image, 1, 0, 0)
    g = color_sensor.imageGetGreen(image, 1, 0, 0)
    b = color_sensor.imageGetBlue(image, 1, 0, 0)
    if (210 <= r <= 220) and (210 <= g <= 220) and (210 <= b <= 220):
        object_state = "tile"
    elif (185 <= r <= 195) and (155 <= g <= 165) and (85 <= b <= 95):
        object_state = "swamp"
    elif (40 <= r <= 80) and (40 <= g <= 85) and (50 <= b <= 100):
        object_state = "checkpoint"
    elif (r <= 40) and (g <= 40) and (b <= 40):
        object_state = "hole"
    

# Start cicle

while robot.step(timeStep) != -1:

    dis_right = distance_right.getValue()
    dis_front = distance_front.getValue()
    dis_left = distance_left.getValue()

    image = color_sensor.getImage()
    
    x = round(gps.getValues()[0]/tilesize, 1)
    y = round(gps.getValues()[2]/tilesize, 1)
    
    encoder_new = encoder_right.getValue()
    
    if condition_block == 0:
        x0 = round(gps.getValues()[0]/tilesize, 1)
        y0 = round(gps.getValues()[2]/tilesize, 1)
        xr = x0
        yr = y0
        coord()
        condition_block += 1     
    position()
    tilecenter()
    wall()
    ang()
    object(image)   
    
    if 0 <= angle < 30:
        angle_prox = 0
    elif 30 <= angle <= 60:
        angle_prox = 45
    elif 60 < angle <= 90:
        angle_prox = 90
    
    
    if stage_state == "linear":
        
        
        if robot_state == "follow":
        
            if movement_state == "advance":
                
                #if angle not in angle_permit:
                    #if ((angle_prox + 10) < angle) or (angle < (angle_prox - 10)):
                        #advance(1,0.97)
                    #movement_state = "advance_fix"
                #else:
                advance(1,1)
                
                if (dis_front < tilesize_front) or (object_state == "hole"):        
                    xr = x
                    yr = y 
                    if dis_right < tilesize_side:
                        encoder_goal = encoder_new - encoder
                        turn(-0.5)
                    else:
                        encoder_goal = encoder_new + encoder
                        turn(0.5)
                    movement_state = "turn"
            
            #elif movement_state == "advance_fix":
                #if ((angle_prox + 7) < angle) or (angle < (angle_prox - 7)):
                    #angle = 0
                    #movement_state = "advance"
            
            elif movement_state == "turn":
                if(abs(encoder_new - encoder_goal) < error_margin):
                    encoder_new = 45
                    angle = 0
                    movement_state = "advance"
                    
            if dis_right > tilesize_side: #cuidado:detecta el agujero como que no está siguiendo la pared
                robot_state = "miss"
        
           
        elif robot_state == "miss":
                
            if (object_state != "hole") and (is_tilecenter == True):        
                encoder_goal = encoder_actual + encoder
                turn(0.5)
                if(abs(encoder_actual - encoder_goal) < turn_range):
                    encoder_actual = 45
            
            if dis_right < tilesize_side:
                robot_state = "follow"
            
            
            
            
# if current_tile == start: 
#   stage_state = "floating"
               
# elif stage_state == "floating"