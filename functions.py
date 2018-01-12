# -*- coding: utf-8 -*-
from datetime import datetime
from itertools import cycle
from order import Order
from poloniex import poloniex
import json
import time

def checkSecret(secret):
	return len(secret) == 128

def initiateModel(APIKey, i_secret):
	try:
		return poloniex(APIKey, i_secret)
	except:
	    print("Unexpected error:", sys.exc_info()[0])

def askForMarket(polo_model):
	command = raw_input("\nPlease insert a BTC Market for trading or insert (s) for an overview... \n")
	if command == 's':
		printMarkets(polo_model)
	else:
		market = checkMarket(command, polo_model)
		if market:
			return market
	return askForMarket(polo_model)

def printMarkets(polo_model):
	markets = getMarketList(polo_model)
	print("\nMarket List: \n")
	for m in markets:
		print(m)

def getMarketList(polo_model):
	markets = []
	output = polo_model.returnTicker()
	for r in output:
		markets.append(r)
	return markets

def checkMarket(command, polo_model):
	markets = getMarketList(polo_model)
	if not command in markets:
		print("\nNot a valid Market entered, please try again... \n")
		return False
	else:
		return command

def askForAmount():
	command = raw_input("\nPlease insert an amount BTC for trading (e.g. 1.00000000) \n")
	if float(0) < float(getAmount(command)):
		return getAmount(command)
	else:
		print("\nCannot send a trade for 0 BTC, please try again....\n")
		askForAmount()

def getAmount(amount):
	try:
		amount = "{:.8f}".format(float(amount))
		return amount
	except:
		amount = raw_input("\nNot a valid amount, please try again... \n")
		return getAmount(amount)

def askForTrend():
	command = raw_input("\nPlease insert the trend for trading, UP (u) or DOWN (d)... \n")
	if command == Order.UP_TREND or command == Order.DOWN_TREND:
		return command
	else:
		return askForTrend()

def askForFB():
	command = raw_input("\nPlease insert the desired Fibonacci amount for a position (e.g. 1024.50)... \n")
	return getAmount(command)

def askForFBExtra():
	command = raw_input("\nPlease insert the desired extra % on top of the Fibonacci position (e.g. 5) \n")
	try:
		fbExtra = int(command)
		return fbExtra
	except:
		print("\nNot a valid number, please try again...")
		return askForFBExtra()

def getLimitAmount(treshold, percentage, trend_order, record):
	if (trend_order == Order.UP_TREND and record == 'win') or (trend_order == Order.DOWN_TREND and record == 'loss'):
		#if UP, WIN = 5 BOVENOP treshold
		#IF DOWN, LOSS = 5 BOVENOP treshold
		return "{:.8f}".format(float(float(treshold) * (float(1) + (float(percentage)/float(100)))))
	elif(trend_order == Order.UP_TREND and record == 'loss') or (trend_order == Order.DOWN_TREND and record == 'win'):
		#IF UP, LOSS = 5 ONDER treshold
		#IF DOWN, WIN = 5 ONDER treshold
		return "{:.8f}".format(float(float(treshold) * (float(1) - (float(percentage)/float(100)))))

def askForLossLimit(treshold, trend_order):
	command = raw_input("\nPlease insert the desired loss limit in % for the "+Order.trendToString(trend_order)+" trend... (e.g. 5)\n")
	try:
		percentage = int(command)
	except:
		print("\nNot a valid number, please try again...")
		return askForFBExtra()

	lossLimit = getLimitAmount(treshold, percentage, trend_order, 'loss')
	return lossLimit

def askForWinLimit(treshold, trend_order):
	command = raw_input("\nPlease insert the desired win limit in % for the "+Order.trendToString(trend_order)+" trend... (e.g. 5)\n")
	try:
		percentage = int(command)
	except:
		print("\nNot a valid number, please try again...")
		return askForFBExtra()

	winLimit = getLimitAmount(treshold, percentage, trend_order, 'win')
	return winLimit

def askForTimeSlot():
	command = raw_input("\nPlease insert the desired timeslot for the bot to check the data from POLONIEX in MINUTES (e.g. 60)... \n")
	try:
		time = int(command)
		return time
	except:
		print("\nNot a valid amount, please try again...")
		return askForTimeSlot()

