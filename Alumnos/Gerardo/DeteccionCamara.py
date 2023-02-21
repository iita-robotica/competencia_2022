from controller import Robot, Camera # Cargo controlador del robot y la camara
import cv2 as cv
import numpy as np
import struct

robot = Robot()

usecamera = True
mensaje = False
distanciaVictima = 0.03

timestep = int(robot.getBasicTimeStep())
camara = robot.getDevice("camera_1")
camara.enable(timestep)

gps = robot.getDevice("gps")
gps.enable(timestep)

def sendMessage(x, z, tipoVictima):
    message = struct.pack('i i c', x, z, tipoVictima)
    print(message)

def sendVictimMessage(victimType='N'):
    global messageSent
    position = gps.getValues()

    if not messageSent:
        sendMessage(int(position[0] * 100), int(position[2] * 100), victimType)
        messageSent = True

def cercano_victima(posicion):
    return posicion < distanciaVictima

def detectVisualSimple(image_data, camera):

    if usecamera:
        coords_list = []
        img = np.array(np.frombuffer(image_data, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4)))
        img[:,:,2] = np.zeros([img.shape[0], img.shape[1]])
        #convert from BGR to HSV color space
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        #apply threshold
        thresh = cv.threshold(gray, 140, 255, cv.THRESH_BINARY)[1]

        # draw all contours in green and accepted ones in red
        contours, h = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        
        for c in contours:
            if cv.contourArea(c) > 1000:
                coords = list(c[0][0])
                coords_list.append(coords)
                print("Victim at x="+str(coords[0])+" y="+str(coords[1]))

        print(coords_list)

    else: 
        return 0

def getVisibleVictims():
    victimas= []
    img = camara.getImage()
    pos = detectVisualSimple(img, camara)

    for victim in pos:
        victimas.append(victim)

    return victimas

def classifyVictim(img):
    '''Permite clasificar la imagen'''
    img = cv.resize(img, (100, 100)) # Redimensionamis la imagen
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY) # Convertimos la imagen a escala de grises para mejor detección
    thresh1 = cv.threshold(gray, 100, 255, cv.THRESH_BINARY_INV)[1]
    conts, h = cv.findContours(thresh1, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    x, y, w, h = cv.boundingRect(conts[0])

    letter = thresh1[y:y + h, x:x + w]
    letter = cv.resize(letter, (100, 100), interpolation=cv.INTER_AREA)

    areaWidth = 20
    areaHeight = 30

    areas = {
        "top": ((0, areaHeight),(50 - areaWidth // 2, 50 + areaWidth // 2)),
        "middle": ((50 - areaHeight // 2, 50 + areaHeight // 2), (50 - areaWidth // 2, 50 + areaWidth // 2)),
        "bottom": ((100 - areaHeight, 100), (50 - areaWidth // 2, 50 + areaWidth // 2 ))
        }

    images = {
        "top": letter[areas["top"][0][0]:areas["top"][0][1], areas["top"][1][0]:areas["top"][1][1]],
        "middle": letter[areas["middle"][0][0]:areas["middle"][0][1], areas["middle"][1][0]:areas["middle"][1][1]],
        "bottom": letter[areas["bottom"][0][0]:areas["bottom"][0][1], areas["bottom"][1][0]:areas["bottom"][1][1]]
        }

    counts = {}
    acceptanceThreshold = 50

    for key in images.keys():
        count = 0
        for row in images[key]:
            for pixel in row:
                if pixel == 255:
                    count += 1
        counts[key] = count > acceptanceThreshold

    letters = {
        "H":{'top': False, 'middle': True, 'bottom': False},
        "S":{'top': True, 'middle': True, 'bottom': True},
        "U":{'top': False, 'middle': False, 'bottom': True}
        }

    #FIXME: Valor que devuelve la función
    for letterKey in letters.keys():
        if counts == letters[letterKey]:
            finalLetter = letterKey
            break
        
    return finalLetter

while robot.step(timestep) != -1:

    # FIXME: Eliminar la necesidad de utilizar bloques try-except.
    try:
        img = camara.getImage()
        img = np.array(np.frombuffer(img, np.uint8).reshape((camara.getHeight(), camara.getWidth(), 4)))
        print(classifyVictim(img))
        cv.waitKey(1)
    except UnboundLocalError:
        pass
    except IndexError:
        pass

#TODO: Detección lograda para letras H, U.
#TODO: Suprimir la necesidad de devolver el valor None.
#TODO: Necesario considerar la corrección de velocidad de procesamiento de las imágenes captadas por cámara.
#TODO: Letra S se clasifica infinitamente. Puede ser arreglado al implementar la función para detectar victimas.
#TODO: Implementar la funcionalidad de la segunda cámara.