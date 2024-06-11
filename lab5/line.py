from typing import List
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QPointF
from point import Point
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

    p1: Point
    p2: Point

    diffCoords: List
    
    def __init__(self, widget: QWidget, p1: Point, p2: Point, pen: QPen = None, is_anime = False) -> None:
        self.setWidget(widget)
        self.p1 = p1
        self.p2 = p2
        # self.setCoords(p1, p2)
        self.setDiff()
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
        # if (check):
        #     p1 = Config.checkLimits(p1[0], p1[1], p1[2])
        #     p2 = Config.checkLimits(p2[0], p2[1], p2[2])

        self.p1.setCoords(p1[0], p1[1], p1[2], check)
        self.p2.setCoords(p2[0], p2[1], p2[2], check)

        self.setDiff()
        

    def setDiff(self) -> None:
        self.diffCoords = self.p2.coords - self.p1.coords

    def initPainter(self) -> None:
        '''
        Инициализация рисовалки
        '''
        self.painter = QPainter(self.widget)
        self.painter.setPen(self.pen)
        self.painter.setRenderHints(QPainter.Antialiasing)

    def initScreen(self) -> None:
        # self.screen = [ np.dot(self.matrix, self.coords[0]),
        #            np.dot(self.matrix, self.coords[1]) ]
        self.p1.initScreen()
        self.p2.initScreen()
        
    def setWidget(self, widget: QWidget) -> None:
        '''
        Дать понять рисовалке на чем рисовать
        '''
        self.widget = widget
    
    # def len(self) -> float:
    #     return math.sqrt((self.x2-self.x1)**2 + (self.y2-self.y1)**2)

    def move(self, dx: float, dy: float, dz: float, check: bool = True) -> None:
        self.setPos(self.p1.x()+dx, self.p1.y()+dy, self.p1.z()+dz, check)
    
    def setPos(self, x: float, y: float, z: float, w: float = 1,  check: bool = True) -> None:
        [x1, y1, z1] = [x, y, z]
        [x2, y2, z2] = [x + self.diffCoords[0], y + self.diffCoords[1], z + self.diffCoords[2]]

        # self.p1.setCoords(x, y, z, w, check)
        # self.p2.setCoords(x + self.diffCoords[0], y + self.diffCoords[1], z + self.diffCoords[2], w, check)
        self.p1.setCoords(x1, y1, z1, check)
        self.p2.setCoords(x2, y2, z2, check)
    
    def draw(self, updateScreen: bool=False) -> None:
        '''
        Рисование линии
        '''
        self.initPainter()
        if updateScreen:
            self.p1.initScreen()
            self.p2.initScreen()
        # self.initScreen()
        # self.painter.draw
        # self.painter.drawLine(QPointF(self.screen[0][0], self.screen[0][1]), QPointF(self.screen[1][0], self.screen[1][1]))
        self.painter.drawLine(QPointF(self.p1.screen[0], self.p1.screen[1]), QPointF(self.p2.screen[0], self.p2.screen[1]))
        self.painter.end()
    
    
        