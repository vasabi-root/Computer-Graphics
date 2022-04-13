from email.charset import QP
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

class Rectangle:
    axis : Axis
    points : List[Point]
    screen_points: List
    screen_lines: List
    lines : List[Line]
    pen: QPen
    painter: QPainter
    pixmap : QPixmap
    image: QImage
    onScreen: bool
    isAnime: bool

    def __init__(self, axis : Axis, points : List[Point], pen : QPen, onScreen: bool = False) -> None:
        self.axis = axis
        self.points = points

        self.pen = pen
        self.pen = QPen(QColor(pen.color().red(), pen.color().green(), pen.color().blue(), 180), 2)
        self.onScreen = onScreen
        self.isAnime = False
    
    def setLines(self) -> None:
        vectors = []
        if not self.onScreen:
            for p in self.points:
                vectors.append(np.dot(self.axis.matrix, p.coords))
        else:
            for p in self.points:
                vectors.append(p.coords)
        screen_points = [
            Point(self.axis.widget, vectors[i][0], vectors[i][1], vectors[i][2])
                for i in range(len(vectors))
        ]
        self.screen_points = [ [p.x(), p.y(), p.z(), p.w()] for p in screen_points]
        self.screen_lines = [ 
            [ [screen_points[i].x(), screen_points[i].y()], 
              [screen_points[i+1 if i+1 < len(screen_points) else 0].x(), screen_points[i+1 if i+1 < len(screen_points) else 0].y()] ] 
            for i in range(len(screen_points))
        ]
        
        self.lines = [
            Line(
                self.axis.widget, screen_points[i].x(), screen_points[i].y(), 
                screen_points[i+1 if i+1 < len(screen_points) else 0].x(), screen_points[i+1 if i+1 < len(screen_points) else 0].y(), 
                self.pen
            )
            for i in range(len(screen_points))
        ]

    def initPainter(self, pen: QPen) -> None:
        '''
        Инициализация рисовалки
        '''
        self.painter = QPainter(self.axis.widget)
        self.painter.setPen(pen)
        self.painter.setRenderHints(QPainter.Antialiasing)

    def fill(self, pen: QPen) -> None:
        minY = int(min([ p[1] for p in self.screen_points ]) - 1)
        maxY = int(max([ p[1] for p in self.screen_points ]) + 1)

        minX = int(min([ p[0] for p in self.screen_points ]) - 1)
        maxX = int(max([ p[0] for p in self.screen_points ]) + 1)

        lines = [ [[l.x1, l.y1],[l.x2, l.y2]] for l in self.lines ]


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
        
        # self.painter.setPen(self.pen)
    
    def setPix(self, x: float, y: float):
        p = QPointF(x, y)
        color = self.image.pixelColor(p.toPoint())

    def draw(self, transperent: int = 80) -> None:
        self.setLines()
        pen = QPen(QColor(self.pen.color().red(), self.pen.color().green(), self.pen.color().blue(), transperent), 1)
        self.fill(pen)
        for l in self.lines:
            l.draw()

    def get_screen_lines(self) -> List:
        self.setLines()
        return self.screen_lines

    def get_screen_points(self) -> List:
        self.setLines()
        return self.screen_points

    def move(self, x: float, y: float, z: float):
        for p in self.points:
            p.setCoords(p.x()+x, p.y()+y, p.z()+z, p.w())
    
    def animeMove(self, d: float, mode: int, pointMode: bool = True) -> None:
        if (-Config.MAX_COORD <= self.points[0].coords[mode] + d <= Config.MAX_COORD):
            self.isAnime = True
            t = 0.0
            starts = [p.coords for p in self.points]
            curPoint = self.axis.widget.selected_point
            while (self.isAnime and t < 1 + 0.001):
                for i in range(len(self.points)):
                    cur = starts[i]
                    x = (cur[0] + d*t) if mode == 0 else cur[0]
                    y = (cur[1] + d*t) if mode == 1 else cur[1]
                    z = (cur[2] + d*t) if mode == 2 else cur[2]
                    self.points[i].setCoords(x, y, z, self.points[i].w())
                    if pointMode:
                        curPoint.setCoords(x if mode == 0 else curPoint.x(), 
                                        y if mode == 1 else curPoint.y(),
                                        z if mode == 2 else curPoint.z(),
                                        curPoint.w())
                self.axis.widget.update()
                qApp.processEvents()
                t += 0.2
            self.isAnime = False
