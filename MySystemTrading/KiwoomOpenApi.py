import os
import time
import copy
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *

import pandas as pd
from pandas import Series, DataFrame
import sqlite3

# 주식 기본정보 Data
stockDB_init_dict = { }

stockDB = {}
stockDB_List = [
    # opt100001
    '종목코드', '종목명', '연중최저', '연중최고', '250일최저', '250일최고', '250최저가대비율', '250최고가대비율', '250최저가일', '250최고가일',
    'PER', 'EPS', 'BPS', 'PBR', 'EV', 'ROE', '시가총액', '상장주식', '시가총액비중', "결산월", "액면가", "자본금", "외진소진률", "매출액",
    "영업이익", "당기순이익", '신용비율', '상한가', '하한가', '현재가', '액면가단위'
    # opt10006
    '시가', '저가', '고가', '종가', '대비', '등락률', '거래량', '거래대금', '체결강도', '회전율',
    # opt10013 신용매매 (신용,대주)
    '신용잔고', '신용잔고증감', '신용잔고율', '신용공여율', '대차잔고', '대차잔고증감', '대차잔고율', '대차공여율',
    # opt10014 공매도 추이
    '공매도량', '공매도비중', '공매도평균가', '공매도거래대금',
    # opt10045 기관/외인 매매 추이
    '기관기간누적', '기관일별순매매수량', '외인기간누적', '외인일별순매매수량', '외인추정평균매수가', '기관추정평균매수가',
    # opt10061 투자자별 순매수 / 순매도 (금액/수량)
    '개인', '외국인', '기관', '금융투자', '보험', '투신', '기타금융', '은행', '연기금', '사모펀드', '국가', '기타법인', '내외국인' ,
    ]


# 주식 기본정보 Data
opt10001_DB = { }
opt10001_DBList = [
    "종목코드", "종목명", "결산월", "액면가", "자본금", "상장주식", "신용비율", "연중최고", "연중최저", "시가총액", "시가총액비중",
    "외진소진률", "대용가", "PER", "EPS", "ROE", "PBR", "EV", "BPS", "매출액", "영업이익", "당기순이익", "250최고", "250최저",
    "시가", "고가", "저가", "상한가", "하한가", "기준가", "예상체결가", "예상체결수량", "250최고가일", "250최저가일", "250최고가대비율",
    "250최저가대비율", "현재가", "대비기호", "전일대비", "등락율", "거래량", "거래대비", "액면가단위",  ]

# opt10006_req - 주식 일/시분 정보
opt10006_DB = { }
opt10006_DBList = [ "시가", "고가", "저가", "종가", "대비", "등락률", "거래량", "거래대금", "체결강도", ]

opt10013_DB = { }
opt10013_DBList = [ "신용잔고", "신용잔고증감", "신용잔고율", "신용공여율", "대차잔고", "대차잔고증감", "대차잔고율", "대차공여율", ]

opt10014_DB = { }
opt10014_DBList = [ "공매도량", "공매도비중", "공매도평균가", "공매도거래대금", ]

# opt10045 기관/외인 매매 추이
opt10045_DB = { }
opt10045_DBList = [ "기관기간누적", "기관일별순매매수량", "외인기간누적", "외인일별순매매수량", "외인추정평균매수가", "기관추정평균매수가" ]

# opt10061 투자자별 순매수 / 순매도 (금액/수량)
opt10061_DB = { }
opt10061_DBList = [ '개인', '외국인', '기관', '금융투자', '보험', '투신', '기타금융', '은행', '연기금', '사모펀드', '국가', '기타법인', '내외국인' , ]

opt10081_DB = []


