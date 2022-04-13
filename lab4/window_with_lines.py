from typing import List
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt

from shared import Colors, RotationMatrices, normalize

from point import Point
from line import Line
import numpy as np

from axis import Axis


class WindowLines:
    '''
    Класс поверхности Безье
    '''

    points: List[Point]

    def __init__(self, widget: QWidget, axis : Axis) -> None:

        self.axis = axis

        self.points: List[Point] = []  # точки-концы линий относительно осей
        self.screenP: List[Point] = [] # точки-концы линий относительно экрана
        self.lines: List[Line] = []    # линии *только на экране

        self.outerPen = QPen(Colors.YELLOW_COLOR, 2, Qt.SolidLine) # Кисть для линий вне экрана
        self.innerPen = QPen(Colors.BLUE_COLOR, 2, Qt.SolidLine) # Кисть для линий внутри экрана
        
    def moveToCentre(self) -> None:
        mX = min([p.x() for p in self.points])
        mY = min([p.y() for p in self.points])

        dX = 0.1 - mX
        dY = 0.1 - mY

        for p in self.points:
            p.setCoords(p.x()+dX, p.y()+dY, p.z(), p.w())

    def add_point(self, point: Point) -> None:
        self.points.append(point)

    def remove_point(self, point: Point) -> None:
        i = self.points.index(point)
        if (i % 2 == 1):
            self.points.remove(self.points[i-1])
        elif (i+1 < len(self.points)):
            self.points.remove(self.points[i+1])
        self.points.remove(point)


    def draw_points(self) -> None:
        for q in self.screenP:
            q.draw()

    def draw_lines(self) -> None:
        for l in self.lines:
            l.draw()


    def draw(self) -> None:
        self.toScreen()
        self.draw_lines()
        self.draw_points()

    def toScreen(self) -> None: 
        '''
        Перевод точек к координатам экрана, формирование линий
        '''
        self.screenP = []
        self.lines = []
        for i in range (len(self.points)):
            p = self.points[i]
            q = np.dot(self.axis.matrix, p.coords)
            self.screenP.append(Point(self.axis.widget, q[0], q[1], q[2], q[3], is_selected=p.is_selected, is_curve=p.is_curve))
            if (i % 2 == 1):
                self.lines.append(Line(self.axis.widget, self.screenP[i-1].x(), self.screenP[i-1].y(), self.screenP[i].x(), self.screenP[i].y(), self.outerPen))
    
    def rotate_x(self, alpha: float) -> None:
        for p in self.points:
            p.coords = np.dot(RotationMatrices.rotate_x(alpha), p.coords)


    def rotate_y(self, alpha: float) -> None:
        for p in self.points:
            p.coords = np.dot(RotationMatrices.rotate_y(alpha), p.coords)

    def rotate_z(self, alpha: float) -> None:
        for p in self.points:
            p.coords = np.dot(RotationMatrices.rotate_z(alpha), p.coords)

