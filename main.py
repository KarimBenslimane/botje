#from poloniex import poloniex
from testpoloniex import poloniex
from order import Order
import functions as fun
import logging

def initialize(poloModel):
	#ask for BTC market --TODO ONLY MARGIN TRADING
	btcMarket = fun.askForMarket(poloModel)
	#ask for how much BTC for order
	amountOrder = fun.askForAmount()
	#ask for trend
	trendOrder = fun.askForTrend()
	#ask for FB amount 
	fbAmount = fun.askForFB()
	#ask for FB amount extra
	fbExtra = fun.askForFBExtra()
	#set variables
	treshold = Order.calculateTreshold(fbAmount, fbExtra, trendOrder)
	#ask for loss limit 
	lossLimit = fun.askForLossLimit(treshold, trendOrder)
	#ask for win limit 
	winLimit = fun.askForWinLimit(treshold, trendOrder)
	#ask for timeslot
	timeSlot = fun.askForTimeSlot()
	#CONFIRMATION, show summary
	orderModel = Order(btcMarket, amountOrder, trendOrder, fbAmount, fbExtra, winLimit, lossLimit, timeSlot)
	if orderModel.confirmation():
		logger.info('created model for market: '+str(btcMarket))
		logger.info('created model for amount: '+str(amountOrder))
		logger.info('created model with trend: '+str(trendOrder))
		logger.info('created model with treshold: '+str(orderModel.treshold))
		logger.info('created model with winLimit: '+str(winLimit))
		logger.info('created model with lossLimit: '+str(lossLimit))
		#start program
		print("\nStarting program.... \n")
		return orderModel
	else:
		print("\nIncorrect information, starting again.... \n")
		return initialize(poloModel)

def initializeLog():
	logger = logging.getLogger('main_bot')
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler('bot.log')
	fh.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	return logger

logger = initializeLog()
logger.info('Starting application')

#karim APIKey = 'C69NO0HO-1AVQNH1P-VUV9I5AX-J7ZFWUMZ'
APIKey = '3QTABJ26-ZVPWR92Q-YP2ZZE7I-KUK1AHE4'
poloModel = ''
iSecret = ''
orderModel = ''

if not iSecret:
	iSecret = raw_input("Welcome to POLONIEX, please enter your secret.... \n")
else:
	print("Welcome to POLONIEX... \n")
while(not fun.checkSecret(iSecret)):
	iSecret = raw_input("\nSecret is not in valid format, please try again... \n")

logger.info('initiating poloniex model')
poloModel = fun.initiateModel(APIKey, iSecret)

logger.info('initiating order model')
orderModel = initialize(poloModel)
final = False
if isinstance(orderModel, Order):
	logger.info('finding position')
	position = fun.findPosition(poloModel, orderModel)
	if position:
		logger.info('validating position')
		validation = fun.validatePosition(poloModel, orderModel)
		if validation:
			logger.info('finalizing position')
			final = fun.finalizePosition(poloModel, orderModel)
if final:
	logger.info('Program ended fully')
	print("\nFully completed. Exiting program, bye!...")
else:
	logger.info('Program ended')
	print("\nExiting program, bye!...")

raw_input("\nPress Enter to Close....")