from functools import singledispatch
from typing import List
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QRectF, QPoint
import numpy as np

from shared import Colors, Config


class Point:
    '''
    Класс точки с вспомогательными удобными методами.
    '''
    WIDTH = 8             # Диаметр, т.к. точка рисуется не как окружность
    HEIGHT = 8
    SELECT_RADIUS = 30     # Радиус нажатия мышкой для выделения

    coords: np.array     # координаты относительно осей
    screen: np.array     # координаты относительно экрана

    matrix: np.array     # матрица перехода из осевых в экранные координаты

    instances = []
    
    def __init__(self, 
            widget: QWidget,
            matrix: np.array, 
            x: float, 
            y: float, 
            z: float, 
            w: float = 1.0, 
            check: bool = False,

            is_selected: bool = False, 
            is_curve: bool = False) -> None:   

        self.__class__.instances.append(self)

        self.setWidget(widget)
        self.matrix = matrix
        self.setCoords(x, y, z, w, check)
        self.setIsSelected(is_selected)
        self.setIsCurve(is_curve)

    def __str__(self) -> str:
        return f'Point ({self.x()}, {self.y()}, {self.z()}, {self.w()})'

    def x(self) -> float:
        return self.coords[0]

    def y(self) -> float:
        return self.coords[1]

    def z(self) -> float:
        return self.coords[2]

    def w(self) -> float:
        return self.coords[3]
    
    @singledispatch
    def setCoords(self, x: float, y: float, z: float, w: float, check: bool = True) -> None:
        '''
        Установка координат в трехмерном пространстве
        '''
        if check:
            [x, y, z] = Config.checkLimits(x, y, z)
            
        self.coords = np.array([ x, y, z, w ], dtype=np.float64)


    @singledispatch
    def move(self, dx, dy, dz, w=1, check = True) -> None:
        self.setCoords(self.coords[0] + dx, self.coords[1] + dy, self.coords[2] + dz, self.w())
    
    def setWidget(self, widget: QWidget) -> None:
        '''
        Дать понять рисовалке на чем рисовать
        '''
        self.widget = widget
        
    def initPainter(self) -> None:
        '''
        Инициализация рисовалки
        '''
        self.painter = QPainter(self.widget) 
        if self.is_selected:
            self.painter.setPen(QPen(Colors.RED_COLOR, 1, Qt.SolidLine))
            self.painter.setBrush(QBrush(Colors.RED_COLOR, Qt.SolidPattern))
        elif self.is_curve:
            self.painter.setPen(QPen(Colors.BLUE_COLOR, 1, Qt.SolidLine))
            self.painter.setBrush(QBrush(Colors.BLUE_COLOR, Qt.SolidPattern))
        # elif self.is_anime:
        #     self.painter.setPen(QPen(Colors.YELLOW_COLOR, 1, Qt.SolidLine))
        #     self.painter.setBrush(QBrush(Colors.YELLOW_COLOR, Qt.SolidPattern))
        else:
            self.painter.setPen(QPen(Colors.GREEN_COLOR, 1, Qt.SolidLine))
            self.painter.setBrush(QBrush(Colors.GREEN_COLOR, Qt.SolidPattern))
        self.painter.setRenderHints(QPainter.Antialiasing)
        
    def setIsCurve(self, is_curve: bool) -> None:
        '''
        Флаг принадлежности точки к кривой Безье
        '''
        self.is_curve = is_curve
        
    def setIsSelected(self, is_selected: bool) -> None:
        '''
        Выбранная точка (красная)
        '''
        self.is_selected = is_selected
    
    def initScreen(self) -> None:
        self.screen = np.dot(self.matrix, self.coords)

    
    def draw(self) -> None:
        '''
        Рисование точки
        '''
        self.initPainter()
        self.initScreen()
        r = Point.WIDTH / 2
        self.painter.drawEllipse(QRectF(self.screen[0] - r, self.screen[1] - r, Point.WIDTH, Point.HEIGHT))
        self.painter.end()
        
    def checkIntersection(self, pos: QPoint) -> bool:
        '''
        Проверка пересечения точки с мышкой
        '''
        # mat = np.dot(matrix, self.coords)
        self.initScreen()
        x = self.screen[0] - abs(Point.SELECT_RADIUS - Point.WIDTH) // 2
        y = self.screen[1] - abs(Point.SELECT_RADIUS - Point.HEIGHT) // 2
        return x <= pos.x() <= x + Point.SELECT_RADIUS and \
                y <= pos.y() <= y + Point.SELECT_RADIUS

