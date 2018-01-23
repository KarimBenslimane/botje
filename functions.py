# -*- coding: utf-8 -*-
from datetime import datetime
from order import Order
from testpoloniex import poloniex
import json
import time
import logging
import math

# create logger
module_logger = logging.getLogger('main_bot.functions')
profit_logger = logging.getLogger('profit_log.functions')

def checkSecret(secret):
	return len(secret) == 128

def initiateModel(APIKey, i_secret):
	try:
		return poloniex(APIKey, i_secret)
	except:
		module_logger.debug('Unexpected error while creating poloniex model')
		print("[error] Unexpected error:", sys.exc_info()[0])

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
		print("\n[error] Not a valid Market entered, please try again... \n")
		return False
	else:
		return command

def askForAmount():
	command = raw_input("\nPlease insert an amount BTC for trading (e.g. 1.00000000) \n")
	if float(0) < float(getAmount(command)):
		return getAmount(command)
	else:
		print("\n[error] Cannot send a trade for 0 BTC, please try again....\n")
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
		print("\n[error] Not a valid number, please try again...")
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
		print("\n[error] Not a valid number, please try again...")
		return askForFBExtra()

	lossLimit = getLimitAmount(treshold, percentage, trend_order, 'loss')
	return lossLimit

def askForWinLimit(treshold, trend_order):
	command = raw_input("\nPlease insert the desired win limit in % for the "+Order.trendToString(trend_order)+" trend... (e.g. 5)\n")
	try:
		percentage = int(command)
	except:
		print("\n[error] Not a valid number, please try again...")
		return askForFBExtra()

	winLimit = getLimitAmount(treshold, percentage, trend_order, 'win')
	return winLimit

def askForTimeSlot():
	command = raw_input("\nPlease insert the desired timeslot for the bot to check the data from POLONIEX in MINUTES (e.g. 60)... \n")
	try:
		time = int(command)
		return time
	except:
		print("\n[error] Not a valid amount, please try again...")
		return askForTimeSlot()

def findPosition(polo_model, order_model):
	try:
		position = False
		currentPrice = ''
		#loop every timeslot untill we have a position in the market:
		while not position:
			startTime = datetime.now()
			#get current price
			currentPrice = getPositionPrice(polo_model, order_model)
			if currentPrice:
				print("\nChecking current price for: "+str(order_model.market)+", price is: "+str(currentPrice)+"....")
				module_logger.info("[FINDPOSITION]Checking current price for: "+str(order_model.market)+", price is: "+str(currentPrice))
				#if currentPrice exceeds constant(FB level + extra) (depending on trend if above or below):
				#try:take position (buy or sell depending on trend with extra %)
				if (order_model.trend == Order.UP_TREND and float(currentPrice) >= float(order_model.treshold)) or (order_model.trend == Order.DOWN_TREND and float(currentPrice) <= float(order_model.treshold)):
					module_logger.info("found a position at price: "+str(currentPrice))
					position = True
				else:
					#wait for next timeslot
					eTimeMinutes = getElapsedTimeInMinutes(startTime)
					waitForTimeInMinutes(order_model, eTimeMinutes)
		return takePosition(currentPrice, order_model, polo_model)
	except Exception as e:
		print("\n[error] Something went wrong while finding position...")
		module_logger.debug("[error] Something went wrong while finding position...")
		raise e
		return False

def takePosition(current_price, order_model, polo_model):
	try:
		module_logger.info('starting to take position')
		print("\nTaking position at: "+str(current_price))
		#neemt het amount dat je wilt verkopen/kopen
		#kijken bij de SUM(BTC) tot welke regel hij erin past
		#en neem dan de prijs van die regel en verkoop/koop daarvoor
		rightPrice = findOrderPrice(polo_model, order_model)
		if rightPrice:
			if order_model.trend == Order.UP_TREND:
				#buythatshit
				module_logger.info("buying: "+str(order_model.market)+" amount: "+str(order_model.amount)+" for price: "+str(rightPrice))
				print("\nmargin Buy market: "+str(order_model.market)+" amount: "+str(order_model.amount)+" for price: "+str(rightPrice))
				poloniexOrder = polo_model.marginBuy(order_model.market, rightPrice, (float(order_model.amount) / float(rightPrice)))
			else:
				#sellthatshit
				module_logger.info("selling:  "+str(order_model.market)+" amount: "+str(order_model.amount)+" for price: "+str(rightPrice))
				print("\nmargin Sell market: "+str(order_model.market)+" amount: "+str(order_model.amount)+" for price: "+str(rightPrice))
				poloniexOrder = polo_model.marginSell(order_model.market, rightPrice, (float(order_model.amount) / float(rightPrice)))
			if 'orderNumber' in poloniexOrder:
				orderNumber = poloniexOrder['orderNumber']
				order_model.position_trades = poloniexOrder['resultingTrades']
				order_model.order_number = orderNumber
				order_model.position = rightPrice
				module_logger.info("order has been placed")
				print("\nOrder has been placed successfully, order#: "+str(orderNumber))
				return True
			else:
				module_logger.debug("[error] Order has NOT been placed successfully...")
				print("\n[error] Order has NOT been placed successfully...")
				print(poloniexOrder)
		else:
			module_logger.debug("[error] cannot find the right price")
			print("\n[error] Something went wrong while finding order price... aborting")
	except Exception, e:
		print("\n[error] Something went wrong while taking position...")
		module_logger.debug("[error] Something went wrong while taking position...")
		raise e
	return False
		

