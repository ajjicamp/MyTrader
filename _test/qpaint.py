import sys, random
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath
from PyQt5.QtCore import Qt


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 400, 400)
        self.setWindowTitle('QPainter를 이용한 그래픽스')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        # self.drawText(event, qp)
        # self.drawPoints(event, qp)
        self.drawRectangles(qp)
        # self.drawLines(qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QColor(0, 0, 0))
        qp.setFont(QFont('나눔명조', 35))
        qp.drawText(event.rect(), Qt.AlignCenter, '스산한 늦가을\n아니.. 초겨울인가?')
        # 그리기 함수의 호출 부분

    def drawPoints(self, event, qp):
        pen = QPen(Qt.gray, 3)
        qp.setPen(pen)
        size = self.size()

        for i in range(700):
            x = random.randint(1, size.width() - 1)
            y = random.randint(1, size.height() - 1)
            qp.drawPoint(x, y)

    def drawRectangles(self, qp):
        col = QColor(0, 0, 0)
        col.setNamedColor('#d4d4d4')
        qp.setPen(col)
        qp.setBrush(QColor(200, 0, 0))
        qp.drawRect(50, 50, 100, 100)
        qp.setBrush(QColor(255, 80, 0, 160))
        qp.drawRect(150, 150, 100, 100)
        qp.setBrush(QColor(25, 0, 90, 200))
        qp.drawRect(250, 250, 100, 100)

    def drawLines(self, qp):
        pen = QPen(Qt.black, 3, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(50, 50, 350, 50)
        pen.setStyle(Qt.DashLine)
        qp.setPen(pen)
        qp.drawLine(50, 110, 350, 110)
        pen.setStyle(Qt.DashDotLine)
        qp.setPen(pen)
        qp.drawLine(50, 170, 350, 170)
        pen.setStyle(Qt.DotLine)
        qp.setPen(pen)
        qp.drawLine(50, 230, 350, 230)
        pen.setStyle(Qt.DashDotDotLine)
        qp.setPen(pen)
        qp.drawLine(50, 290, 350, 290)
        pen.setStyle(Qt.CustomDashLine)
        pen.setDashPattern([1, 4, 5, 4])
        qp.setPen(pen)
        qp.drawLine(50, 350, 350, 350)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWindow()
    sys.exit(app.exec_())