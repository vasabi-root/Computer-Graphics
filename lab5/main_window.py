from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QKeyEvent, QResizeEvent, QMouseEvent, QWheelEvent
from PyQt5.QtCore import QEvent, Qt

from interface import Interface
from shared import Config

import numpy as np

class Window(QMainWindow):
    '''
    Класс окна приложения. В нем содержится ссылка на интерфейс,
    который реализует всю анимацию и логику приложения.
    '''
    
    def __init__(self) -> None:
        super().__init__()
        self.title = "VECTOR-SQUAD LAB-5.5"
        
        self.interface = Interface()
        self.initWindow()
        
        self.setCentralWidget(self.interface)
        
    def initWindow(self):
        '''
        Инициализация окна. Устанавливаем отступы и размеры.
        '''
        self.setWindowTitle(self.title)

        self.setGeometry(Config.WINDOW_TOP_PAD, Config.WINDOW_LEFT_PAD, Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        self.show()

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseMove:
            if event.buttons() == Qt.NoButton:
                self.interface.moveCursor(event.pos())
                # print('mouse')
                # self.edit.setText('x: %d, y: %d' % (pos.x(), pos.y()))
            else:
                pass # do other stuff
        return QMainWindow.eventFilter(self, source, event)
    
    def mousePressEvent(self, mouse: QMouseEvent) -> None:
        self.interface.mousePressEvent(mouse)
    
    def keyPressEvent(self, key: QKeyEvent) -> None:
        '''
        Ловим события нажатия на клавишы и передаем обработку события интерфейсу.
        '''
        self.interface.keyPressEvent(key)

    def keyReleaseEvent(self, key: QKeyEvent) -> None:
        self.interface.keyReleaseEvent(key)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.interface.axis.setCenterCoords(
            self.width() // 2,
            self.height() // 2,
        )
        self.interface.isPressed = True
    
    def wheelEvent(self, wheel: QWheelEvent) -> None:
        self.interface.wheelEvent(wheel)
        

