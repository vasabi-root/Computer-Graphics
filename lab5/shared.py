import imp
from typing import List
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import enum
import numpy as np
import mathematics as mat


def normalize(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v, ord=1)
    if norm == 0:
        norm = np.finfo(v.dtype).eps
    return v / norm


class Config:
    '''
    Настройки проекта
    '''
    WINDOW_TOP_PAD = 200
    WINDOW_LEFT_PAD = 300
    WINDOW_WIDTH = 850
    WINDOW_HEIGHT = 540

    R_LEFT_X = 0
    R_LEFT_Y = 0
    R_RIGHT_X = 180
    R_RIGHT_Y = 100

    AXIS_LINE_LENGTH = 200

    MAX_COORD = 2.5

    STEP = 0.05

    @staticmethod
    def checkLimits(x: float, y: float, z: float) -> List:
        # print(x, y, z)
        x = x if x <= Config.MAX_COORD else Config.MAX_COORD
        x = x if x >= -Config.MAX_COORD else -Config.MAX_COORD
        y = y if y <= Config.MAX_COORD else Config.MAX_COORD
        y = y if y >= -Config.MAX_COORD else -Config.MAX_COORD
        z = z if z <= Config.MAX_COORD else Config.MAX_COORD
        z = z if z >= -Config.MAX_COORD else -Config.MAX_COORD
        return [x, y, z]

class Colors:
    '''
    База данных цветов
    '''
    YELLOW_COLOR = QColor("#FFD800")
    BLUE_COLOR = QColor("#0057B8")
    GREEN_COLOR = QColor("#50AB91")
    RED_COLOR = Qt.red
    RED_A120 = QColor(255, 0, 0, 120)
    BLACK_COLOR = Qt.black
    WHITE_COLOR = Qt.white
    BLACK_A100 = QColor(0, 0, 0, 100)
    TRANSPARENT = QColor(0, 0, 0, 0)


class RotationMatrices:
    '''
    Матрицы для скалирования, поворота для соответсвующих осей
    '''
    
    @staticmethod
    def rotate_x(alpha: float) -> np.ndarray:
        '''
        Вращение по OX
        '''
        rad = np.deg2rad(alpha)
        return np.array([
            [1, 0, 0, 0],
            [0, np.cos(rad), -np.sin(rad), 0],
            [0, np.sin(rad), np.cos(rad), 0],
            [0, 0, 0, 1],
        ], dtype=np.float64)

    @staticmethod
    def rotate_y(alpha: float) -> np.ndarray:
        '''
        Вращение по OY
        '''
        rad = np.deg2rad(alpha)
        return np.array([
            [np.cos(rad), 0, np.sin(rad), 0],
            [0, 1, 0, 0],
            [-np.sin(rad), 0, np.cos(rad), 0],
            [0, 0, 0, 1],
        ], dtype=np.float64)

    @staticmethod
    def rotate_z(alpha: float) -> np.ndarray:
        '''
        Вращение по OZ
        '''
        rad = np.deg2rad(alpha)
        return np.array([
            [np.cos(rad), -np.sin(rad), 0, 0],
            [np.sin(rad), np.cos(rad), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ], dtype=np.float64)

    @staticmethod
    def get_translation(dx: float, dy: float, dz: float) -> np.ndarray:
        '''
        Установка смещения
        '''
        return np.array([
            [1, 0, 0, dx],
            [0, 1, 0, dy],
            [0, 0, 1, dz],
            [0, 0, 0, 1],
        ], dtype=np.float64)

    @staticmethod
    def get_scale(sx: float, sy: float, sz: float) -> np.ndarray:
        '''
        Установка размера
        '''
        return np.array([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1],
        ], dtype=np.float64)

class Light:
    '''
    Работа со светом
    '''
    @staticmethod
    def computeLightForDot(light, P: np.array, N: np.array) -> float: 
        i = 1 - light.intensity
        l = light.coords - P
        L = np.array([l[0], l[1], l[2]])
        N_dot_L = L.dot(N)
        if (N_dot_L > 0):
            # print(N_dot_L, self.light.intensity)
            i += light.intensity*N_dot_L / (np.sqrt((N*N).sum())* np.sqrt((L*L).sum()))
        return i

    @staticmethod
    def iteration(xList, yList, painter, borderSize, polygons):
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
                    painter.setPen(minZV[0])
                    for i in range (-borderSize, borderSize+1):
                        for j in range (-borderSize, borderSize+1):
                            painter.drawPoint(x+i, y+j)