class KiwoomOpenApi(QAxWidget):
    def __init__(self):
        super().__init__()

        self.connected = False
        self.handle = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        # Login Request Function
        self.handle.dynamicCall("CommConnect()")
        self.handle.OnEventConnect.connect(self.OnEventConnect)

        # void OnReceiveTrData(LPCTSTR sScrNo, LPCTSTR sRQName, LPCTSTR sTrCode, LPCTSTR sRecordName, LPCTSTR sPreNext, LONG nDataLength, LPCTSTR sErrorCode, LPCTSTR sMessage, LPCTSTR sSplmMsg)
        self.handle.OnReceiveTrData.connect(self.OnReceiveTrData)

        # void OnReceiveRealData(LPCTSTR sJongmokCode, LPCTSTR sRealType, LPCTSTR sRealData)
        self.handle.OnReceiveRealData.connect(self.OnReceiveRealData)

        # void OnReceiveMsg(LPCTSTR sScrNo, LPCTSTR sRQName, LPCTSTR sTrCode, LPCTSTR sMsg)
        self.handle.OnReceiveMsg.connect(self.OnReceiveMsg)

        # void OnReceiveChejanData(LPCTSTR sGubun, LONG nItemCnt, LPCTSTR sFidList);
        self.handle.OnReceiveChejanData.connect(self.OnReceiveChejanData)

        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.InitStockInfo()

        '''
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
        '''

    # Login Status Check function
    def OnEventConnect(self, errCode):
        print("OnEventConnect", "(", errCode, ")")
        if errCode == 0:
            print("connected")
            self.connected = True
        else:
            self.connected = False
            print("disconnected")

    def GetStockInfo(self, reqID) :
        if(reqID == 'ALL') :
            return stockDB
        elif(reqID == 'opt10001') :
            return opt10001_DB
        elif(reqID == 'opt10006') :
            return opt10006_DB
        elif(reqID == 'opt10013') :
            return opt10013_DB
        elif(reqID == 'opt10014') :
            return opt10014_DB
        elif(reqID == 'opt10045') :
            return opt10045_DB
        elif(reqID == 'opt10061') :
            return opt10061_DB
        elif(reqID == 'opt10081') :
            return opt10081_DB
            return

    def InitStockInfo(self) :
        stockDB = { }
        opt10001_DB = { }
        opt10006_DB = { }
        opt10013_DB = { }
        opt10014_DB = { }
        opt10045_DB = { }
        opt10061_DB = { }
        opt10081_DB = [ ]



    # Request opt00001 - 기본 정보
    def request_opt10001_GetStockBasicInfo(self, code) :
        self.SetInputValue("종목코드", code)
        self.CommRqData("opt10001_req", "opt10001", "0", "0101")

    # opt10006_req - 주식 일/시분 정보
    def request_opt10006_GetStockBasicInfo(self, code) :
        self.SetInputValue("종목코드", code)
        self.CommRqData("opt10006_req", "opt10006", "0", "0101")

    # opt10013 신용매매 (신용)
    def request_opt10013_DebtTransactionInfo(self, code, date, mode = 1) :
        self.SetInputValue("종목코드", code)
        self.SetInputValue("일자"	,  date);
        # 조회구분 = 1:융자, 2:대주
        if(mode != 1) : mode = 2
        self.SetInputValue("조회구분"	,  str(mode));
        self.CommRqData("opt10013_req1", "opt10013", "0", "0101")

    # opt10014 공매도 추이
    def request_opt10014_DebtSellTransactionInfo(self, code, startDate, endDate) :
        self.SetInputValue("종목코드"	,  code);
        # 시간구분 = 0:시작일, 1:기간
        self.SetInputValue("시간구분"	,  '1');
        self.SetInputValue("시작일자"	,  startDate);
        self.SetInputValue("종료일자"	,  endDate);
        self.CommRqData("opt10014_req", "opt10014", "0", "0101")

    # opt10045 기관/외인 매매 추이
    def request_opt10045_OrgForeignBuynSellInfo(self, code, startDate, endDate, organ = 1, foriegn = 1) :
        self.SetInputValue("종목코드"	,  code);
        self.SetInputValue("시작일자"	,  startDate);
        self.SetInputValue("종료일자"	,  endDate);
        # 기관추정단가구분 = 1:매수단가, 2:매도단가
        if(organ != 1) : organ = 2
        self.SetInputValue("기관추정단가구분"	,  str(organ));
        # 외인추정단가구분 = 1:매수단가, 2:매도단가
        if(foriegn != 1) : foriegn = 2
        self.SetInputValue("외인추정단가구분"	,  str(foriegn));
        self.CommRqData( "opt10045_req"	,  "opt10045"	,  "0"	,  "0101");

    # opt10061 투자자별 순매수 / 순매도 (금액/수량)
    def request_opt10061_EachGroupBuynSellInfo(self, code, startDate, endDate, unit = 2, diff = 0, scale = 1) :
        self.SetInputValue("종목코드"	,  code);
        self.SetInputValue("시작일자"	,  startDate);
        self.SetInputValue("종료일자"	,  endDate);
        # 금액수량구분 = 1:금액, 2:수량
        if(unit != 1) : unit = 2
        self.SetInputValue("금액수량구분"	,  str(unit));
        # 매매구분 = 0:순매수, 1:매수, 2:매도
        if(diff > 2) : diff = 0
        self.SetInputValue("매매구분"	,  str(diff));
        # 단위구분 = 1000:천주, 1:단주
        if(scale != 1) : scale = 1000
        self.SetInputValue("단위구분"	,  str(scale));
        self.CommRqData( "opt10061_req"	,  "opt10061"	,  "0"	,  "0101");

    # Get Daily Chart Info
    #수정주가구분 = 0 or 1, 수신데이터 1:유상증자, 2:무상증자, 4:배당락, 8:액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락
    def request_opt10081_GetDailyChartInfo(self, code, startDate) :
        self.SetInputValue("종목코드"	,  code);
        self.SetInputValue("기준일자"	,  startDate);
        self.SetInputValue("수정주가구분"	,  0);
        self.CommRqData("opt10081_req1", "opt10081", 0, "0101")
        #self.CommRqData("opt10081_req2", "opt10081", 0, "0101")

    #==================================================================================================================
    # opt10001_req - 주식 기본정보
    # self.kiwoom.SetInputValue("종목코드", code)
    # self.kiwoom.CommRqData("opt10001_req", "opt10001", 0, "0101")
    #==================================================================================================================
    def opt10001_GetStockBasicInfo(self, RQName, TrCode) :
        opt10001_selectionList = [ '종목코드', '종목명', '연중최저', '연중최고', '250최저', '250최고', '250최저가대비율',
                                    '250최고가대비율', '250최저가일', '250최고가일', 'PER', 'EPS', 'BPS', 'PBR', 'EV', 'ROE',
                                    '시가총액', '상장주식', '시가총액비중', "결산월", "액면가", "자본금", "외진소진률", "매출액",
                                    "영업이익", "당기순이익", '신용비율', '상한가', '하한가', '현재가', '액면가단위', ]

        for key in opt10001_DBList :
            opt10001_DB[key] = (self.CommGetData(TrCode, "", RQName, 0, key))

        for key in opt10001_selectionList :
            stockDB[key] = self.CommGetData(TrCode, "", RQName, 0, key)


    #==================================================================================================================
    # opt10006_req - 종목별 가격 및 거래량, 등락정보
    # self.kiwoom.SetInputValue("종목코드", code)
    # self.kiwoom.CommRqData("opt10006_req", "opt10006", 0, "0101")
    #==================================================================================================================
    def opt10006_GetPriceAmounts(self, RQName, TrCode) :
        # opt10006_req - 주식 일/시분 정보
        for key in opt10006_DBList :
            opt10006_DB[key] = self.CommGetData(TrCode, "", RQName, 0, key)
            stockDB[key] = self.CommGetData(TrCode, "", RQName, 0, key)

    #==================================================================================================================
    # opt10013 신용매매 (신용,대주) - 지정일로부터 100개 표시
    # self.kiwoom.SetInputValue("종목코드", code)
    # self.kiwoom.SetInputValue("일자"	,  "20180412");
    # self.kiwoom.SetInputValue("조회구분"	,  1); - 조회구분 = 1:융자, 2:대주
    # self.kiwoom.CommRqData("opt10013_req1", "opt10013", 0, "0101")
    #==================================================================================================================
    def opt10013_DebtTransactionInfo(self, RQName, TrCode, getCurrent = True) :
        querylist = [ "잔고", "대비", "잔고율", "공여율", ]
        keya = [ "신용잔고", "신용잔고증감", "신용잔고율", "신용공여율", ]
        keyb = [ "대차잔고", "대차잔고증감", "대차잔고율", "대차공여율", ]
        cnt = self.GetRepeatCnt(TrCode, RQName)
        print("opt10013_req1 count =", cnt)
        if(getCurrent) :
            if(RQName == 'opt10013_req1'):
                index = 0
                for key in keya :
                    stockDB[key] = (self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                    opt10013_DB[key] = (self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                    index += 1
            elif(RQName == 'opt10013_req2'):
                index = 0
                for key in keyb :
                    stockDB[key] = (self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                    opt10013_DB[key] = (self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                    index += 1
            else :
                pass
        else :
            if(RQName == 'opt10013_req1'):
                index = 0
                for key in keya :
                    opt10013_DB[key] = []
                    for i in range(cnt):
                        opt10013_DB[key].append(self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                    index += 1
            elif(RQName == 'opt10013_req2'):
                index = 0
                for key in keyb :
                    opt10013_DB[key] = []
                    for i in range(cnt):
                        opt10013_DB[key].append(self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                    index += 1
            else :
                pass
        pass

    #==================================================================================================================
    # opt10014 공매도 추이 - 지정일로부터 100개 표시
    # opt10014 공매도 추이
    # self.kiwoom.SetInputValue("종목코드"	,  code);
    # 시간구분 = 0:시작일, 1:기간
    # self.kiwoom.SetInputValue("시간구분"	,  1);
    # self.kiwoom.SetInputValue("시작일자"	,  '20180412');
    # self.kiwoom.SetInputValue("종료일자"	,  '20180412');
    # self.kiwoom.CommRqData("opt10014_req", "opt10014", 0, "0101")
    #==================================================================================================================
    def opt10014_DebtSellTransactionInfo(self, RQName, TrCode, getCurrent = True) :
        querylist = [ "공매도량",  "매매비중", "공매도평균가", "공매도거래대금", ]
        cnt = self.GetRepeatCnt(TrCode, RQName)
        print("opt10014_req count =", cnt)
        index = 0
        if(getCurrent) :
            for key in opt10014_DBList :
                stockDB[key] = (self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                opt10014_DB[key] = (self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                index += 1
        else :
            for key in opt10014_DBList :
                opt10014_DB[key] = []
                for i in cnt :
                    opt10014_DB[key].append(self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                index += 1
        pass


    #==================================================================================================================
    # opt10045 기관/외인 매매 추이
    # self.kiwoom.SetInputValue("종목코드"	,  code);
    # self.kiwoom.SetInputValue("시작일자"	,  '20180412');
    # self.kiwoom.SetInputValue("종료일자"	,  '20180412');
    # 기관추정단가구분 = 1:매수단가, 2:매도단가
    # self.kiwoom.SetInputValue("기관추정단가구분"	,  1);
    # 외인추정단가구분 = 1:매수단가, 2:매도단가
    # self.kiwoom.SetInputValue("외인추정단가구분"	,  1);
    # self.kiwoom.CommRqData( "opt10045_req"	,  "opt10045"	,  "0"	,  "0101");
    #==================================================================================================================
    def opt10045_OrgForeignBuynSellInfo(self, RQName, TrCode, getCurrent = True) :
        querylist = [ "기관기간누적",  "기관일별순매매수량", "외인기간누적", "외인일별순매매수량", "외인추정평균가", "기관추정평균가", ]
        cnt = self.GetRepeatCnt(TrCode, RQName)
        print("opt10045_req count =", cnt)
        if(getCurrent) :
            index = 0
            for key in opt10045_DBList :
                stockDB[key] = (self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                opt10045_DB[key] = (self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                index += 1
        else :
            index = 0
            for key in opt10045_DBList :
                opt10045_DB[key] = []
                for i in cnt :
                    opt10045_DB[key].append(self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                index += 1
        pass


    #==================================================================================================================
    # opt10061 투자자별 순매수 / 순매도 (금액/수량)
    # self.kiwoom.SetInputValue("종목코드"	,  code);
    # self.kiwoom.SetInputValue("시작일자"	,  '20180412');
    # self.kiwoom.SetInputValue("종료일자"	,  '20180412');
    # 금액수량구분 = 1:금액, 2:수량
    # self.kiwoom.SetInputValue("금액수량구분"	,  2);
    # 매매구분 = 0:순매수, 1:매수, 2:매도
    # self.kiwoom.SetInputValue("매매구분"	,  0);
    # 단위구분 = 1000:천주, 1:단주
    # self.kiwoom.SetInputValue("단위구분"	,  1);
    # self.kiwoom.CommRqData( "opt10061_req"	,  "opt10061"	,  "0"	,  "0101");
    #==================================================================================================================
    def opt10061_EachGroupBuynSellInfo(self, RQName, TrCode, getCurrent = True) :
        querylist = [ "개인투자자",  "외국인투자자", "기관계", "금융투자", "보험", "투신", "기타금융", "은행", "연기금등", "사모펀드", "국가", "기타법인", "내외국인" ]
        cnt = self.GetRepeatCnt(TrCode, RQName)
        print("opt10061_req count =", cnt)
        if(getCurrent) :
            index = 0
            for key in opt10061_DBList :
                stockDB[key] = (self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                opt10061_DB[key] = (self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                index += 1
        else :
            index = 0
            for key in opt10061_DBList :
                opt10061_DB[key] = []
                for i in cnt :
                    opt10061_DB[key].append(self.CommGetData(TrCode, "", RQName, 0, querylist[index]))
                index += 1
        pass



    #==================================================================================================================
    # opt10081 Get Daily Chart Info
    #==================================================================================================================
    def opt10081_GetDailyChartInfo(self, RQName, TrCode) :
        colName = ['종목코드', '현재가', '거래량', '거래대금', '일자', '시가', '고가', '저가',
                   '수정주가구분', '수정비율', '대업종구분', '소업종구분', '종목정보', '수정주가이벤트', '전일종가']
        cnt = self.GetRepeatCnt(TrCode, RQName)
        print("opt10081_req count =", cnt)
        global opt10081_DB
        opt10081_DB = self.GetCommDataEx(TrCode, "주식일봉차트조회")
        pass
    #==================================================================================================================
    # OnReceiveTrData : Transaction Data 수신 처리 함수
    #==================================================================================================================
    def OnReceiveTrData(self, ScrNo, RQName, TrCode, RecordName, PrevNext, DataLength, ErrorCode, Message, SplmMsg):
        print("OnReceiveTrData", "(", ScrNo, RQName, TrCode, RecordName, PrevNext, DataLength, ErrorCode, Message, SplmMsg, ")")
        self.prev_next = PrevNext
        print("PreNext = ", self.prev_next)
        # opt10001_req - 주식기본정보
        if RQName == "opt10001_req":
            self.opt10001_GetStockBasicInfo(RQName, TrCode)
            pass

        # opt10006_req - 종목별 가격 및 거래량, 등락정보
        if RQName == "opt10006_req":
            self.opt10006_GetPriceAmounts(RQName, TrCode)
            pass

        # opt10013 신용매매 (신용,대주) - 지정일로부터 100개 표시
        if RQName == "opt10013_req1" or RQName == "opt10013_req2":
            self.opt10013_DebtTransactionInfo(RQName, TrCode, True)
            pass

        # opt10014 공매도 추이
        if RQName == "opt10014_req":
            self.opt10014_DebtSellTransactionInfo(RQName, TrCode, True)
            pass

        # opt10045 기관/외인 매매 추이
        if RQName == "opt10045_req":
            self.opt10045_OrgForeignBuynSellInfo(RQName, TrCode, True)
            pass

        # opt10061 투자자별 순매수 / 순매도 (금액/수량)
        if RQName == "opt10061_req":
            self.opt10061_EachGroupBuynSellInfo(RQName, TrCode, True)
            pass



        # 예수금 현황 상세 정보 요청 : 예수금 현황
        if RQName == "opw00001_req":
            estimated_day2_deposit = self.CommGetData(TrCode, "", RQName, 0, "d+2추정예수금")
            estimated_day2_deposit = self.change_format(estimated_day2_deposit)
            self.data_opw00001 = estimated_day2_deposit

        # opt10081 Get Daily Chart Info
        if RQName == "opt10081_req1":
            self.opt10081_GetDailyChartInfo(RQName, TrCode)
            pass

        # opt10081 Get Daily Chart Info
        if RQName == "opt10081_req2":
            cnt = self.GetRepeatCnt(TrCode, RQName)
            for i in range(cnt):
                if i == 0 :
                    self.DailyChartInfo["종목코드"] = self.CommGetData(TrCode, "", RQName, i, "종목코드")
                self.DailyChartInfo["일자"].append(self.CommGetData(TrCode, "", RQName, i, "일자"))
                self.DailyChartInfo["현재가"].append(int(self.CommGetData(TrCode, "", RQName, i, "현재가")))
                self.DailyChartInfo["시가"].append(int(self.CommGetData(TrCode, "", RQName, i, "시가")))
                self.DailyChartInfo["고가"].append(int(self.CommGetData(TrCode, "", RQName, i, "고가")))
                self.DailyChartInfo["저가"].append(int(self.CommGetData(TrCode, "", RQName, i, "저가")))
                self.DailyChartInfo["거래량"].append(int(self.CommGetData(TrCode, "", RQName, i, "거래량")))
                self.DailyChartInfo["거래대금"].append(int(self.CommGetData(TrCode, "", RQName, i, "거래대금")))
                '''
                self.DailyChartInfo["수정주가구분"].append((self.CommGetData(TrCode, "", RQName, i, "수정주가구분")))
                self.DailyChartInfo["수정비율"].append((self.CommGetData(TrCode, "", RQName, i, "수정비율")))
                self.DailyChartInfo["대업종구분"].append((self.CommGetData(TrCode, "", RQName, i, "대업종구분")))
                self.DailyChartInfo["소업종구분"].append((self.CommGetData(TrCode, "", RQName, i, "소업종구분")))
                self.DailyChartInfo["종목정보"].append((self.CommGetData(TrCode, "", RQName, i, "종목정보")))
                self.DailyChartInfo["수정주가이벤트"].append((self.CommGetData(TrCode, "", RQName, i, "수정주가이벤트")))
                self.DailyChartInfo["전일종가"].append((self.CommGetData(TrCode, "", RQName, i, "전일종가")))
                '''
            print("count=", cnt)
            print(self.DailyChartInfo)


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
        pass

    # void OnReceiveRealData(LPCTSTR sJongmokCode, LPCTSTR sRealType, LPCTSTR sRealData)
    def OnReceiveRealData(self, sJongmokCode, sRealType, sRealData):
        print("OnReceiveRealData", "(",sJongmokCode, sRealType, sRealData, ")")

        if sRealType == "주식체결" :
            print("Realtype 1.............")
            self.data = sRealData.split('\t')
            now = time.localtime()
            #ct = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
            ct = time.monotonic()
            self.timetick.append(ct)
            self.RealStockInfo["종목코드"].append(sJongmokCode)
            self.RealStockInfo["체결번호"].append(self.data[0])
            self.RealStockInfo["현재가"].append(self.data[1])
            self.RealStockInfo["전일대비"].append(self.data[2])
            self.RealStockInfo["등락율"].append(self.data[3])
            self.RealStockInfo["매도호가"].append(self.data[4])
            self.RealStockInfo["매수호가"].append(self.data[5])
            self.RealStockInfo["틱채결량"].append(self.data[6])
            self.RealStockInfo["거래량"].append(self.data[7])
            self.RealStockInfo["거래대금_백만"].append(self.data[8])
            self.RealStockInfo["시가"].append(self.data[9])
            self.RealStockInfo["고가"].append(self.data[10])
            self.RealStockInfo["저가"].append(self.data[11])
            self.RealStockInfo["전일대비부족거래량"].append(self.data[13])
            self.RealStockInfo["전일대비거래량비중"].append(self.data[15])
            self.RealStockInfo["체결강도"].append(self.data[18])
            self.RealStockInfo["매도호가총잔량"].append(self.data[18])
            self.RealStockInfo["매수호가총잔량"].append(self.data[18])
            self.index += 1

        if sRealType == "주식호가잔량" :
            print("Realtype 2.............")
            '''
            if (self.index > 1 and self.data[0] == self.RealStockInfo["체결번호"][self.index-1]) :
                print("Add 121, 125 info to RealStockInfo['매수,매도총잔량']")
                selltotal = self.GetCommRealData(sRealType, 121)
                buytotal = self.GetCommRealData(sRealType, 125)
                self.RealStockInfo["매도호가총잔량"].append(selltotal)
                self.RealStockInfo["매수호가총잔량"].append(buytotal)
            '''
        else :
            print("unknown realtype.............")

        if self.index >= 5 :
            filePathName = "E:/workspace/GitHub/systemtrading/MySystemTrading/stockDB_"+sJongmokCode+".db"
            self.saveRealDataToDB(sJongmokCode, filePathName)
            self.Init_RealType_Data()


    def saveRealDataToDB(self, code, filePathName):
        con = sqlite3.connect(filePathName)
        col = list(self.RealStockInfo.keys())
        print(col)
        print(self.timetick)
        print(self.RealStockInfo)
        df_RealStockInfo = DataFrame(self.RealStockInfo, columns = col, index = self.timetick)
        print(df_RealStockInfo)
        # 파라미터	설명
        # name	SQL 테이블 이름으로 파이썬 문자열로 형태로 나타낸다.
        # con	Cursor 객체
        # flavor	사용한 DBMS를 지정할 수 있는데 ‘sqlite’ 또는 ‘mysql’을 사용할 수 있다. 기본값은 ‘sqlite’이다.
        # schema	Schema를 지정할 수 있는데 기본값은 None이다.
        # if_exists	‘fail’, ‘replace’, ‘append’ 중 하나를 사용할 수 있는데 기본값은 ‘fail’이다. ‘fail’은 데이터베이스에 테이블이 존재하는 경우 아무 동작도 수행하지 않는다. ‘replace’는 테이블이 존재하면 기존 테이블을 삭제하고 새로 테이블을 생성한 후 데이터를 삽입한다. ‘append’는 테이블이 존재하면 데이터만을 추가한다.
        # index	DataFrame의 index를 데이터베이스에 칼럼으로 추가할지에 대한 여부를 지정한다. 기본값은 True이다.
        # index_label	인덱스 칼럼에 대한 라벨을 지정할 수 있다. 기본값은 None이다.
        # chunksize	한 번에 써지는 로우의 크기를 정숫값으로 지정할 수 있다. 기본값은 None으로 DataFrame 내의 모든 로우가 한 번에 써진다.
        # dtype	칼럼에 대한 SQL 타입을 파이썬 딕셔너리로 넘겨줄 수 있다.
        df_RealStockInfo.to_sql(code, con, flavor='sqlite', schema=None, if_exists='append', index=True, index_label=None, chunksize=None, dtype=None)

        #cursor = con.cursor()
        #str	str	long	int	int	float	int	int	int	long	long	int	int	int	long	float	float	long	long
        #time	종목코드	ID	현재가	전일대비	등락율	매도호가	매수호가	채결량(틱)	거래량	거래대금(백만)	시가	고가	저가	전일대비 부족거래양	전일대비거래량비중	당일채결강도	매도호가 총잔량	매수호가 총잔량
        #cursor.execute("CREATE TABLE stockInfo(시간 text, 종목코드 text, id int, 현재가 int, 전일대비 int, 등락율 float, 매도호가 int, 매수호가 int, 채결량틱 int, 거래량 int, 거래대금_백만 int, 시가 int, 고가 int, 저가 int, 전일대비부족거래량 int, 전일대비거래량비중 int, 체결강도 float, 매도호가총잔량 int, 매수호가총잔량 int )")
        #cursor.execute("INSERT INTO stockInfo VALUES('16.06.04', '030200', '122234', 97000, 98600, 96900, 98000, 0, 321405, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)")
        #con.commit()
        con.close()

        #PATH = ""
        #os.path.exists("")
        #os.path.isdir("")
        #os.path.isfile("")

    def readRealDataFromDB(self, filename, tablename):
        cmd = 'SELECT * FROMM %s' % tablename
        df_RealStockInfo = pd.read_sql(cmd, con, index_col='index')
        return df_RealStockInfo
        #con = sqlite3.connect(filePathName)
        #cursor = con.cursor()
        #cmd = 'SELECT * FROMM %s' % tablename
        #cursor.execute(cmd)
        #cursor.fetchone()
        #cursor.fetchall()

    # void OnReceiveMsg(LPCTSTR sScrNo, LPCTSTR sRQName, LPCTSTR sTrCode, LPCTSTR sMsg)
    def OnReceiveMsg(self, sRQName, sTrCode, sMsg):
        print("OnReceiveMsg", "(",sRQName, sTrCode, sMsg, ")")
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
        self.handle.dynamicCall("SetInputValue(QString, QString)", sID, sValue)

    #
    def CommRqData(self, sRQName, sTRCode, nPrevNext, sScreenNo):
        print("OnReceiveChejanData", "(", sRQName, sTRCode, nPrevNext, sScreenNo, ")")
        self.handle.dynamicCall("CommRqData(QString, QString, int, QString)", sRQName, sTRCode, nPrevNext, sScreenNo)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    #
    # 1 Tran 데이터  ===  sJongmokCode : Tran명,  sRealType : 사용안함, sFieldName : 레코드명, nIndex : 반복인덱스, sInnerFieldName: 아이템명
    # 2 실시간 데이터 === sJongmokCode : Key Code, sRealType : Real Type, sFieldName : Item Index, nIndex : 사용안함, sInnerFieldName:사용안함
    # 3 체결 데이터  === sJongmokCode : 체결구분, sRealType : “-1”, sFieldName : 사용안함, nIndex : ItemIndex, sInnerFieldName :사용안함
    def CommGetData(self, sJongmokCode, sRealType, sFieldName, nIndex, sInnerFiledName):
        data = self.handle.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sJongmokCode, sRealType,
                                sFieldName, nIndex, sInnerFiledName)
        return data.strip()

    # 확인 필요...
    def GetCommData(self, sTrCode, sRecordName, nIndex, sItemName):
        data = self.handle.dynamicCall("GetCommData(QString, QString, long, QString)", sTrCode, sRecordName,
                                nIndex, sItemName)
        return data.strip()

    def GetCommDataEx(self, sTrCode, sRecordName):
        data = self.handle.dynamicCall("GetCommDataEx(QString, QString)", sTrCode, sRecordName)
        return data


    # 확인 필요...
    def GetCommRealData(self, sRealType, nFid):
        data = self.handle.dynamicCall("GetCommRealData(QString, long)", sRealType, nFid)
        return data.strip()


    # LONG SendOrder( BSTR sRQName, BSTR sScreenNo, BSTR sAccNo, LONG nOrderType, BSTR sCode, LONG nQty, LONG nPrice, BSTR sHogaGb,BSTR sOrgOrderNo)
    # nOrderType : (1:신규매수, 2:신규매도, 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정)
    # sHogaGb : 00:지정가, 03:시장가, 05:조건부지정가, 06:최유리지정가, 07:최우선지정가, 10:지정가IOC, 13:시장가IOC, 16:최유리IOC, 20:지정가FOK, 23:시장가FOK, 26:최유리FOK, 61:장전시간외종가, 62:시간외단일가, 81:장후시간외종가
    def SendOrder(self, sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo):
        self.handle.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", [sRQName, sScreenNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo])

    #
    def GetRepeatCnt(self, sTrCode, sRecordName):
        ret = self.handle.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRecordName)
        return ret

    # sMarket – 0:장내, 3:ELW, 4:뮤추얼펀드, 5:신주인수권, 6:리츠, 8:ETF, 9:하이일드펀드, 10:코스닥, 30:제3시장
    def GetCodeListByMarket(self, sMarket):
        cmd = 'GetCodeListByMarket("%s")' % sMarket
        ret = self.handle.dynamicCall(cmd)
        #return ret
        item_codes = ret.split(';')
        return item_codes

    #
    def GetMasterCodeName(self, strCode):
        cmd = 'GetMasterCodeName("%s")' % strCode
        ret = self.handle.dynamicCall(cmd)
        return ret

    # 업종코드 List 얻어오기
    def GetThemeGroupList(self, nType) :
        cmd = 'GetThemeGroupList("%s")' % nType
        ret = self.handle.dynamicCall(cmd)
        return ret

    # 업종코드 List 얻어오기
    def GetThemeGroupCode(self, nType) :
        cmd = 'GetThemeGroupCode("%s")' % nType
        ret = self.handle.dynamicCall(cmd)
        return ret


    #
    def GetChejanData(self, nFid):
        cmd = 'GetChejanData("%s")' % nFid
        ret = self.handle.dynamicCall(cmd)
        return ret

    #
    def GetConnectState(self):
        ret = self.handle.dynamicCall("GetConnectState()")
        return ret

    # ["ACCNO", "USER_ID", "USER_NAME"]
    def GetLoginInfo(self, info):
        ret = self.handle.dynamicCall("GetLoginInfo(QString)", info)
        return ret

    # sScrNo : Screen 번호, sCodeList : 실시간 등록할 종목 코드 (복수 가능 - "종목1;종목2;....")
    # sFidList : 실시간 등록할 FID ("fid1;fid2;fid3.........")
    # sRealType : 0 - 마지막 등록된 코드만 실시간, 1 - 같은 화면에서 다른종목 추가시 같이 실시간 받음 (추가 개념임)
    def SetRealReg(self, sScrNo, sCodeList, sFidList, sRealType):
        ret = self.handle.dynamicCall("SetRealReg(QString, QString, QString, QString)", sScrNo, sCodeList, sFidList, sRealType)
        return ret

    # sScrNo : Screen 번호, sDelCode : 실시간 해제할 종목
    def SetRealRemove(self, sScrNo, sDelCode):
        ret = self.handle.dynamicCall("SetRealRemove(QString, QString)", sScrNo, sDelCode)
        return ret

    # 화면내 모든 Real Data 요청 제거
    # sScrNo : Screen 번호
    def DisconnectRealData(self, sScrNo):
        self.handle.dynamicCall("DisconnectRealData(QString)", sScrNo)



    #
    def InitOHLCRawData(self):
        self.ohlc = {'date': [], 'open': [], 'high': [], 'low': [], 'close': []}

    #
    def Init_opw00018_data(self):
        self.data_opw00018 = {'single': [], 'multi': [] }

    #
    def Init_RealType_Data(self):
        self.index = 0
        self.timetick = []
        self.RealStockInfo = {
            "종목코드" : [],
            "체결번호" : [],
            "현재가" : [],
            "전일대비" : [],
            "등락율" : [],
            "매도호가" : [],
            "매수호가" : [],
            "틱채결량" : [],
            "거래량" : [],
            "거래대금_백만" : [],
            "시가" : [],
            "고가" : [],
            "저가" : [],
            "전일대비부족거래량" : [],
            "전일대비거래량비중" : [],
            "체결강도" : [],
            "매도호가총잔량" : [],
            "매수호가총잔량" : [] }


        # 주식 일봉 차트 조회
        self.DailyChartInfo = {
            "종목코드" : [],
            "일자" : [],
            "현재가" : [],
            "시가" : [],
            "고가" : [],
            "저가" : [],
            "거래량" : [],
            "거래대금" : [],
            "수정주가구분" : [],
            "수정비율" : [],
            "대업종구분" : [],
            "소업종구분" : [],
            "종목정보" : [],
            "수정주가이벤트" : [],
            "전일종가" : [] }

        # 신용 / 대주거래 현황
        self.ShinyongInfo = {
            "일자" : [],
            "현재가" : [],
            "전일대비기호" : [],
            "전일대비" : [],
            "거래량" : [],
            "신규" : [],
            "상환" : [],
            "잔고" : [],
            "금액" : [],
            "대비" : [],
            "공여율" : [],
            "잔고율" : [] }

        # 공매도 추이요청
        self.GomgmaedoInfo = {
            "일자" : [],
            "종가" : [],
            "전일대비기호" : [],
            "전일대비" : [],
            "등락율" : [],
            "거래량" : [],
            "공매도량" : [],
            "매매비중" : [],
            "공매도거래대금" : [],
            "공매도평균가" : [] }
