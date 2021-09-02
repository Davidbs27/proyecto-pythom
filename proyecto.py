import pygame, sys, random
from pygame.locals import *

# Creamos las constantes para el tamaño del tablero, color de las celdas y fondo.
numColumnas = 4  # le asignaremos el nº de colmnunas
numFilas = 4  # y lo mismo para el nº de filas
celdaSize = 80
anchoVentana = 640
alturaVentana = 480
FPS = 30
BLANK = None

BLACK = (0, 0, 0, 128)
WHITE = (255, 255, 255, 128)
BRIGHTBLUE = (0, 50, 255, 128)
DARKTURQUOISE = (3, 54, 73, 128)
PURPEL = (128, 0, 255, 0)

BGCOLOR = DARKTURQUOISE
TILECOLOR = PURPEL
TEXTCOLOR = WHITE
BORDERCOLOR = BRIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((anchoVentana - (celdaSize * numColumnas + (numColumnas - 1))) / 2)
YMARGIN = int((alturaVentana - (celdaSize * numFilas + (numFilas - 1))) / 2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((anchoVentana, alturaVentana))
    pygame.display.set_caption('Slide Puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # Guardamos las distintas acciones de nuestros botones.
    RESET_SURF, RESET_RECT = makeText('Reset', TEXTCOLOR, TILECOLOR, anchoVentana - 120, alturaVentana - 90)
    NEW_SURF, NEW_RECT = makeText('New game', TEXTCOLOR, TILECOLOR, anchoVentana - 120, alturaVentana - 60)
    SOLVE_SURF, SOLVE_RECT = makeText('Resolver', TEXTCOLOR, TILECOLOR, anchoVentana - 120, alturaVentana - 30)

    # le asignamos el tamaño de las celdas para generarlo.
    mainBoard, solutionSeq = generateNewPuzzle(80)
    SOLVEDBOARD = getStartingBoard()  # Un tablero resuelto es lo mismo que un tablero en el estado inicial.
    allMoves = []  # El array que contiene la lista de movimientos necesarios para resolver el puzzle.

    while True:  # Bucle principal del juego.
        slideTo = None  # la dirección, siempre que exista la posibilidad, la baldosa debe deslizarse hacia ella.
        msg = 'Haz click en las celdas o usa las flechas para moverte.'  # este mensaje se mostrara arraiba a la izq.
        if mainBoard == SOLVEDBOARD:
            msg = 'Resuelto!'

        drawBoard(mainBoard, msg)  # metodo que dibujuba el tablero y los mensajes

        comprobarCierre()
        for event in pygame.event.get():  # este bucle maneja los distintos eventos para las posiciones de las celdas y los click del ratón.
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    # Comprueba si el usuario a hecho click en algun boton de las opciones.
                    if RESET_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, allMoves)  # Pulsó el boton reset
                        allMoves = []
                    elif NEW_RECT.collidepoint(event.pos):
                        mainBoard, solutionSeq = generateNewPuzzle(80)  # Pulsó el boton juego nuevo
                        allMoves = []
                    elif SOLVE_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, solutionSeq + allMoves)  # Pulsó el boton resolver
                        allMoves = []
                else:
                    # Comprobamos si la celda donde hemos hecho click está al lado de un espacio vacio.

                    blankx, blanky = getBlankPosition(mainBoard)
                    if spotx == blankx + 1 and spoty == blanky:  # si el espacio vacio esta a la izquerda de la celda pulsada se movera hacia la izquerda.
                        slideTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slideTo = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slideTo = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slideTo = DOWN

            elif event.type == KEYUP:
                # verifica si el usuario presionó una tecla para deslizar una celda
                if event.key in (K_LEFT, K_a) and movimientoValido(mainBoard,
                                                                   LEFT):  # comprueba si ha pulsado la letra A o la flecha izq en este caso y si es asi la celda se mueve a la izquerda.
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and movimientoValido(mainBoard,
                                                                      RIGHT):  # lo mismo con la letra D y la fecha derecha.
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and movimientoValido(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and movimientoValido(mainBoard, DOWN):
                    slideTo = DOWN

        if slideTo:
            slideAnimation(mainBoard, slideTo, 'Haz click en las celdas o usa las flechas para moverte',
                           8)  # mostramos el mensaje en la pantalla.
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo)  # Guarda el movimiento
        pygame.display.update()
        FPSCLOCK.tick(FPS)


# Salimos de la aplicación.
def cerrarAplicaicon():
    pygame.quit()
    sys.exit()


