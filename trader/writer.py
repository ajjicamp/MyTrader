from PyQt5 import QtWidgets, QtCore, QtGui, uic


class Writer(QtCore.QThread):
    data0_signal = QtCore.pyqtSignal(list)
    print('data0')

    def __init__(self, windowQ):
        super().__init__()
        self.windowQ = windowQ
        print('init실행')

    def run(self):
        print('run됨')
        while True:
            data = self.windowQ.get()
            print("windowq_get", data)
            if data[0] == 'LOG':
                self.data0_signal.emit(data)
            elif data[0] == 'GSJM':
                self.data1_signal.emit(data)
