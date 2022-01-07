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
# from trader.writer import Writer
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
        self.writer.LOG_signal.connect(self.update_text_edit)
        self.writer.GSJM_signal.connect(self.update_gwansimjongmok)

        self.writer.start()

    def update_text_edit(self, msg):
        print('여기까지 옴')

        if msg[0] == 'LOG':
            now = datetime.datetime.now()
            self.textEdit.append(f'{str(now)} : {msg[1]}')

        else:
            self.textEdit.append(msg[1])

    def update_gwansimjongmok(self, data):  # data = ('initial', "", "")

        if data[0] == 'initial':
            # 1차로 수동으로 지정하기 전에 관심종목중 첫째 항목을 지정종목으로 감시 시작
            # print('선택된주식코드', N_.code)

            rows = len(D_GSJM_name)
            self.table_gwansim.setRowCount(rows)

            # 관심종목명만 우선 table에 기재(0번 칼럼)
            for row, (code, name) in enumerate(D_GSJM_name.items()):
                # todo 아래 코드도 일관되게 고쳐야 한다.
                item = QtWidgets.QTableWidgetItem(name)
                self.table_gwansim.setItem(row, 0, item)
                # 관심종목의 코드별로 해당 row값을 저장
                self.code_index[code] = row

        elif data[0] == 'real':     # data = ('real', code, name, c, db, per, cv, cva, ch)
            code = data[1]
            code_info = data[2:] # (name, c, db, per, cv, cva, ch)

            row = self.code_index[code]  # code_index dict에서 row값 검색 {code:row, code:row ...}
            for col in range(7):  # table_gwansim columns 수
                self.table_gwansim.setItem(row, col, QtWidgets.QTableWidgetItem())
                item = code_info[col]
                if type(item) == int or type(item) == float:
                    item = format(item, ',')
                    self.table_gwansim.item(row, col).setTextAlignment(int(Qt.AlignRight) | int(Qt.AlignVCenter))
                self.table_gwansim.item(row, col).setData(Qt.DisplayRole, item)



class Writer(QtCore.QThread):
    LOG_signal = QtCore.pyqtSignal(list)
    GSJM_signal = QtCore.pyqtSignal(list)
    print("writer")

    def __init__(self):
        super().__init__()
        print('init실행')
        # self.windowQ = windowQ

    def run(self):
        print('run됨')
        while True:
            data = windowQ.get()
            print("windowq_get", data)
            if data[0] == 'LOG':
                self.LOG_signal.emit(data)
            elif data[0] == 'GSJM':
                self.GSJM_signal.emit(data)


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



