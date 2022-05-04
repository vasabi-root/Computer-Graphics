from calendar import isleap
from email.charset import QP
import enum
from typing import List
from PyQt5.QtWidgets import QWidget, qApp
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QColor, QPixmap, QImage, qRgba
from PyQt5.QtCore import Qt, QRectF, QPointF, QPoint
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
    pixels: List        # расчитанный свет для каждого пикселя
    image: QImage

    painter: QPainter
    penFill: QPen   # перо для заливки
    penLines: QPen  # перо для линий
    light: Point    # свет

    isLines: bool    # надо ли рисовать граничные линии
    isLight: bool    # надо ли уучитывать свет

    diffCoords: List # координаты точек относительно нулевой точки полигона

    def __init__(self, widget: QWidget, matrix: np.array, points : List, penFill: QPen, penLines: QPen, light: Point, isLines: bool = True, isLight = False) -> None:
        self.widget = widget
        self.matrix = matrix

        self.penFill = penFill
        self.penLines = penLines
        self.light = light

        self.setLines(points)

        self.isLines = isLines
        self.isLight = isLight

        # if self.isLight:
        #     self.computeLight()
    
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
    
    def computeLight(self) -> None:
        # pen = self.penFill
        # for l in self.lines:
        #     l.initScreen() 

        # minY = int(min([ p[1] for l in self.lines for p in l.screen ]) - 1)
        # maxY = int(max([ p[1] for l in self.lines for p in l.screen ]) + 1)

        # minX = int(min([ p[0] for l in self.lines for p in l.screen ]) - 1)
        # maxX = int(max([ p[0] for l in self.lines for p in l.screen ]) + 1)

        poly = mat.eq_poly(self.lines[0].coords[0], self.lines[1].coords[0], self.lines[2].coords[0], self.lines[0].coords[0])
        N = np.array([poly[0], poly[1], poly[2]])
        N = N/np.sqrt((N*N).sum())
        color = self.penFill.color()

        # lines = [ [[l.screen[0][0], l.screen[0][1]],[l.screen[1][0], l.screen[1][1]]] for l in self.lines ]
        # polyScreenP = self.get_screen_points()
        # polyScreen = mat.eq_poly(polyScreenP[0], polyScreenP[1], polyScreenP[2], polyScreenP[0])
        # reverse = np.linalg.inv(self.matrix)

        # self.image = QImage(self.widget.width(), self.widget.height(), QImage.Format.Format_RGBA64)
        # self.image.fill(Colors.TRANSPARENT)
        P = self.lines[0].coords[0]
        i = self.computeLightForDot(P, N)
        c = QColor(int(color.red()*i), int(color.green()*i), int(color.blue()*i), color.alpha())
        pen = QPen(c, 1, Qt.SolidLine)
        self.fill(pen)
        

        # for y in range(minY, maxY, 1):
        #     seg = [[minX, y], [maxX, y]]
        #     crosses = []
        #     for l in lines:
        #         c = mat.param_cross(seg, l)
        #         if c != None:
        #             crosses.append(c)
        #     if (len(crosses) >= 2):
        #         minCx = int(min([c[0] for c in crosses]))
        #         maxCx = int(max([c[0] for c in crosses]))
        #         for x in range (minCx, maxCx+1):
        #             z = mat.get_z_in_poly(x, y, polyScreen)
                    
        #             if z != None:
        #                 P = np.dot(reverse, np.array([x, y, z, 1]))
        #                 i = self.computeLightForDot(P, N)
        #                 # print(i)
        #                 c = qRgba(int(color.red()*i), int(color.green()*i), int(color.blue()*i), color.alpha())
        #                 if i != 0.5:
        #                     print(i)
        #                     self.setPix(x, y, c)

        # self.initPainter(self.penFill)
        # self.painter.drawImage(QPoint(0,0),self.image)
        # self.painter.end()


        
    
    def computeLightForDot(self, P: np.array, N: np.array): 
        i = 0.5
        
        l = self.light.coords - P
        L = np.array([l[0], l[1], l[2]])
        N_dot_L = L.dot(N)
        if (N_dot_L > 0):
            # print(N_dot_L, self.light.intensity)
            i += self.light.intensity*N_dot_L / (np.sqrt((N*N).sum())* np.sqrt((L*L).sum()))
        return i

    def fill(self, pen: QPen) -> None:
        # pen = self.penFill
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
                # if crosses[0][0] > crosses[1][0]:
                #     crosses[0][0], crosses[1][0] = crosses[1][0], crosses[0][0]
                self.painter.drawLine(QPointF(crosses[0][0], crosses[0][1]), QPointF(crosses[1][0], crosses[1][1]))
            self.painter.end()
            
    
    def setPix(self, x: float, y: float, c: int):
        if 0 <= x < self.widget.width() and 0 <= y < self.widget.height():
            p = QPointF(x, y)
            self.image.setPixel(p.toPoint(), c)
            color = self.image.pixelColor(p.toPoint())

    def draw(self, transparent: int = 80) -> None:
        if self.isLight:
            self.computeLight()
        else:
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