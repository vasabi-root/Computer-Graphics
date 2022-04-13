from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import enum
import numpy as np


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
    BLACK_A100 = QColor(0, 0, 0, 100)


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
