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

from point import Point
from line import Line
from shared import Colors, Config
from window_with_lines import WindowLines
from rectangle import Rectangle

import mathematics as mat

class Interface(QWidget):
    
    '''
    Главный класс приложения. В нем подключается и реализуется вся логика приложения.
    '''

    rectangleX : Rectangle
    rectangleY : Rectangle
    rectangleZ : Rectangle

    cursorOnX: bool
    cursorOnY: bool
    cursorOnZ: bool

    lockRects: bool
    addPoint: bool
    isAnime: bool
    isWheelMoved: bool

    pos: np.array

    def __init__(self) -> None:
        super().__init__()
        
        self.qp = QPainter()                # Просто специальная рисовалка
        self.axis: Axis = Axis(self)
        self.winLines : WindowLines = WindowLines(self, self.axis)
        self.initRects()

        self.selected_point: Point = None

        self.helpPen = QPen(Colors.RED_COLOR, 1, Qt.DashLine) # Кисть для вспомогательных линий
        self.helpPen.setStyle(Qt.CustomDashLine)
        self.helpPen.setDashPattern([4, 3])

        self.pen = QPen(Colors.RED_COLOR, 2, Qt.SolidLine)
        
        self.keys = {81: False, 65: False, 87: False, 83: False, 69: False, 68: False,
                     73: False, 75: False, 79: False, 76: False, 80: False, 59: False}
        self.isWheelMoved = False


    def initRects(self) -> None:
        '''
        Инициализация прямоугольников, лежащим между осями
        '''
        pen = QPen(Colors.RED_COLOR, 2)

        pX = [Point(self.axis.widget, 0, 0, 0),
              Point(self.axis.widget, 0, 1, 0),
              Point(self.axis.widget, 0, 1, 1),
              Point(self.axis.widget, 0, 0, 1)]
        self.rectangleX = Rectangle(self.axis, pX, pen)
        self.cursorOnX = False

        pY = [Point(self.axis.widget, 0, 0, 0),
              Point(self.axis.widget, 0, 0, 1),
              Point(self.axis.widget, 1, 0, 1),
              Point(self.axis.widget, 1, 0, 0)]
        self.rectangleY = Rectangle(self.axis, pY, pen)
        self.cursorOnY = False

        pZ = [Point(self.axis.widget, 0, 0, 0),
              Point(self.axis.widget, 1, 0, 0),
              Point(self.axis.widget, 1, 1, 0),
              Point(self.axis.widget, 0, 1, 0)]
        self.rectangleZ = Rectangle(self.axis, pZ, pen)
        self.cursorOnZ = False

        self.lockRects = True
        self.addPoint = False
        self.isAnime = False

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
            qArray.append(self.rectangleX.points[1].coords)
            qArray.append(self.rectangleX.points[3].coords)
            qArray.append(self.axis.ox.coords)
            self.drawHelper(self.rectangleX, qArray, 0)
                
        if (self.cursorOnY):
            self.rectangleY.draw()
            qArray.append(self.rectangleY.points[1].coords)
            qArray.append(self.rectangleY.points[3].coords)
            qArray.append(self.axis.oy.coords)
            self.drawHelper(self.rectangleY, qArray, 1)
        if (self.cursorOnZ):
            self.rectangleZ.draw()
            qArray.append(self.rectangleZ.points[1].coords)
            qArray.append(self.rectangleZ.points[3].coords)
            qArray.append(self.axis.oz.coords)
            self.drawHelper(self.rectangleZ, qArray, 2)

    def drawHelper(self, rect: Rectangle, qArray: List, mode: int) -> None:
        sel = self.selected_point
        p = rect.points[0].coords
        q = qArray[2]
        f = np.array([0, 0, 0, 1])
        self.drawHelpLines(p, q, f, mode)
        if (sel != None):
            lines = []
            pointsAxis = []
            pointsAxis.append([ sel.x() if mode != 0 else rect.points[0].x(),
                                sel.y() if mode != 1 else rect.points[0].y(),
                                sel.z() if mode != 2 else rect.points[0].z(),
                                sel.w() ])

            pointsAxis.append([ rect.points[0].x() if mode in [0, 1] else sel.x(),
                                rect.points[0].y() if mode in [1, 2] else sel.y(),
                                rect.points[0].z() if mode in [0, 2] else sel.z(),
                                sel.w() ])

            pointsAxis.append([ rect.points[0].x() if mode in [0, 2] else sel.x(),
                                rect.points[0].y() if mode in [0, 1] else sel.y(),
                                rect.points[0].z() if mode in [1, 2] else sel.z(),
                                sel.w() ])

            A = np.dot(self.axis.matrix, sel.coords)
            B = np.dot(self.axis.matrix, pointsAxis[0])
            C = np.dot(self.axis.matrix, pointsAxis[1])
            D = np.dot(self.axis.matrix, pointsAxis[2])
            lines.append(Line(self, A[0], A[1], B[0], B[1], self.helpPen))
            lines.append(Line(self, B[0], B[1], C[0], C[1], self.helpPen))
            lines.append(Line(self, B[0], B[1], D[0], D[1], self.helpPen))
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

                    self.drawHelpLines(p, q, rect.points[0].coords, trueMode)

    def drawHelpLines(self, p: List, q: List, f: List, mode: int) -> None:
        '''
        Рисование вспомогательных линий (для ощущения объёма)
        '''
        if (p[mode] > q[mode]):
            A = np.dot(self.axis.matrix, q)
            B = np.dot(self.axis.matrix, p)
            line = Line(self, A[0], A[1], B[0], B[1], self.helpPen)
            line.draw()
        elif (p[mode] < f[mode]):
            A = np.dot(self.axis.matrix, f)
            B = np.dot(self.axis.matrix, p)
            line = Line(self, A[0], A[1], B[0], B[1], self.helpPen)
            line.draw()
    
    def draw(self) -> None:
        '''
        Рисование всего на экран
        '''
        self.clearScreen()
        self.axis.draw()
        self.drawRects()
        self.winLines.draw()
        
    def checkPointIntersectionEvent(self, pos: QPoint) -> Point:
        '''
        Поиск точки, на которую было произведено нажатие
        '''
        pnt = list(filter(lambda p: p.checkIntersection(pos, self.axis.matrix), self.winLines.points))
        return pnt[0] if pnt else False

    def searchCursorRectCross(self, pos: QPoint, rect: Rectangle) -> np.array:
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
    def mouseHelper(self, rect: Rectangle, mouse: QMouseEvent, mode: int) -> None:
        if (self.lockRects and not self.addPoint):
            self.pos = self.searchCursorRectCross(mouse.pos(), rect)
            self.lockRects = False
            if (self.selected_point != None):
                d = 0
                d = self.selected_point.x() if mode == 0 else d
                d = self.selected_point.y() if mode == 1 else d
                d = self.selected_point.z() if mode == 2 else d
                rect.animeMove(d, mode, False)
            else:
                axisPos = self.searchCursorRectCross(mouse.pos(), rect)
                self.pos = axisPos
                self.winLines.add_point(Point(self, axisPos[0], axisPos[1], axisPos[2], axisPos[3], check=True))
                self.selectPoint(self.winLines.points[-1])
        elif (not self.addPoint):
