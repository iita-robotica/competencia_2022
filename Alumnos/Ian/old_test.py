from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor
import math


#Start robot & sensors

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


#Start movement variables

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


#Start mapping variables

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

cardinal = "north"

Mapping = {
    "Comienzo": Start,
    "Pantano": Swamp,
    "Agujero": Hole,
    "Guardado": Checkpoint
}


#Start movement functions

def advance(vx, vy):
    ruedaIzquierda.setVelocity(vx)
    ruedaDerecha.setVelocity(vy)

def turn(vel):
    ruedaIzquierda.setVelocity(-vel)
    ruedaDerecha.setVelocity(vel)
    
def get_angle():
    global x
    global y
    global x1
    global y1
    global angulo
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

def is_swamp(image):
    r = colorSensor.imageGetRed(image, 1, 0, 0)
    g = colorSensor.imageGetGreen(image, 1, 0, 0)
    b = colorSensor.imageGetBlue(image, 1, 0, 0)
    if (210 <= r <= 240) and (180 <= g <= 210) and (100 <= b <= 130):
        return True
    
def is_hole(image):
    r = colorSensor.imageGetRed(image, 1, 0, 0)
    g = colorSensor.imageGetGreen(image, 1, 0, 0)
    b = colorSensor.imageGetBlue(image, 1, 0, 0)
    if (r <= 47) and (g <= 47) and (b <= 47):
        return True
    
def is_checkpoint(image):
    r = colorSensor.imageGetRed(image, 1, 0, 0)
    g = colorSensor.imageGetGreen(image, 1, 0, 0)
    b = colorSensor.imageGetBlue(image, 1, 0, 0)
    if (75 <= r <= 95) and (75 <= g <= 95) and (90 <= b <= 110):
        return True



while robot.step(timeStep) != -1:
    
    #Update robot & sensors

    dis_frontal = distancia_frontal.getValue()
    dis_lateral = distancia_lateral.getValue()

    image = colorSensor.getImage()
    
    
    #Update movement variables
    
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
    
    
    #Update mapping variables
    
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
        
    
    #Initialize state machine

    if counter % 110 == 0 :
        get_angle()
        counter %= 5

    if state == "advance":
        #print("x:", x, " x1:", x1, " y:", y, " y1:", y1)
        #print("angulo:", angle)
        
        if x1 < x:
            cardinal == "east"
            if x - x1 >= 2:
                row += 1
                x1 = x
        elif x < x1:
            cardinal == "west"
            if x1 - x >= 2:
                row -= 1
                x1 = x
        if y1 < y:
            cardinal == "south"
            if y - y1 >= 2:
                column -= 1
                y1 = y
        elif y < y1:
            cardinal == "north"
            if y1 - y >= 2:
                column += 1
                y1 = y
        #print("columna:", column, " fila:", row)
        
        if angle not in angle_permit:
            state = "advance_fix"
            if (diff_max <= angle_prox) or (angle_prox <= diff_min):
                if turn_counter == 20:
                    turn_counter = 0
                    advance(1,0.97)
        else:
            advance(1,1)
            
        
        if is_checkpoint(image):
            #print("checkpoint")
            if cardinal == "east":
                Checkpoint.append((row +1, column))
            elif cardinal == "west":
                Checkpoint.append((row -1, column))
            elif cardinal == "north":
                Checkpoint.append((row, column +1))
            elif cardinal == "south":
                Checkpoint.append((row, column -1))
            #print(Checkpoint)
        
        
        if (dis_frontal < tilesize_detection) or is_swamp(image) or is_hole(image):
            
            x1 = x
            y1 = y
            
            if is_swamp(image):
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
            elif is_hole(image):
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
                
        #print("punto=", point)
        #print(cardinal)
        #for i in range(row_total):
            #rows.append(row)
        #rows_order = sorted(rows)
    
    
    elif state == "advance_fix":
        if (angle_prox < diff_max) or (diff_min < angle_prox):
            state = "advance"
            angle = 0
    
    
    elif state == "turn":
        angle = 0
        if(abs(encoder_actual - encoder_goal) < turn_range):
            state = "advance"
            encoder_actual = 45





#Mapeo:
#https://jarroba.com/mapeo-mapping-y-mapeo-mutable-mutablemapping-en-python/