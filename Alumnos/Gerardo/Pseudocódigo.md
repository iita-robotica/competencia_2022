# Código para avance de baldoza en baldoza

    proximaTile = 0
    def calcNextTile(y):
        '''Función para calcular la próxima baldoza'''
        global cardinal
        global proximaTile

        if cardinal == 'north':
            proximaTile = proximaTile - 2
        elif cardinal == 'south':
            proximaTile = proximaTile + 2
    
## Código dentro del loop
    '''Permite comprobar si es necesario calcular la proxima posición'''

    if y == proximaTile:
                calcNextTile(y) #
            else:
                advance(2,2)