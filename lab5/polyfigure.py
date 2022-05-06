from itertools import islice
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

    def __init__(self, widget: QWidget, matrix: np.array, controlDot: Point, polyPoints: List, penFill: QPen, penBorder: QPen, light: Point, isLight: bool = False) -> None:
        super().__init__(widget, matrix, controlDot, penFill, penBorder, light, isLight)
        self.setPolyList(polyPoints)

    def setPolyList(self, polyPoints: List) -> None:
        self.polyList = []
        self.diffCoords = []
        for pointsList in polyPoints:
            self.polyList.append(Polygon(self.widget, self.matrix, pointsList, self.penFill, self.penBorder, self.light, isLight=self.isLight))
            self.diffCoords.append([ self.polyList[-1].getCoords()[0] - self.controlDot.x(),
                                     self.polyList[-1].getCoords()[1] - self.controlDot.y(),
                                     self.polyList[-1].getCoords()[2] - self.controlDot.z() ])

    def setPos(self) -> None:
        for i, poly in enumerate(self.polyList):
            poly.setPos(self.controlDot.x() + self.diffCoords[i][0], 
                        self.controlDot.y() + self.diffCoords[i][1], 
                        self.controlDot.z() + self.diffCoords[i][2])

    def draw(self) -> None:
        # for poly in self.polyList:
        #     poly.draw()
        zBuff = []
        for poly in self.polyList:
            polyVerts = []
            for l in poly.lines:
                z = np.dot(self.matrix, l.coords[0])[2]
                i = 0 
                for dot in polyVerts: # сортировка вершин полигона по возрастанию Z
                    if (z < dot):
                        break
                    i += 1
                polyVerts.insert(i, z)
            i = 0
            flag = True
            while (i < len(zBuff) and flag):
                item = zBuff[i][1]
                length = min(len(item), len(polyVerts))
                
                for j in range(length):
                    if (polyVerts[j]+0.001 < item[j] < polyVerts[j]-0.001): # buff[j] == item[j]
                        continue
                    elif (polyVerts[j] > item[j]):
                        flag = False
                        i -= 1
                        break
                i += 1
            # print (i)
            zBuff.insert(i, [poly, polyVerts])

        for item in zBuff:
            item[0].draw()
        self.controlDot.draw()