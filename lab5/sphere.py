from audioop import reverse
import re
from figure import Figure
from shared import Colors, Config, Light
from polygon import Polygon 
from typing import Any, List
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPen, QColor, QPixmap, QImage, qRgba, QPainter
from PyQt5.QtCore import QPointF, QPoint
import numpy as np
from point import Point

import pyopencl as cl
import pyopencl.array as cl_array

class Sphere(Figure):

    center: Point
    radius: np.float32
    image: QImage

    ctx: Any
    queue: Any
    mf: Any
    prg: cl.Program

    def __init__(self, widget: QWidget, matrix: np.array, controlDot: Point, center: Point, radius: float, penFill: QPen, penBorder: QPen, light: List[Point]) -> None:
        super().__init__(widget, matrix, controlDot, penFill, penBorder, light)

        self.center = center
        self.radius = np.float32(radius*Config.AXIS_LINE_LENGTH)
        self.diff = center.coords - controlDot.coords
        self.image = None
        self.initVGA()
        # print(self.diff)

    def initVGA(self) -> None:
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)
        self.mf = cl.mem_flags
        self.prg = cl.Program(self.ctx, open('D:\\Users\\vasab\\Documents\\COMP_GRAPH\\lab5\\vga.cl').read()).build()



    def initPainter(self, pen: QPen) -> None:
        '''
        Инициализация рисовалки
        '''
        self.painter = QPainter(self.widget)
        self.painter.setPen(pen)
        self.painter.setRenderHints(QPainter.Antialiasing)
    
    def draw(self, isUpdate: bool = False) -> None:
        if (isUpdate or self.image == None):
            self.image = QImage(self.widget.width(), self.widget.height(), QImage.Format.Format_RGBA64)
            self.image.fill(Colors.TRANSPARENT)
            self.center.initScreen()
            coords = np.array([c for c in self.center.coords], np.float32)
            screen = np.array([s for s in self.center.screen], np.float32)
            light = np.array([s for s in self.light.coords], np.float32)
            reverse = np.linalg.inv(self.matrix)
            rev_l = []
            for i in range(4):
                for j in range(4):
                    rev_l.append(reverse[i][j])
            reverse = np.array(rev_l, np.float32)
            
            color_l = self.penFill.color()
            color = np.array([color_l.red(), color_l.green(), color_l.blue(), color_l.alpha()], dtype=np.int32)

            step =np.float32(0.10)
            m = int(np.pi/2 / step) + 1
            n = 4*m
            pixel_size = 2

            pix = np.zeros((m*n, 4), np.float32)
            computed_color = np.zeros((m*n, 4), np.int32)

            # pix = np.zeros((1, 4), np.float32)
            # computed_color = np.zeros((1, 4), np.int32)


            # print(reverse)
            # print('coords = ', coords)
            # print('screen = ', screen)
            # print(self.widget.width(), self.widget.height())

            size_g = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=np.int32(n))
            coords_g = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=coords)
            screen_g = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=screen)
            reverse_g = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=reverse)
            R_g = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=self.radius)
            step_g = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=step)
            color_g = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=color)
            light_g = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=light)
            intensity_g = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=self.light.intensity)

            pix_g = cl.Buffer(self.ctx, self.mf.READ_WRITE, pix.nbytes)
            computed_color_g = cl.Buffer(self.ctx, self.mf.READ_WRITE, pix.nbytes)

            self.prg.computeLightForSphere(
                self.queue,
                (m, n),
                None,

                size_g,
                coords_g,
                screen_g,
                reverse_g,
                R_g,
                step_g,
                color_g,
                light_g,
                intensity_g,

                pix_g,
                computed_color_g
            )

            cl.enqueue_copy(self.queue, pix, pix_g)
            cl.enqueue_copy(self.queue, computed_color, computed_color_g)

            for i in range(m):
                for j in range(n):
                    index = i*n + j
                    x = pix[index][0]
                    y = pix[index][1]
                    r = computed_color[index][0]
                    g = computed_color[index][1]
                    b = computed_color[index][2]
                    a = computed_color[index][3]

                    c = qRgba(r, g, b, a)
                    # print([x, y, r, g, b])
                    if (0 <= x < self.widget.width()-1 and 0 <= y < self.widget.height()-1):
                        self.setPix(x, y, c, -pixel_size, pixel_size+1)

            # theta = np.pi/2
            # pixSize = 2
            # while (theta <= np.pi):
            #     fi = 0
            #     R = self.radius
            #     if (np.pi/2 < theta < np.pi/2+3*step):
            #         R += pixSize
            #     while (fi < 2*np.pi):

            #         x = screen[0] + R*np.sin(theta)*np.cos(fi)
            #         y = screen[1] + R*np.sin(theta)*np.sin(fi)
            #         z = screen[2] + R*np.cos(theta)
            #         P = np.dot(reverse, np.array([x, y, z, 1]))
            #         N = np.array([P[0] - coords[0], P[1] - coords[1], P[2] - coords[2]])
                    
            #         i = Light.computeLightForDot(self.light, P, N)
            #         c = qRgba(int(color_l.red()*i), int(color_l.green()*i), int(color_l.blue()*i), color_l.alpha())
            #         if (np.pi/2 < theta < np.pi/2+3*step):
            #             self.setPix(x, y, c, -1, 2)
            #             fi += 0.03
            #         else:
            #             self.setPix(x, y, c, -pixSize, pixSize+1)
            #             fi += step
            #     theta += step

        self.initPainter(self.penFill)
        self.painter.drawImage(QPoint(0,0),self.image)
        self.painter.end()

        self.controlDot.draw()
                

    def setPix(self, x: float, y: float, c: int, start, end):
        points = []
        for i in range(start, end):
            for j in range(start, end):
                if 0 <= x+i < self.widget.width()-1 and 0 <= y+j < self.widget.height()-1:
                    self.image.setPixel(QPointF(x+i, y+j).toPoint(), c)

    def setPos(self) -> None:
        self.center.coords = self.controlDot.coords + self.diff
                
    
