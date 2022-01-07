import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QAxContainer import QAxWidget
import pythoncom
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.setting import *

class Worker:
    app = QtWidgets.QApplication(sys.argv)

    def __init__(self, windowQ):
        self.windowQ = windowQ
        self.dict_bool = {
            '실시간조건검색시작': False,
            '실시간조건검색중단': False,
            '장중단타전략시작': False,

            '로그인': False,
            'TR수신': False,
            'TR다음': False,
            'CD수신': False,
            'CR수신': False
        }

        self.dict_code = {}     # 종목코드(코스피+코스닥)
        self.dict_name = {}     # 종목이름(코스피+코드닥)
        self.dict_cond = {}     # 조건검색식 리스트(번호:이름)

        self.list_trcd = []
        self.list_kosd = []

        self.ocx = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')

        self.ocx.OnEventConnect.connect(self._event_connect)
        self.ocx.OnReceiveTrData.connect(self._receive_tr_data)
        self.ocx.OnReceiveRealData.connect(self._receive_real_data)
        self.ocx.OnReceiveChejanData.connect(self._receive_chejan_data)
        self.ocx.OnReceiveTrCondition.connect(self._receive_tr_condition)
        self.ocx.OnReceiveConditionVer.connect(self._receive_condition_ver)
        self.ocx.OnReceiveRealCondition.connect(self._receive_real_condition)
        self.start()

    def start(self):
        self.comm_connect()

    def comm_connect(self):
        self.ocx.dynamicCall('CommConnect()')
        while not self.dict_bool['로그인']:
            pythoncom.PumpWaitingMessages()

        self.dict_bool['CD수신'] = False
        # 조건검색식 수시요청; 수신에 성공하면 OnReceiveConditionVer 이벤트가 발생
        self.ocx.dynamicCall('GetConditionLoad()')
        while not self.dict_bool['CD수신']:
            pythoncom.PumpWaitingMessages()

        self.list_kosd = self.get_code_list_by_market('10')
        list_code = self.get_code_list_by_market('0') + self.list_kosd
        df = pd.DataFrame(columns=['종목명'])
        for code in list_code:
            name = self.get_master_code_name(code)
            df.at[code] = name
            self.dict_name[code] = name
            self.dict_code[name] = code

        # self.queryQ.put([2, df, 'codename', 'replace'])
        # self.windowQ.put([3, self.dict_code])
        # self.windowQ.put([4, self.dict_name])

        # 조건검색식 가져오기; OnReceiveConditionVer 이벤트 내에서 실행하라고 되어 있는데 이렇게 해도 되나보다
        data = self.ocx.dynamicCall('GetConditionNameList()')  # "1^내조건식1;2^내조건식2;5^내조건식3;....."
        conditions = data.split(';')[:-1]    # 맨뒤부분은 ;공백 이므로 잘라낸다.
        for condition in conditions:
            cond_index, cond_name = condition.split('^')
            self.dict_cond[int(cond_index)] = cond_name
        print('조건검색식 리스트', self.dict_cond)

        self.list_code = self.send_condition([sn_con, self.dict_cond[1], 1, 0])

        # print('selflistcode', self.list_code)
        # print('sn_reg', sn_reg)

        k = 0
        for i in range(0, len(self.list_code), 100):
            rreg = [sn_reg + k, ';'.join(self.list_code[i:i + 100]), '10;12;14;30;228;41;61;71;81', 1]
            # 실시간 등록 (rreg)
            self.ocx.dynamicCall('SetRealReg(QString, QString, QString, QString)', rreg)

            text = f"실시간 알림 등록 완료 - [{sn_reg + k}] 종목갯수 {len(rreg[1].split(';'))}"
            print('text', text)
            self.windowQ.put(['LOG', text])
            k += 1

    def get_code_list_by_market(self, market):
        data = self.ocx.dynamicCall('GetCodeListByMarket(QString)', market)
        tokens = data.split(';')[:-1]
        return tokens

    def get_master_code_name(self, code):
        return self.ocx.dynamicCall('GetMasterCodeName(QString)', code)

    def _event_connect(self, err_code):
        if err_code == 0:
            self.dict_bool['로그인'] = True

    def _receive_condition_ver(self, ret, msg):
        if msg == '':
            return
        if ret == 1:   # 수신 성공
            self.dict_bool['CD수신'] = True

    def _receive_tr_condition(self, screen, code_list, cond_name, cond_index, nnext):
        if screen == "" and cond_name == "" and cond_index == "" and nnext == "":
            return
        codes = code_list.split(';')[:-1]
        self.list_trcd = codes
        self.dict_bool['CR수신'] = True

    def _receive_real_condition(self):
        pass

    def send_condition(self, cond):
        self.dict_bool['CR수신'] = False
        self.ocx.dynamicCall('SendCondition(QString, QString, int, int)', cond)
        while not self.dict_bool['CR수신']:
            pythoncom.PumpWaitingMessages()
        return self.list_trcd

    def _receive_tr_data(self):
        pass

    def _receive_real_data(self):
        pass

    def _receive_chejan_data(self):
        pass