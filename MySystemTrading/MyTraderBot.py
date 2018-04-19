import os
import sys
import threading
import datetime
import time

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5 import uic

import KiwoomOpenApi

#form_class = uic.loadUiType("E:\workspace\GitHub\systemtrading\MySystemTrading\QtUI\MainUI.ui")[0]
form_class = uic.loadUiType("./QtUI/StockInfo.ui")[0]

#class MyWindow(QMainWindow):
class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.code = "030200"

        # Kiwoom Login
        self.kiwoom = KiwoomOpenApi.KiwoomOpenApi()

        # Timer 1sec
        self.timer_1sec = QTimer(self)
        self.timer_1sec.start(10000)
        self.timer_1sec.timeout.connect(self.timeout_1sec)

        self.SaveStockInfoBtn.clicked.connect(self.SaveStockInfo)
        self.Btn1.clicked.connect(self.getStockCodeList)
        self.Btn2.clicked.connect(self.getThemeGroupList)
        self.Btn3.clicked.connect(self.getThemeGroupList)
        self.Btn4.clicked.connect(self.getWorkingDateList)
        self.Btn5.clicked.connect(self.getBasicInfo)
        self.Btn6.clicked.connect(self.getDailyStockInfo)

        self.Btn7.clicked.connect(self.getWorkingDateList)
        self.Btn8.clicked.connect(self.getWorkingDateList)
        self.Btn9.clicked.connect(self.getWorkingDateList)
        self.Btn10.clicked.connect(self.getWorkingDateList)
        self.Btn11.clicked.connect(self.getWorkingDateList)


    def setRealData(self) :
        print("======== SetRealReg =========")
        a = self.kiwoom.SetRealReg("0101", "000020", "10;11;12;27;28;13", 0)
        print(a)
        a = self.kiwoom.SetRealReg("0101", "034220", "10;11;12;27;28;13", 1)
        print(a)

    def getStockCodeList(self) :
        print("======== code list =========")
        self.kiwoom.Init_RealType_Data()
        market = "0"
        # init kospi dictionary Data.....
        codelist = list(self.kiwoom.GetCodeListByMarket(market))
        print(codelist)
        return codelist

    def getThemeGroupList(self) :
        market = 0
        themelist = self.kiwoom.GetThemeGroupList(market)
        result = {}
        print("======== getThemeGroupList =========")
        themelist = themelist.split(';')
        #print(themelist)
        for theme in themelist :
            theme = theme.split('|')
            result[theme[0]] = theme[1]

        print(result)


    def getThemeGroupCode(self) :
        print("=========getThemeGroupCode===========")
        themecode = 400
        k = self.kiwoom.GetThemeGroupCode(themecode)
        print(k)


    def getWorkingDateList(self) :
        code = "034220"
        today = str(datetime.date.today())
        today.replace('-', '')
        self.kiwoom.request_opt10081_GetDailyChartInfo(code, today)
        print("======== getWorkingDateList =========")
        k = self.kiwoom.GetStockInfo('opt10081')
        result = []
        for info in k :
            result.append(info[4])
        print(result)

        a = ['20180421', '20180420', '20180419']
        #c = list(set([a]) - set([result]))
        c = [item for item in a if item not in result]
        print(c)
        #print(self.kiwoom.DailyChartInfo)
        #opt10081_DB = DataFrame(data, columns=colName)

    def getBasicInfo(self) :
        print("======== getBasicInfo =========")
        # Request opt00001 - 기본 정보
        code = "034220"
        self.kiwoom.request_opt10001_GetStockBasicInfo(code)
        k = self.kiwoom.GetStockInfo('opt10001')
        print(k)

    def getDailyStockInfo(self) :
        print("======== getDailyStockInfo =========")
        # opt10006_req - 주식 일/시분 정보
        code = "034220"
        self.kiwoom.request_opt10006_GetStockBasicInfo(code)
        k = self.kiwoom.GetStockInfo('opt10006')
        print(k)


    def getTrustTrading(self) :
        print("======== getTrustTrading =========")
        code = "034220"
        startDate = "20180419"
        self.kiwoom.request_opt10013_DebtTransactionInfo(code, startDate, 1)
        self.kiwoom.request_opt10013_DebtTransactionInfo(code, startDate, 2)
        k = self.kiwoom.GetStockInfo('opt10013')
        print(k)

    def getDebtSelling(self) :
        print("======== getDebtSelling =========")
        code = "034220"
        startDate = "20180401"
        endDate = "20180419"
        # opt10014 공매도 추이
        self.kiwoom.request_opt10014_DebtSellTransactionInfo(code, startDate, endDate)
        k = self.kiwoom.GetStockInfo('opt10014')
        print(k)

    def OrgForeignBuynSellInfo(self) :
        print("======== OrgForeignBuynSellInfo =========")
        code = "034220"
        startDate = "20180401"
        endDate = "20180419"
        # opt10045 기관/외인 매매 추이
        self.kiwoom.request_opt10045_OrgForeignBuynSellInfo(code, startDate, endDate)
        k = self.kiwoom.GetStockInfo('opt10045')
        print(k)


    def EachGroupByunSellInfo(self) :
        print("======== EachGroupByunSellInfo =========")
        code = "034220"
        startDate = "20180401"
        endDate = "20180419"
        # opt10061 투자자별 순매수 / 순매도 (금액/수량)
        self.kiwoom.request_opt10061_EachGroupBuynSellInfo(code, startDate, endDate)
        k = self.kiwoom.GetStockInfo('opt10061')
        print(k)


    def SaveStockInfo(self) :
        self.kiwoom.Init_RealType_Data()
        # init kospi dictionary Data.....
        codelist = list(self.kiwoom.GetCodeListByMarket("0"))
        print("======== code list =========")
        print(codelist)

        startDate = "20180413"
        endDate = startDate
        for code in codelist :
            code = "034220"
            self.kiwoom.InitStockInfo()
            # Request opt00001 - 기본 정보
            self.kiwoom.request_opt10001_GetStockBasicInfo(code)

            # opt10006_req - 주식 일/시분 정보
            self.kiwoom.request_opt10006_GetStockBasicInfo(code)
            time.sleep(1)

            # opt10013 신용매매 (신용)
            self.kiwoom.request_opt10013_DebtTransactionInfo(code, startDate, 1)
            self.kiwoom.request_opt10013_DebtTransactionInfo(code, startDate, 2)

            # opt10014 공매도 추이
            self.kiwoom.request_opt10014_DebtSellTransactionInfo(code, startDate, endDate)
            time.sleep(1)

            # opt10045 기관/외인 매매 추이
            self.kiwoom.request_opt10045_OrgForeignBuynSellInfo(code, startDate, endDate)
            time.sleep(1)

            # opt10061 투자자별 순매수 / 순매도 (금액/수량)
            self.kiwoom.request_opt10061_EachGroupBuynSellInfo(code, startDate, endDate)

            k = self.kiwoom.GetThemeGroupList(0)
            print("=========GetThemaGroupList===========")
            print(k)

            k = self.kiwoom.GetThemeGroupCode(400)
            print("=========GetThemaGroupCode===========")
            print(k)

            print("=========ALL===========")
            k = self.kiwoom.GetStockInfo('ALL')
            print(k)

            print("=========opt10001===========")
            k = self.kiwoom.GetStockInfo('opt10001')
            print(k)

            print("=========opt10006===========")
            k = self.kiwoom.GetStockInfo('opt10006')
            print(k)

            print("=========opt10013===========")
            k = self.kiwoom.GetStockInfo('opt10013')
            print(k)

            print("=========opt10014===========")
            k = self.kiwoom.GetStockInfo('opt10014')
            print(k)

            print("=========opt10045===========")
            k = self.kiwoom.GetStockInfo('opt10045')
            print(k)

            print("=========opt10061===========")
            k = self.kiwoom.GetStockInfo('opt10061')
            print(k)

            break


        # Get Specific stock item from dictionary


    # 1 sec timer callback
    def timeout_1sec(self):
        current_time = QTime.currentTime()
        text_time = current_time.toString("hh:mm:ss")
        time_msg = "현재시간: " + text_time

        state = self.kiwoom.GetConnectState()
        if state == 1:
            state_msg = "서버 연결 중"
        else:
            state_msg = "서버 미 연결 중"
        #self.statusbar.showMessage(state_msg + " | " + time_msg)
        print(state_msg + " | " + time_msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