#             self.lockRects = True
            self.addPoint = True
            axisPos = self.searchCursorRectCross(mouse.pos(), rect)
            self.pos = axisPos
            if (self.selected_point == None):
                self.winLines.add_point(Point(self, axisPos[0], axisPos[1], axisPos[2], axisPos[3], check=True))
                self.selectPoint(self.winLines.points[-1])
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
        
    def createPoint(self, mouse: QMouseEvent) -> None:
        '''
        Создание новой точки
        '''
        self.points.append(Point(self, mouse.x(), mouse.y()))

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

        if key.key() == 73 or self.keys[73]:
            self.winLines.rotate_x(alpha)
        elif key.key() == 75 or self.keys[75]:
            self.winLines.rotate_x(-alpha)
        if key.key() == 79 or self.keys[79]:
            self.winLines.rotate_y(alpha)
        elif key.key() == 76 or self.keys[76]:
            self.winLines.rotate_y(-alpha)
        if key.key() == 80 or self.keys[80]:
            self.winLines.rotate_z(alpha)
        elif key.key() == 59 or self.keys[59]:
            self.winLines.rotate_z(-alpha)

        if (not self.addPoint and self.lockRects):
            if key.key() in (Qt.Key_Backspace, Qt.Key_Delete) and self.selected_point:
                self.winLines.remove_point(self.selected_point)
                self.selected_point = None
                self.update()
            if(key.key() == Qt.Key_Escape):
                self.winLines.points.clear()
        elif (key.key() == Qt.Key_Enter-1):
            self.selectPoint(None)
            self.initRects()

        self.keys[key.key()] = True
        self.update()

    def moveCursor(self, pos: QPoint) -> None:
        '''
        обработка движения курсора
        '''
        if (self.lockRects and not self.addPoint): # 
            self.cursorOnX = False
            self.cursorOnY = False
            self.cursorOnZ = False
            if (not self.checkPointIntersectionEvent(pos)):
                posList = [pos.x(), pos.y()]
                recX_w = inf
                recY_w = inf
                recZ_w = inf
                
                if (mat.dot_in_poly(posList, self.rectangleX.get_screen_lines()) == 1):
                    recX_w = self.rectangleX.get_screen_points()[2][2]

                if (mat.dot_in_poly(posList, self.rectangleY.get_screen_lines()) == 1):
                    recY_w = self.rectangleY.get_screen_points()[2][2]

                if (mat.dot_in_poly(posList, self.rectangleZ.get_screen_lines()) == 1):
                    recZ_w = self.rectangleZ.get_screen_points()[2][2]

                if (recX_w < recY_w and recX_w < recZ_w):
                    self.cursorOnX = True
                elif (recY_w < recX_w and recY_w < recZ_w):
                    self.cursorOnY = True
                elif (recZ_w < recX_w and recZ_w < recY_w):
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

    def moveHelper(self, rect1: Rectangle, rect2: Rectangle, pos: QPoint, mode: int):
        if self.addPoint:
            curPos = self.searchCursorRectCross(pos, rect1)
            self.selected_point.setCoords(curPos[0], curPos[1], curPos[2], curPos[3], check=True)
            self.pos = curPos

    def wheelEvent(self, wheel: QWheelEvent) -> None:
        p = wheel.angleDelta()
        d = p.y()/120 / 3 

        if (not self.isWheelMoved and not self.lockRects):
            if (self.cursorOnX and not self.rectangleX.isAnime):
                self.rectangleX.animeMove(d, 0)
            elif (self.cursorOnY and not self.rectangleY.isAnime):
                self.rectangleY.animeMove(d, 1)
            elif (self.cursorOnZ and not self.rectangleZ.isAnime):
                self.rectangleZ.animeMove(d, 2)
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



            

            

        
    


