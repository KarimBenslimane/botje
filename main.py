from poloniex import poloniex
import functions as fun 

APIKey = 'C69NO0HO-1AVQNH1P-VUV9I5AX-J7ZFWUMZ'
poloModel = ''

i_secret = raw_input("Welcome to POLONIEX, please enter your secret.... \n")
while(not fun.checkSecret(i_secret)):
	i_secret = raw_input("\nSecret is not in valid format, please try again... \n")

poloModel = fun.initiateModel(APIKey, i_secret)

#ask for BTC market
btcMarket = fun.askForMarket(poloModel)
#ask for how much money for order
moneyOrder = fun.askForMoney()
#ask for trend
#ask for FB level
#ask for FB level extra
#ask for loss limit
#ask for win limit
#ask for timeslot
#CONFIRMATION, show summary

#gather information on markets
#calculate FB level amount plus extra amount on top

#loop every timeslot untill we have a position in the market:
	#get current price
	#if currentprice exceeds constant(FB level + extra) (depending on trend if above or below):
		#try:take position (buy or sell depending on trend with extra %)
		#except: 
	#wait for next timeslot

#loop untill validation for position
#if after 10 minutes no validation, cancel order

#loop every timeslot 
	#if untill position greater or less then constant(loss/win) limit:
		#liquidize
	#else:
		#wait...


print("Exiting program, bye!...")

