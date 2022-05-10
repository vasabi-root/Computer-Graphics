from abc import abstractmethod
from typing import List
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPen
import numpy as np

from shared import Config
from point import Point

class Figure:
    '''
    Базовый класс фигур из полигонов 
    При наследовании в него обязательно надо добавить объекты, определяющие саму фигуру
    (список полигонов / список уравнений)
    '''
    instances = []
    widget: QWidget
    matrix: np.array

    controlDot: Point       # управляющая точка (для перетаскивания фигуры)

    penFill: QPen           # цвет заливки
    penBorder: QPen         # цвет границы
    light: Point            # источник света

    isLight: bool

    diffCoords: List        # расстояния от контрольной точки до вершин фигуры (для перемещения фигуры)

    def __init__(self, widget: QWidget, matrix: np.array, controlDot: Point, penFill: QPen, penBorder: QPen, light: Point, isLight: bool = False) -> None:
        self.__class__.instances.append(self) # учёт всех объектов

        self.widget = widget
        self.matrix = matrix

        self.penFill = penFill
        self.penBorder = penBorder
        self.light = light

        self.isLight = isLight

        self.controlDot = controlDot

    @abstractmethod
    def setPos(self) -> None:
        """
        Метод синхронизации фигуры с управляющей точкой
        тут надо обновить все координаты фигуры относительно self.controlDot и self.diffCoords
        """
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

    @staticmethod
    def checkBelong(p: Point):
        """
        Проверка на то, является ли точка управляющей для какой-то фигуры
        """
        for fig in Figure.instances:
            if (p == fig.controlDot):
                return fig
        return None

def moveDecorator(func):
    # self.controlDot.move(x, y, z)
    '''
    Декоратор для Point.move() -- уже не нужен, но я оставил для потомков
    '''
    print (len(Figure.instances))
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        fig = Figure.checkBelong(args[0])
        if fig != None:
            fig.setPos()
    return wrapper


# @moveDecorator
@Point.move.register
def _(p: Point, dx: float, dy: float, dz: float, w: float=1, check: bool = True) -> None:
    p.setCoords(p.coords[0] + dx, p.coords[1] + dy, p.coords[2] + dz, w, check)

    fig = Figure.checkBelong(p)         
    if fig:                   # если точка управляющая
        fig.setPos()          # то синхронизируем движение точки с фигурой



@Point.setCoords.register
def _(p: Point, x: float, y: float, z: float, w: float=1, check: bool = True) -> None:
    '''
    Установка координат в трехмерном пространстве
    '''
    p.incorrect = [x, y, z]
    if check:
        [x, y, z] = Config.checkLimits(x, y, z)
    p.coords = np.array([ x, y, z, w ], dtype=np.float64)

    fig = Figure.checkBelong(p)
    if fig:                  # если точка управляющая
        fig.setPos()         # то синхронизируем движение точки с фигурой
