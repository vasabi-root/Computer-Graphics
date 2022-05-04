from typing import List
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import numpy as np

from point import Point
from line import Line

def mk_OP(a):      # построение ограничительного прямоугольника
    x1 = min(a[0][0],a[1][0])
    x2 = max(a[0][0],a[1][0])
    y1 = min(a[0][1],a[1][1])
    y2 = max(a[0][1],a[1][1])
    t1 = [x1,y1]
    t2 = [x2,y2]
    p = [t1,t2]
    return p

def find_OP_cross(p1,p2): # нахождение пересечеений между ограничительными прямоугольниками
    if((p1[1][0] >= p2[0][0]) and (p2[1][0] >= p1[0][0]) and (p1[1][1] >= p2[0][1]) and (p2[1][1] >= p1[0][1])):
        return True
    else:
        return False
    
def area(a,b,c):  # ориентированная площадь треугольника
    S = (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
    return S

def exact_method(a,b):  # точный метод определения пересечения 2-х отрезков
    S1 = area(a[0],a[1],b[0])
    S2 = area(a[0],a[1],b[1])
    S3 = area(b[0],b[1],a[0])
    S4 = area(b[0],b[1],a[1])
    if (S1 * S2 > 0) or (S3 * S4 > 0):
        return 0 # не пересекаются
    elif (S1 == 0) and (S2 == 0) and (S3 == 0) and (S4 == 0):
        return -1 # накладываются друг на друга (пресекаются и лежат на одной прямой)
    elif (S1 == 0 and S2 < 0) or (S2 == 0 and S1 < 0):
        return 0
    else: 
        return 1 # все остальные случаи, когда отрезки не пересекаются, были отброшены на первом этапе
    

def PPPO(a,b): # эффективный метод проверки пересечения 2-х отрезков
    if not(find_OP_cross(mk_OP(a),mk_OP(b))):
        return 0
    else:
        return exact_method(a,b)

def cross(a,b): # координаты точки пересечения 2-х отрезков  (если они на одной прямой, то за точку пересечения берётся точка конца отрезка, которая пересекается с другим отрезком)
    p = PPPO(a,b)
    c = None
    if (p == 1):
        A1 = a[0][1] - a[1][1]
        B1 = a[1][0] - a[0][0]
        C1 = a[0][0]*a[1][1] - a[1][0]*a[0][1]
        
        A2 = b[0][1] - b[1][1]
        B2 = b[1][0] - b[0][0]
        C2 = b[0][0]*b[1][1] - b[1][0]*b[0][1]
       
        x = (B2*C1 - B1*C2) / (A2*B1 - A1*B2)
        if (B1 != 0):
            y = (-A1*x - C1) / B1
        else:
            y = (-A2*x - C2) / B2
        c = [x,y]
    elif (p == -1):
        if (a[1][0] < b[1][0]):
            c = a[1]
        elif (a[1][0] > b[1][0]):
            c = b[1]
        elif (a[1][1] < b[1][1]):
            c = a[1]
        else:
            c = b[1]
    return c
        
def sorter(mas): # сортировка координат точек начала и конца отрезков списка mas по возрастанию х, если же х1 == х2, то по у
    # print(mas)
    for i in range (0,len(mas)):
        if (mas[i][0][0] > mas[i][1][0]) or ((mas[i][0][0] == mas[i][1][0]) and (mas[i][0][1] > mas[i][1][1])):
            mas[i][0],mas[i][1] = mas[i][1],mas[i][0]
    return mas

def dot_in_poly(dot: List, poly: List) -> int: 
    '''
    проверка, лежит ли точка в многоугольнике
    '''
    p = sorter(poly)
    lenP = len(p)
    max_x = max(p[i][1][0] for i in range (0, lenP))
    min_x = min(p[i][0][0] for i in range (0, lenP))
    max_y = max(max(p[i][0][1], p[i][1][1]) for i in range (0,lenP))
    min_y = min(min(p[i][0][1], p[i][1][1]) for i in range (0,lenP))

    if (dot[0] >= min_x and dot[0] <= max_x and dot[1] >= min_y and dot[1] <= max_y):
        seg = [[dot[0], dot[1]], [max_x+1, dot[1]]]
        crosses = 0
        for l in p:
            if (exact_method(seg, l) != 0):
                crosses += 1
        if (crosses % 2 == 1):
            return 1
    return 0 #не пересекаются

def parametr_line(A: List, B: List) -> List: # параметрическое уравнение прямой по двум точкам
    P = [B[0]-A[0], B[1]-A[1], B[2]-A[2] if len(A) >= 3 and len(B) >= 3 else 0]
    M = [A[0], A[1], A[2] if len(A) >= 3 else 0]

    return [ [P[0], M[0]],
             [P[1], M[1]],
             [P[2], M[2]] ]

def get_coords_param_line(line: List, t: float) -> List: # координаты точки на прямой, заданной параметрически и t
    x = line[0][0]*t + line[0][1]
    y = line[1][0]*t + line[1][1]
    z = 0
    if (len(line) >= 3):
        z = line[2][0]*t + line[2][1]
    return [x, y, z]

def eq_poly(A: List, B: List, C: List, M: List) -> List: # Ax + By + Cz + D = 0
    '''
    Составляет уравнение плоскости вида Ax + By + Cz + D = 0, параллельной той, 
    что задана точками A, B, C и проходящей через точку M
    '''
    Mx = M[0]
    My = M[1]
    Mz = M[2]

    Vx = B[0] - A[0]
    Vy = B[1] - A[1]
    Vz = B[2] - A[2]

    Wx = C[0] - A[0]
    Wy = C[1] - A[1]
    Wz = C[2] - A[2]

    detX = Vy*Wz - Wy*Vz
    detY = Vx*Wz - Wx*Vz
    detZ = Vx*Wy - Wx*Vy

    return [detX, -detY, detZ, -(Mx*detX - My*detY + Mz*detZ)]

def get_z_in_poly(x: float, y: float, poly: List) -> float:
    if poly[2] != 0:
        return -(poly[0]*x+poly[1]*y+poly[3]) / poly[2]
    return None

def line_poly_cross(line: List, poly: List) -> List:
    ''' 
    Точка пересечения линии, заданной параметрически, с плоскостью, заданной в виде  Ax + By + Cz + D = 0 
    '''
    A = poly[0]
    B = poly[1]
    C = poly[2]
    D = poly[3]

    Px = line[0][0]
    Py = line[1][0]
    Pz = line[2][0]

    x1 = line[0][1]
    y1 = line[1][1]
    z1 = line[2][1]

    num = -(A*x1 + B*y1 + C*z1 + D)
    den = A*Px + B*Py + C*Pz

    t = num / den

    return get_coords_param_line(line, t)

def param_cross(a: List, b: List) -> List:
    '''
    точка пересечения 2-х отрезков, заданных двумя точками (решение в параметрическом виде)
    '''
    p = PPPO(a,b)
    if p != 0:
        a_param = parametr_line(a[0], a[1])
        b_param = parametr_line(b[0], b[1])
        if p == 1:
            V1x = a_param[0][0]
            V1y = a_param[1][0]
            W1x = a_param[0][1]
            W1y = a_param[1][1]

            V2x = b_param[0][0]
            V2y = b_param[1][0]
            W2x = b_param[0][1]
            W2y = b_param[1][1]

            num = V2x*(W1y - W2y) - V2y*(W1x - W2x)
            den = V1x*V2y - V1y*V2x

            t = num / den
            return get_coords_param_line(a_param, t)
        elif p == -1:
            return get_coords_param_line(b_param, 0)
    else:
        return None








