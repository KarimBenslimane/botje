#from poloniex import poloniex
from testpoloniex import poloniex
from datetime import datetime
from order import Order
import functions as fun
import logging
import os

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

def initializeLog(starttime):
	logger = logging.getLogger('main_bot')
	logger.setLevel(logging.DEBUG)
	fh = logging.FileHandler('log/bot'+starttime+'.log')
	fh.setLevel(logging.DEBUG)
	return createLogger(logger, fh)
	
def initializeProfitLog():
	profitLogger = logging.getLogger('profit_log')
	profitLogger.setLevel(logging.INFO)
	fh = logging.FileHandler('log/profit.log')
	fh.setLevel(logging.INFO)
	return createLogger(profitLogger, fh)

def createLogger(logger, fh):
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	logger.addHandler(fh)
	return logger

def closeFile(starttime, currentDir):
	os.rename(currentDir+'/log/bot'+starttime+'.log', currentDir+'/log/[FINISHED]bot'+starttime+'.log')

starttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
currentDir = os.path.dirname(os.path.abspath(__file__))
logger = initializeLog(starttime)
profitLogger = initializeProfitLog()
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

final = False
try:
	logger.info('initiating order model')
	orderModel = initialize(poloModel)
	if isinstance(orderModel, Order):
		logger.info('finding position')
		position = fun.findPosition(poloModel, orderModel)
		if position:
			logger.info('validating position')
			validation = fun.validatePosition(poloModel, orderModel)
			if validation:
				logger.info('finalizing position')
				final = fun.finalizePosition(poloModel, orderModel)
except Exception, e:
	print(str(e))
	logger.debug(str(e))

if final:
	fun.logProfit(orderModel, starttime)
	closeFile(starttime, currentDir)
	logger.info('Program ended fully')
	print("\nFully completed. Exiting program, bye!...")
else:
	logger.info('Program ended')
	print("\nExiting program, bye!...")

raw_input("\nPress Enter to Close....")