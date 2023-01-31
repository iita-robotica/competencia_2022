from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor
import math
import pandas as pd


# Start robot & sensors

robot = Robot()

timeStep = 32
robot.step(timeStep)

gps = robot.getDevice("gps")
gps.enable(timeStep)

ruedaIzquierda = robot.getDevice("wheel_1 motor")
ruedaIzquierda.setPosition(float('inf'))
ruedaDerecha = robot.getDevice("wheel_2 motor")
ruedaDerecha.setPosition(float('inf'))

encoderIzquierdo = ruedaIzquierda.getPositionSensor()
encoderIzquierdo.enable(timeStep)
encoderDerecho = ruedaDerecha.getPositionSensor()
encoderDerecho.enable(timeStep)

distance_right = robot.getDevice("distance_sensor_1")
distance_right.enable(timeStep)
distance_front = robot.getDevice("distance_sensor_2")
distance_front.enable(timeStep)
distance_left = robot.getDevice("distance_sensor_3")
distance_left.enable(timeStep)

colorSensor = robot.getDevice("colour_sensor")
colorSensor.enable(timeStep)

robot_state = "explore"
overlap_counter = 0


# Start movement variables

tilesize = 0.06
tilesize_front = 0.05
tilesize_side = 0.07

is_tile_center = False
wall = False

turn_range = 0.01
turn_counter = 0
turn_escape = 0

encoder = 2.215
encoder_goal = encoder 

x = 0
x1 = 0
y = 0
y1 = 0

angle = 0
angle_permit = [0, 45, 90]
angle_prox = 0

diff_max = 0
diff_min = 0

movement_state = "advance"

time_counter = 0


# Start mapping variables

column = 0
column_max = 0
column_min = 0
column_total = 0

row = 0
row_max = 0
row_min = 0
row_total = 0

Start = (row, column)
Swamp = []
Hole = []
Checkpoint = []

trajectory = []
duplicate = []

original_tile = ((0,0))
next_tile = ((0,0))

cardinal = "north"

Mapping = {
    "Comienzo": Start,
    "Pantano": Swamp,
    "Agujero": Hole,
    "Guardado": Checkpoint
}

object_state = "tile"


# Start movement functions

def advance(vx, vy):
    ruedaIzquierda.setVelocity(vx)
    ruedaDerecha.setVelocity(vy)

def turn(vel):
    ruedaIzquierda.setVelocity(-vel)
    ruedaDerecha.setVelocity(vel)
    
def get_angle():
    global angle
    if x != x1 and y != y1:
        angle = math.atan2(abs(y-y1),abs(x-x1)) * 180/math.pi
    else:
        angle = 0
    return angle

def angle_normalizer():
    global angle
    angle = angle % 90
    if angle < 0:
        angle += 90
    return angle

def wall_check():
    global wall
    update_position()
    #if cardinal == "north":
    if (dis_front < tilesize_front):
        wall = True
    else:
        wall = False

def tile_center():
    global is_tile_center
    update_position()
    if cardinal == "north" or cardinal == "south":
        if abs(y%1) == 0:
            is_tile_center = True
        else:
            is_tile_center = False
    elif cardinal == "west" or cardinal == "east":
        if abs(x%1) == 0:
            is_tile_center = True
        else:
            is_tile_center = False
    #print(is_tile_center)

def escape():
    update_position()
    wall_check()
    tile_center()
    save_object()
    global trajectory
    global duplicate
    global overlap_counter
    global turn_escape
    global robot_state
    if (movement_state == "advance") and (next_tile not in trajectory):
        trajectory.append((original_tile))
        trajectory = list(pd.unique(trajectory))
        #duplicate.clear()
    else:
        #print("?")
        if (movement_state == "advance") and (wall == False):
            duplicate.append((original_tile))
            duplicate = list(pd.unique(duplicate))
            overlap_counter = len(duplicate)
        if turn_escape == 5:
            duplicate.clear()
            turn_escape = 0
        if (overlap_counter >= 3):
            if is_tile_center == True:
                robot_state = "release"
                #print("done")
                #print(duplicate)
            else:
                robot_state = "explore"
    #print("t:", trajectory)
    #print(overlap_counter)
    print("d:", duplicate)
    #print(is_tile_center)


# Start mapping functions

def update_position():
    global x1
    global y1
    global cardinal
    global row
    global column
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
    #print("fila:", row, " columna:", column)

