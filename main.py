import sqlite3
import sys
import os
import logging
from PyQt5 import QtWidgets, uic
from PyQt5 import QtCore
from utility.setting import *
from utility.static import *
from multiprocessing import Process, Queue

from trader.worker import Worker
form_class = uic.loadUiType('C:/Users/USER/PycharmProjects/MyTrader/mywindow.ui')[0]


class Window(QtWidgets.QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger('Main')
        self.log.setLevel(logging.INFO)
        filehandler = logging.FileHandler(f"{SYSTEM_PATH}/log/S{strf_time('%Y%m%d')}.txt", encoding='utf-8')
        self.log.addHandler(filehandler)

        # ui setup(모듈이용)
        self.setupUi(self)

        # 필요한 변수설정

        # signalslot Writer 설정
        self.writer = Writer()
        # self.writer.data0.connect()
        print('self', self)

    # 이벤트 슬롯 설정


class Writer(QtCore.QThread):
    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    # queue 설정

    os.system(f'python {SYSTEM_PATH}/login/versionupdater.py')
    # 2번 계좌를 이용하여 실시간 틱데이터 수집하기
    os.system(f'python {SYSTEM_PATH}/login/autologin2.py')
    # 수집모듈
    worker = Worker()

    # 1번 계좌를 이용하여 trading
    # os.system(f'python {SYSTEM_PATH}/login/autologin1.py')


    app = QtWidgets.QApplication(sys.argv)
    main = Window()
    main.show()
    app.exec_()



