from typing import List
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import numpy as np

from shared import Config, Colors, normalize, RotationMatrices
from point import Point
from line import Line

class Axis:
    '''
    Класс осей координат
    '''
    matrix: np.ndarray      # матрица осей (для математики)

    center: np.array           # центральная точка

    ox: np.array               # крайняя точка оси OX
    oy: np.array               # крайняя точка оси OY
    oz: np.array               # крайняя точка оси OZ

    lines: List[Line]          # линии, образующие оси

    pen: QPen               # карандаш рисования
    widget: QWidget         # ссылка на класс Interface

    x_angle: float          # текущий поворот оси OX
    y_angle: float          # текущий поворот оси OY
    z_angle: float          # текущий поворот оси OZ

    def __init__(self, widget: QWidget) -> None:
        super().__init__()

        self.setWidget(widget)
        self.initPen()
        self.setAngles(0.0, 0.0, 0.0)
        self.initMatrix()
        self.initAxisCoords()
        self.initAxisLines()

    def initMatrix( self,
                    center_x = Config.WINDOW_WIDTH // 2, 
                    center_y = Config.WINDOW_HEIGHT // 2, 
                    axis_line_length = Config.AXIS_LINE_LENGTH) -> None:
        '''
        Инициализация матрицы осей
        '''
        self.matrix = None
        # self.matrix = [ [1, 0, 0, 0],
        #                 [0, 1, 0, 0],
        #                 [0, 0, 1, 0],
        #                 [0, 0, 0.5/Config.AXIS_LINE_LENGTH, 1] ]
        self.setCenterCoords(center_x, center_y)
        self.setScale(axis_line_length)
        # self.rotate_x(120.0, is_init=True)
        # self.rotate_z(230.0, is_init=True)
        self.rotate_z(90.0, is_init=True)
        self.rotate_x(180.0, is_init=True)
        self.rotate_x(self.x_angle, is_init=True)
        self.rotate_y(self.y_angle, is_init=True)
        self.rotate_z(self.z_angle, is_init=True)

    def setMatrix(self, matrix: np.array) -> None:
        for i in range(0, len(self.matrix)):
            self.matrix[i] = matrix[i]

    def setCenterCoords(self, x: float, y: float) -> None:
        '''
        Установка центра осей
        '''
        if self.matrix is not None:
            self.matrix[0][3] = x
            self.matrix[1][3] = y
        else:
            self.matrix = np.dot(
                self.matrix if self.matrix is not None else np.eye(4, dtype=np.float64),
                RotationMatrices.get_translation(x, y, 0),
            )

    def setScale(self, axis_line_length: float) -> None:
        '''
        Установка длины осей
        '''
        self.setMatrix(
            np.dot(
            self.matrix if self.matrix is not None else np.eye(4, dtype=np.float64),
            RotationMatrices.get_scale(*([axis_line_length] * 3)))
        )

    def initAxisCoords(self) -> None:
        '''
        Инициализация координат осей
        '''
        self.center = np.array([0, 0, 0, 1])
        self.ox = np.array([1, 0, 0, 1])
        self.oy = np.array([0, 1, 0, 1])
        self.oz = np.array([0, 0, 1, 1])

    def initPen(self) -> None:
        self.pen = QPen(Colors.BLACK_COLOR, 1, Qt.SolidLine)

    def setAngles(self, x_angle: float, y_angle: float, z_angle: float) -> None:
        '''
        Установка текущего поворота осей
        '''
        self.x_angle = x_angle
        self.y_angle = y_angle
        self.z_angle = z_angle

    def setWidget(self, widget: QWidget) -> None:
        self.widget = widget

    def setAxisPoints(self) -> List[Point]:
        '''
        Получение координат точек осей на экране
        '''

        return [
            np.dot(self.matrix, self.center),
            np.dot(self.matrix, self.ox),
            np.dot(self.matrix, self.oy),
            np.dot(self.matrix, self.oz)
        ]
        # return [
        #     Point(self.widget, vectors[i][0], vectors[i][1], vectors[i][2])
        #     for i in range(len(vectors))
        # ]

    def initAxisLines(self) -> None:
        '''
        Получение линий осей
        '''
        # axis_points = self.setAxisPoints()
        # center = axis_points[0]
        self.lines = [ Line(self.widget, self.matrix, self.center, self.ox, self.pen), 
                       Line(self.widget, self.matrix, self.center, self.oy, self.pen), 
                       Line(self.widget, self.matrix, self.center, self.oz, self.pen) ]
        # return [
        #     Line(self.widget, center[0], center[1], axis_points[i], axis_points[i].y(), self.pen)
        #     for i in range(1, len(axis_points))
        # ]

    def drawAxis(self) -> None:
        '''
        Рисование осей
        '''

        for i, line in enumerate(self.lines):
            line.draw()
            qp = QPainter(self.widget)
            qp.setPen(self.pen)
            qp.drawText(int(line.screen[1][0]), int(line.screen[1][1]), chr(ord('X') + i))
            qp.end()

    def rotate_x(self, alpha: float, is_init: bool = False) -> None:
        '''
        Поворот вокруг оси OX
        '''
        # self.matrix = 
        self.setMatrix(np.dot(self.matrix, RotationMatrices.rotate_x(alpha)))
        if not is_init:
            self.x_angle += alpha

    def rotate_y(self, alpha: float, is_init: bool = False) -> None:
        '''
        Поворот вокруг оси OY
        '''
        # self.matrix = 
        self.setMatrix(np.dot(self.matrix, RotationMatrices.rotate_y(alpha)))
        if not is_init:
            self.y_angle += alpha

    def rotate_z(self, alpha: float, is_init: bool = False) -> None:
        '''
        Поворот вокруг оси OZ
        '''
        # self.matrix = 
        self.setMatrix(np.dot(self.matrix, RotationMatrices.rotate_z(alpha)))
        if not is_init:
            self.z_angle += alpha


    def draw(self) -> None:
        '''
        Рисование осей и поверхности Безье
        '''
        self.drawAxis()
