from distutils.command.config import config
from netrc import NetrcParseError
from typing import List
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QPointF
from shared import Config, Colors

import math


import numpy as np


class Line:
    '''
    Класс линии с вспомогательными удобными методами
    '''
    
    LINE_WIDTH = 1              # Толщина
    YELLOW_COLOR = QColor("#FFD800")    # Цвета
    BLUE_COLOR =   QColor("#0057B8")

    coords: np.array    # координаты концов линии относительно осей
    screen: np.array    # координаты концов линии относительно экрана

    matrix: np.array    # матрица перехода

    diffCoords: List
    
    def __init__(self, widget: QWidget, matrix: np.array, p1: List, p2: List, pen: QPen = None, is_anime = False) -> None:
        self.setWidget(widget)
        self.matrix = matrix
        self.setCoords(p1, p2)
        self.setPen(pen)
        self.setAnime(is_anime)
    
    def setPen(self, pen:QPen) -> None:
        '''
        Инициализация пера (цвет, текстура)
        '''
        self.pen = pen

    def setAnime(self, is_anime:bool):
        self.is_anime = is_anime

    def setCoords(self, p1: List, p2: List, check: bool = True) -> None:
        '''
        Установка координат
        '''
        if (check):
            p1 = Config.checkLimits(p1[0], p1[1], p1[2])
            p2 = Config.checkLimits(p2[0], p2[1], p2[2])

        self.diffCoords = []

        if (len(p1) != 4):
            p1.append(1)
        if (len(p2) != 4):
            p2.append(1)
        self.coords = [ np.array(p1), 
                        np.array(p2) ]
        self.diffCoords.append(p2[0]-p1[0])
        self.diffCoords.append(p2[1]-p1[1])
        self.diffCoords.append(p2[2]-p1[2])
    def initPainter(self) -> None:
        '''
        Инициализация рисовалки
        '''
        self.painter = QPainter(self.widget)
        self.painter.setPen(self.pen)
        self.painter.setRenderHints(QPainter.Antialiasing)

    def initScreen(self) -> None:
        self.screen = [ np.dot(self.matrix, self.coords[0]),
                        np.dot(self.matrix, self.coords[1]) ]
        
    def setWidget(self, widget: QWidget) -> None:
        '''
        Дать понять рисовалке на чем рисовать
        '''
        self.widget = widget
    
    # def len(self) -> float:
    #     return math.sqrt((self.x2-self.x1)**2 + (self.y2-self.y1)**2)

    def move(self, dx: float, dy: float, dz: float, check: bool = True) -> None:
        self.setCoords([self.coords[0][0] + dx, self.coords[0][1] + dy, self.coords[0][2] + dz, self.coords[0][3]],
                       [self.coords[1][0] + dx, self.coords[1][1] + dy, self.coords[1][2] + dz, self.coords[1][3]])
    
    def setPos(self, x: float, y: float, z: float, w: float = 1,  check: bool = True) -> None:
        [x, y, z] = Config.checkLimits(x, y, z)

        self.coords[0] = np.array([x, y, z, w])
        self.coords[1] = np.array([x + self.diffCoords[0], y + self.diffCoords[1], z + self.diffCoords[2], w])
    
    def draw(self) -> None:
        '''
        Рисование линии
        '''
        self.initPainter()
        self.initScreen()
        # self.painter.draw
        self.painter.drawLine(QPointF(self.screen[0][0], self.screen[0][1]), QPointF(self.screen[1][0], self.screen[1][1]))
        self.painter.end()
    
    
        