def findOrderPrice(polo_model, order_model):
	module_logger.info('starting to find the right order price')
	print("\nFinding correct price to: ")
	try:
		#neem alle orders voor een market van de API en pak alleen de BUY of SELL orders afhankelijk van de trend
		orderBook = polo_model.returnOrderBook(order_model.market)
		if order_model.trend == Order.UP_TREND:
			print("BUY "+str(order_model.amount))
			orderBook = iter(orderBook['asks'])
		else:
			print("SELL "+str(order_model.amount))
			orderBook = iter(orderBook['bids'])
		#Nu blijven wij zoeken in de oders (beginnen bovenaan) totdat de order die wij willen maken gelijk in 1 van de Sell/buy orders past
		fit = False
		bottomPrice = 0
		askAmount = 0
		while not fit:
			try:
				ask = next(orderBook)
			except Exception as e:
				module_logger.debug('[error] Amount does not fit in orders')
				print("\n[error] Amount does not fit in orders... aborting")
				return False
			askAmount += float(ask[0]) * float(ask[1])
			logOrderPrice(ask, askAmount)
			if float(askAmount) >= float(order_model.amount):
				module_logger.info('Found order that fits the amount at price: '+str(ask[0]))
				print("\nThis order FITS the amount at price: "+str(ask[0]))
				fit = True
				bottomPrice = "{:.8f}".format(float(ask[0]))
		return bottomPrice
	except Exception as e:
		module_logger.debug("[error] Finding the order price went wrong")
		print("\n[error] Something went wrong while finding the order price...")
		raise e
	return False

def logOrderPrice(ask, askAmount):
	print("\nNext order:")
	print("Price: \t\t"+str(ask[0]))
	print("Amount: \t"+str(ask[1]))
	print("SUM BTC: \t\t"+"{:.8f}".format(askAmount))

def validatePosition(polo_model, order_model):
	try:
		orderNumber= order_model.order_number
		module_logger.info("Validating ordernumber:"+str(orderNumber))
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
					module_logger.debug("[error] order is not found in openorderlist and not found in tradehistorylist")
					print("\n[error] Order is NOT found in OPENORDERLIST and NOT found in TRADEHISTORYLIST, aborting...")
					return False
				else:
					module_logger.info("order is fully validated")
					print("\nOrder is fully validated...")
					validation = True
			#als wel in openorderlijst dan wachten..
			else:
				eTimeMinutes = getElapsedTimeInMinutes(startTime)
				if eTimeMinutes >= 10:
					#na 10 minuten cancel openorders
					module_logger.info("10 minutes have passed and order is still open")
					cancelOrder(polo_model, order_model, orderNumber)
					#kijken of er trades zijn gedaan -> positie hebben -> doorgaan
					#anders geen positie -> stoppen met programma
					if checkOrderNumberInList(orderNumber, tradeHistoryList):
						module_logger.info("trades found for order, position has been taken, continue with program")
						print("\nTrades found for order, position has been taken, continue with program...")
						validation = True
					else:
						module_logger.debug("[error] no trades found, aborting program")
						print("\n[error] No trades found, aborting program...")
						return False
		return validation
	except Exception, e:
		print("\n[error] Something went wrong while validating position...")
		module_logger.debug("[error] Something went wrong while validating position...")
		raise e
		return False
	
def cancelOrder(polo_model, order_model, orderNumber):
	module_logger.info("cancelling order")
	action = False
	while not action:
		cancel = polo_model.cancel(order_model.market,orderNumber)
		if cancel['success'] != 1:
			module_logger.debug("[error] order cancel has gone wrong")
			print("\n[error] Order cancel has gone wrong, please confirm manually...")
		else:
			module_logger.info("order successfully canceled")
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
	remainingTime = (float(order_model.timeslot) - float(eTimeMinutes))
	if remainingTime > 0:
		print("\nWaiting for: "+str(remainingTime)+" minutes....")
		time.sleep(float(remainingTime*60))

