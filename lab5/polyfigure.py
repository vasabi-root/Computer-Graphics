from figure import Figure
from polygon import Polygon 
from typing import List
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPen
import numpy as np

from point import Point

class PolyFigure(Figure):
    '''
    Класс фигур из полигонов 
    '''
    polyList: List[Polygon] # список полигонов

    def __init__(self, widget: QWidget, matrix: np.array, controlDot: Point, polyPoints: List, penFill: QPen, penBorder: QPen) -> None:
        super().__init__(widget, matrix, controlDot, penFill, penBorder)
        self.setPolyList(polyPoints)

    def setPolyList(self, polyPoints: List) -> None:
        self.polyList = []
        self.diffCoords = []
        for pointsList in polyPoints:
            self.polyList.append(Polygon(self.widget, self.matrix, pointsList, self.penFill, self.penBorder, True))
            self.diffCoords.append([ self.polyList[-1].getCoords()[0] - self.controlDot.x(),
                                     self.polyList[-1].getCoords()[1] - self.controlDot.y(),
                                     self.polyList[-1].getCoords()[2] - self.controlDot.z() ])

    def setPos(self) -> None:
        for i, poly in enumerate(self.polyList):
            poly.setPos(self.controlDot.x() + self.diffCoords[i][0], 
                        self.controlDot.y() + self.diffCoords[i][1], 
                        self.controlDot.z() + self.diffCoords[i][2])

    def draw(self) -> None:
        for poly in self.polyList:
            poly.draw()
        self.controlDot.draw()