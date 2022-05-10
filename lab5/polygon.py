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
from lab5.mathematics import cross

from shared import Config, Colors, Light, normalize, RotationMatrices
from point import Point
from line import Line
from axis import Axis
import mathematics as mat

class Polygon:
    widget: QWidget
    
    points : List[Point] 
    # matrix: np.matrix
    lines : List[Line]
    fillLines: List[Line]
    pixels: List        # расчитанный свет для каждого пикселя
    image: QImage

    painter: QPainter
    penFill: QPen   # перо для заливки
    penLines: QPen  # перо для линий
    light: Point    # свет

    isLines: bool    # надо ли рисовать граничные линии
    isLight: bool    # надо ли уучитывать свет

    diffCoords: List # координаты точек относительно нулевой точки полигона
    diffFill: List

    def __init__(self, widget: QWidget, points : List[Point], penFill: QPen, penLines: QPen, light: Point, isLines: bool = True, isLight = False) -> None:
        self.widget = widget

        self.penFill = penFill
        self.penLines = penLines
        self.computedPen = penFill
        self.light = light

        self.matrix = points[0].matrix

        self.points = points

        self.setLines()

        self.isLines = isLines
        self.isLight = isLight

        self.initFillLines()

        # if self.isLight:
        #     self.computeLight()
    
    def setLines(self) -> None:
        self.lines = []
        self.diffCoords = []
        # self.lines = [ Line(self.widget, self.matrix, points[i], points[(i+1) % len(points)], self.penLines) 
        #                for i in range(0, len(points))]
        start = self.points[0]
        for i, p in enumerate(self.points):
            p.addPolygon(self)
            self.lines.append(Line(self.widget, p, self.points[(i+1) % len(self.points)], self.penLines))
            self.diffCoords.append(p.coords - start.coords)

    def initPainter(self, pen: QPen) -> None:
        '''
        Инициализация рисовалки
        '''
        self.painter = QPainter(self.widget)
        self.painter.setPen(pen)
        self.painter.setRenderHints(QPainter.Antialiasing)

    def setIsDrawed(self) -> None:
        for p in self.points:
            p.is_drawed = True
    
    def computeLight(self) -> QPen:
        # pen = self.penFill
        # for l in self.lines:
        #     l.initScreen() 

        # minY = int(min([ p[1] for l in self.lines for p in l.screen ]) - 1)
        # maxY = int(max([ p[1] for l in self.lines for p in l.screen ]) + 1)

        # minX = int(min([ p[0] for l in self.lines for p in l.screen ]) - 1)
        # maxX = int(max([ p[0] for l in self.lines for p in l.screen ]) + 1)

        poly = mat.eq_poly(self.points[0].coords, self.points[1].coords, self.points[2].coords, self.points[0].coords)
        N = np.array([poly[0], poly[1], poly[2]])
        N = N/np.sqrt((N*N).sum())
        color = self.penFill.color()

        # lines = [ [[l.screen[0][0], l.screen[0][1]],[l.screen[1][0], l.screen[1][1]]] for l in self.lines ]
        # polyScreenP = self.get_screen_points()
        # polyScreen = mat.eq_poly(polyScreenP[0], polyScreenP[1], polyScreenP[2], polyScreenP[0])
        # reverse = np.linalg.inv(self.matrix)

        # self.image = QImage(self.widget.width(), self.widget.height(), QImage.Format.Format_RGBA64)
        # self.image.fill(Colors.TRANSPARENT)
        P = self.points[0].coords
        i = Light.computeLightForDot(self.light,P, N)
        c = QColor(int(color.red()*i), int(color.green()*i), int(color.blue()*i), color.alpha())
        pen = QPen(c, 2, Qt.SolidLine)
        return pen

        # self.fill(pen)
        

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

    def initFillLines(self) -> None:
        self.fillLines = []
        self.diffFill = []
        step = 1/Config.AXIS_LINE_LENGTH

        minX = min([ p.x() for p in self.points ])
        maxX = max([ p.x() for p in self.points ])

        minY = min([ p.y() for p in self.points ])
        maxY = max([ p.y() for p in self.points ])

        minZ = min([ p.z() for p in self.points ])
        maxZ = max([ p.z() for p in self.points ])

        start = self.points[0]

        # lines = [ [[l.p1.coords[0], l.p1.coords[1], ],[l.p2.coords[0], l.p2.coords[1]]] for l in self.lines ]
        

        # for z in range(minZ, maxZ, 1):
        polygon = mat.eq_poly(self.points[0].coords, self.points[1].coords, self.points[2].coords, self.points[0].coords)
        # print(polygon)
        l_param = []
        for l in self.lines:
            l_param.append(mat.parametr_line(l.p1.coords, l.p2.coords))
        if (polygon[0] == 0 and polygon[1] == 0):
            y = minY
            while (y <= maxY):
                # seg = [[minX, y], [maxX, y]]
                poly = mat.eq_poly([minX, y, minZ], [minX+1, y, minZ], [minX, y, minZ+1], [minX, y, minZ])
                crosses = []
                for l in l_param:
                    c = mat.line_poly_cross(l, poly)
                    if c != None and 0 <= c[1] <= 1: #or (len(crosses) != 0 and crosses.index(c) == ValueError):
                        crosses.append(c)
                if (len(crosses) >= 2):
                    # if crosses[0][0] > crosses[1][0]:
                    #     crosses[0][0], crosses[1][0] = crosses[1][0], crosses[0][0]
                    self.fillLines.append(Line(self.widget, Point(self.widget, self.matrix, crosses[0][0][0], crosses[0][0][1], crosses[0][0][2]),
                                                            Point(self.widget, self.matrix, crosses[1][0][0], crosses[1][0][1], crosses[1][0][2]), self.penFill))
                    self.diffFill.append(self.fillLines[-1].p1.coords - start.coords)
                    # self.painter.drawLine(QPointF(crosses[0][0], crosses[0][1]), QPointF(crosses[1][0], crosses[1][1]))
                y += step
        else:
            z = minZ
            while (z <= maxZ):
                # seg = [[minX, y], [maxX, y]]
                poly = mat.eq_poly([minX, minY, z], [minX+1, minY, z], [minX, minY+1, z ], [minX, minY, z ])
                # print(poly, z)
                crosses = []

                for l in l_param:
                    # l_param = mat.parametr_line(l.p1.coords, l.p2.coords)
                    # c = mat.param_cross(seg, l)
                    c = mat.line_poly_cross(l, poly)
                    # print(c)
                    if c != None and 0 <= c[1] <= 1: #or (len(crosses) != 0 and crosses.index(c) == ValueError):
                        crosses.append(c)
                if (len(crosses) >= 2):
                    # print(crosses)
                    # if crosses[0][0] > crosses[1][0]:
                    #     crosses[0][0], crosses[1][0] = crosses[1][0], crosses[0][0]
                    self.fillLines.append(Line(self.widget, Point(self.widget, self.matrix, crosses[0][0][0], crosses[0][0][1], crosses[0][0][2]),
                                                            Point(self.widget, self.matrix, crosses[1][0][0], crosses[1][0][1], crosses[1][0][2]), self.penFill))
                    self.diffFill.append(self.fillLines[-1].p1.coords - start.coords)
                    # self.painter.drawLine(QPointF(crosses[0][0], crosses[0][1]), QPointF(crosses[1][0], crosses[1][1]))
                z += step

    def fill(self, pen: QPen) -> None:
        # pen = self.penFill
        for l in self.lines:
            l.initScreen() 

        minX = int(min([ x for l in self.lines for x in [l.p1.screen[0], l.p2.screen[0]] ]) - 1)
        maxX = int(max([ x for l in self.lines for x in [l.p1.screen[0], l.p2.screen[0]] ]) + 1)

        minY = int(min([ y for l in self.lines for y in [l.p1.screen[1], l.p2.screen[1]] ]) - 1)
        maxY = int(max([ y for l in self.lines for y in [l.p1.screen[1], l.p2.screen[1]] ]) + 1)

        lines = [ [[l.p1.screen[0], l.p1.screen[1]],[l.p2.screen[0], l.p2.screen[1]]] for l in self.lines ]
        

        self.initPainter(pen)
        for y in range(minY, maxY, 1):
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

    def minZ(self) -> float:
        return min([p.screen[2] for p in self.points])

    def maxZ(self) -> float:
        return max([p.screen[2] for p in self.points])

    def draw(self, updateScreen:bool = False, transparent: int = 80) -> None:
        for p in self.points:
                p.is_drawed = False
        if updateScreen:
            for p in self.points:
                p.initScreen()
        if self.isLight:
            self.computedPen = self.computeLight()
            for l in self.fillLines:
                l.setPen(self.computedPen)
                l.draw(updateScreen=True)
        else:
            # self.fill(self.penFill)
            for l in self.fillLines:
                l.draw(updateScreen=True)
        if self.isLines:
            for l in self.lines:
                l.draw(updateScreen=True)

    def get_screen_lines(self) -> List:
        screen_lines = []
        self.initScreen()
        for l in self.lines:
            screen_lines.append([l.p1.screen, l.p2.screen])
        return screen_lines

    def get_screen_points(self) -> List:
        screen_points = []
        self.initScreen()
        for p in self.points:
            screen_points.append(p.screen)
        return screen_points

    def initScreen(self) -> None:
        for p in self.points:
            p.initScreen()

    def move(self, dx: float, dy: float, dz: float, check: bool = True):
        for p in self.points:
            p.move(dx, dy, dz, check)
        for l in self.fillLines:
            l.move(dx, dy, dz, check)
            # l.move(dx, dy, dz, check)

    def setFillPos(self) -> None:
        start = self.points[0]
        for i, l in enumerate(self.fillLines):
            try:
                l.setPos(start.incorrect[0] + self.diffFill[i][0], start.incorrect[1] + self.diffFill[i][1], start.incorrect[2] + self.diffFill[i][2])
            except AttributeError:
                l.setPos(start.x() + self.diffFill[i][0], start.y() + self.diffFill[i][1], start.z() + self.diffFill[i][2])

    def setPos(self, x: float, y: float, z: float, check: bool = True):
        for i, p in enumerate(self.points):
            p.setCoords(x + self.diffCoords[i][0], y + self.diffCoords[i][1], z + self.diffCoords[i][2])
        for i, l in enumerate(self.fillLines):
            l.setPos(x + self.diffFill[i][0], y + self.diffFill[i][1], z + self.diffFill[i][2], check)
            # l.setPos(x + self.diffCoords[i][0], y + self.diffCoords[i][1], z + self.diffCoords[i][2])

    def getCoords(self) -> List:
        return self.lines[0].coords[0]

    def animeMove(self, d: float, mode: int, curPoint: Point, pointMode: bool = True) -> None:
        if (-Config.MAX_COORD <= self.points[0].coords[mode] + d <= Config.MAX_COORD):
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