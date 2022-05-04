from figure import Figure
from lab5.shared import Colors, Config
from polygon import Polygon 
from typing import List
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPen, QColor, QPixmap, QImage
import numpy as np
from point import Point

class Sphere(Figure):

    coords: List
    radius: float
    image: QImage

    def __init__(self, widget: QWidget, matrix: np.array, controlDot: Point, coords: List, radius: float, penFill: QPen, penBorder: QPen, light: List[Point]) -> None:
        super().__init__(widget, matrix, controlDot, penFill, penBorder, light[0])

        self.coords = coords
        self.radius = radius
        self.image = QImage(self.radius*2 * Config.AXIS_LINE_LENGTH, QImage.Format_RGB)

    def draw(self) -> None:
        self.image.fill(Colors.TRANSPARENT)
        
        pass

    
