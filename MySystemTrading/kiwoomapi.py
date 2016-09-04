import os
import time
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QAxContainer import *
import pandas as pd
from pandas import Series, DataFrame
import sqlite3

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
        print("PreNext = ", self.prev_next)
        # opt10001_req - 주식기본정보
        if RQName == "opt10001_req":
            self.opt10001_data["종목코드"] = self.CommGetData(TrCode, "", RQName, 0, "종목코드")
            self.opt10001_data["종목명"] = self.CommGetData(TrCode, "", RQName, 0, "종목명")
            self.opt10001_data["결산월"] = self.CommGetData(TrCode, "", RQName, 0, "결산월")
            self.opt10001_data["액면가"] = self.CommGetData(TrCode, "", RQName, 0, "액면가")
            self.opt10001_data["자본금"] = self.CommGetData(TrCode, "", RQName, 0, "자본금")
            self.opt10001_data["상장주식"] = self.CommGetData(TrCode, "", RQName, 0, "상장주식")
            self.opt10001_data["신용비율"] = self.CommGetData(TrCode, "", RQName, 0, "신용비율")
            self.opt10001_data["연중최고"] = self.CommGetData(TrCode, "", RQName, 0, "연중최고")
            self.opt10001_data["연중최저"] = self.CommGetData(TrCode, "", RQName, 0, "연중최저")
            self.opt10001_data["시가총액"] = self.CommGetData(TrCode, "", RQName, 0, "시가총액")
            self.opt10001_data["외진소진률"] = self.CommGetData(TrCode, "", RQName, 0, "외진소진률")
            self.opt10001_data["대용가"] = self.CommGetData(TrCode, "", RQName, 0, "대용가")
            self.opt10001_data["PER"] = self.CommGetData(TrCode, "", RQName, 0, "PER")
            self.opt10001_data["EPS"] = self.CommGetData(TrCode, "", RQName, 0, "EPS")
            self.opt10001_data["ROE"] = self.CommGetData(TrCode, "", RQName, 0, "ROE")
            self.opt10001_data["PBR"] = self.CommGetData(TrCode, "", RQName, 0, "PBR")
            self.opt10001_data["EV"] = self.CommGetData(TrCode, "", RQName, 0, "EV")
            self.opt10001_data["BPS"] = self.CommGetData(TrCode, "", RQName, 0, "BPS")
            self.opt10001_data["매출액"] = self.CommGetData(TrCode, "", RQName, 0, "매출액")
            self.opt10001_data["영업이익"] = self.CommGetData(TrCode, "", RQName, 0, "영업이익")
            self.opt10001_data["당기순이익"] = self.CommGetData(TrCode, "", RQName, 0, "당기순이익")
            self.opt10001_data["250최고"] = self.CommGetData(TrCode, "", RQName, 0, "250최고")
            self.opt10001_data["250최저"] = self.CommGetData(TrCode, "", RQName, 0, "250최저")
            self.opt10001_data["시가"] = self.CommGetData(TrCode, "", RQName, 0, "시가")
            self.opt10001_data["고가"] = self.CommGetData(TrCode, "", RQName, 0, "고가")
            self.opt10001_data["저가"] = self.CommGetData(TrCode, "", RQName, 0, "저가")
            self.opt10001_data["상한가"] = self.CommGetData(TrCode, "", RQName, 0, "상한가")
            self.opt10001_data["하한가"] = self.CommGetData(TrCode, "", RQName, 0, "하한가")
            self.opt10001_data["기준가"] = self.CommGetData(TrCode, "", RQName, 0, "기준가")
            self.opt10001_data["예상체결가"] = self.CommGetData(TrCode, "", RQName, 0, "예상체결가")
            self.opt10001_data["예상체결수량"] = self.CommGetData(TrCode, "", RQName, 0, "예상체결수량")
            self.opt10001_data["250최고가일"] = self.CommGetData(TrCode, "", RQName, 0, "250최고가일")
            self.opt10001_data["250최저가일"] = self.CommGetData(TrCode, "", RQName, 0, "250최저가일")
            self.opt10001_data["250최고가대비율"] = self.CommGetData(TrCode, "", RQName, 0, "250최고가대비율")
            self.opt10001_data["현재가"] = self.CommGetData(TrCode, "", RQName, 0, "현재가")
            self.opt10001_data["대비기호"] = self.CommGetData(TrCode, "", RQName, 0, "대비기호")
            self.opt10001_data["전일대비"] = self.CommGetData(TrCode, "", RQName, 0, "전일대비")
            self.opt10001_data["등락율"] = self.CommGetData(TrCode, "", RQName, 0, "등락율")
            self.opt10001_data["거래량"] = self.CommGetData(TrCode, "", RQName, 0, "거래량")
            self.opt10001_data["거래대비"] = self.CommGetData(TrCode, "", RQName, 0, "거래대비")
            self.opt10001_data["액면가단위"] = self.CommGetData(TrCode, "", RQName, 0, "액면가단위")
            #print(self.opt10001_data)
            pass

        # 예수금 현황 상세 정보 요청 : 예수금 현황
        if RQName == "opw00001_req":
            estimated_day2_deposit = self.CommGetData(TrCode, "", RQName, 0, "d+2추정예수금")
            estimated_day2_deposit = self.change_format(estimated_day2_deposit)
            self.data_opw00001 = estimated_day2_deposit

        # 주식 일봉챠트 조회
        if RQName == "opt10081_req":
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

    # void OnReceiveRealData(LPCTSTR sJongmokCode, LPCTSTR sRealType, LPCTSTR sRealData)
    def OnReceiveRealData(self, sJongmokCode, sRealType, sRealData):
        print("OnReceiveRealData", "(",sJongmokCode, sRealType, sRealData, ")")

        if len(sRealType) == 4 :
            print("Realtype 1.............")
            data = sRealData.split('\t')
            now = time.localtime()
            ct = "%04d-%02d-%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
            self.timetick.append[ct]
            self.RealStockInfo["종목코드"].append(sJongmokCode)
            self.RealStockInfo["체결번호"].append(data[0])
            self.RealStockInfo["현재가"].append(data[1])
            self.RealStockInfo["전일대비"].append(data[2])
            self.RealStockInfo["등락율"].append(data[3])
            self.RealStockInfo["매도호가"].append(data[4])
            self.RealStockInfo["매수호가"].append(data[5])
            self.RealStockInfo["틱채결량"].append(data[6])
            self.RealStockInfo["거래량"].append(data[7])
            self.RealStockInfo["거래대금_백만"].append(data[8])
            self.RealStockInfo["시가"].append(data[9])
            self.RealStockInfo["고가"].append(data[10])
            self.RealStockInfo["저가"].append(data[11])
            self.RealStockInfo["전일대비부족거래량"].append(data[13])
            self.RealStockInfo["전일대비거래량비중"].append(data[15])
            self.RealStockInfo["체결강도"].append(data[18])
            self.index += 1

        elif len(sRealType) == 6 :
            print("Realtype 2.............")
            if (self.index > 1 and data[0] == self.RealStockInfo["체결번호"][self.index-1]) :
                print("Add 121, 125 info to RealStockInfo['매수,매도총잔량']")
                selltotal = self.GetCommRealData(sRealType, 121)
                buytotal = self.GetCommRealData(sRealType, 125)
                self.RealStockInfo["매도호가총잔량"].append(selltotal)
                self.RealStockInfo["매수호가총잔량"].append(buytotal)
        else :
            print("unknown realtype.............")

        if i >= 200 :
            filePathName = "D:/workspace/GitHub/systemtrading/MySystemTrading/kospi_"+sJongmokCode+".db"
            self.saveRealDataToDB(sJongmokCode, filePathName)
            self.Init_RealType_Data()


    def saveRealDataToDB(self, code, filePathName):
        con = sqlite3.connect(filePathName)
        col = list(self.RealStockInfo.keys())
        df_RealStockInfo = DataFrame(self.RealStockInfo, columns = col, index = self.timetick)
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
        self.dynamicCall("SetInputValue(QString, QString)", sID, sValue)

    #
    def CommRqData(self, sRQName, sTRCode, nPrevNext, sScreenNo):
        print("OnReceiveChejanData", "(", sRQName, sTRCode, nPrevNext, sScreenNo, ")")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", sRQName, sTRCode, nPrevNext, sScreenNo)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    #
    # 1 Tran 데이터  ===  sJongmokCode : Tran명,  sRealType : 사용안함, sFieldName : 레코드명, nIndex : 반복인덱스, sInnerFieldName: 아이템명
    # 2 실시간 데이터 === sJongmokCode : Key Code, sRealType : Real Type, sFieldName : Item Index, nIndex : 사용안함, sInnerFieldName:사용안함
    # 3 체결 데이터  === sJongmokCode : 체결구분, sRealType : “-1”, sFieldName : 사용안함, nIndex : ItemIndex, sInnerFieldName :사용안함
    def CommGetData(self, sJongmokCode, sRealType, sFieldName, nIndex, sInnerFiledName):
        data = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sJongmokCode, sRealType,
                                sFieldName, nIndex, sInnerFiledName)
        return data.strip()

    # 확인 필요...
    def GetCommData(self, sTrCode, sRecordName, nIndex, sItemName):
        data = self.dynamicCall("GetCommData(QString, QString, long, QString)", sTrCode, sRecordName,
                                nIndex, sItemName)
        return data.strip()

    # 확인 필요...
    def GetCommRealData(self, sRealType, nFid):
        data = self.dynamicCall("GetCommRealData(QString, long)", sRealType, nFid)
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

    # sScrNo : Screen 번호, sCodeList : 실시간 등록할 종목 코드 (복수 가능 - "종목1;종목2;....")
    # sFidList : 실시간 등록할 FID ("fid1;fid2;fid3.........")
    # sRealType : 0 - 마지막 등록된 코드만 실시간, 1 - 같은 화면에서 다른종목 추가시 같이 실시간 받음 (추가 개념임)
    def SetRealReg(self, sScrNo, sCodeList, sFidList, sRealType):
        ret = self.dynamicCall("SetRealReg(QString, QString, QString, QString)", sScrNo, sCodeList, sFidList, sRealType)
        return ret

    # sScrNo : Screen 번호, sDelCode : 실시간 해제할 종목
    def SetRealRemove(self, sScrNo, sDelCode):
        ret = self.dynamicCall("SetRealRemove(QString, QString)", sScrNo, sDelCode)
        return ret

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

        # 주식 기본정보 Data
        self.opt10001_data = {
            "종목코드" : '',
            "종목명" : '',
            "결산월" : '',
            "액면가" : '',
            "자본금" : '',
            "상장주식" : '',
            "신용비율" : '',
            "연중최고" : '',
            "연중최저" : '',
            "시가총액" : '',
            "시가총액비중" : '',
            "외진소진률" : '',
            "대용가" : '',
            "PER" : '',
            "EPS" : '',
            "ROE" : '',
            "PBR" : '',
            "EV" : '',
            "BPS" : '',
            "매출액" : '',
            "영업이익" : '',
            "당기순이익" : '',
            "250최고" : '',
            "250최저" : '',
            "시가" : '',
            "고가" : '',
            "저가" : '',
            "상한가" : '',
            "하한가" : '',
            "기준가" : '',
            "예상체결가" : '',
            "예상체결수량" : '',
            "250최고가일" : '',
            "250최저가일" : '',
            "250최고가대비율" : '',
            "250최저가대비율" : '',
            "현재가" : '',
            "대비기호" : '',
            "전일대비" : '',
            "등락율" : '',
            "거래량" : '',
            "거래대비" : '',
            "액면가단위" : '' }
        '''
        # 주식 기본정보 Data
        self.opt10001_data = {
            "종목코드" : [],
            "종목명" : [],
            "결산월" : [],
            "액면가" : [],
            "자본금" : [],
            "상장주식" : [],
            "신용비율" : [],
            "연중최고" : [],
            "연중최저" : [],
            "시가총액" : [],
            "시가총액비중" : [],
            "외진소진률" : [],
            "대용가" : [],
            "PER" : [],
            "EPS" : [],
            "ROE" : [],
            "PBR" : [],
            "EV" : [],
            "BPS" : [],
            "매출액" : [],
            "영업이익" : [],
            "당기순이익" : [],
            "250최고" : [],
            "250최저" : [],
            "시가" : [],
            "고가" : [],
            "저가" : [],
            "상한가" : [],
            "하한가" : [],
            "기준가" : [],
            "예상체결가" : [],
            "예상체결수량" : [],
            "250최고가일" : [],
            "250최저가일" : [],
            "250최고가대비율" : [],
            "250최저가대비율" : [],
            "현재가" : [],
            "대비기호" : [],
            "전일대비" : [],
            "등락율" : [],
            "거래량" : [],
            "거래대비" : [],
            "액면가단위" : [] }
        '''
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
'''
FID  설명
10  현재가, 체결가, 실시간종가
11  전일 대비
12  등락율
27  (최우선)매도호가
28  (최우선)매수호가
13  누적거래량, 누적첵ㄹ량
14  누적거래대금
16  시가
17  고가
18  저가
25  전일대비기호
26  전일거래량 대비(계약,주)
29  거래대금 증감
30  전일거래량 대비(비율)
31  거래회전율
32  거래비용
311 시가총액(억)

20  체결시간 (HHMMSS)
10  현재가, 체결가, 실시간종가
11  전일 대비
12  등락율
27  (최우선)매도호가
28  (최우선)매수호가
15  거래량, 체결량
13  누적거래량, 누적체결량
14  누적거래대금
16  시가
17  고가
18  저가
25  전일대비 기호
26  전일거래량 대비(계약, 주)
29  거래대금 증감
30  전일거래량 대비(비율)
31  거래회전율
32  거래비용
228 체결강도
311 시가총액(억)
290 장구분
691 K,O 접근도 (ELW조기종료발생 기준가격, 지수)
'''
