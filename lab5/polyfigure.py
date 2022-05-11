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


    def __init__(self, widget: QWidget, matrix: np.array, controlDot: Point, polyPoints: List, penFill: QPen, penBorder: QPen, light: Point, isLight: bool = False) -> None:
        super().__init__(widget, matrix, controlDot, penFill, penBorder, light, isLight)
        Figure.instances.append(self) # учёт всех объектов
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
            self.polyList.append(Polygon(self.widget, pointsList, self.penFill, self.penBorder, self.light, isLight=self.isLight))
            for p in pointsList:
                try:
                    self.points.index(p)
                except ValueError:
                    self.points.append(p)
                    self.diffCoords.append(p.coords - self.controlDot.coords)
                

    def setPos(self) -> None:
        for i, p in enumerate(self.points):
            # poly.setPos(self.controlDot.x() + self.diffCoords[i][0], 
            #             self.controlDot.y() + self.diffCoords[i][1], 
            #             self.controlDot.z() + self.diffCoords[i][2])
            p.setCoords(self.controlDot.x() + self.diffCoords[i][0], 
                        self.controlDot.y() + self.diffCoords[i][1], 
                        self.controlDot.z() + self.diffCoords[i][2])
        for poly in self.polyList:
            poly.setFillPos()
    
    def getScreenPolyes(self) -> List[Polygon]:
        for p in self.points:
            p.initScreen()   
        for poly in self.polyList:
            poly.controlDot.initScreen() 
        self.polyList.sort(key=lambda x:x.controlDot.screen[2])
        circle = Jarvis(self.points)
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

    def draw(self) -> None:
        buff = self.getScreenPolyes()
        for poly in buff:
            poly.draw()
            # if checkPoly(poly, circle, maxZ):
            #     buffer.append(poly)
        # self.painter.end()
        # for poly in buffer:
        #     poly.draw()
        

        self.controlDot.draw()

    @staticmethod
    def ifCrossFigures() -> bool:
        borderPoints = []
        for fig in PolyFigure.instances:
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
                # print([A[1][0], B[0][0]], [B[1][0], A[0][0]], [A[1][1], B[0][1]], [B[1][1] , A[0][1]])
                # print(A[1][0] >= B[0][0] and B[1][0] >= A[0][0] and A[1][2] >= B[0][2] and B[1][2] >= A[0][2])
                # print(A[1][1] >= B[0][1] and B[1][1] >= A[0][1] and A[1][2] >= B[0][2] and B[1][2] >= A[0][2])
                if (A[1][0] >= B[0][0] and B[1][0] >= A[0][0] and A[1][1] >= B[0][1] and B[1][1] >= A[0][1] and
                    A[1][0] >= B[0][0] and B[1][0] >= A[0][0] and A[1][2] >= B[0][2] and B[1][2] >= A[0][2] and
                    A[1][1] >= B[0][1] and B[1][1] >= A[0][1] and A[1][2] >= B[0][2] and B[1][2] >= A[0][2]):
                    return True
        # return [False, [ [min(p[0][0] for p in borderPoints), min(p[0][1] for p in borderPoints), min(p[0][2] for p in borderPoints)],
        #                  [max(p[1][0] for p in borderPoints), max(p[1][1] for p in borderPoints), max(p[1][2] for p in borderPoints)] ]]
        return False

def equal(a, b) -> bool:
    return a-0.001 < b < a+0.001

def checkPoly(poly: Polygon, points: List[Point], maxZ) -> bool:
    borderPoints = []
    for p in poly.points:
        if not equal(p.screen[2], maxZ) and p.screen[2] > maxZ:
            return False
        else:
            try:
                points.index(p)
                borderPoints.append(p)
            except ValueError:
                pass
    maxBorderZ = max(p.screen[2] for p in borderPoints)
    for p in poly.points:
        if not equal(p.screen[2], maxBorderZ) and p.screen[2] > maxBorderZ:
            return False
    return True


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
    # start point
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
    # for l in L:
    #     print(l[0].name, l[1].name)
    # print()
    # return [A[i] for i in H]
    return L




#  polyList = []
#             for poly in minV.polygons:
#                 polyVerts = []

#                 for p in poly.points:
#                     z = p.screen[2]
#                     i = 0
#                     for dot in polyVerts:
#                         if (z < dot):
#                             break
#                         i += 1

#                     polyVerts.insert(i, z)
#                 flag = True

#                 i = 0
#                 flag = True
#                 while (i < len(polyList) and flag):
#                     item = polyList[i][1]
#                     length = min(len(item), len(polyVerts))
                    
#                     for j in range(length):
#                         if (polyVerts[j]+0.001 < item[j] < polyVerts[j]-0.001): # buff[j] == item[j]
#                             continue
#                         elif (polyVerts[j] > item[j]):
#                             flag = False
#                             i -= 1
#                             break
#                     i += 1
#                 polyList.insert(i, [poly, polyVerts])
#             print('V = ',minV)

        # minX = int(min([ p.screen[0] for p in self.points ]))
        # maxX = int(max([ p.screen[0] for p in self.points ]))

        # minY = int(min([ p.screen[1] for p in self.points ]))
        # maxY = int(max([ p.screen[1] for p in self.points ]))

        # maxZ = int(max([ p.screen[2] for p in self.points ]))

        # polyLines = []
        # for poly in self.polyList:
        #     poly.computedPen = poly.computeLight()
        #     polyLines.append([])
        #     for l in poly.fillLines:
        #         l.initScreen()
        #         polyLines[-1].append(mat.parametr_line(l.p1.screen, l.p2.screen))
        #         # polyLines.append([mat.parametr_line(l.p1.screen, l.p2.screen) for l in poly.fillLines])
        #     # polyLines.append([ [[l.p1.screen[0], l.p1.screen[1], l.p1.screen[2] ],[l.p2.screen[0], l.p2.screen[1], l.p2.screen[2]]] for l in poly.fillLines ])
        # for y in range (minY, maxY):
        #     # seg = [[minX, y], [maxX, y]]
        #     poly = mat.eq_poly([minX, y, 0], [minX+Config.AXIS_LINE_LENGTH, y, 0], [minX, y, Config.AXIS_LINE_LENGTH], [minX, y, 0])
        #     polyCrosses = []
        #     minC = 100000
        #     maxC = -1
        #     for i, polyL in enumerate(polyLines):
        #         polyCrosses.append([self.polyList[i].computedPen, {x: maxZ for x in range(minX, maxX)}])
        #         for l in polyL:
        #             c = mat.line_poly_cross(l, poly)
        #             if c != None and 0 <= c[1] <= 1: 
        #                 polyCrosses[-1][1][int(c[0][0])] = c[0][2]   # словарь заполняется в виде xi: zi ибо y мы и так знаем
        #                 # print(c)
        #                 if (minC > int(c[0][0])):
        #                     # print(c)
        #                     minC = int(c[0][0])
        #                 if (maxC < int(c[0][0])):
        #                     maxC = int(c[0][0])
        #         # for crosses in polyCrosses:
        #     # print (minC, maxC)
        #     for x in range(minC, maxC):
        #         minV = min([p for p in polyCrosses], key=lambda p:p[1][x])
        #         # print (minV, x)
        #         self.painter.setPen(minV[0])
        #         self.painter.drawPoint(x, y)
