# -*- coding: utf-8 -*-
from poloniex import poloniex
import json

def checkSecret(secret):
	if len(secret) != 128:
		return False
	return True

def initiateModel(APIKey, i_secret):
	try:
		return poloniex(APIKey, i_secret)
	except:
	    print "Unexpected error:", sys.exc_info()[0]

def askForMarket(poloModel):
	command = raw_input("\n Please insert a BTC Market for trading or insert (s) for an overview... \n")
	if command == 's':
		printMarkets(poloModel)
	else:
		market = checkMarket(command, poloModel)
		if market:
			return market
	return askForMarket(poloModel)

def printMarkets(poloModel):
	markets = getMarketList(poloModel)
	print("\n Market List: \n")
	for m in markets:
		print(m)

def getMarketList(poloModel):
	markets = []
	output = poloModel.returnTicker()
	for r in output:
		markets.append(r)
	return markets

def checkMarket(command, poloModel):
	markets = getMarketList(poloModel)
	if not command in markets:
		print("\n Not a valid Market entered, please try again... \n")
		return False
	else:
		return command

def askForMoney():
	command = raw_input("\n Please insert an amount $$ for trading (e.g. 100.00) \n")
	try:
		money = "{:.2f}".format(float(command))
		return money
	except:
		print("\n Not a valid amount, please try again \n")
		return askForMoney()

def printTickerorVolume(output):
	for r in output:
		print("\n"+r+":")
		if type(output[r]) is dict:
			for i in output[r]:
				if i != '0':
					print("\t"+str(i)+": "),
					print(output[r][i])
		else:
			print("\t"+str(output[r]))
