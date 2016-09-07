import os
import sys
import threading
import datetime
import time

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

#from kiwoomapi import *
import kiwoomapi

import pymysql
import sqlite3

import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import pandas_datareader.data as web

import pywinauto
import win32com.client as win32


class DBSync_Threadjobs(threading.Thread):
    def run(self):
        print(threading.currentThread().getName())
        pass


form_class = uic.loadUiType("D:\workspace\GitHub\systemtrading\MySystemTrading\QtUI\MainUI.ui")[0]
#form_class = uic.loadUiType("./QtUI/MainUI.ui")[0]

#class MyWindow(QMainWindow):
class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.code = "030200"
#       self.kiwoom = KiwoomApi()
        self.kiwoom = kiwoomapi.KiwoomApi()
        self.kiwoom.CommConnect()

        # Timer 1sec
        self.timer_1sec = QTimer(self)
        self.timer_1sec.start(1000)
        self.timer_1sec.timeout.connect(self.timeout_1sec)

        # Timer 5sec
        self.timer_5sec = QTimer(self)
        self.timer_5sec.start(5000)
        self.timer_5sec.timeout.connect(self.timeout_5sec)

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

        self.checkBox_RealTime_codeinfo.clicked.connect(self.check_realtime_codeinfo)
        self.kiwoom.Init_RealType_Data()


    def check_realtime_codeinfo(self):
        if self.checkBox_RealTime_codeinfo.isChecked() == True:
            self.kiwoom.SetRealReg("0101", self.code, "10;121;125", 0)
        else:
            self.kiwoom.SetRealRemove("0101", self.code)
            self.kiwoom.Init_RealType_Data()


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

    # 5 sec timer callback
    def timeout_5sec(self):
        if self.checkBox_RealTime_codeinfo.isChecked() == True:
            #self.textEdit_Terminal_RealTime.clear()
            #self.textEdit_Terminal_RealTime.append(self.kiwoom.RealData)
            #print(self.kiwoom.RealData)
            pass

    # 10 sec timer callback
    def timeout_10sec(self):
        if self.checkBox_RealTime.isChecked() == True:
            self.check_balance()

    # code 변경시 자동 종목명 검색 및 표시
    def code_changed(self):
        self.code = self.lineEdit_Code.text()
        code_name = self.kiwoom.GetMasterCodeName(self.code)
        if len(code_name) > 0 :
            self.lineEdit_CodeName.setText(code_name)
            self.kiwoom.Init_RealType_Data()
            '''
            # Request opw00001
            self.kiwoom.SetInputValue("종목코드", self.code)
            self.kiwoom.CommRqData("opt10001_req", "opt10001", 0, "0101")
            '''

            # Request opw00001
            '''
            self.kiwoom.SetInputValue("종목코드", self.code)
            self.kiwoom.SetInputValue("기준일자", "20160902")
            self.kiwoom.SetInputValue("수정주가구분", 0)
            self.kiwoom.CommRqData("opt10081_req", "opt10081", 0, "0101")
            self.Save_Excelfile("D:\\test_excel.xls")
            #self.Open_Excelfile("D:\\test_excel.xls")
            '''

            # request 융자 / 대주거래 현황
            self.kiwoom.SetInputValue("종목코드", self.code)
            self.kiwoom.SetInputValue("일자", "20160907")
            self.kiwoom.SetInputValue("조회구분", 1)
            self.kiwoom.CommRqData("opt10013_req", "opt10013", 0, "0101")

            # request 공매도 현황
            self.kiwoom.SetInputValue("종목코드", self.code)
            self.kiwoom.SetInputValue("시간구분", 1)
            self.kiwoom.SetInputValue("시작일자", "20160101")
            self.kiwoom.SetInputValue("종료일자", "20160907")
            self.kiwoom.CommRqData("opt10014_req", "opt10014", 0, "0101")



    # 주식 주문 및 취소
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

    # 계좌정보 얻어오기
    def get_AccountInfo(self):
        user_id = self.kiwoom.GetLoginInfo(["USER_ID"])
        user_name = self.kiwoom.GetLoginInfo(["USER_NAME"])
        accouns_num = int(self.kiwoom.GetLoginInfo(["ACCOUNT_CNT"]))
        accounts = self.kiwoom.GetLoginInfo(["ACCNO"])
        accounts_list = accounts.split(';')[0:accouns_num]
        self.comboBox_Account.addItems(accounts_list)

    # 계좌 잔고 조회 및 수익율 조회
    def check_balance(self):
        self.kiwoom.Init_opw00018_data()
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

    # Kospi 종목 조회
    def check(self):
        self.kiwoom.Init_RealType_Data()
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        excel.Visible = True
        wb = excel.Workbooks.Add()
        # Add worksheet....
        ws = wb.Worksheets.Add()
        ws.Name = "종목정보"
        # select sheet
        ws = wb.Worksheets("종목정보")
        codekeylist = list(self.kiwoom.opt10001_data.keys())

        col = 1;
        for i in codekeylist:
            ws.Cells(1, col).Value = str(i)
            col+=1

        # init kospi dictionary Data.....
        codelist = list(self.kiwoom.GetCodeListByMarket("0"))
        cnt = len(codelist)
        row = 2
        for i in codelist:
            col = 1
            #self.textEdit_Terminal.append(i)
            self.code = i;
            # Request opw00001
            self.kiwoom.SetInputValue("종목코드", self.code)
            self.kiwoom.CommRqData("opt10001_req", "opt10001", 0, "0101")

            for j in codekeylist:
                if len(self.kiwoom.opt10001_data[j]) > 0 :
                    data = self.kiwoom.opt10001_data[j]
                    ws.Cells(row, col).Value = data
                col+=1
            row+=1
            time.sleep(0.5)

        wb.Save(PathName)
        excel.Application.Quit()





    # Thread 생성 Test
    def create_Thread_test(self):
        # Create Thread
        joba = DBSync_Threadjobs(name="joba")
        joba.start()



    def Save_Excelfile(self, PathName):
        # Alternately, you can autofit all rows in the worksheet
        # ws.Rows.AutoFit()
        # ws.columns.AutoFit()
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        excel.Visible = True
        wb = excel.Workbooks.Add()

        # select sheet and rename
        #ws = wb.Worksheets("Sheet1")
        #ws.Name = "RenameSheet"

        # Add worksheet....
        ws = wb.Worksheets.Add()
        ws.Name = "MySheet3"
        ws = wb.Worksheets.Add()
        ws.Name = "MySheet2"
        ws = wb.Worksheets.Add()
        ws.Name = "MySheet1"

        # select sheet
        ws = wb.Worksheets("MySheet2")

        # Modify Sheet Data..........
        ws.Range("A1:A2").Value = "1 line"
        ws.Rows(1).RowHeight = 60
        ws.Range("2:2").RowHeight = 120
        ws.Rows(1).VerticalAlignment = win32.constants.xlCenter
        ws.Range("2:2").VerticalAlignment = win32.constants.xlCenter
        ws.Cells(1,1).Value = "ss"
        ws.Cells(1,1).Interior.ColorIndex = 3
        wb.Save(PathName)
        excel.Application.Quit()

    def Open_Excelfile(self, PathName):
        # Alternately, you can autofit all rows in the worksheet
        # ws.Rows.AutoFit()
        # ws.columns.AutoFit()
        excel = win32.gencache.EnsureDispatch('Excel.Application')
        excel.Visible = True
        wb = excel.Workbooks.Open(PathName)

        # Get Active Sheet........
        #ws = wb.ActiveSheet

        # select Sheet.........
        ws = wb.Worksheets("MySheet1")
        ws.Cells(1,15).Value = "sssss"
        wb.Save()
        excel.Application.Quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    myWindow.create_Thread_test()
    app.exec_()
