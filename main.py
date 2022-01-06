import sqlite3
import sys
import os
import logging
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtCore import Qt
from utility.setting import *
from utility.static import *
from multiprocessing import Process, Queue
from trader.worker import Worker
form_class = uic.loadUiType('C:/Users/USER/PycharmProjects/MyTrader/mywindow.ui')[0]


class Window(QtWidgets.QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        # self.windowQ = windowQ
        self.log = logging.getLogger('Main')
        self.log.setLevel(logging.INFO)
        filehandler = logging.FileHandler(f"{SYSTEM_PATH}/log/S{strf_time('%Y%m%d')}.txt", encoding='utf-8')
        self.log.addHandler(filehandler)

        # ui setup(모듈이용)
        self.setupUi(self)

        self.table_gwansim.setColumnWidth(0, 120)
        self.table_gwansim.setColumnWidth(3, 70)
        self.table_gwansim.setColumnWidth(6, 70)
        self.table_account.setColumnWidth(0, 120)
        self.table_acc_eva.setColumnWidth(1, 100)
        self.table_hoga1.setColumnWidth(0, 120)

        # hoga2 table의 0,6 column의 색상을 gray로 설정, 1번 column의 alignment 정의
        for row in range(22):
            self.table_hoga2.setItem(row, 0, QtWidgets.QTableWidgetItem())
            # self.table_hoga2.item(row, 0).setBackground(QtGui.QBrush(Qt.gray))
            self.table_hoga2.item(row, 0).setBackground(QtGui.QColor(100, 100, 100, 50))

            self.table_hoga2.setItem(row, 6, QtWidgets.QTableWidgetItem())
            self.table_hoga2.item(row, 6).setBackground(QtGui.QColor(100, 100, 100, 50))

            self.table_hoga2.setItem(row, 1, QtWidgets.QTableWidgetItem())
            self.table_hoga2.item(row, 1).setTextAlignment(int(Qt.AlignRight) | int(Qt.AlignVCenter))

        # hoga2 table의 매도호가를 옅은 붉은색으로 매수호가를 옅은 푸른색으로 설정
        for index in range(4):    # hg_db, hg_sr, hg_ga, per 순회
            for index2 in range(11):
                row, col = index2, index + 2
                self.table_hoga2.setItem(row, col, QtWidgets.QTableWidgetItem())
                self.table_hoga2.item(row, col).setTextAlignment(int(Qt.AlignRight) | int(Qt.AlignVCenter))
                self.table_hoga2.item(row, col).setBackground(QtGui.QColor(0, 0, 100, (index2+1) * 7))

            for index2 in range(11, 22):
                row, col = index2, index + 2
                self.table_hoga2.setItem(row, col, QtWidgets.QTableWidgetItem())
                self.table_hoga2.item(row,col).setTextAlignment(int(Qt.AlignRight) | int(Qt.AlignVCenter))
                self.table_hoga2.item(row,col).setBackground(QtGui.QColor(100, 0, 0, (22 - index2) * 7))

        # 필요한 변수설정

        # 이벤트 설정
        # self.table_gwansim.cellClicked.connect(self.gwansim_cellClicked)
        # self.table_account.cellClicked.connect(self.account_cellClicked)
        # self.gwansimNaccount.tabBarClicked.connect(self.gwansimNaccount_tabBarClicked)

        # signalslot Writer 설정
        self.writer = Writer()
        self.writer.data0_signal.connect(self.update_text_edit)
        # print('self', self)

    def update_text_edit(self, msg):
        # if msg[0] == '수신시간':
        print('여기까지 옴')

        if msg[0] == 'LOG':
            now = datetime.datetime.now()
            self.textEdit.append(f'{str(now)} : {msg[1]}')

        else:
            self.textEdit.append(msg[1])


class Writer(QtCore.QThread):
    data0_signal = QtCore.pyqtSignal(list)
    print('data0')

    def __init__(self):
        super().__init__()
        print('init실행')
        # self.windowQ = windowQ

    def run(self):
        # print('run됨')
        while True:
            data = windowQ.get()
            print("windowq_get", data)
            if data[0] == 'LOG':
                self.data0_signal.emit(data)
            elif data[0] == 'GSJM':
                self.data1_signal.emit(data)


if __name__ == '__main__':
    # queue 설정
    windowQ = Queue()

    # os.system(f'python {SYSTEM_PATH}/login/versionupdater.py')
    # 2번 계좌를 이용하여 실시간 틱데이터 수집하기
    # os.system(f'python {SYSTEM_PATH}/login/autologin2.py')
    # 수집모듈
    Process(target=Worker, args=(windowQ,), daemon=True).start()
    # worker = Worker(windowQ)

    # 1번 계좌를 이용하여 trading
    # os.system(f'python {SYSTEM_PATH}/login/autologin1.py')


    app = QtWidgets.QApplication(sys.argv)
    main = Window()
    main.show()
    app.exec_()



