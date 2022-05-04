from audioop import reverse
from cmath import inf
from distutils import bcppcompiler
from email.charset import QP
from time import sleep
from typing import List
from PyQt5.QtWidgets import QWidget, QPushButton, qApp, QLabel
from PyQt5.QtGui import QPainter, QBrush, QPen, QFont, QColor, QWheelEvent
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent, QKeyEvent
import numpy as np
from axis import Axis
from sphere import Sphere
from polyfigure import PolyFigure

from point import Point
from line import Line
from shared import Colors, Config
from polygon import Polygon

import mathematics as mat

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
        
        self.qp = QPainter()                # Просто специальная рисовалка
        self.axis: Axis = Axis(self)
        # self.winLines : WindowLines = WindowLines(self, self.axis)
        self.light = Point(self, self.axis.matrix, 2, 2, 2, is_light=True)
        self.initRects()

        self.selected_point: Point = None

        self.helpPen = QPen(Colors.RED_COLOR, 1, Qt.DashLine) # Кисть для вспомогательных линий
        self.helpPen.setStyle(Qt.CustomDashLine)
        self.helpPen.setDashPattern([4, 3])

        self.pen = QPen(Colors.RED_COLOR, 2, Qt.SolidLine)
        
        self.keys = {81: False, 65: False, 87: False, 83: False, 69: False, 68: False,
                     73: False, 75: False, 79: False, 76: False, 80: False, 59: False}
        self.isWheelMoved = False

        self.lines = []
        self.isPressed = False

        self.initFigures()

    def initRects(self) -> None:
        '''
        Инициализация прямоугольников, лежащим между осями
        '''
        penLines = QPen(Colors.RED_COLOR, 2)
        penFill = QPen(QColor(penLines.color().red(), penLines.color().green(), penLines.color().blue(), 80), 1)

        pX = [ [0, 0, 0],
               [0, 1, 0],
               [0, 1, 1],
               [0, 0, 1] ]
        self.rectangleX = Polygon(self, self.axis.matrix, pX, penFill, penLines, self.light)
        self.cursorOnX = False

        pY = [ [0, 0, 0],
               [0, 0, 1],
               [1, 0, 1],
               [1, 0, 0] ]
        self.rectangleY = Polygon(self, self.axis.matrix, pY, penFill, penLines, self.light)
        self.cursorOnY = False

        pZ = [ [0, 0, 0],
               [1, 0, 0],
               [1, 1, 0],
               [0, 1, 0] ]
        self.rectangleZ = Polygon(self, self.axis.matrix, pZ, penFill, penLines, self.light)
        self.cursorOnZ = False

        self.lockRects = True
        self.addPoint = False
        self.isAnime = False

    def initFigures(self) -> None:
        ''''
        Инициализация фигур
        '''
        penFill = QPen(Colors.BLUE_COLOR, 1, Qt.SolidLine)
        penBorder = QPen(Colors.YELLOW_COLOR, 1, Qt.SolidLine)
        A = [0.75, 0.5, 0]
        B = [0.25, 0.25, 0]
        C = [0.25, 0.75, 0]
        D = [0.42, 0.5, 0.5]

        pyramidList = [ 
            [A, B, C], 
            [A, D, B],
            [C, D, A],
            [B, D, C]
        ]

        pyramidPoint = Point(self, self.axis.matrix, 0.42, 0.5, -0.25)
        self.pyramid = PolyFigure(self, self.axis.matrix, pyramidPoint, pyramidList, penFill, penBorder, self.light, True)

        A1 = [1.5, 1, 0]
        B1 = [1.5, 0.5, 0]
        C1 = [1, 0.5, 0]
        D1 = [1, 1, 0]

        A2 = [1.5, 1, 0.5]
        B2 = [1.5, 0.5, 0.5]
        C2 = [1, 0.5, 0.5]
        D2 = [1, 1, 0.5]

        cubeList = [
            [ A1, B1, C1, D1 ],
            [ A2, B2, B1, A1 ],
            [ B2, C2, C1, B1 ],
            [ C2, D2, D1, C1 ],
            [ D2, A2, A1, D1 ],
            [ D2, C2, B2, A2 ]
        ]
        
        cubePoint = Point(self, self.axis.matrix, 1.25, 0.75, -0.25)
        self.cube = PolyFigure(self, self.axis.matrix, cubePoint, cubeList, penFill, penBorder, self.light, True)

        centerPoint = Point(self, self.axis.matrix, 0.75, 1.25, 0.25)
        spherePoint = Point(self, self.axis.matrix, 0.75, 1.25,-0.25)
        self.sphere = Sphere(self, self.axis.matrix, spherePoint, centerPoint, 0.25, penFill, penBorder, self.light)

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
        brush.setColor( QColor("#70CBB1"))

        self.qp.setBrush(brush)
        self.qp.drawRect(-1, -1, w+1, h+1)
    
    def drawRects(self) -> None:
        qArray = []
        if (self.cursorOnX):
            self.rectangleX.draw()
            qArray.append(self.rectangleX.lines[1].coords[0])
            qArray.append(self.rectangleX.lines[3].coords[0])
            qArray.append(self.axis.ox)
            self.drawHelper(self.rectangleX, qArray, 0)
                
        if (self.cursorOnY):
            self.rectangleY.draw()
            qArray.append(self.rectangleY.lines[1].coords[0])
            qArray.append(self.rectangleY.lines[3].coords[0])
            qArray.append(self.axis.oy)
            self.drawHelper(self.rectangleY, qArray, 1)
        if (self.cursorOnZ):
            self.rectangleZ.draw()
            qArray.append(self.rectangleZ.lines[1].coords[0])
            qArray.append(self.rectangleZ.lines[3].coords[0])
            qArray.append(self.axis.oz)
            self.drawHelper(self.rectangleZ, qArray, 2)

    def drawHelper(self, rect: Polygon, qArray: List, mode: int) -> None:
        sel = self.selected_point
        p = rect.lines[0].coords[0]
        q = qArray[2]
        f = np.array([0, 0, 0, 1])
        self.drawHelpLines(p, q, f, mode)
        if (sel != None):
            lines = []
            pointsAxis = []
            pointsAxis.append([ sel.x() if mode != 0 else rect.lines[0].coords[0][0],
                                sel.y() if mode != 1 else rect.lines[0].coords[0][1],
                                sel.z() if mode != 2 else rect.lines[0].coords[0][2],
                                sel.w() ])

            pointsAxis.append([ rect.lines[0].coords[0][0] if mode in [0, 1] else sel.x(),
                                rect.lines[0].coords[0][1] if mode in [1, 2] else sel.y(),
                                rect.lines[0].coords[0][2] if mode in [0, 2] else sel.z(),
                                sel.w() ])

            pointsAxis.append([ rect.lines[0].coords[0][0] if mode in [0, 2] else sel.x(),
                                rect.lines[0].coords[0][1] if mode in [0, 1] else sel.y(),
                                rect.lines[0].coords[0][2] if mode in [1, 2] else sel.z(),
                                sel.w() ])

            A = sel.coords
            B = pointsAxis[0]
            C = pointsAxis[1]
            D = pointsAxis[2]

            lines.append(Line(self, self.axis.matrix, A, B, self.helpPen))
            lines.append(Line(self, self.axis.matrix, B, C, self.helpPen))
            lines.append(Line(self, self.axis.matrix, B, D, self.helpPen))
            for l in lines:
                l.draw()

            for p in [pointsAxis[1], pointsAxis[2]]:
                for i in range (2):
                    trueMode = 0
                    if (mode == 0 and i == 0) or (mode == 2 and i == 1):
                        trueMode = 1
                    elif (mode == 1 and i == 0) or (mode == 0 and i == 1):
                        trueMode = 2
                    q = qArray[i]

                    self.drawHelpLines(p, q, rect.lines[0].coords[0], trueMode)

    def drawHelpLines(self, p: List, q: List, f: List, mode: int) -> None:
        '''
        Рисование вспомогательных линий (для ощущения объёма)
        '''
        if (p[mode] > q[mode]):
            line = Line(self, self.axis.matrix, q, p, self.helpPen)
            line.draw()
        elif (p[mode] < f[mode]):
            line = Line(self, self.axis.matrix, f, p, self.helpPen)
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
        self.pyramid.draw()
        self.cube.draw()
        sphereUpdate = False
        if ((self.selected_point == self.sphere.controlDot
             or self.selected_point == self.light) and not self.lockRects
             or self.isPressed):
             sphereUpdate = True
             self.isPressed = False
        self.sphere.draw(sphereUpdate)
        self.light.draw()
        # self.winLines.draw()

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
        posCross = [cross[0], cross[1], cross[2], 1]
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
            pass
            # if key.key() in (Qt.Key_Backspace, Qt.Key_Delete) and self.selected_point:
            #     self.points.remove(self.selected_point)
            #     self.selected_point = None
            #     self.update()
            # if(key.key() == Qt.Key_Escape):
            #     self.points.clear()
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



            

            

        
    


