from cmath import inf
from itertools import islice
from traceback import print_tb
from figure import Figure
from lab5.shared import Config
from polygon import Polygon 
from typing import List
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPen, QPainter
import numpy as np

from point import Point
import mathematics as mat

class PolyFigure(Figure):
    '''
    Класс фигур из полигонов 
    '''
    polyList: List[Polygon] # список полигонов
    points: List[Point]     # список вершин


    def __init__(self, widget: QWidget, matrix: np.array, controlDot: Point, polyPoints: List, penFill: QPen, penBorder: QPen, light: Point, isLight: bool = False, isBorders=True) -> None:
        super().__init__(widget, matrix, controlDot, penFill, penBorder, light, isLight)
        Figure.instances.append(self) # учёт всех объектов
        self.isBorders = isBorders
        self.setPolyList(polyPoints)
        
    def initPainter(self, pen: QPen) -> None:
        '''
        Инициализация рисовалки
        '''
        self.painter = QPainter(self.widget)
        self.painter.setPen(pen)
        self.painter.setRenderHints(QPainter.Antialiasing)

    def setPolyList(self, polyPoints: List[List[Point]]) -> None:
        self.polyList = []
        self.points = []
        self.diffCoords = []
        for pointsList in polyPoints:
            self.polyList.append(Polygon(self.widget, pointsList, self.penFill, self.penBorder, self.light, isLines=self.isBorders, isLight=self.isLight))
            for p in pointsList:
                try:
                    self.points.index(p)
                except ValueError:
                    self.points.append(p)
                    self.diffCoords.append(p.coords - self.controlDot.coords)

    def setIsBorders(self, isBorders):
        self.isBorders = isBorders
        for poly in self.polyList:
            poly.isLines = isBorders

    def setPos(self) -> None:
        for i, p in enumerate(self.points):
            p.setCoords(self.controlDot.x() + self.diffCoords[i][0], 
                        self.controlDot.y() + self.diffCoords[i][1], 
                        self.controlDot.z() + self.diffCoords[i][2], check=False)
        for poly in self.polyList:
            poly.setFillPos(False)
    
    def getScreenPolyes(self) -> List[Polygon]:
        for p in self.points:
            p.initScreen()   
        for poly in self.polyList:
            poly.controlDot.initScreen() 
        self.polyList.sort(key=lambda x:x.controlDot.screen[2])
        circle = Jarvis(self.points)[1]
        # circle.sort(key=lambda x:x.screen[2])
        buff = []
        for poly in self.polyList:
            buff.append(poly)
            lineI = 0
            while lineI < len(circle):
                line = circle[lineI]
                for i, p in enumerate(poly.points):
                    if (line[0] == p and line[1] == poly.points[(i+1) % len(poly.points)] or
                        line[1] == p and line[0] == poly.points[(i+1) % len(poly.points)]):
                        circle.pop(lineI)
                        lineI -= 1
                        continue
                    
                lineI += 1
            if len(circle) == 0:
                break
        return buff

    def makeShadow(self, points: List[Point]) -> List[Polygon]:
        c = [0, 0, 0]
        x = [1, 0, 0]
        y = [0, 1, 0]
        z = [0, 0, 1]
        polyX = mat.eq_poly(y, c, z)
        polyY = mat.eq_poly(x, c, z)
        polyZ = mat.eq_poly(x, c, y)
        polygons = [polyX, polyY, polyZ]
        points = [[], [], []]
        for p in points:
            lineL = [ [self.light.coords[0], self.light.coords[1], self.light.coords[2]], [p.coords[0], p.coords[1], p.coords[2]] ]
            line = mat.parametr_line(lineL)
            crosses = []
            for poly in polygons:
                c = mat.line_poly_cross(line, poly)
                if  (c != None and c[1] >= 0):
                    crosses.append([c[0], poly])
            for item in crosses:
                x = item[0][0]
                y = item[0][1]
                z = item[0][2]
                if ( (x > 0 or equal(x, 0)) and (y > 0 or equal(y, 0)) and (z > 0 or equal(z, 0)) ):
                    if item[1] == polyX:
                        points[0].append(item[0])
                    elif item[1] == polyY:
                        points[1].append(item[0])
                    elif item[1] == polyZ:
                        points[2].append(item[0])

    def draw(self) -> None:
        for p in self.points:
            p.initScreen()   
        for poly in self.polyList:
            poly.controlDot.initScreen() 
        self.polyList.sort(key=lambda x:x.controlDot.screen[2], reverse=True)

        buff = self.getScreenPolyes()
        for poly in buff: # self.polyList:
            poly.draw()
        self.controlDot.draw()

    @staticmethod
    def ifCrossFigures():
        borderPoints = []
        for fig in PolyFigure.instances:
            if fig.__class__.__name__ == PolyFigure.__name__:
                x1 = min(p.coords[0] for p in fig.points)
                y1 = min(p.coords[1] for p in fig.points)
                z1 = min(p.coords[2] for p in fig.points)

                x2 = max(p.coords[0] for p in fig.points)
                y2 = max(p.coords[1] for p in fig.points)
                z2 = max(p.coords[2] for p in fig.points)

                borderPoints.append([[x1, y1, z1], [x2, y2, z2]])
        # print(borderPoints)
        for i in range(len(borderPoints)):
            A = borderPoints[i]
            for j in range(i+1, len(borderPoints)):
                B = borderPoints[j]
                if (A[1][0] >= B[0][0] and B[1][0] >= A[0][0] and A[1][1] >= B[0][1] and B[1][1] >= A[0][1] and
                    A[1][0] >= B[0][0] and B[1][0] >= A[0][0] and A[1][2] >= B[0][2] and B[1][2] >= A[0][2] and
                    A[1][1] >= B[0][1] and B[1][1] >= A[0][1] and A[1][2] >= B[0][2] and B[1][2] >= A[0][2]):
                    return True
        return False

