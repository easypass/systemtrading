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

    def SaveStockInfo(self) :
        self.kiwoom.Init_RealType_Data()
        # init kospi dictionary Data.....
        codelist = list(self.kiwoom.GetCodeListByMarket("0"))
        print("======== code list =========")
        print(codelist)
        # Request opw00001
        self.kiwoom.SetInputValue("종목코드", '034220')
        self.kiwoom.CommRqData("opt10001_req", "opt10001", 0, "0101")



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