def findPosition(polo_model, order_model):
	position = False
	currentPrice = ''
	#loop every timeslot untill we have a position in the market:
	while not position:
		startTime = datetime.now()
		#get current price
		print("\nChecking current price for: "+str(order_model.market)+"....\n")
		currentPrice = getCurrentPrice(polo_model.returnTicker(), order_model.market)
		print(currentPrice)
		#if currentPrice exceeds constant(FB level + extra) (depending on trend if above or below):
		#try:take position (buy or sell depending on trend with extra %)
		if (order_model.trend == Order.UP_TREND and float(currentPrice) >= float(order_model.treshold)) or (order_model.trend == Order.DOWN_TREND and float(currentPrice) <= float(order_model.treshold)):
			position = True
		else:
			#wait for next timeslot
			eTimeMinutes = getElapsedTimeInMinutes(startTime)
			waitForTimeInMinutes(order_model, eTimeMinutes)
	try:
		return takePosition(currentPrice, order_model, polo_model)
	except Exception as e:
		print("\n[error] Something went wrong while taking position...\n")
		print(e)
		return False

def takePosition(current_price, order_model, polo_model):
		print("\nTaking position at: "+current_price)
		#neemt het amount dat je wilt verkopen/kopen
		#kijken bij de SUM(BTC) tot welke regel hij erin past
		#en neem dan de prijs van die regel en verkoop/koop daarvoor
		rightPrice = findOrderPrice(polo_model, order_model)
		if order_model.trend == Order.UP_TREND:
			#buythatshit
			print("\nmargin Buy market: "+str(order_model.market)+" amount: "+str(order_model.amount)+" for price: "+str(rightPrice))
			poloniexOrder = polo_model.marginBuy(order_model.market, rightPrice, (order_model.amount / rightPrice))
		else:
			#sellthatshit
			print("\nmargin Sell market: "+str(order_model.market)+" amount: "+str(order_model.amount)+" for price: "+str(rightPrice))
			poloniexOrder = polo_model.marginSell(order_model.market, rightPrice, (order_model.amount / rightPrice))
		print("\n TESTING ----------------------")
		print(poloniexOrder)
		print("\n TESTING ----------------------")
		#for testing purpose:
		# poloniexOrder = {}
		# poloniexOrder['success'] = 1
		# poloniexOrder['orderNumber'] = "test"
		# poloniexOrder['date'] = datetime.now()
		if poloniexOrder['success'] == 1:
			orderNumber = poloniexOrder['orderNumber']
			# orderDate = poloniexOrder['date']
			order_model.order_number = orderNumber
			# order_model.order_date = orderDate
			print("\nOrder has been placed successfully, order#: "+str(orderNumber)+"\n")
			return True
		else:
			print("\n[error] Order has NOT been placed successfully\n")
			print(poloniexOrder)
			return False

def findOrderPrice(polo_model, order_model):
	print("\nFinding correct price to: ")
	try:
		#neem alle orders voor een market van de API en pak alleen de BUY of SELL orders afhankelijk van de trend
		orderBook = polo_model.returnOrderBook(order_model.market)
		if order_model.trend == Order.UP_TREND:
			print("BUY "+str(order_model.amount))
			orderBook = cycle(orderBook['asks'])
		else:
			print("SELL "+str(order_model.amount))
			orderBook = cycle(orderBook['bids'])
		#Nu blijven wij zoeken in de oders (beginnen bovenaan) totdat de order die wij willen maken gelijk in 1 van de Sell/buy orders past
		fit = False
		bottomPrice = 0
		askAmount = 0
		while not fit:
			ask = next(orderBook)
			askAmount += float(ask[0]) * float(ask[1])
			print("\nNext order:")
			print("Price: \t\t"+str(ask[0]))
			print("Amount: \t"+str(ask[1]))
			print("SUM BTC: \t\t"+"{:.8f}".format(askAmount))
			if float(askAmount) >= float(order_model.amount):
				print("\nThis order FITS the amount at price: "+str(ask[0]))
				fit = True
				bottomPrice = "{:.8f}".format(float(ask[0]))
		return bottomPrice
	except Exception as e:
		print(e)
		return False

