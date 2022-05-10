from itertools import islice
from traceback import print_tb
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
    points: List[Point]     # список вершин


    def __init__(self, widget: QWidget, matrix: np.array, controlDot: Point, polyPoints: List, penFill: QPen, penBorder: QPen, light: Point, isLight: bool = False) -> None:
        super().__init__(widget, matrix, controlDot, penFill, penBorder, light, isLight)
        self.setPolyList(polyPoints)

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

    def draw(self) -> None:
        # for poly in self.polyList:
        #     poly.draw()
        # zBuff = []
        # for poly in self.polyList:
        #     polyVerts = []
        #     for p in poly.points:
        #         p.initScreen()
        #         z = p.screen[2]
        #         i = 0 
        #         for dot in polyVerts: # сортировка вершин полигона по возрастанию Z
        #             if (z < dot):
        #                 break
        #             i += 1
        #         polyVerts.insert(i, z)
        #     i = 0
        #     flag = True
        #     while (i < len(zBuff) and flag):
        #         item = zBuff[i][1]
        #         length = min(len(item), len(polyVerts))
                
        #         for j in range(length):
        #             if (polyVerts[j]+0.001 < item[j] < polyVerts[j]-0.001): # buff[j] == item[j]
        #                 continue
        #             elif (polyVerts[j] > item[j]):
        #                 flag = False
        #                 i -= 1
        #                 break
        #         i += 1
        #     # print (i)
        #     zBuff.insert(i, [poly, polyVerts])

        # for item in zBuff:
        #     item[0].draw()

        for p in self.points:
            p.initScreen()
        circle = Graham(self.points)
        points = self.points.copy()
        # print(points[0].is_drawed)
        minV = min(points, key=lambda x: x.screen[2])
        minV = points[0]
        print('min calc')
        for p in points:
            print(p, p.screen)
            if (minV.screen[2] > p.screen[2]):
                minV = p
                
        maxZ = max([p.screen[2] for p in circle])
        print('circle')
        for p in circle:
            print(p)
        print(len(circle), '\n')
        buffer = []
        flag = True
        print('start')
        while flag:
            # minV.polygons.sort(key=lambda x: x.minZ())
            print('MIN V', minV, len(minV.polygons))
            
            for poly in minV.polygons:
                print(poly.points[0])
            print()
            for poly in minV.polygons:
                if poly.maxZ() > maxZ:
                    print('over')
                    for p in poly.points:
                        print(p)
                    continue
                print()
                try:
                    buffer.index(poly)
                except ValueError:
                    print(poly.points[0])
                    buffer.append(poly)
                    poly.setIsDrawed()
                    if (checkIfDrawed(circle)):
                        flag = False
                        break
            points.pop(points.index(minV))
            minV = min([p for p in points], key=lambda x: x.screen[2])
        print('stop')
        for poly in buffer:
            poly.draw()

        self.controlDot.draw()
        print('END\n\n\n\n')

def checkIfDrawed(points: List[Point]) -> bool:
    for p in points:
        if not p.is_drawed:
            return False
    return True

def Jarvis(points: List[Point]) -> List[Point]:
    a = points.copy()
    n = len(a) 
    CH_p = []
    p_start = a[0]
    p_current = a[0]
    min_x = a[0].screen[0]
    min_index = 0
    for i in range (n):
        if a[i].screen[0] < min_x:
            min_x = a[i].screen[0]
            p_start = a[i]
    for i in range (0, n):
        if (a[i].screen[0] == min_x):
            if (a[i].screen[1] < a[min_index].screen[1]):
                min_index = i
    p_start = a[min_index]
    a.insert(0, a[min_index])
    CH_p.append(p_start)
    p_next = p_start
    p_current_index = 0
    p_next_index = 1
    while (p_next_index != min_index):
        p_current = p_next
        p_next_index = p_current_index + 1
        p_next = a[p_next_index]
        for i in range (p_next_index + 1, n+1):
            p_i = a[i]
            S = (p_next.screen[0] - p_current.screen[0])*(p_i.screen[1] - p_current.screen[1]) - (p_next.screen[1] - p_current.screen[1])*(p_i.screen[0] - p_current.screen[0])
            if ((S < 0) or (S == 0 and not ((p_current.screen[0]+p_current.screen[1] < p_i.screen[0]+p_i.screen[1] < p_next.screen[0]+p_next.screen[1]) or 
                                            (p_current.screen[0]+p_current.screen[1] > p_i.screen[0]+p_i.screen[1] > p_next.screen[0]+p_next.screen[1])))):
                p_next = p_i
                p_next_index = i
            
        CH_p.append(p_next)
        a.insert(p_current_index+1, a.pop(p_next_index))
        if (p_next_index > min_index):
            min_index += 1
    CH_p.pop(-1)
    return CH_p

def rotate(A: Point,B: Point,C: Point):
    return (B.screen[0]-A.screen[0])*(C.screen[1]-B.screen[1])-(B.screen[1]-A.screen[1])*(C.screen[0]-B.screen[0])

def Graham(A: List[Point]) -> List[Point]:
    n = len(A) # число точек
    P = list(range(n)) # список номеров точек
    for i in range(1,n):
        if A[P[i]].screen[0]<A[P[0]].screen[0]: # если P[i]-ая точка лежит левее P[0]-ой точки
            P[i], P[0] = P[0], P[i] # меняем местами номера этих точек 
    for i in range(2,n): # сортировка вставкой
        j = i
        while j>1 and (rotate(A[P[0]],A[P[j-1]],A[P[j]])<0): 
            P[j], P[j-1] = P[j-1], P[j]
            j -= 1
    S = [P[0],P[1]] # создаем стек
    for i in range(2,n):
        while rotate(A[S[-2]],A[S[-1]],A[P[i]])<0:
            S.pop(-1) # pop(S)
        S.append(P[i]) # push(S,P[i])
    return [A[i] for i in S]


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