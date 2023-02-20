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

init = 0
timer = 0
block_condition = 0
block_cicle = 0
block_state = 0

tilesize = 0.06
tilesize_front = 0.05
tilesize_side = 0.07

x = 0
y = 0
x1 = 0
y1 = 0

x0 = 0
y0 = 0
xr = 0
yr = 0

xa = 0
ya = 0
xb = 0
yb = 0

row = 0
column = 0

cardinal = "north"

is_tilecenter = False
is_wall_front = False
is_wall_right = False

error_margin = 0.01
encoder = 2.215
encoder_goal = encoder 

angle = 0
angle_permit = [0, 45, 90]
angle_prox = 0

start = (0,0)
tile_current = (0,0)
tile_next = (0,0)
tile_right = (0,0)
trajectory = []
hole = []

stage_state = "linear"
movement_state = "advance"
object_state = "tile"


# Define functions

def advance(vx, vy):
    wheel_left.setVelocity(vx)
    wheel_right.setVelocity(vy)

def fix():
    #if angle not in angle_permit:
        #if ((angle_prox + 10) < angle) or (angle < (angle_prox - 10)):
            #advance(1,0.97)
    #else:
    advance(1,1)
        
def turn(vel):
    wheel_left.setVelocity(-vel)
    wheel_right.setVelocity(vel)
    
def encd(n):
    global encoder_new
    global movement_state
    if(abs(encoder_new - encoder_goal) < error_margin):
        encoder_new = n * 45
        movement_state = "advance"
        
def encd_right():
    global encoder_goal
    global movement_state
    encoder_goal = encoder_new + encoder
    turn(0.5)
    movement_state = "turn"
        
def encd_left():
    global encoder_goal
    global movement_state
    encoder_goal = encoder_new - encoder
    turn(-0.5)
    movement_state = "turn"

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
    
def off():
    global x1
    global y1
    if xa != 0:
        x1 += xa
    if ya != 0:
        y1 += ya

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

def tile():
    global tile_current
    global tile_next
    global tile_right
    tile_current = (row, column)
    if cardinal == "east":
        tile_next = (row+1, column)
        tile_right = (row, column-1)
    elif cardinal == "west":
        tile_next = (row-1, column)
        tile_right = (row, column+1)
    elif cardinal == "north":
        tile_next = (row, column+1)
        tile_right = (row+1, column)
    elif cardinal == "south":
        tile_next = (row, column-1)
        tile_right = (row-1, column)

def tilecenter():
    global is_tilecenter
    global xb
    global yb
    xb = 1 - (round(x, 1) % 1)
    yb = 1 - (round(y, 1) % 1)
    if cardinal == "north" or cardinal == "south":
        if yb == ya and y1 == y:
            is_tilecenter = True
        else:
            is_tilecenter = False
    elif cardinal == "west" or cardinal == "east":
        if xb == xa and x1 == x:
            is_tilecenter = True
        else:
            is_tilecenter = False
    #print(is_tilecenter)

def wall():
    global is_wall_front
    global is_wall_right
    if dis_front <= tilesize_front:
        is_wall_front = True
    elif dis_front > tilesize_front:
        is_wall_front = False
    if (dis_right <= tilesize_side) or (tile_right in hole):
        is_wall_right = True
    elif (dis_right > tilesize_side) and (tile_right not in hole):
        is_wall_right = False

def object(image):
    global object_state
    global hole
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
        hole.append(tile_next)
        hole = list(pd.unique(hole))

       
def start_basic():
    global dis_right
    global dis_front
    global dis_left
    global image
    global x
    global y
    global encoder_new
            
    dis_right = distance_right.getValue()
    dis_front = distance_front.getValue()
    dis_left = distance_left.getValue()
        
    image = color_sensor.getImage()
        
    x = round(gps.getValues()[0]/tilesize, 1)
    y = round(gps.getValues()[2]/tilesize, 1)
        
    encoder_new = encoder_right.getValue()

    
def start_advanced():
    global xr
    global yr
    global angle_prox
    global start
    global block_condition
    
    off()
    position()
    ang()
    tile()
    tilecenter()
    wall()
    object(image)
     
    if block_condition == 0:
        x0 = round(gps.getValues()[0]/tilesize, 1)
        y0 = round(gps.getValues()[2]/tilesize, 1)
        xr = x0
        yr = y0
        coord()
        start = tile_current
        block_condition += 1
                
    if 0 <= angle < 30:
        angle_prox = 0
    elif 30 <= angle <= 60:
        angle_prox = 45
    elif 60 < angle <= 90:
        angle_prox = 90
        

# Start cicles

while (robot.step(timeStep) != -1) and (init >= 0):
    
    start_basic()
    start_advanced()

    if movement_state == "advance":

        if (is_wall_front == False) and (object_state != "hole"):
            fix()
        
        else:
            encd_right()
            if tile_current != start:
                fix()
            else:
                init = -1
        
    elif movement_state == "turn":
        encd(2)

        

while (robot.step(timeStep) != -1) and (init == -1):
    
    start_basic()
    start_advanced()
        
    if stage_state == "linear":
        
        if movement_state == "advance":
            
            trajectory.append((tile_current))
            trajectory = list(pd.unique(trajectory))
                        
            if block_state == 0:
                if is_wall_right == True:
                    fix()       
                    if (is_wall_front == True) or (object_state == "hole"):        
                        xr = x
                        yr = y
                        encd_left()
                else:
                    block_state = 1        
                
            if block_state == 1:
                    if block_cicle == 0:
                        if is_tilecenter == True:
                            encd_right()
                            block_cicle = 1
                    elif block_cicle == 1:
                        if timer <= 165:
                            fix()
                            timer += 1
                        else:
                            block_cicle = 0
                            timer = 0
                            block_state = 0
                
        elif movement_state == "turn":
            encd(1)
            xa = 1 - (round(x, 1) % 1)
            ya = 1 - (round(y, 1) % 1)
        
            

# if current_tile == start: 
#   stage_state = "floating"
                
# elif stage_state == "floating"
