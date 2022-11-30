from PyQt5.QtWidgets import *
import sys


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()
    def setupUi(self):
        self.setWindowTitle("GIT")
        self.move(200, 200)
        self.resize(800, 400)
        self.lbl = QLabel('Введите адрес репозитория', self)
        self.lbl.move(15, 15)
        self.lbl.resize(150, 20)

        self.adr = QLineEdit(self)
        self.adr.move(170, 17)
        self.adr.resize(500, 20)

        self.button = QPushButton('Проверить', self)
        self.button.move(685,11)
        self.button.clicked.connect(self.btn_clicked)

    def btn_clicked(self):
        print(self.adr.text())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())