def comprobarCierre():
    for event in pygame.event.get(QUIT):  # cogemos todos los eventos de QUIT
        cerrarAplicaicon()  # salimos de la aplicacion si alguno de los enventos QUIT esta presente.
    for event in pygame.event.get(KEYUP):  # cogemos todos los eventos KEYUP
        if event.key == K_ESCAPE:
            cerrarAplicaicon()  # salimos de la aplicacion si el evento KEYUP fue para la tecla Esc
        pygame.event.post(event)  # poner los otros objetos de evento KEYUP de nuevo


def getStartingBoard():
    # Devuelve un array con las posiciones celdas ordenas, es decir resuelto
    # Por ejemplo: si el numero de columnas y filas es 3, la funcion nos devolvera:
    # [[1, 4, 7], [2, 5, 8], [3, 6, BLANK]]
    counter = 1
    board = []
    for x in range(numColumnas):
        column = []
        for y in range(numFilas):
            column.append(counter)
            counter += numColumnas
        board.append(column)
        counter -= numColumnas * (numFilas - 1) + numColumnas - 1

    board[numColumnas - 1][numFilas - 1] = BLANK
    return board


def getBlankPosition(board):
    # Devuelve las coordenadas X e Y del tablero del espacio en blanco.
    for x in range(numColumnas):
        for y in range(numFilas):
            if board[x][y] == BLANK:
                return (x, y)


def makeMove(board, move):
    # Esta función no comprueba si el movimiento es válido.
    blankx, blanky = getBlankPosition(board)

    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]


def movimientoValido(board, move):
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != len(board) - 1) or \
           (move == RIGHT and blankx != 0)


def getRandomMove(board, lastMove=None):
    # start with a full list of all four moves
    # empezamos con una lista comleta de mivimientos cuando iniciemos la apliación o le demos a jugar de nuevo
    validMoves = [UP, DOWN, LEFT, RIGHT]

    # Elimina los movimientos de la lista no sean validos.
    if lastMove == UP or not movimientoValido(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not movimientoValido(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not movimientoValido(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not movimientoValido(board, LEFT):
        validMoves.remove(LEFT)

    # Delvolvemos un movimiento aleatorio de la lista de los movientos restantes.
    return random.choice(validMoves)


# obtenemos la celda superior izquierda.
def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * celdaSize) + (tileX - 1)
    top = YMARGIN + (tileY * celdaSize) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    # a partir de las coordenadas de los píxeles X e Y, obtenemos las coordenadas X e yY del tablero.
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, celdaSize, celdaSize)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


# Dibjuamos las celdas
def drawTile(tilex, tiley, number, adjx=0, adjy=0):
    # Dibuja una celda en las coordenadas de tablero X y Y.
    left, top = getLeftTopOfTile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, celdaSize, celdaSize))
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(celdaSize / 2) + adjx, top + int(celdaSize / 2) + adjy
    DISPLAYSURF.blit(textSurf, textRect)


def makeText(text, color, bgcolor, top, left):
    # Crea los objetos Surface y Rect para algún texto.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


# dibujamos el tablero
def drawBoard(board, message):
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])

    left, top = getLeftTopOfTile(0, 0)
    width = numColumnas * celdaSize
    height = numFilas * celdaSize
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)


def slideAnimation(board, direction, message, animationSpeed):
    blankx, blanky = getBlankPosition(board)
    if direction == UP:
        movex = blankx
        movey = blanky + 1
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky

    # prepara la base del tablero
    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()
    # draw a blank space over the moving tile on the baseSurf Surface. dibuja un espacio en blanco sobre la celda que se ha movido en el tablero
    moveLeft, moveTop = getLeftTopOfTile(movex, movey)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, celdaSize, celdaSize))

    for i in range(0, celdaSize, animationSpeed):
        # animacion de la celda deslizando sobre el tablero
        comprobarCierre()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -i)
        if direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, i)
        if direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -i, 0)
        if direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateNewPuzzle(numSlides):
    # Desde una configuración inicial, hace un número de movimientos correspondientes(con su animacion) para empezar a jugar.
    sequence = []
    board = getStartingBoard()
    drawBoard(board, '')
    pygame.display.update()
    pygame.time.wait(500)  # relizar una pausa de 500 milisegundos por cada efecto
    lastMove = None
    for i in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, 'Generando un nuevo puzzle...', animationSpeed=int(celdaSize / 3))
        makeMove(board, move)
        sequence.append(move)
        lastMove = move
    return (board, sequence)


def resetAnimation(board, allMoves):
    # Rehace todos los movientos hechos en el tablero
    revAllMoves = allMoves[:]  # hacemos una copia de la lista de movientos realizados.
    revAllMoves.reverse()

    for move in revAllMoves:
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, '', animationSpeed=int(celdaSize / 2))
        makeMove(board, oppositeMove)


if __name__ == '__main__':
    main()