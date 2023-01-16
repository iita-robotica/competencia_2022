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

point = 0
cardinal = "north"


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
        angle = math.atan2(abs(y-1),abs(x-x1)) * 180/math.pi
    else:
        angle = 0
    return angle

def angle_normalizer(ang):
    ang = ang % 90
    if ang < 0:
        ang += 90
    return ang

def danger(image):
    r = colorSensor.imageGetRed(image, 1, 0, 0)
    g = colorSensor.imageGetGreen(image, 1, 0, 0)
    b = colorSensor.imageGetBlue(image, 1, 0, 0)
    if (210 <= r <= 240) and (180 <= g <= 210) and (100 <= b <= 130):
        return True
    elif (r <= 47) and (g <= 47) and (b <= 47):
        return True

nextTile = -3

def calcNextTile(y):
    '''Función para calcular la próxima baldoza'''
    global cardinal
    global nextTile

    if state != "turn":
        if cardinal == 'north':
            nextTile = nextTile - 2
        elif cardinal == 'south':
            nextTile = nextTile + 2

def setCardinal(actualPoint):
    global cardinal 
    if point == 0 or point == -4:
        cardinal = "north"
    elif point == 1 or point == -3:
        cardinal = "east"
    elif point == 2 or point == -2:
        cardinal = "south"
    elif point == 3 or point == -1:
        cardinal = "west"

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
    
    if (4 <= point) or (point <= -5):
        point = 0
    
    #Initialize state machine

    print(cardinal)
    print(nextTile)

    if counter % 110 == 0 :
        get_angle()
        counter %= 5

    if state == "advance":
        #print("x:", x, " x1:", x1, " y:", y, " y1:", y1)
        #print("angulo:", angle)
        if angle not in angle_permit:
            state = "advance_fix"
            if (diff_max <= angle_prox) or (angle_prox <= diff_min):
                if turn_counter == 20:
                    turn_counter = 0
                    advance(1,0.97)
        else:
            setCardinal(point)
            if y == nextTile:
                calcNextTile(y)
            else:
                advance(1,1)
            
        if dis_frontal < tilesize_detection or danger(image):
            x1 = x
            y1 = y
            state = "turn"
            if cardinal == 'north':
                nextTile = nextTile + 2
            elif cardinal == 'south':
                nextTile = nextTile - 2
                
            if dis_lateral < tilesize_detection:
                encoder_goal = encoder_actual - encoder
                turn_counter += 1
                point -= 1
                turn(-0.5)
            else:
                encoder_goal = encoder_actual + encoder
                turn_counter += 1
                point += 1
                turn(0.5)
                
        #print("punto=", point)
        #print(cardinal)
        # for i in range(row_total):
        #     rows.append(row)
        # rows_order = sorted(rows)
        
    elif state == "turn":
        angle = 0
        if(abs(encoder_actual - encoder_goal) < turn_range):
            state = "advance"
            encoder_actual = 45
    
    elif state == "advance_fix":
        if (angle_prox < diff_max) or (diff_min < angle_prox):
            state = "advance"
            angle = 0


#determinar cada cuanos valores del gps se avanza una casilla
#norte o este suma uno a la columa o fila, sur u este resta uno a la columna o fila