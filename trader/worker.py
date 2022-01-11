import datetime
import os
import sys
from PyQt5 import QtWidgets
from PyQt5.QAxContainer import QAxWidget
import pythoncom
import pandas as pd
import logging
import time
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.setting import *
from utility.static import *

app = QtWidgets.QApplication(sys.argv)


class Worker:

    def __init__(self, windowQ, workerQ):
        self.windowQ = windowQ
        self.workerQ = workerQ
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
        self.dict_tick = {}
        self.dict_hoga = {}
        self.operation = 1

        self.list_trcd = []
        self.list_kosd = []

        self.str_tday = strf_time('%Y%m%d')
        self.str_open_time = self.str_tday + '090000'
        self.dt_mtct = None


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
        self.event_loop()
        # app.exec_()

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

        self.list_code = self.send_condition([sn_con, self.dict_cond[1], 1, '0'])

        # print('selflistcode', self.list_code)
        # print('sn_reg', sn_reg)

        # ret = self.set_real_reg('3030', '005930', '20;41', 1)
        # print('ret', ret)
        print('총 종목수: ', len(self.list_code))

        k = 0
        for i in range(0, len(self.list_code), 100):
            rreg = [sn_reg + k, ';'.join(self.list_code[i:i + 100]), '10;12;14;30;228;41;61;71;81', 1]
            # 실시간 등록 (rreg)
            ret = self.set_real_reg(rreg)
            if ret == 0:
                text = f"실시간 알림 등록 완료 - [{sn_reg + k}] 종목갯수 {len(rreg[1].split(';'))}"
                print('text', text)
                self.windowQ.put(['LOG', text])
            if i == 2400:
                break
            k += 1
        print('등록완료%%%%%%%%%%%%%')

    def event_loop(self):

        while True:
            pythoncom.PumpWaitingMessages()
            if not self.workerQ.empty():
                data = self.workerQ.get()
                print('workerQ_data 수신')
                if data == 'GetAccountJango':
                    self.GetAccountJango()
                elif data == 'GetAccountEvaluation':
                    self.GetAccountEvaluation()

            time_loop = now() + datetime.timedelta(seconds=0.25)
            # print(now(), time_loop)
            while now() < time_loop:
                pythoncom.PumpWaitingMessages()
                time.sleep(0.0001)

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

    def _receive_real_data(self,  code, realtype, realdata):
        logging.info(f"OnReceiveRealData {code} {realtype} {realdata}")

        # print('receive_time', datetime.datetime.now())
        if realdata == '':
            return

        print('realdata', code, realdata)

        if realtype == '장시작시간':
            try:
                self.operation = int(self.get_comm_real_data(code, 215))
                current = self.get_comm_real_data(code, 20)
                remain = self.get_comm_real_data(code, 214)
            except Exception as e:
                self.windowQ.put(['LOG', f'OnReceiveRealData 장시작시간 {e}'])
            else:
                self.windowQ.put(['LOG', f'장운영 시간 수신 알림 - {self.operation} {current[:2]}:{current[2:4]}:{current[4:]}'
                                     f' 남은시간 {remain[:2]}:{remain[2:4]}:{remain[4:]}'])
        elif realtype == '주식체결':
            print('주식체결실시간', code, realdata)

            try:
                c = abs(int(self.get_comm_real_data(code, 10)))
                o = abs(int(self.get_comm_real_data(code, 16)))
                v = int(self.get_comm_real_data(code, 15))
                dt = self.str_tday + self.get_comm_real_data(code, 20)
            except Exception as e:
                self.windowQ.put(['LOG', f'OnReceiveRealData 주식체결 {e}'])
            else:
                if self.operation == 1:
                    self.operation = 3
                if dt != self.str_open_time and int(dt) > int(self.str_open_time):
                    self.str_jcct = dt
                # if code not in self.dict_vipr.keys():
                #     self.InsertViPrice(code, o)
                # if code in self.dict_vipr.keys() and not self.dict_vipr[code][0] and now() > self.dict_vipr[code][1]:
                #     self.UpdateViPrice(code, c)
                try:
                    pret = self.dict_tick[code][0]
                    bid_volumns = self.dict_tick[code][1]
                    ask_volumns = self.dict_tick[code][2]
                except KeyError:
                    pret = None
                    bid_volumns = 0
                    ask_volumns = 0
                if v > 0:
                    self.dict_tick[code] = [dt, bid_volumns + abs(v), ask_volumns]
                else:
                    self.dict_tick[code] = [dt, bid_volumns, ask_volumns + abs(v)]
                if dt != pret:
                    bids = self.dict_tick[code][1]
                    asks = self.dict_tick[code][2]
                    self.dict_tick[code] = [dt, 0, 0]
                    try:
                        h = abs(int(self.get_comm_real_data(code, 17)))
                        low = abs(int(self.get_comm_real_data(code, 18)))
                        per = float(self.get_comm_real_data(code, 12))
                        dm = int(self.get_comm_real_data(code, 14))
                        ch = float(self.get_comm_real_data(code, 228))
                        name = self.get_master_code_name(code)
                    except Exception as e:
                        self.windowQ.put(['LOG', f'OnReceiveRealData 주식체결 {e}'])
                    else:
                        if code in self.dict_hoga.keys():
                            self.update_tick_data(code, name, c, o, h, low, per, dm, ch, bids, asks, dt, now())
            
        elif realtype == '주식호가잔량':
            try:
                tsjr = int(self.get_comm_real_data(code, 121))
                tbjr = int(self.get_comm_real_data(code, 125))
                s5hg = abs(int(self.get_comm_real_data(code, 45)))
                s4hg = abs(int(self.get_comm_real_data(code, 44)))
                s3hg = abs(int(self.get_comm_real_data(code, 43)))
                s2hg = abs(int(self.get_comm_real_data(code, 42)))
                s1hg = abs(int(self.get_comm_real_data(code, 41)))
                b1hg = abs(int(self.get_comm_real_data(code, 51)))
                b2hg = abs(int(self.get_comm_real_data(code, 52)))
                b3hg = abs(int(self.get_comm_real_data(code, 53)))
                b4hg = abs(int(self.get_comm_real_data(code, 54)))
                b5hg = abs(int(self.get_comm_real_data(code, 55)))
                s5jr = int(self.get_comm_real_data(code, 65))
                s4jr = int(self.get_comm_real_data(code, 64))
                s3jr = int(self.get_comm_real_data(code, 63))
                s2jr = int(self.get_comm_real_data(code, 62))
                s1jr = int(self.get_comm_real_data(code, 61))
                b1jr = int(self.get_comm_real_data(code, 71))
                b2jr = int(self.get_comm_real_data(code, 72))
                b3jr = int(self.get_comm_real_data(code, 73))
                b4jr = int(self.get_comm_real_data(code, 74))
                b5jr = int(self.get_comm_real_data(code, 75))
            except Exception as e:
                self.windowQ.put(['LOG', f'OnReceiveRealData 주식호가잔량 {e}'])
            else:
                self.dict_hoga[code] = [tsjr, tbjr,
                                        s5hg, s4hg, s3hg, s2hg, s1hg, b1hg, b2hg, b3hg, b4hg, b5hg,
                                        s5jr, s4jr, s3jr, s2jr, s1jr, b1jr, b2jr, b3jr, b4jr, b5jr]

    def _receive_chejan_data(self):
        pass

    def update_tick_data(self, code, name, c, o, h, low, per, dm, ch, bids, asks, dt, now):
        print('udata_tick_data', code, name, c, o, h, low, per, dm, ch, bids, asks, dt, now)


    #-------------------------------------------------------------------------------------------------------------------
    # OpenAPI+ 메서드
    #-------------------------------------------------------------------------------------------------------------------

    def get_comm_real_data(self, code, fid):
        return self.ocx.dynamicCall('GetCommRealData(QString, int)', code, fid)

    # def set_real_reg(self, screen, code_list, fid_list, real_type):
    def set_real_reg(self, rreg):
        ret = self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)", rreg)
        return ret

