from cmath import inf
from datetime import datetime
from distutils import bcppcompiler
from email.charset import QP
import multiprocessing
from multiprocessing.dummy import Array
from time import sleep
from typing import List
from PyQt5.QtWidgets import QWidget, QPushButton, qApp, QLabel,QOpenGLWidget
from PyQt5.QtGui import QPainter, QBrush, QPen, QFont, QColor, QWheelEvent
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent, QKeyEvent
import numpy as np
from axis import Axis
from lab5.figure import Figure
from lab5.shared import Light
from sphere import Sphere
from polyfigure import PolyFigure

from multiprocessing import Process

from point import Point
from line import Line
from shared import Colors, Config
from polygon import Polygon

import mathematics as mat

arr = []

class Interface(QWidget):
    
    '''
    Главный класс приложения. В нем подключается и реализуется вся логика приложения.
    '''
    axis: Axis 
    qp: QPainter
    selected_point: Point
    helpPen: QPen
    pen: QPen
    isWheelMoved: bool

    rectangleX : Polygon
    rectangleY : Polygon
    rectangleZ : Polygon

    cursorOnX: bool
    cursorOnY: bool
    cursorOnZ: bool

    lockRects: bool
    addPoint: bool
    isAnime: bool
    isWheelMoved: bool

    pos: np.array

    light: Point

    pyramid: PolyFigure
    cube: PolyFigure
    sphere: Sphere

    line: List[Line]

    def __init__(self) -> None:
        super().__init__()
        # VGA = (self)
        self.qp = QPainter()                # Просто специальная рисовалка
        self.axis: Axis = Axis(self)
        # self.winLines : WindowLines = WindowLines(self, self.axis)
        self.light = Point(self, self.axis.matrix, 2, 2, 2, is_light=True, is_help=False)
        self.initRects()

        self.selected_point: Point = None

        self.helpPen = QPen(Colors.RED, 1, Qt.DashLine) # Кисть для вспомогательных линий
        self.helpPen.setStyle(Qt.CustomDashLine)
        self.helpPen.setDashPattern([4, 3])

        self.pen = QPen(Colors.RED, 2, Qt.SolidLine)
        
        self.keys = {81: False, 65: False, 87: False, 83: False, 69: False, 68: False,
                     73: False, 75: False, 79: False, 76: False, 80: False, 59: False}
        self.isWheelMoved = False

        self.lines = []
        self.isPressed = False

        self.isBorders = False

        self.initFigures()

    def initRects(self) -> None:
        '''
        Инициализация прямоугольников, лежащим между осями
        '''
        penLines = QPen(Colors.RED, 2)
        penFill = QPen(QColor(penLines.color().red(), penLines.color().green(), penLines.color().blue(), 80), 1)

        pX = [ Point(self, self.axis.matrix, 0, 0, 0),
               Point(self, self.axis.matrix, 0, 1, 0),
               Point(self, self.axis.matrix, 0, 1, 1),
               Point(self, self.axis.matrix, 0, 0, 1) ]
        self.rectangleX = Polygon(self, pX, penFill, penLines, self.light, isDraw=False)
        self.cursorOnX = False

        pY = [ Point(self, self.axis.matrix, 0, 0, 0),
               Point(self, self.axis.matrix, 0, 0, 1),
               Point(self, self.axis.matrix, 1, 0, 1),
               Point(self, self.axis.matrix, 1, 0, 0) ]
        self.rectangleY = Polygon(self, pY, penFill, penLines, self.light, isDraw=False)
        self.cursorOnY = False

        pZ = [ Point(self, self.axis.matrix, 0, 0, 0),
               Point(self, self.axis.matrix, 1, 0, 0),
               Point(self, self.axis.matrix, 1, 1, 0),
               Point(self, self.axis.matrix, 0, 1, 0) ]
        self.rectangleZ = Polygon(self, pZ, penFill, penLines, self.light, isDraw=False)
        self.cursorOnZ = False

        self.lockRects = True
        self.addPoint = False
        self.isAnime = False

    def initFigures(self) -> None:
        ''''
        Инициализация фигур
        '''
        isBorders = False

        penFill = QPen(Colors.GREEN, 1, Qt.SolidLine)
        penBorder = QPen(Colors.YELLOW, 1, Qt.SolidLine)
        A = Point(self, self.axis.matrix, 0.75, 0.5, 0, name='A')
        B = Point(self, self.axis.matrix, 0.25, 0.25, 0, name='B')
        C = Point(self, self.axis.matrix, 0.25, 0.75, 0, name='C')
        D = Point(self, self.axis.matrix, 0.42, 0.5, 0.5, name='D')

        pyramidList = [ 
            [ A, B, C ], 
            [ A, D, B ],
            [ C, D, A ],
            [ B, D, C ]
        ]

        pyramidPoint = Point(self, self.axis.matrix, 0.42, 0.5, -0.25, is_help=False)
        self.pyramid = PolyFigure(self, self.axis.matrix, pyramidPoint, pyramidList, penFill, penBorder, self.light, True, isBorders=isBorders)

        A1 = Point(self, self.axis.matrix, 1.5, 1, 0, name='A1')
        B1 = Point(self, self.axis.matrix, 1.5, 0.5, 0, name='B1')
        C1 = Point(self, self.axis.matrix, 1, 0.5, 0, name='C1')
        D1 = Point(self, self.axis.matrix, 1, 1, 0, name='D1')

        A2 = Point(self, self.axis.matrix, 1.5, 1, 0.5, name='A2')
        B2 = Point(self, self.axis.matrix, 1.5, 0.5, 0.5, name='B2')
        C2 = Point(self, self.axis.matrix, 1, 0.5, 0.5, name='C2')
        D2 = Point(self, self.axis.matrix, 1, 1, 0.5, name='D2')

        cubeList = [
            [ A1, B1, C1, D1 ],
            [ A2, B2, B1, A1 ],
            [ B2, C2, C1, B1 ],
            [ C2, D2, D1, C1 ],
            [ D2, A2, A1, D1 ],
            [ D2, C2, B2, A2 ]
        ]

        penFill = QPen(Colors.BLUE, 1, Qt.SolidLine)
        penBorder = QPen(Colors.YELLOW, 1, Qt.SolidLine)
        cubePoint = Point(self, self.axis.matrix, 1.25, 0.75, -0.25, is_help=False)
        self.cube = PolyFigure(self, self.axis.matrix, cubePoint, cubeList, penFill, penBorder, self.light, True, isBorders=isBorders)
        
        r = 0.35
        hr = 2*r/3
        x = 0.6
        y = 1.4
        z = 0.25
        
        A1 = Point(self, self.axis.matrix, x,    y+r,  z, name='A')
        B1 = Point(self, self.axis.matrix, x+r/2, y+hr, z+r/2, name='B1')
        C1 = Point(self, self.axis.matrix, x-r/2, y+hr, z+r/2, name='C1')
        D1 = Point(self, self.axis.matrix, x-r/2, y+hr, z-r/2, name='D1')
        E1 = Point(self, self.axis.matrix, x+r/2, y+hr, z-r/2, name='E1')
        F =  Point(self, self.axis.matrix, x, y, z+r, name='F')
        G =  Point(self, self.axis.matrix, x-hr, y, z+hr, name='G')
        H =  Point(self, self.axis.matrix, x-r, y, z, name='H')
        I =  Point(self, self.axis.matrix, x-hr, y, z-hr, name='I')
        J =  Point(self, self.axis.matrix, x, y, z-r, name='J')
        K =  Point(self, self.axis.matrix, x+hr, y, z-hr, name='K')
        L =  Point(self, self.axis.matrix, x+r, y, z, name='L')
        M =  Point(self, self.axis.matrix, x+hr, y, z+hr, name='M')
        A2 = Point(self, self.axis.matrix, x,    y-r,  z, name='A')
        B2 = Point(self, self.axis.matrix, x+r/2, y-hr, z+r/2, name='B2')
        C2 = Point(self, self.axis.matrix, x-r/2, y-hr, z+r/2, name='C2')
        D2 = Point(self, self.axis.matrix, x-r/2, y-hr, z-r/2, name='D2')
        E2 = Point(self, self.axis.matrix, x+r/2, y-hr, z-r/2, name='E2')

        sphereList = [
            [ A1, C1, B1 ],
            [ A1, D1, C1 ],
            [ A1, E1, D1 ],
            [ A1, B1, E1 ],

            [ F, M, B1 ],
            [ F, B1, C1 ],
            [ F, C1, G ],
            [ F, G, C2 ],
            [ F, C2, B2 ],
            [ F, B2, M ],

            [ H, G, C1 ],
            [ H, C1, D1 ],
            [ H, D1, I ],
            [ H, I, D2 ],
            [ H, D2, C2 ],
            [ H, C2, G ],

            [ J, I, D1 ],
            [ J, D1, E1 ],
            [ J, E1, K ],
            [ J, K, E2 ],
            [ J, E2, D2 ],
            [ J, D2, I ],

            [ L, K, E1 ],
            [ L, E1, B1 ],
            [ L, B1, M ],
            [ L, M, B2 ],
            [ L, B2, E2 ],
            [ L, E2, K ],

            [ A2, B2, C2 ],
            [ A2, C2, D2 ],
            [ A2, D2, E2 ],
            [ A2, E2, B2 ],
        ]


        # penFill = QPen(Colors.YELLOW_COLOR, 1, Qt.SolidLine)
        # penBorder = QPen(Colors.BLUE_COLOR, 1, Qt.SolidLine)
        penFill = QPen(Colors.YELLOW, 1, Qt.SolidLine)
        penBorder = QPen(Colors.BLUE, 1, Qt.SolidLine)
        spherePoint = Point(self, self.axis.matrix, x, y, -0.25, is_help=False)
        
        self.sphere = PolyFigure(self, self.axis.matrix, spherePoint, sphereList, penFill, penBorder, self.light, True, isBorders=isBorders)
        # spherePoint = Point(self, self.axis.matrix, 0.75, 1.25,-0.25, is_help=False)
        # self.sphere = Sphere(self, self.axis.matrix, spherePoint, centerPoint, 0.25, penFill, penBorder, self.light)

    def paintEvent(self, event) -> None:
        '''
        Событие рисования на экране. Вызывается при вызове метода self.update()
        '''
        self.qp.begin(self)
        self.draw()
        self.qp.end()
        
    def clearScreen(self) -> None:
        '''
        Очистка экрана
        '''
        w = self.size().width()
        h = self.size().height()

        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(Colors.LIGHT_GREEN)

        self.qp.setBrush(brush)
        self.qp.drawRect(-1, -1, w+1, h+1)
    
    def drawRects(self) -> None:
        qArray = []
        if (self.cursorOnX):
            self.rectangleX.draw()
            qArray.append(self.rectangleX.points[1])
            qArray.append(self.rectangleX.points[3])
            qArray.append(self.axis.ox)
            self.drawHelper(self.rectangleX, qArray, 0)
                
        if (self.cursorOnY):
            self.rectangleY.draw()
            qArray.append(self.rectangleY.points[1])
            qArray.append(self.rectangleY.points[3])
            qArray.append(self.axis.oy)
            self.drawHelper(self.rectangleY, qArray, 1)
        if (self.cursorOnZ):
            self.rectangleZ.draw()
            qArray.append(self.rectangleZ.points[1])
            qArray.append(self.rectangleZ.points[3])
            qArray.append(self.axis.oz)
            self.drawHelper(self.rectangleZ, qArray, 2)

    def drawHelper(self, rect: Polygon, qArray: List, mode: int) -> None:
        sel = self.selected_point
        p = rect.points[0]
        q = qArray[2]
        self.drawHelpLines(p, q, self.axis.center, mode)
        if (sel != None):
            lines = []
            recX = rect.points[0].coords[0]
            recY = rect.points[0].coords[1]
            recZ = rect.points[0].coords[2]

            A = Point(self, self.axis.matrix, sel.x() if mode != 0 else recX,
                                              sel.y() if mode != 1 else recY,
                                              sel.z() if mode != 2 else recZ,
                                              sel.w() )

            B = Point(self, self.axis.matrix, recX if mode in [0, 1] else sel.x(),
                                              recY if mode in [1, 2] else sel.y(),
                                              recZ if mode in [0, 2] else sel.z(),
                                              sel.w())

            C = Point(self, self.axis.matrix, recX if mode in [0, 2] else sel.x(),
                                              recY if mode in [0, 1] else sel.y(),
                                              recZ if mode in [1, 2] else sel.z(),
                                              sel.w())
            

            lines.append(Line(self, sel, A, self.helpPen))
            lines.append(Line(self, A, B, self.helpPen))
            lines.append(Line(self, A, C, self.helpPen))
            for l in lines:
                l.draw(updateScreen=True)

            for p in [B, C]:
                for i in range (2):
                    trueMode = 0
                    if (mode == 0 and i == 0) or (mode == 2 and i == 1):
                        trueMode = 1
                    elif (mode == 1 and i == 0) or (mode == 0 and i == 1):
                        trueMode = 2
                    q = qArray[i]

                    self.drawHelpLines(p, q, rect.points[0], trueMode)

    def drawHelpLines(self, p: Point, q: Point, f: Point, mode: int) -> None:
        '''
        Рисование вспомогательных линий (для ощущения объёма)
        '''
        if (p.coords[mode] > q.coords[mode]):
            line = Line(self, q, p, self.helpPen)
            line.draw()
        elif (p.coords[mode] < f.coords[mode]):
            line = Line(self, f, p, self.helpPen)
            line.draw()
    
    def draw(self) -> None:
        '''
        Рисование всего на экран
        '''
        # self.lines = []
        self.clearScreen()
        self.axis.draw()
        self.drawRects()
        for l in self.lines:
            l.draw()
        self.drawFigures()
        # sphereUpdate = False
        # if ((self.selected_point == self.sphere.controlDot
        #      or self.selected_point == self.light) and not self.lockRects
        #      ):
        #      sphereUpdate = True
        #      self.isPressed = False
        # self.sphere.draw(sphereUpdate)

        self.light.draw()
    
    def setIsBorders(self) -> None:
        for fig in PolyFigure.instances:
            fig.setIsBorders(not fig.isBorders)

    def drawFigures(self) -> None:
        for inst in PolyFigure.instances:
            inst.controlDot.initScreen()
         # габариты
        if (PolyFigure.ifCrossFigures() == False):
            PolyFigure.instances.sort(key=lambda x:x.controlDot.screen[2], reverse=True)
            for fig in PolyFigure.instances:
                fig.draw()
        else:
            polygons = []
            for fig in PolyFigure.instances:
                for poly in fig.getScreenPolyes():
                    polygons.append(poly)
            for poly in polygons:
                poly.computeLight()

            xMin = int(min(p.screen[0] for poly in polygons for p in poly.points))
            yMin = int(min(p.screen[1] for poly in polygons for p in poly.points))

            xMax = int(max(p.screen[0] for poly in polygons for p in poly.points))
            yMax = int(max(p.screen[1] for poly in polygons for p in poly.points))

            painter = QPainter(self)

            pixSize = Config.AXIS_LINE_LENGTH // 25
            borderSize = pixSize // 2

            procNum = 6
            processes = []
            array = multiprocessing.Array('i', 0)
            step = (yMax-yMin) // pixSize // procNum
            
            # figures = []
            # for fig in PolyFigure.instances:
            #     figures.append(fig.getScreenPolyes())
            # start = datetime.now()  
            # for i in range(len(figures)):
            #     for j in range(i+1, len(figures)):
            #         for poly1 in figures[i]:
            #             for poly2 in figures[j]:
            #                 for point in poly1.fillDots:
            #                     if ()        
            for y in range(yMin, yMax, pixSize):
                for x in range(xMin, xMax, pixSize):
                    zBuff = []
                    for poly in polygons:
                        if (mat.dot_in_poly([x, y], poly.get_screen_lines()) == 1):
                            points = poly.get_screen_points()
                            polyEq = mat.eq_poly(points[0], points[1], points[2], points[0])
                            c = mat.get_z_in_poly(x, y, polyEq)
                            if (c != None):
                                zBuff.append([poly.computedPen, c])
                    if (len(zBuff) > 0):
                        minZV = min(zBuff, key=lambda p:p[1])
                        pen = minZV[0]
                        pen.setWidth(pixSize)
                        painter.setPen(pen)
                        painter.drawLine(x-borderSize, y, x+borderSize, y)
                        # for i in range (-borderSize, borderSize+1):
                        #     for j in range (-borderSize, borderSize+1):
                        #         painter.drawPoint(x+i, y+j)
            painter.end()
            for fig in PolyFigure.instances:
                fig.controlDot.draw()

    


                        

    def checkPress(self):
        for button in self.keys:
            if button:
                return True
        return False

    def checkPointIntersectionEvent(self, pos: QPoint) -> Point:
        '''
        Поиск точки, на которую было произведено нажатие
        '''
        pnt = list(filter(lambda p: p.checkIntersection(pos), Point.instances))
        return pnt[0] if pnt else False

    def searchCursorRectCross(self, pos: QPoint, rect: Polygon) -> np.array:
        '''
        Поиск пересечения текущей позиции кусрсора с прямоугольником rect
        '''
        reverse = np.linalg.inv(self.axis.matrix)

        A = [pos.x(), pos.y(), 0]
        B = [pos.x(), pos.y(), 3]

        recP = rect.get_screen_points()
        poly = mat.eq_poly(recP[0], recP[1], recP[2], recP[0])
        line = mat.parametr_line(A, B)

        cross = mat.line_poly_cross(line, poly)
        posCross = [cross[0][0], cross[0][1], cross[0][2], 1]
        posArray = np.array(posCross)

        return np.dot(reverse, posArray)

    
    def mousePressEvent(self, mouse: QMouseEvent) -> None:
        '''
        Обрабортка нашатия на кнопку мыши
        '''

        intersection_pnt = self.checkPointIntersectionEvent(mouse.pos())
        if (self.lockRects and not self.addPoint) and intersection_pnt:
            self.selectPoint(intersection_pnt)

        if (self.cursorOnX):
            self.mouseHelper(self.rectangleX, mouse, 0)
        elif (self.cursorOnY):
            self.mouseHelper(self.rectangleY, mouse, 1)
        elif (self.cursorOnZ):
            self.mouseHelper(self.rectangleZ, mouse, 2)


        self.update()
    def mouseHelper(self, rect: Polygon, mouse: QMouseEvent, mode: int) -> None:
        if (self.lockRects and not self.addPoint):
            self.pos = self.searchCursorRectCross(mouse.pos(), rect)
            self.lockRects = False
            if (self.selected_point != None):
                d = 0
                d = self.selected_point.x() if mode == 0 else d
                d = self.selected_point.y() if mode == 1 else d
                d = self.selected_point.z() if mode == 2 else d
                rect.animeMove(d, mode, self.selected_point, False)
            else:
                axisPos = self.searchCursorRectCross(mouse.pos(), rect)
                self.pos = axisPos
                self.points.append(Point(self, self.axis.matrix, axisPos[0], axisPos[1], axisPos[2], axisPos[3], check=True))
                self.selectPoint(self.points[-1])
        elif (not self.addPoint):
            # self.lockRects = True
            self.addPoint = True
            axisPos = self.searchCursorRectCross(mouse.pos(), rect)
            self.pos = axisPos
            if (self.selected_point == None):
                self.points.append(Point(self, self.axis.matrix, axisPos[0], axisPos[1], axisPos[2], axisPos[3], check=True))
                self.selectPoint(self.points[-1])
            else:
                self.anime(self.selected_point)#, [axisPos[0], axisPos[1], axisPos[2], axisPos[3]])
        else:
            self.selectPoint(None)
            self.initRects()
    
    def selectPoint(self, point: Point) -> None:
        '''
        Выделение точки (красная)
        '''
        if (self.selected_point == point):
            self.selected_point.setIsSelected(False)
            self.selected_point = None
        else:
            if (self.selected_point != None):
                self.selected_point.setIsSelected(False)
                self.selected_point = None
            if (point != None):
                self.selected_point = point
                self.selected_point.setIsSelected(True)

    def keyReleaseEvent(self, key: QKeyEvent) -> None:
        self.keys[key.key()] = False
        
    def keyPressEvent(self, key: QKeyEvent) -> None:
        '''
        Событие нажатия на клавишу клавиатуры. Удаление точки, если была нажата кнопка DELETE, BACK_SPACE.
        ESC -- удаление всех точек
        "Q" и "A" - вращение осей по OX
        "W" и "S" - вращение осей по OY
        "E" и "D" - вращение осей по OZ

        "I" и "K" - вращение точек по OX
        "O" и "L" - вращение точек по OY
        "P" и ";" - вращение точек по OZ
        '''
        alpha = 3.0
        if key.key() == 81 or self.keys[81]:
            self.axis.rotate_x(alpha)
        elif key.key() == 65 or self.keys[65]:
            self.axis.rotate_x(-alpha)
        if key.key() == 87 or self.keys[87]:
            self.axis.rotate_y(alpha)
        elif key.key() == 83 or self.keys[83]:
            self.axis.rotate_y(-alpha)
        if key.key() == 69 or self.keys[69]:
            self.axis.rotate_z(alpha)
        elif key.key() == 68 or self.keys[68]:
            self.axis.rotate_z(-alpha)

        if (not self.addPoint and self.lockRects):
            # pass
            # if key.key() in (Qt.Key_Backspace, Qt.Key_Delete) and self.selected_point:
            #     self.points.remove(self.selected_point)
            #     self.selected_point = None
            #     self.update()
            if(key.key() == Qt.Key_Escape):
                self.setIsBorders() 
                # self.points.clear()
        elif (key.key() == Qt.Key_Enter-1):
            self.selectPoint(None)
            self.initRects()

        self.isPressed = True
        self.keys[key.key()] = True
        self.update()

    def moveCursor(self, pos: QPoint) -> None:
        '''
        обработка движения курсора
        '''
        if (self.lockRects and self.selected_point != None and not self.addPoint): # 
            self.cursorOnX = False
            self.cursorOnY = False
            self.cursorOnZ = False
            self.lines = []
            if (not self.checkPointIntersectionEvent(pos)):
                posList = [pos.x(), pos.y()]
                recX_z = inf
                recY_z = inf
                recZ_z = inf
                
                if (mat.dot_in_poly(posList, self.rectangleX.get_screen_lines()) == 1):
                    recX_z = self.rectangleX.get_screen_points()[2][2]

                if (mat.dot_in_poly(posList, self.rectangleY.get_screen_lines()) == 1):
                    recY_z = self.rectangleY.get_screen_points()[2][2]

                if (mat.dot_in_poly(posList, self.rectangleZ.get_screen_lines()) == 1):
                    recZ_z = self.rectangleZ.get_screen_points()[2][2]

                if (recX_z < recY_z and recX_z < recZ_z):
                    self.cursorOnX = True
                elif (recY_z < recX_z and recY_z < recZ_z):
                    self.cursorOnY = True
                elif (recZ_z < recX_z and recZ_z < recY_z):
                    self.cursorOnZ = True
                
            self.update()
        elif (not self.isAnime):
            if (self.cursorOnX):
                self.moveHelper(self.rectangleX, self.rectangleY, pos, 0)
                self.update()
            elif (self.cursorOnY):
                self.moveHelper(self.rectangleY, self.rectangleZ, pos, 1)
                self.update()
            elif (self.cursorOnZ):
                self.moveHelper(self.rectangleZ, self.rectangleX, pos, 2)
                self.update()

    def moveHelper(self, rect1: Polygon, rect2: Polygon, pos: QPoint, mode: int):
        if self.addPoint:
            curPos = self.searchCursorRectCross(pos, rect1)
            self.selected_point.setCoords(curPos[0], curPos[1], curPos[2], curPos[3], check=True)
            self.pos = curPos

    def wheelEvent(self, wheel: QWheelEvent) -> None:
        p = wheel.angleDelta()
        d = p.y()/120 / 10

        if (not self.isWheelMoved and not self.lockRects):
            if (self.cursorOnX and not self.rectangleX.isAnime):
                self.rectangleX.animeMove(d, 0, self.selected_point)
            elif (self.cursorOnY and not self.rectangleY.isAnime):
                self.rectangleY.animeMove(d, 1, self.selected_point)
            elif (self.cursorOnZ and not self.rectangleZ.isAnime):
                self.rectangleZ.animeMove(d, 2, self.selected_point)
        self.isWheelMoved = not self.isWheelMoved
        
        

    def anime(self, start: Point, end: List = None) -> None:
        '''
        Анимация движения точки из положения start в положение end по прямой
        '''
        flag = False
        if end == None:
            end = self.pos
            flag = True
        self.isAnime = True
        for i in range (0, 101, 20):
            if flag:
                end = self.pos
            t = i / 100
            cur = start.coords
            x = (cur[0] + (end[0] - cur[0])*t)
            y = (cur[1] + (end[1] - cur[1])*t)
            z = (cur[2] + (end[2] - cur[2])*t)
            start.setCoords(x, y, z, start.w())
            self.update()
            qApp.processEvents()
        self.isAnime = False



