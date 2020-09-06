from PySide2 import QtCore, QtWidgets, QtGui

# https://stackoverflow.com/questions/2711033/how-code-a-image-button-in-pyqt
class PicButton(QtWidgets.QAbstractButton):
    def __init__(self, pixmap, pixmap_hover, pixmap_pressed, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap_hover = pixmap_hover
        self.pixmap_pressed = pixmap_pressed

        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def paintEvent(self, event):
        pix = self.pixmap_hover if self.underMouse() else self.pixmap
        if self.isDown():
            pix = self.pixmap_pressed

        painter = QtGui.QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return self.pixmap.size()
        

class MainUI(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(TestDialog, self).__init__(parent)

        self.setWindowTitle("Main Window")
        #self.setMinimumWidth(200)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self._create_widgets()
        self._create_layouts()

    def _create_widgets(self):
        pm1 = QtGui.QPixmap(r"G:\personalProjects\hair-picker\icons\0.png")
        self.button1 = PicButton(pm1,pm1,pm1)
        
        pm2 = QtGui.QPixmap(r"G:\personalProjects\hair-picker\icons\1.png")
        self.button2 = PicButton(pm2,pm2,pm2)
        
        pm3 = QtGui.QPixmap(r"G:\personalProjects\hair-picker\icons\2.png")
        self.button3 = PicButton(pm3,pm3,pm3)
        
        pm4 = QtGui.QPixmap(r"G:\personalProjects\hair-picker\icons\3.png")
        self.button4 = PicButton(pm4,pm4,pm4)
        
        pm5 = QtGui.QPixmap(r"G:\personalProjects\hair-picker\icons\4.png")
        self.button5 = PicButton(pm5,pm5,pm5)

        pm6 = QtGui.QPixmap(r"G:\personalProjects\hair-picker\icons\5.png")
        self.button6 = PicButton(pm6,pm6,pm6)
        
        pm7 = QtGui.QPixmap(r"G:\personalProjects\hair-picker\icons\6.png")
        self.button7 = PicButton(pm7,pm7,pm7)

        pm8 = QtGui.QPixmap(r"G:\personalProjects\hair-picker\icons\7.png")
        self.button8 = PicButton(pm8,pm8,pm8)

        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)       
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setTickInterval(10)

       
    def _create_layouts(self):
        button_layout = QtWidgets.QHBoxLayout(self)
        button_layout.addStretch()
        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)
        button_layout.addWidget(self.button3)
        button_layout.addWidget(self.button4)
        button_layout.addWidget(self.button5)
        button_layout.addWidget(self.button6)
        button_layout.addWidget(self.button7)
        button_layout.addWidget(self.button8)
        button_layout.addWidget(self.slider)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(button_layout)




if __name__ == "__main__":

    d = TestDialog()
    d.show()