def validatePosition(polo_model, order_model):
	orderNumber= order_model.order_number
	print("\nStarting validation for order#: "+str(orderNumber))
	#loop untill validation for position
	#if after 10 minutes no validation, cancel order
	validation = False
	startTime = datetime.now()
	while not validation:
		#check openorderlijst of order# er niet meer in staat (afgehandeld)
		#en tradehistorylijst voor 1 keer order (een trade gedaan voor die order)
		#doorgaan met programma
		openOrderList = polo_model.returnOpenOrders(order_model.market)
		tradeHistoryList = polo_model.returnTradeHistory(order_model.market)
		#als niet in openorderlijst en niet in trade history dan is er iets fout
		#als niet in openorderlijst en WEL in trade history dan is ie klaar
		if not checkOrderNumberInList(orderNumber, openOrderList):
			if not checkOrderNumberInList(orderNumber, tradeHistoryList):
				print("\nOrder is NOT found in OPENORDERLIST and NOT found in TRADEHISTORYLIST, aborting...")
				return False
			else:
				print("\nOrder is fully validated...")
				validation = True
		#als wel in openorderlijst dan wachten..
		else:
			eTimeMinutes = getElapsedTimeInMinutes(startTime)
			if eTimeMinutes >= 1:
				#na 10 minuten cancel openorders
				cancelOrder(polo_model, order_model, orderNumber)
				#kijken of er trades zijn gedaan -> positie hebben -> doorgaan
				#anders geen positie -> stoppen met programma
				if checkOrderNumberInList(orderNumber, tradeHistoryList):
					print("\nTrades found for order, position has been taken, continue with program...")
					validation = True
				else:
					print("\nNo trades found, aborting program...")
					return False
	return validation

def cancelOrder(polo_model, order_model, orderNumber):
	action = False
	while not action:
		cancel = polo_model.cancel(order_model.market,orderNumber)
		if cancel['success'] != 1:
			print("\nOrder cancel has gone wrong, please confirm manually...")
		else:
			print("\nOrder has been successfully canceled...")
			action = True

def checkOrderNumberInList(order_number, list):
	for o in list:
		if str(order_number) == str(o['orderNumber']):
			return True
	return False

def getElapsedTimeInMinutes(start_time):
	elapsedTime = datetime.now()
	eTimeMinutes = (elapsedTime - start_time).total_seconds() / 60
	return eTimeMinutes

def waitForTimeInMinutes(order_model, eTimeMinutes):
	remainingTime = (order_model.timeslot - eTimeMinutes)
	if remainingTime > 0:
		print("\n Waiting for: "+str(remainingTime)+" minutes....")
		time.sleep(remainingTime*60)

def finalizePosition(polo_model, order_model):
	liquidize = False
	#loop every timeslot untill position greater or less then constant(loss/win) limit -> liquidize
	#else wait...
	while not liquidize:
		print("\nChecking current price for: "+str(order_model.market)+"....\n")
		startTime = datetime.now()
		currentPrice = getCurrentPrice(polo_model.returnTicker(), order_model.market)
		if positionInRange(order_model, currentPrice):
			print("\nCurrent price is in range, liquidizing... at "+str(currentPrice))
			liquidize = True
		else:
			eTimeMinutes = getElapsedTimeInMinutes(startTime)
			waitForTimeInMinutes(order_model, eTimeMinutes)
	#close position
	return closePosition(polo_model, order_model)

def closePosition(polo_model, order_model):
	close = polo_model.closeMarginPosition(order_model.market)
	if close['success'] != 1:
		print("\nClosing the margin position has gone wrong...")
		print(close)
		return False
	else:
		print("\nSuccessfully closed the margin position...")
		return True

def positionInRange(order_model, current_price):
	if order_model.trend == Order.UP_TREND: return ((current_price >= order_model.win_limit) or ((current_price <= order_model.loss_limit) and (current_price > (order_model.loss_limit / 1.05))))
	else: return ((current_price <= order_model.win_limit) or ((current_price >= order_model.loss_limit) and (current_price < (order_model.loss_limit * 1.05))))

def getCurrentPrice(markets, d_market):
	for r in markets:
		if r == d_market:
			return markets[r]['last']