def equal(a, b) -> bool:
    return a-0.001 < b < a+0.001

def checkIfDrawed(points: List[Point]) -> bool:
    for p in points:
        if not p.is_drawed:
            return False
    return True

def rotate(A: Point,B: Point,C: Point):
    return (B.screen[0]-A.screen[0])*(C.screen[1]-B.screen[1])-(B.screen[1]-A.screen[1])*(C.screen[0]-B.screen[0])

def Graham(A: List[Point]) -> List[Point]:
    n = len(A) # число точек
    P = list(range(n)) # список номеров точек
    L = []
    for i in range(1,n):
        if A[P[i]].screen[0]<A[P[0]].screen[0]: # если P[i]-ая точка лежит левее P[0]-ой точки
            P[i], P[0] = P[0], P[i] # меняем местами номера этих точек 
    for i in range(2,n): # сортировка вставкой
        j = i
        while j>1 and (rotate(A[P[0]],A[P[j-1]],A[P[j]])<0): 
            P[j], P[j-1] = P[j-1], P[j]
            j -= 1
    S = [P[0],P[1]] # создаем стек
    L.append([ A[S[-1]], A[S[-2]] ])
    for i in range(2,n):
        while rotate(A[S[-2]],A[S[-1]],A[P[i]])<0:
            S.pop(-1) # pop(S)
        S.append(P[i]) # push(S,P[i])
        L.append([ A[S[-1]], A[S[-2]] ])
    return [A[i] for i in S]

def Jarvis(A: List[Point]) -> List[List[Point]]:
    n = len(A)
    P = list(range(n))
    L = []
    for i in range(1,n):
        if A[P[i]].screen[0]<A[P[0]].screen[0]: 
            P[i], P[0] = P[0], P[i]  
    H = [P[0]]
    P.pop(0)
    P.append(H[0])
    while True:
        right = 0
        for i in range(1,len(P)):
            if rotate(A[H[-1]],A[P[right]],A[P[i]])<0:
                right = i
        if P[right]==H[0]: 
            break
        else:
            H.append(P[right])
            L.append([ A[H[-2]], A[H[-1]] ])
            P.pop(right)
    L.append([ A[H[-1]], A[H[0]] ])
    return [[A[i] for i in H], L]