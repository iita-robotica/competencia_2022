from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor
import math


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

distancia_frontal = robot.getDevice("distance_sensor_2")
distancia_frontal.enable(timeStep)
distancia_lateral = robot.getDevice("distance_sensor_1")
distancia_lateral.enable(timeStep)

colorSensor = robot.getDevice("colour_sensor")
colorSensor.enable(timeStep)


# Start movement variables

tiles = 0
tilesize = 0.06
tilesize_detection = tilesize/2

turn_range = 0.01
turn_counter = 0

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

state = "advance"

counter = 0


# Start mapping variables

column = 0
column_max = 0
column_min = 0
column_total = 0

row = 0
row_max = 0
row_min = 0
row_total = 0
rows = []

Start = (row, column)
Swamp = []
Hole = []
Checkpoint = []
value = (0,0)

cardinal = "north"

Mapping = {
    "Comienzo": Start,
    "Pantano": Swamp,
    "Agujero": Hole,
    "Guardado": Checkpoint
}

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

def angle_normalizer(ang):
    ang = ang % 90
    if ang < 0:
        ang += 90
    return ang

# Start mapping functions

def check_object(image):
    '''Return the zone where is the robot'''
    r = colorSensor.imageGetRed(image, 1, 0, 0)
    g = colorSensor.imageGetGreen(image, 1, 0, 0)
    b = colorSensor.imageGetBlue(image, 1, 0, 0)
    if (210 <= r <= 240) and (180 <= g <= 210) and (100 <= b <= 130):
        return ("swamp")
    elif (r <= 47) and (g <= 47) and (b <= 47):
        return ("hole")
    elif (75 <= r <= 95) and (75 <= g <= 95) and (90 <= b <= 110):
        return ("checkpoint")
    
def save_object():
    global value
    global row
    global column
    if cardinal == "east":
        row += 1
    elif cardinal == "west":
        row -= 1
    elif cardinal == "north":
        column += 1
    elif cardinal == "south":
        column -= 1
    value = (row, column)
    return (value)

nextTileY = -3
nextTileX = -3.5

def calcNextTileY():
    '''Define the next tile on Y axis'''
    global cardinal
    global nextTileY

    if state != "turn":
        if cardinal == 'north':
            nextTileY = nextTileY - 2
        elif cardinal == 'south':
            nextTileY = nextTileY + 2

def calcNextTileX(x):
    '''Define the next tile on X axis'''
    global cardinal
    global nextTileX

    if state != 'turn':
        if cardinal == 'east':
            nextTileX = nextTileX + 2
        elif cardinal == 'west':
            nextTileX = nextTileX - 2

def cardinalDefine(x, y):
    '''Refresh cardinal values'''
    global cardinal
    global column
    global row
    global x1
    global y1

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

while robot.step(timeStep) != -1:
    # Update robot & sensors

    dis_frontal = distancia_frontal.getValue()
    dis_lateral = distancia_lateral.getValue()

    image = colorSensor.getImage()
    
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
    
    counter += 1
    
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
    
    # Initialize state machine

    if counter % 110 == 0 :
        get_angle()
        counter %= 5

    if state == "advance":
        # print("columna:", column, " fila:", row)
        if angle not in angle_permit:
            state = "advance_fix"
            if (diff_max <= angle_prox) or (angle_prox <= diff_min):
                if turn_counter == 20:
                    turn_counter = 0
                    advance(1,0.97)
        else:
            cardinalDefine(x,y)
            if y == nextTileY:
                calcNextTileY()
            if x >= nextTileX:
                calcNextTileX(x)
            else:
                advance(1,1)

        if check_object(image) == "checkpoint":
            print("checkpoint")
            save_object()
            Checkpoint.append(value)
            print(Checkpoint) 
        
        if (dis_frontal < tilesize_detection) or (check_object(image)=="swamp") or (check_object(image)=="hole"):
            x1 = x
            y1 = y

            if cardinal == 'north':
                nextTileY = nextTileY + 2
            elif cardinal == 'south':
                nextTileY = nextTileY - 2

            if check_object(image)=="swamp":
                #print("swamp")
                if cardinal == "east":
                    Swamp.append((row +1, column))
                elif cardinal == "west":
                    Swamp.append((row -1, column))
                elif cardinal == "north":
                    Swamp.append((row, column +1))
                elif cardinal == "south":
                    Swamp.append((row, column -1))
                #print(Swamp)

            elif check_object(image)=="hole":
                #print("hole")
                if cardinal == "east":
                    Hole.append((row +1, column))
                elif cardinal == "west":
                    Hole.append((row -1, column))
                elif cardinal == "north":
                    Hole.append((row, column +1))
                elif cardinal == "south":
                    Hole.append((row, column -1))
                #print(Hole)
            
            state = "turn"

            if dis_lateral < tilesize_detection:
                encoder_goal = encoder_actual - encoder
                turn_counter += 1
                turn(-0.5)
            else:
                encoder_goal = encoder_actual + encoder
                turn_counter += 1
                turn(0.5)
    
    elif state == "advance_fix":
        if (angle_prox < diff_max) or (diff_min < angle_prox):
            state = "advance"
            angle = 0
    
    elif state == "turn":
        angle = 0
        if(abs(encoder_actual - encoder_goal) < turn_range):
            state = "advance"
            encoder_actual = 45
