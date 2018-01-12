class poloniex:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret

    def returnTicker(self):
        return {
                    "ETH_BTC":{
                                "last":"0.09632893",
                                "lowestAsk":"0.02589999",
                                "highestBid":"0.0251",
                                "percentChange":"0.02390438",
                                "baseVolume":"6.16485315",
                                "quoteVolume":"245.82513926"
                    },
                    "BTC_NXT":{
                                "last":"0.00005730",
                                "lowestAsk":"0.00005710",
                                "highestBid":"0.00004903",
                                "percentChange":"0.16701570",
                                "baseVolume":"0.45347489",
                                "quoteVolume":"9094"
                    }
        }

    def returnOrderBook(self, currencyPair):
        return  {
                    "asks":[
                            [0.09600000,0.07829428], #BTC 4.30739611 SUM 4.30739611
                            [0.09613640,0.05000000],  #BTC 0.00752693 SUM 0.01477924
                    ],
                    "bids":[
                            [0.09632893,65.71400000], #BTC 6.33015931 SUM 6.33015931
                            [0.09636022,66.07000000], #BTC 6.36651974 SUM 6.39156527
                    ],
                    "isFrozen": 0,
                    "seq": 18849
        }

    def returnOpenOrders(self,currencyPair):
        return  [
                    {
                        "orderNumber":"154407998",
                        "type":"sell",
                        "rate":"0.025",
                        "amount":"100",
                        "total":"2.5"
                    },
                    {
                        "orderNumber":"120467",
                        "type":"sell",
                        "rate":"0.04",
                        "amount":"100",
                        "total":"4"
                    }, 
        ]

    def returnTradeHistory(self,currencyPair):
        return  [
                    { 
                        "globalTradeID": 25129732, 
                        "tradeID": "6325758", 
                        "date": "2016-04-05 08:08:40", 
                        "rate": "0.02565498", 
                        "amount": "0.10000000", 
                        "total": "0.00256549", 
                        "fee": "0.00200000", 
                        "orderNumber": "124124124", 
                        "type": "sell", 
                        "category": "exchange" 
                    },
                    { 
                        "globalTradeID": 25129628, 
                        "tradeID": "6325741", 
                        "date": "2016-04-05 08:07:55", 
                        "rate": "0.02565499", 
                        "amount": "0.10000000", 
                        "total": "0.00256549", 
                        "fee": "0.00200000", 
                        "orderNumber": "34225195693", 
                        "type": "buy", 
                        "category": "exchange" 
                    },
        ]

    def marginBuy(self, currencyPair, rate, amount):
        return  {
                    "success":1,
                    "message":"Margin order placed.",
                    "orderNumber":"154407998",
                    "resultingTrades":{
                                        str(currencyPair): [
                                                        {
                                                            "amount":"1.00000000",
                                                            "date":"2015-05-10 22:47:05",
                                                            "rate":str(rate),
                                                            "total":str(amount),
                                                            "tradeID":"1213556",
                                                            "type":"buy"
                                                        }
                                        ]
                    }
        }
   
    def marginSell(self, currencyPair, rate, amount):
        return {
                    "success":1,
                    "message":"Margin order placed.",
                    "orderNumber":"154407998",
                    "resultingTrades":{
                                        str(currencyPair): [
                                                        {
                                                            "amount":"1.00000000",
                                                            "date":"2015-05-10 22:47:05",
                                                            "rate":str(rate),
                                                            "total":str(amount),
                                                            "tradeID":"1213556",
                                                            "type":"sell"
                                                        }
                                        ]
                    }
        }

    def closeMarginPosition(self, currencyPair):
        return {
                    "success":1,
                    "message":"Successfully closed margin position.",
                    "resultingTrades":{
                                        str(currencyPair):[
                                                            {
                                                                "amount":"7.09215901",
                                                                "date":"2015-05-10 22:38:49",
                                                                "rate":"0.00235337",
                                                                "total":"0.01669047",
                                                                "tradeID":"1213346","type":"sell"
                                                            },
                                                            {
                                                                "amount":"24.00289920",
                                                                "date":"2015-05-10 22:38:49",
                                                                "rate":"0.00235321",
                                                                "total":"0.05648386",
                                                                "tradeID":"1213347",
                                                                "type":"sell"
                                                            }
                                        ]
                    }
        }

    def cancel(self,currencyPair,orderNumber):
        return {
                    "success":1
        }