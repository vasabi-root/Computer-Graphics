from calendar import isleap
from email.charset import QP
import enum
from typing import List
from PyQt5.QtWidgets import QWidget, qApp
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QColor, QPixmap, QImage
from PyQt5.QtCore import Qt, QRectF, QPointF
import numpy as np

from shared import Config, Colors, normalize, RotationMatrices
from point import Point
from line import Line
from axis import Axis
import mathematics as mat

class Polygon:
    widget: QWidget
    
    # points : List
    matrix: np.matrix
    lines : List[Line]
    image: QImage

    painter: QPainter
    penFill: QPen   # перо для заливки
    penLines: QPen  # перо для линий

    isLines: bool   # надо ли рисовать граничные линии
    isAnime: bool

    diffCoords: List # координаты точек относительно нулевой точки полигона

    def __init__(self, widget: QWidget, matrix: np.array, points : List, penFill: QPen, penLines: QPen, isLines: bool = True) -> None:
        self.widget = widget
        self.matrix = matrix
        # self.points = points

        self.penFill = penFill
        self.penLines = penLines

        self.setLines(points)
        # self.pen = QPen(QColor(pen.color().red(), pen.color().green(), pen.color().blue(), 180), 2)
        self.isLines = isLines
        self.isAnime = False
    
    def setLines(self, points) -> None:
        self.lines = []
        self.diffCoords = []
        # self.lines = [ Line(self.widget, self.matrix, points[i], points[(i+1) % len(points)], self.penLines) 
        #                for i in range(0, len(points))]
        start = points[0]
        for i, p in enumerate(points):
            self.lines.append(Line(self.widget, self.matrix, p, points[(i+1) % len(points)], self.penLines))
            self.diffCoords.append([ self.lines[-1].coords[0][0] - start[0],
                                     self.lines[-1].coords[0][1] - start[1],
                                     self.lines[-1].coords[0][2] - start[2] ])
        

    def initPainter(self, pen: QPen) -> None:
        '''
        Инициализация рисовалки
        '''
        self.painter = QPainter(self.widget)
        self.painter.setPen(pen)
        self.painter.setRenderHints(QPainter.Antialiasing)

    def fill(self, pen: QPen) -> None:
        for l in self.lines:
            l.initScreen() 

        minY = int(min([ p[1] for l in self.lines for p in l.screen ]) - 1)
        maxY = int(max([ p[1] for l in self.lines for p in l.screen ]) + 1)

        minX = int(min([ p[0] for l in self.lines for p in l.screen ]) - 1)
        maxX = int(max([ p[0] for l in self.lines for p in l.screen ]) + 1)

        lines = [ [[l.screen[0][0], l.screen[0][1]],[l.screen[1][0], l.screen[1][1]]] for l in self.lines ]

        for y in range(minY, maxY, 1):
            self.initPainter(pen)
            seg = [[minX, y], [maxX, y]]
            crosses = []
            for l in lines:
                c = mat.param_cross(seg, l)

                if c != None: #or (len(crosses) != 0 and crosses.index(c) == ValueError):
                    crosses.append(c)
            if (len(crosses) >= 2):
                if crosses[0][0] > crosses[1][0]:
                    crosses[0][0], crosses[1][0] = crosses[1][0], crosses[0][0]
                self.painter.drawLine(QPointF(crosses[0][0], crosses[0][1]), QPointF(crosses[1][0], crosses[1][1]))
            self.painter.end()
    
    def setPix(self, x: float, y: float):
        p = QPointF(x, y)
        color = self.image.pixelColor(p.toPoint())

    def draw(self, transparent: int = 80) -> None:
        self.fill(self.penFill)
        if self.isLines:
            for l in self.lines:
                l.draw()

    def get_screen_lines(self) -> List:
        screen_lines = []
        for l in self.lines:
            l.initScreen()
            screen_lines.append(l.screen)
        return screen_lines

    def get_screen_points(self) -> List:
        screen_points = []
        for l in self.lines:
            l.initScreen()
            screen_points.append(l.screen[0])
        return screen_points

    def move(self, dx: float, dy: float, dz: float, check: bool = True):
        for l in self.lines:
            l.move(dx, dy, dz, check)

    def setPos(self, x: float, y: float, z: float, check: bool = True):
        for i, l in enumerate(self.lines):
            # dx = self.lines[i].coords[0][0] - self.lines[0].coords[0][0]
            # dy = self.lines[i].coords[0][1] - self.lines[0].coords[0][1]
            # dz = self.lines[i].coords[0][2] - self.lines[0].coords[0][2]
            l.setPos(x + self.diffCoords[i][0], y + self.diffCoords[i][1], z + self.diffCoords[i][2])

    def getCoords(self) -> List:
        return self.lines[0].coords[0]

    def animeMove(self, d: float, mode: int, curPoint: Point, pointMode: bool = True) -> None:
        if (-Config.MAX_COORD <= self.lines[0].coords[0][mode] + d <= Config.MAX_COORD):
            self.isAnime = True
            t = 0.0
            step = 0.2
            diff = float(d*step)
            if (curPoint != None):
                while (self.isAnime and t < 1):
                    dx = diff if mode == 0 else 0
                    dy = diff if mode == 1 else 0
                    dz = diff if mode == 2 else 0
                    # for l in self.lines:
                    #     l.move(dx, dy, dz)
                    self.move(dx, dy, dz)
                    if pointMode:
                        curPoint.move(dx, dy, dz, curPoint.w())

                    self.widget.update()
                    qApp.processEvents()
                    t += step
            self.isAnime = False