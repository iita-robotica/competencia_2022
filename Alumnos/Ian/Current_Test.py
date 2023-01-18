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

movement_state = "advance"
object_state = "tile"

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

Start = (row, column)
Swamp = []
Hole = []
Checkpoint = []

next_tile = (0,0)

cardinal = "north"

Mapping = {
    "Comienzo": Start,
    "Pantano": Swamp,
    "Agujero": Hole,
    "Guardado": Checkpoint
}

r1 = 241
g1 = 241
b1 = 241
ar = 0
ag = 0
ab = 0


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


# Start mapping functions

def update_position():
    global x
    global y
    global x1
    global y1
    global cardinal
    global row
    global column
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

def check_object(image):
    global object_state
    global r1
    global g1
    global b1
    global ar
    global ag
    global ab
    r = colorSensor.imageGetRed(image, 1, 0, 0)
    g = colorSensor.imageGetGreen(image, 1, 0, 0)
    b = colorSensor.imageGetBlue(image, 1, 0, 0)
    if (210 <= r <= 240) and (180 <= g <= 210) and (100 <= b <= 130):
        object_state = "swamp"
    elif (r <= 47) and (g <= 47) and (b <= 47):
        object_state = "hole"
    elif (75 <= r <= 95) and (75 <= g <= 95) and (90 <= b <= 110):
        object_state = "checkpoint"
    ar = abs(r - r1)
    ag = abs(g - g1)
    ab = abs(b - b1) 
    
def save_object():
    global next_tile
    global row
    global column
    update_position()
    check_object(image)
    if (object_state != "tile"): #and (tile_counter2 != tile_counter1):
        if cardinal == "east":
            next_tile = (row+1, column)
        elif cardinal == "west":
            next_tile = (row-1, column)
        elif cardinal == "north":
            next_tile = (row, column+1)
        elif cardinal == "south":
            next_tile = (row, column-1)



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
        
    
    # Initialize movement state machine

    if counter % 110 == 0 :
        get_angle()
        counter %= 5

    if movement_state == "advance":
        #print("x:", x, " x1:", x1, " y:", y, " y1:", y1)
        #print("angulo:", angle)
        update_position()
        check_object(image)
        
        if angle not in angle_permit:
            movement_state = "advance_fix"
            if (diff_max <= angle_prox) or (angle_prox <= diff_min):
                if turn_counter == 20:
                    turn_counter = 0
                    advance(1,0.97)
        else:
            advance(1,1)
        
        if (dis_frontal < tilesize_detection) or (object_state=="hole"):        
            x1 = x
            y1 = y
            movement_state = "turn"
            if dis_lateral < tilesize_detection:
                encoder_goal = encoder_actual - encoder
                turn_counter += 1
                turn(-0.5)
            else:
                encoder_goal = encoder_actual + encoder
                turn_counter += 1
                turn(0.5)
    
    elif movement_state == "advance_fix":
        if (angle_prox < diff_max) or (diff_min < angle_prox):
            movement_state = "advance"
            angle = 0
    
    elif movement_state == "turn":
        angle = 0
        if(abs(encoder_actual - encoder_goal) < turn_range):
            movement_state = "advance"
            encoder_actual = 45


    # Initialize object state machine
    
    check_object(image)
    save_object()
    
    if (20 < ar) and (20 < ag) and (20 < ab):
        
        if object_state == "checkpoint":
            #print("checkpoint")
            Checkpoint.append(next_tile)
            #print(Checkpoint)
        
        elif object_state == "swamp":
            #print("swamp")
            Swamp.append(next_tile)
            print(Swamp)
        
        elif object_state == "hole":
            #print("hole")
            save_object()
            Hole.append(next_tile)
            #print(Hole)



#guardar casilla anerior, compararla con la actual y ver si es diferente para recien guardar el valor
#hacer un contador, si encuentra algo, que sume uno (aumenta cada vez que cambia de color)
#chequear si el valor ya está en la lista, si es uno nuevo, aregarlo
