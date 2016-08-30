from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QAxContainer import *
import time


class KiwoomApi(QAxWidget):
    def __init__(self):
        super().__init__()

        #self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        #self.kiwoom.connect(self.kiwoom, SIGNAL("OnEventConnect(int)"), self.OnEventConnect)
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        # void OnEventConnect(LONG nErrCode);
        self.connect(self, SIGNAL("OnEventConnect(int)"), self.OnEventConnect)

        # void OnReceiveTrData(LPCTSTR sScrNo, LPCTSTR sRQName, LPCTSTR sTrCode, LPCTSTR sRecordName, LPCTSTR sPreNext, LONG nDataLength, LPCTSTR sErrorCode, LPCTSTR sMessage, LPCTSTR sSplmMsg)
        self.connect(self, SIGNAL("OnReceiveTrData(QString, QString, QString, QString, QString, int, QString, QString, QString)"), self.OnReceiveTrData)

        # void OnReceiveRealData(LPCTSTR sJongmokCode, LPCTSTR sRealType, LPCTSTR sRealData)
        self.connect(self, SIGNAL("OnReceiveRealData(QString, QString, QString)"), self.OnReceiveRealData)

        # void OnReceiveMsg(LPCTSTR sScrNo, LPCTSTR sRQName, LPCTSTR sTrCode, LPCTSTR sMsg)
        self.connect(self, SIGNAL("OnReceiveMsg(QString, QString, QString, QString)"), self.OnReceiveMsg)

        # void OnReceiveChejanData(LPCTSTR sGubun, LONG nItemCnt, LPCTSTR sFidList);
        self.connect(self, SIGNAL("OnReceiveChejanData(QString, int, QString)"), self.OnReceiveChejanData)


    # Login Request Function
    def CommConnect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()


    # Login Status Check function
    def OnEventConnect(self, errCode):
        print("OnEventConnect", "(", errCode, ")")
        if errCode == 0:
            print("connected")
        else:
            print("disconnected")

        self.ErrCode = errCode;
        self.login_event_loop.exit()

    #
    def change_format(self, data, percent=0):
        is_minus = False

        if data.startswith('-'):
            is_minus = True

        strip_str = data.lstrip('-0')

        if strip_str == '':
            if percent == 1:
                return '0.00'
            else:
                return '0'

        if percent == 1:
            strip_data = int(strip_str)
            strip_data = strip_data / 100
            form = format(strip_data, ',.2f')
        elif percent == 2:
            strip_data = float(strip_str)
            form = format(strip_data, ',.2f')
        else:
            strip_data = int(strip_str)
            form = format(strip_data, ',d')

        if form.startswith('.'):
            form = '0' + form
        if is_minus:
            form = '-' + form

        return form

    #
    def OnReceiveTrData(self, ScrNo, RQName, TrCode, RecordName, PrevNext, DataLength, ErrorCode, Message, SplmMsg):
        print("OnReceiveTrData", "(", ScrNo, RQName, TrCode, RecordName, PrevNext, DataLength, ErrorCode, Message, SplmMsg, ")")
        self.prev_next = PrevNext

        # opt10001_req - 주식기본정보
        if RQName == "opt10001_req":
            self.code = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", TrCode, "", RQName, 0, "종목명")
            self.volume = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", TrCode, "", RQName, 0, "거래량")
            self.price = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", TrCode, "", RQName, 0, "현재가")
            self.pbr = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", TrCode, "", RQName, 0, "PBR")

        # 예수금 현황 상세 정보 요청 : 예수금 현황
        if RQName == "opw00001_req":
            estimated_day2_deposit = self.CommGetData(TrCode, "", RQName, 0, "d+2추정예수금")
            estimated_day2_deposit = self.change_format(estimated_day2_deposit)
            self.data_opw00001 = estimated_day2_deposit

        #
        if RQName == "opt10081_req":
            cnt = self.GetRepeatCnt(TrCode, RQName)
            for i in range(cnt):
                date = self.CommGetData(TrCode, "", RQName, i, "일자")
                open = self.CommGetData(TrCode, "", RQName, i, "시가")
                high = self.CommGetData(TrCode, "", RQName, i, "고가")
                low  = self.CommGetData(TrCode, "", RQName, i, "저가")
                close  = self.CommGetData(TrCode, "", RQName, i, "현재가")
                self.ohlc['date'].append(date)
                self.ohlc['open'].append(int(open))
                self.ohlc['high'].append(int(high))
                self.ohlc['low'].append(int(low))
                self.ohlc['close'].append(int(close))

        # 계좌평가 잔고내역 : 잔고 및 보유종목 현황
        if RQName == "opw00018_req":
            # Single Data
            single = []
            total_purchase_price = self.CommGetData(TrCode, "", RQName, 0, "총매입금액")
            total_purchase_price = self.change_format(total_purchase_price)
            single.append(total_purchase_price)

            total_eval_price = self.CommGetData(TrCode, "", RQName, 0, "총평가금액")
            total_eval_price = self.change_format(total_eval_price)
            single.append(total_eval_price)

            total_eval_profit_loss_price = self.CommGetData(TrCode, "", RQName, 0, "총평가손익금액")
            total_eval_profit_loss_price = self.change_format(total_eval_profit_loss_price)
            single.append(total_eval_profit_loss_price)

            total_earning_rate = self.CommGetData(TrCode, "", RQName, 0, "총수익률(%)")
            total_earning_rate = self.change_format(total_earning_rate, 1)
            single.append(total_earning_rate)

            estimated_deposit = self.CommGetData(TrCode, "", RQName, 0, "추정예탁자산")
            estimated_deposit = self.change_format(estimated_deposit)
            single.append(estimated_deposit)

            self.data_opw00018['single'] = single

            # Multi Data
            cnt = self.GetRepeatCnt(TrCode, RQName)
            for i in range(cnt):
                data = []

                item_name = self.CommGetData(TrCode, "", RQName, i, "종목명")
                data.append(item_name)

                quantity = self.CommGetData(TrCode, "", RQName, i, "보유수량")
                quantity = self.change_format(quantity)
                data.append(quantity)

                purchase_price = self.CommGetData(TrCode, "", RQName, i, "매입가")
                purchase_price = self.change_format(purchase_price)
                data.append(purchase_price)

                current_price = self.CommGetData(TrCode, "", RQName, i, "현재가")
                current_price = self.change_format(current_price)
                data.append(current_price)

                eval_profit_loss_price = self.CommGetData(TrCode, "", RQName, i, "평가손익")
                eval_profit_loss_price = self.change_format(eval_profit_loss_price)
                data.append(eval_profit_loss_price)

                earning_rate = self.CommGetData(TrCode, "", RQName, i, "수익률(%)")
                earning_rate = self.change_format(earning_rate, 2)
                data.append(earning_rate)
                self.data_opw00018['multi'].append(data)

        self.tr_event_loop.exit()

    # void OnReceiveRealData(LPCTSTR sJongmokCode, LPCTSTR sRealType, LPCTSTR sRealData)
    def OnReceiveRealData(self, sJongmokCode, sRealType, sRealData):
        print("OnReceiveRealData", "(",sJongmokCode, sRealType, sRealData, ")")
        if sRealType == "주식시세":
            pass

    # void OnReceiveMsg(LPCTSTR sScrNo, LPCTSTR sRQName, LPCTSTR sTrCode, LPCTSTR sMsg)
    def OnReceiveMsg(self, sRQName, sTrCode, sMsg):
        print("OnReceiveMsg", "(",sRQName, sTrCode, sMsg, ")")
        if sRQName == "주식기본정보":
            pass

    # void OnReceiveChejanData(LPCTSTR sGubun, LONG nItemCnt, LPCTSTR sFidList);
    # FID	설명
    # 9203	주문번호
    # 302	종목명
    # 900	주문수량
    # 901	주문가격
    # 902	미체결수량
    # 904	원주문번호
    # 905	주문구분
    # 908	주문/체결시간
    # 909	체결번호
    # 910	체결가
    # 911	체결량
    # 10	현재가, 체결가, 실시간종가
    def OnReceiveChejanData(self, sGubun, nItemCnt, sFidList):
        print("OnReceiveChejanData", "(",sGubun, nItemCnt, sFidList, ")")
        print("sGubun: ", sGubun)
        print(self.GetChejanData(9203))
        print(self.GetChejanData(302))
        print(self.GetChejanData(10))
        for i in range(900,912):
            if(i != 904):
                print(self.GetChejanData(i))

    # Set Input Value
    def SetInputValue(self, sID, sValue):
        self.dynamicCall("SetInputValue(QString, QString)", sID, sValue)

    #
    def CommRqData(self, sRQName, sTRCode, nPrevNext, sScreenNo):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", sRQName, sTRCode, nPrevNext, sScreenNo)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    #
    def CommGetData(self, sJongmokCode, sRealType, sFieldName, nIndex, sInnerFiledName):
        data = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sJongmokCode, sRealType,
                                sFieldName, nIndex, sInnerFiledName)
        return data.strip()

    # LONG SendOrder( BSTR sRQName, BSTR sScreenNo, BSTR sAccNo, LONG nOrderType, BSTR sCode, LONG nQty, LONG nPrice, BSTR sHogaGb,BSTR sOrgOrderNo)
    # nOrderType : (1:신규매수, 2:신규매도, 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정)
    # sHogaGb : 00:지정가, 03:시장가, 05:조건부지정가, 06:최유리지정가, 07:최우선지정가, 10:지정가IOC, 13:시장가IOC, 16:최유리IOC, 20:지정가FOK, 23:시장가FOK, 26:최유리FOK, 61:장전시간외종가, 62:시간외단일가, 81:장후시간외종가
    def SendOrder(self, sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo):
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", [sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo])

    #
    def GetRepeatCnt(self, sTrCode, sRecordName):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRecordName)
        return ret

    # sMarket – 0:장내, 3:ELW, 4:뮤추얼펀드, 5:신주인수권, 6:리츠, 8:ETF, 9:하이일드펀드, 10:코스닥, 30:제3시장
    def GetCodeListByMarket(self, sMarket):
        cmd = 'GetCodeListByMarket("%s")' % sMarket
        ret = self.dynamicCall(cmd)
        #return ret
        item_codes = ret.split(';')
        return item_codes

    #
    def GetMasterCodeName(self, strCode):
        cmd = 'GetMasterCodeName("%s")' % strCode
        ret = self.dynamicCall(cmd)
        return ret

    #
    def GetChejanData(self, nFid):
        cmd = 'GetChejanData("%s")' % nFid
        ret = self.dynamicCall(cmd)
        return ret

    #
    def GetConnectState(self):
        ret = self.dynamicCall("GetConnectState()")
        return ret

    # ["ACCNO", "USER_ID", "USER_NAME"]
    def GetLoginInfo(self, info):
        ret = self.dynamicCall("GetLoginInfo(QString)", info)
        return ret

    #
    def InitOHLCRawData(self):
        self.ohlc = {'date': [], 'open': [], 'high': [], 'low': [], 'close': []}

    #
    def init_opw00018_data(self):
        self.data_opw00018 = {'single': [], 'multi': [] }