# xList = list(range(xMin, xMax, pixSize))
# for i in range(6):
#     yList = list(range(step*i, step*(i+1), pixSize))
#     p = Process(target=iteration, args=(xList, yList, borderSize, Polygon.instances, array))
#     processes.append(p)
#     p.start()

# for p in processes:
#     p.join()
# for item in array:
#     painter.setPen(item[1])
#     painter.drawPoint(item[0][0], item[0][1])
# array = Array('i', 0)
def iteration(xList, yList, borderSize, polygons, array):
    for y in yList:
        for x in xList:
            A = [x, y, 0]
            B = [x, y, 3]
            zBuff = []
            for poly in polygons:
                if (mat.dot_in_poly([x, y], poly.get_screen_lines()) == 1):
                    points = poly.get_screen_points()
                    polyEq = mat.eq_poly(points[0], points[1], points[2], points[0])
                    line = mat.parametr_line(A, B)
                    c = mat.line_poly_cross(line, polyEq)
                    zBuff.append([poly.computedPen, c[0]])
            if (len(zBuff) > 0):
                minZV = min(zBuff, key=lambda p:p[1][2])
                # painter.setPen(minZV[0])
                for i in range (-borderSize, borderSize+1):
                    for j in range (-borderSize, borderSize+1):
                        array.acquire()
                        try:

                        # global array
                        # with array.get():
                            array.append([[x+i, y+j], minZV[0]])
                        finally:
                            array.release()
                        # painter.drawPoint(x+i, y+j)       

            

        
    