def finalizePosition(polo_model, order_model):
	try:
		liquidize = False
		#loop every timeslot untill position greater or less then constant(loss/win) limit -> liquidize
		#else wait...
		while not liquidize:
			startTime = datetime.now()
			currentPrice = getCurrentPrice(polo_model.returnTicker(), order_model.market)
			print("\nChecking current price for: "+str(order_model.market)+" at: "+str(currentPrice))
			module_logger.info("[CLOSINGPOSITION]Checking current price for: "+str(order_model.market)+" at: "+str(currentPrice))
			if positionInRange(order_model, currentPrice):
				module_logger.info("price for market is in range, liquidizing at "+str(currentPrice))
				print("\nCurrent price is in range, liquidizing... at "+str(currentPrice))
				liquidize = True
				order_model.closedAt = currentPrice
			else:
				eTimeMinutes = getElapsedTimeInMinutes(startTime)
				waitForTimeInMinutes(order_model, eTimeMinutes)
		#close position
		return closePosition(polo_model, order_model)
	except Exception, e:
		print("\n[error] Something went wrong while finalizing position...")
		module_logger.debug("[error] Something went wrong while finalizing position...")
		raise e
	return False
	

def closePosition(polo_model, order_model):
	try:
		module_logger.info("closing position")
		close = polo_model.closeMarginPosition(order_model.market)
		if close['success'] != 1:
			module_logger.debug("[error] closing position has gone wrong")
			print("\nClosing the margin position has gone wrong...")
			print(close)
		else:
			order_model.result_trades = close['resultingTrades']
			module_logger.info("successfully closed the margin position")
			print("\nSuccessfully closed the margin position...")
			return True
	except Exception, e:
		print("\n[error] Something went wrong while closing position...")
		module_logger.debug("[error] Something went wrong while closing position")
		raise e
	return False
	

def positionInRange(order_model, current_price):
	current_price = float(current_price)
	lossLimit = float(order_model.loss_limit)
	winLimit = float(order_model.win_limit)
	if order_model.trend == Order.UP_TREND: return ((current_price >= winLimit) or ((current_price <= lossLimit) and (current_price > (lossLimit / 1.05))))
	else: return ((current_price <= winLimit) or ((current_price >= lossLimit) and (current_price < (lossLimit * 1.05))))

def getCurrentPrice(markets, d_market):
	for r in markets:
		if r == d_market:
			return markets[r]['last']

def getPositionPrice(polo_model, order_model):
	try:
		orders = polo_model.returnOrderBook(order_model.market)
		if order_model.trend == Order.UP_TREND:
			orders = orders['asks']
		else:
			orders = orders['bids']
		return orders[0][0]
	except Exception as e:
		module_logger.debug("[error] could not get position price")
		print("\n[error] Could not get position price....")
		raise e
		return False

def logProfit(order_model, starttime):
	profit = calculateProfit(order_model)
	if profit >= 0:
		profitStr = "[PROFIT] "
	else:
		profitStr = "[LOSS] "
	profitStr += "Bot started at: "+str(starttime)
	profitStr += ", at pair: "+str(order_model.market)
	profitStr += ", with trend: "+str(order_model.trend)
	profitStr += ", %win: "+str(order_model.win_limit)
	profitStr += ", %loss: "+str(order_model.loss_limit)
	profitStr += ", took position at: "+str(order_model.position)
	profitStr += ", closed at: "+str(order_model.closedAt)
	profitStr += ", made profit: "+ str(profit)
	profit_logger.info(profitStr)

def calculateProfit(order_model):
	positionTrades = order_model.position_trades
	closingTrades = order_model.result_trades
	positionTotal = 0.0
	closingTotal = 0.0
	for positionPair in positionTrades[order_model.market]:
		positionTotal += float(positionPair['total'])
	for closingPair in closingTrades[order_model.market]:
		closingTotal += float(closingPair['total'])
	if order_model.trend == Order.UP_TREND:
		#positiontrades opgeteld (BTC) - closingtrades opgeteld (BTC)
		#bijvoorbeeld eerst 50 BTC gekocht daarna 55 BTC verkocht = 5 BTC winst
		return (float(closingTotal) - float(positionTotal))
	else:
		#positiontrades opgeteld (BTC) -  closingtrades opgeteld(BTC) * - 1
		#bijvoorbeeld eerst 50 BTC verkocht daarna 55 BTC gekocht = 5 BTC winst
		return (float(closingTotal) - float(positionTotal)) * float(-1)