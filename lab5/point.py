from functools import singledispatch
from itertools import chain
import string
from traceback import print_tb
from typing import List
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QRectF, QPoint, QPointF
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
    polygons: List       # список полигонов, ссылающихся на эту точку
    
    def __init__(self, 
            widget: QWidget,
            matrix: np.array, 
            x: float, 
            y: float, 
            z: float, 
            w: float = 1.0, 
            check: bool = False,
            pen: QPen = None,
            name: string = 'point',

            is_selected: bool = False, 
            is_light: bool = False,
            is_help: bool = True) -> None:   
        
        if (not is_help):
            self.__class__.instances.append(self)
        self.is_help = is_help
        self.is_drawed = False
        self.setWidget(widget)
        self.matrix = matrix
        self.setCoords(x, y, z, w, check)
        self.setIsSelected(is_selected)
        self.setIsLight(is_light)
        self.polygons = []
        self.pen = pen
        self.name = name
        

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

    def addPolygon(self, poly) -> None:
        self.polygons.append(poly)
    
    @singledispatch
    def setCoords(self, x: float, y: float, z: float, w: float=1, check: bool = True) -> None:
        '''
        Установка координат в трехмерном пространстве
        '''
        self.incorrect = [x, y, z]
        # if check:
        #     [x, y, z] = Config.checkLimits(x, y, z)
            
        self.coords = np.array([ x, y, z, w ], dtype=np.float32)

    @singledispatch
    def move(self, dx, dy, dz, w=1, check = True) -> None:
        self.setCoords(self.coords[0] + dx, self.coords[1] + dy, self.coords[2] + dz, self.w())
    
    def setWidget(self, widget: QWidget) -> None:
        '''
        Дать понять рисовалке на чем рисовать
        '''
        self.widget = widget
        
    def initPainter(self, size=1) -> None:
        '''
        Инициализация рисовалки
        '''
        self.painter = QPainter(self.widget) 
        if self.is_help and self.pen != None:
            self.pen.setWidth(size)
            self.painter.setPen(self.pen)
            # self.painter.setBrush(QBrush(Colors.RED, Qt.SolidPattern))
        elif self.is_selected:
            self.painter.setPen(QPen(Colors.RED, 1, Qt.SolidLine))
            self.painter.setBrush(QBrush(Colors.RED, Qt.SolidPattern))
        elif self.is_light:
            self.painter.setPen(QPen(Colors.WHITE, 1, Qt.SolidLine))
            self.painter.setBrush(QBrush(Colors.WHITE, Qt.SolidPattern))
        # elif self.is_anime:
        #     self.painter.setPen(QPen(Colors.YELLOW, 1, Qt.SolidLine))
        #     self.painter.setBrush(QBrush(Colors.YELLOW, Qt.SolidPattern))
        else:
            self.painter.setPen(QPen(Colors.GREEN, 1, Qt.SolidLine))
            self.painter.setBrush(QBrush(Colors.GREEN, Qt.SolidPattern))
        self.painter.setRenderHints(QPainter.Antialiasing)
    def initHelp(self) -> None:
        self.painter = QPainter(self.widget) 
        self.painter.setPen(self.pen)
        
    def setIsLight(self, is_light: bool) -> None:
        '''
        Флаг принадлежности точки к кривой Безье
        '''
        self.is_light = is_light
        if is_light:
            self.intensity = np.float32(0.6)
        
    def setIsSelected(self, is_selected: bool) -> None:
        '''
        Выбранная точка (красная)
        '''
        self.is_selected = is_selected
    
    def initScreen(self) -> None:
        # m = [ [1, 0, 0, 0],
        #       [0, 1, 0, 0],
        #       [0, 0, 1, 0],
        #       [0, 0, 0.5/Config.AXIS_LINE_LENGTH, 1] ]
        # matrix = np.dot(m, self.matrix)
        self.screen = np.dot(self.matrix, self.coords)
        # screen = np.dot(m, screen)
        # self.screen = np.divide(screen, screen[3])

    def setPen(self, pen: QPen) -> None:
        self.pen = pen
    
    def draw(self, pixSize=1) -> None:
        '''
        Рисование точки
        '''
        self.initPainter(pixSize)
        self.initScreen()
        if (self.is_help):
            # self.initHelp()
            size = pixSize//2
            self.painter.drawLine(QPointF(self.screen[0]-size, self.screen[1]),QPointF(self.screen[0]+size, self.screen[1]))
            # for i in range(-size, size+1):
            #     for j in range(-size, size+1):
            #         self.painter.drawPoint(QPointF(self.screen[0]+i, self.screen[1]+j))
                    # self.painter.drawLine(QPointF(self.screen[0]+i, self.screen[1]+j).toPoint(),QPointF(self.screen[0]+i, self.screen[1]+j).toPoint())
        else:
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