def check_object(image):
    global object_state
    r = colorSensor.imageGetRed(image, 1, 0, 0)
    g = colorSensor.imageGetGreen(image, 1, 0, 0)
    b = colorSensor.imageGetBlue(image, 1, 0, 0)
    if (210 <= r <= 220) and (210 <= g <= 220) and (210 <= b <= 220):
        object_state = "tile"
    elif (185 <= r <= 195) and (155 <= g <= 165) and (85 <= b <= 95):
        object_state = "swamp"
    elif (40 <= r <= 80) and (40 <= g <= 85) and (50 <= b <= 100):
        object_state = "checkpoint"
    elif (r <= 40) and (g <= 40) and (b <= 40):
        object_state = "hole"
    
def save_object():
    global row
    global column
    global original_tile
    global next_tile
    update_position()
    original_tile = ((row, column))
    if cardinal == "east":
        next_tile = ((row+1, column))
    elif cardinal == "west":
        next_tile = ((row-1, column))
    elif cardinal == "north":
        next_tile = ((row, column+1))
    elif cardinal == "south":
        next_tile = ((row, column-1))
    #print(next_tile)


while robot.step(timeStep) != -1:
    
    # Update robot & sensors

    dis_right = distance_right.getValue()
    dis_front = distance_front.getValue()
    dis_left = distance_left.getValue()

    image = colorSensor.getImage()

    time_counter += 1

    if time_counter % 90 == 0 :
        # valores dentro del contador no requieren actualización constante
        get_angle()
        angle_normalizer()
        save_object()
        escape()
        time_counter %= 5
    # valores fuera del contador requieren actualización constante
    update_position()
    tile_center()
    check_object(image)
    
    # Update movement variables
    
    x = round(gps.getValues()[0]/tilesize, 1)
    y = round(gps.getValues()[2]/tilesize, 1)

    encoder_actual = encoderDerecho.getValue()
    
    if 0 <= angle < 30:
        angle_prox = 0
    elif 30 <= angle <= 60:
        angle_prox = 45
    elif 60 < angle <= 90:
        angle_prox = 90
        
    diff_max = angle + 12
    diff_min = angle - 12
    
    
    # Update mapping variables
    
    if column_max < column:
        column_max = column
    elif column < column_min:
        column_min = column
    column_total = abs(column_min) + column_max
        
    if row_max < row:
        row_max = row
    elif row < row_min:
        row_min = row
    row_total = abs(row_min) + row_max
        
    
    # Initialize movement state machine
    
    if robot_state == "explore":
        #print("explore")
        if movement_state == "advance":
            #print("x:", x, " x1:", x1, " y:", y, " y1:", y1)
            #print("angulo:", angle)
            
            if angle not in angle_permit:
                movement_state = "advance_fix"
                if (diff_max <= angle_prox) or (angle_prox <= diff_min):
                    if turn_counter == 20:
                        turn_counter = 0
                        advance(1,0.97)
            else:
                advance(1,1)
            
            if (dis_front < tilesize_front) or (object_state == "hole"):        
                #x1 = x
                #y1 = y
                movement_state = "turn"
                turn_counter += 1
                turn_escape += 1
                if dis_right < tilesize_side:
                    encoder_goal = encoder_actual - encoder
                    turn(-0.5)
                else:
                    encoder_goal = encoder_actual + encoder
                    turn(0.5)
        
        elif movement_state == "advance_fix":
            if (angle_prox < diff_max) or (diff_min < angle_prox):
                movement_state = "advance"
                angle = 0
        
        elif movement_state == "turn":
            if(abs(encoder_actual - encoder_goal) < turn_range):
                movement_state = "advance"
                encoder_actual = 45
                angle = 0

  
    elif robot_state == "release":
        #print("release")
        if movement_state == "advance":
            advance(1,1)
            
            if object_state != "hole":        
                #x1 = x
                #y1 = y
                movement_state = "turn"
                #print(x, y)
                if dis_right > tilesize_side:
                    encoder_goal = encoder_actual + encoder
                    turn(0.5)
                    duplicate.clear()
                    #print("derecha")
                elif dis_left > tilesize_side:
                    encoder_goal = encoder_actual - encoder
                    turn(-0.5)
                    duplicate.clear()
                    #print("izquierda")
        
        elif movement_state == "turn":
            if(abs(encoder_actual - encoder_goal) < turn_range):
                movement_state = "advance"
                encoder_actual = 45
                angle = 0
            robot_state = "explore"
    

    # Initialize object state machine
        
    if object_state == "checkpoint":
        #print("checkpoint")
        if original_tile not in Checkpoint:
            Checkpoint.append(next_tile)
            Checkpoint = list(pd.unique(Checkpoint))
            #print(Checkpoint)

    elif object_state == "swamp":
        #print("swamp")
        if original_tile not in Swamp:  
            Swamp.append(next_tile)
            Swamp = list(pd.unique(Swamp))
            #print(Swamp)
        
    elif object_state == "hole":
        #print("hole")
        Hole.append(next_tile)
        Hole = list(pd.unique(Hole))
        #print(Hole)

