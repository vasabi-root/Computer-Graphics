from audioop import reverse
from figure import Figure
from shared import Colors, Config, Light
from polygon import Polygon 
from typing import List
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPen, QColor, QPixmap, QImage, qRgba, QPainter
from PyQt5.QtCore import QPointF, QPoint
import numpy as np
from point import Point

class Sphere(Figure):

    center: Point
    radius: float
    image: QImage

    def __init__(self, widget: QWidget, matrix: np.array, controlDot: Point, center: Point, radius: float, penFill: QPen, penBorder: QPen, light: List[Point]) -> None:
        super().__init__(widget, matrix, controlDot, penFill, penBorder, light)

        self.center = center
        self.radius = radius*Config.AXIS_LINE_LENGTH
        self.diff = center.coords - controlDot.coords
        self.image = None
        print(self.diff)

    def initPainter(self, pen: QPen) -> None:
        '''
        Инициализация рисовалки
        '''
        self.painter = QPainter(self.widget)
        self.painter.setPen(pen)
        self.painter.setRenderHints(QPainter.Antialiasing)
    
    def draw(self, isUpdate: bool = False) -> None:
        if (isUpdate or self.image == None):
            self.image = QImage(self.widget.width(), self.widget.height(), QImage.Format.Format_RGBA64)
            self.image.fill(Colors.TRANSPARENT)
            self.center.initScreen()
            screen = self.center.screen
            coords = self.center.coords
            reverse = np.linalg.inv(self.matrix)
            color = self.penFill.color()

            step = 0.06

            theta = np.pi/2
            while (theta <= np.pi):
                fi = 0
                while (fi < 2*np.pi):
                    x = screen[0] + self.radius*np.sin(theta)*np.cos(fi)
                    y = screen[1] + self.radius*np.sin(theta)*np.sin(fi)
                    z = screen[2] + self.radius*np.cos(theta)
                    P = np.dot(reverse, np.array([x, y, z, 1]))
                    N = np.array([P[0] - coords[0], P[1] - coords[1], P[2] - coords[2]])
                    # N[3] = 1
                    # print(N, P)
                    i = Light.computeLightForDot(self.light, P, N)
                    c = qRgba(int(color.red()*i), int(color.green()*i), int(color.blue()*i), color.alpha())
                    # print(x, y, i)
                    self.setPix(x, y, c)
                    fi += step
                theta += step

        self.initPainter(self.penFill)
        self.painter.drawImage(QPoint(0,0),self.image)
        self.painter.end()

        self.controlDot.draw()
                

    def setPix(self, x: float, y: float, c: int):
        if 0 <= x+1 < self.widget.width()-1 and 0 <= y+1 < self.widget.height()-1:
            # for i in [0, 1]
            points = []
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    self.image.setPixel(QPointF(x+i, y+j).toPoint(), c)
            # p1 = QPointF(x, y)
            # p2 = QPointF(x+1, y)
            # p3 = QPointF(x, y+1)
            # p4 = QPointF(x+1, y+1)


            # self.image.setPixel(p1.toPoint(), c)
            # self.image.setPixel(p2.toPoint(), c)
            # self.image.setPixel(p3.toPoint(), c)
            # self.image.setPixel(p4.toPoint(), c)

    def setPos(self) -> None:
        self.center.coords = self.controlDot.coords + self.diff
                
    
