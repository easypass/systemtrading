    # Request opt00001 - 기본 정보
    request_opt10001_GetStockBasicInfo(self, code)

    # opt10006_req - 주식 일/시분 정보
    request_opt10006_GetStockBasicInfo(self, code) :

    # opt10013 신용매매 (신용)
    request_opt10013_DebtTransactionInfo(self, code, date, mode = 1) :

    # opt10014 공매도 추이
    request_opt10014_DebtSellTransactionInfo(self, code, startDate, endDate) :

    # opt10045 기관/외인 매매 추이
    request_opt10045_OrgForeignBuynSellInfo(self, code, startDate, endDate, organ = 1, foriegn = 1) :

    # opt10061 투자자별 순매수 / 순매도 (금액/수량)
    request_opt10061_EachGroupBuynSellInfo(self, code, startDate, endDate, unit = 2, diff = 0, scale = 1) :
