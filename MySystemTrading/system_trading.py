import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
#from kiwoomapi import *
import kiwoomapi
import pandas as pd
import sqlite3

from PyQt4 import uic

form_class = uic.loadUiType("D:\workspace\GitHub\systemtrading\MySystemTrading\QtUI\MainUI.ui")[0]
#form_class = uic.loadUiType("./QtUI/MainUI.ui")[0]

#class MyWindow(QMainWindow):
class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

#       self.kiwoom = KiwoomApi()
        self.kiwoom = kiwoomapi.KiwoomApi()
        self.kiwoom.CommConnect()

        # Timer 1sec
        self.timer_1sec = QTimer(self)
        self.timer_1sec.start(1000)
        self.timer_1sec.timeout.connect(self.timeout_1sec)

        # Timer 10sec
        self.timer_10sec = QTimer(self)
        self.timer_10sec.start(1000*10)
        self.timer_10sec.timeout.connect(self.timeout_10sec)

        # Signal - Callback mapping..........
        self.lineEdit_Code.textChanged.connect(self.code_changed)
        self.get_AccountInfo()
        self.pushButton_Order.clicked.connect(self.send_order)
        self.pushButton_GetBalanceInfo.clicked.connect(self.check_balance)
        self.pushButton_Check.clicked.connect(self.check)


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
        self.statusbar.showMessage(state_msg + " | " + time_msg)

    # 10 sec timer callback
    def timeout_10sec(self):
        if self.checkBox_RealTime.isChecked() == True:
            self.check_balance()

    # code 변경시 자동 종목명 검색 및 표시
    def code_changed(self):
        code = self.lineEdit_Code.text()
        code_name = self.kiwoom.GetMasterCodeName(code)
        self.lineEdit_CodeName.setText(code_name)

    def send_order(self):
        order_type_lookup = {'신규매수': 1, '신규매도': 2, '매수취소': 3, '매도취소': 4}
        hoga_lookup = {'지정가': "00", '시장가': "03"}
        account = self.comboBox_Account.currentText()
        order_type = self.comboBox_OrderType.currentText()
        code = self.lineEdit_Code.text()
        hoga = self.comboBox_Hoga.currentText()
        num = self.spinBox_Amount.value()
        price = self.spinBox_Price.value()
        self.kiwoom.SendOrder("SendOrder_req", "0101", account, order_type_lookup[order_type], code, num, price, hoga_lookup[hoga], "")

    def get_AccountInfo(self):
        user_id = self.kiwoom.GetLoginInfo(["USER_ID"])
        user_name = self.kiwoom.GetLoginInfo(["USER_NAME"])
        accouns_num = int(self.kiwoom.GetLoginInfo(["ACCOUNT_CNT"]))
        accounts = self.kiwoom.GetLoginInfo(["ACCNO"])
        accounts_list = accounts.split(';')[0:accouns_num]
        self.comboBox_Account.addItems(accounts_list)

    def check_balance(self):
        self.kiwoom.init_opw00018_data()
        account = self.comboBox_Account.currentText()

        # Request opw00018
        self.kiwoom.SetInputValue("계좌번호", account)
        #self.kiwoom.SetInputValue("비밀번호", "0000")
        self.kiwoom.CommRqData("opw00018_req", "opw00018", 0, "2000")

        while self.kiwoom.prev_next == '2':
            time.sleep(0.2)
            self.kiwoom.SetInputValue("계좌번호", account)
            #self.kiwoom.SetInputValue("비밀번호", "0000")
            self.kiwoom.CommRqData("opw00018_req", "opw00018", 2, "2000")

        # Request opw00001
        self.kiwoom.SetInputValue("계좌번호", account)
        #self.kiwoom.SetInputValue("비밀번호", "0000")
        self.kiwoom.CommRqData("opw00001_req", "opw00001", 0, "2000")

        # balance - 계좌 잔고 표시
        item = QTableWidgetItem(self.kiwoom.data_opw00001)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.tableWidget_AccountInfo.setItem(0, 0, item)

        for i in range(1, 6):
            item = QTableWidgetItem(self.kiwoom.data_opw00018['single'][i-1])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.tableWidget_AccountInfo.setItem(0, i, item)

        self.tableWidget_AccountInfo.resizeRowsToContents()

        # 보유종목 수익율 표시 - Item list
        item_count = len(self.kiwoom.data_opw00018['multi'])
        self.tableWidget_DetailCodeInfo.setRowCount(item_count)

        for j in range(item_count):
            row = self.kiwoom.data_opw00018['multi'][j]
            for i in range(len(row)):
                item = QTableWidgetItem(row[i])
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.tableWidget_DetailCodeInfo.setItem(j, i, item)

        self.tableWidget_DetailCodeInfo.resizeRowsToContents()

    def check(self):
        recommend = { "1" : [] }
        codelist = []
        codelist = self.kiwoom.GetCodeListByMarket("0")
        cnt = len(codelist)
        j = 0
        for i in codelist:
            self.textEdit_Terminal.append(i)
            recommend[i] = []
            j = j+1

        print(recommend)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
