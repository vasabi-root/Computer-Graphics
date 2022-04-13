from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import QPointF
import math


class Line:
    '''
    Класс линии с вспомогательными удобными методами
    '''
    
    LINE_WIDTH = 1              # Толщина
    YELLOW_COLOR = QColor("#FFD800")    # Цвета
    BLUE_COLOR =   QColor("#0057B8")
    
    def __init__(self, widget: QWidget, x1:float, y1:float, x2:float, y2:float, pen: QPen = None, is_anime = False) -> None:
        self.setWidget(widget)
        self.setCoords(x1, y1, x2, y2)
        self.setPen(pen)
        self.setAnime(is_anime)
    
    def setPen(self, pen:QPen) -> None:
        '''
        Инициализация пера (цвет, текстура)
        '''
        self.pen = pen

    def setAnime(self, is_anime:bool):
        self.is_anime = is_anime

    def setCoords(self, x1:float, y1:float, x2:float, y2:float) -> None:
        '''
        Установка координат
        '''
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        
    def initPainter(self) -> None:
        '''
        Инициализация рисовалки
        '''
        self.painter = QPainter(self.widget)
        self.painter.setPen(self.pen)
        self.painter.setRenderHints(QPainter.Antialiasing)
        
    def setWidget(self, widget: QWidget) -> None:
        '''
        Дать понять рисовалке на чем рисовать
        '''
        self.widget = widget
    
    def len(self) -> float:
        return math.sqrt((self.x2-self.x1)**2 + (self.y2-self.y1)**2)
    
    def draw(self) -> None:
        '''
        Рисование линии
        '''
        self.initPainter()
        self.painter.drawLine(QPointF(self.x1, self.y1), QPointF(self.x2, self.y2))
        self.painter.end()
    
    
        