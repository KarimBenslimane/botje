from poloniex import poloniex
from order import Order
import functions as fun 

APIKey = 'C69NO0HO-1AVQNH1P-VUV9I5AX-J7ZFWUMZ'
poloModel = ''
iSecret = '75c0d45aee16fb705fc8bff330e7030bf40146d87a3d224720b005541cf35b494828af0b68bf3c9bfa3c28a220bd1c11c9983cdd9ceac78be7dfd0b0353fd3d9'
orderModel = ''

if not iSecret:
	iSecret = raw_input("Welcome to POLONIEX, please enter your secret.... \n")
else:
	print("Welcome to POLONIEX... \n")
while(not fun.checkSecret(iSecret)):
	iSecret = raw_input("\nSecret is not in valid format, please try again... \n")

poloModel = fun.initiateModel(APIKey, iSecret)

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
		#start program
		print("\nStarting program.... \n")
		return orderModel
	else:
		print("\nIncorrect information, starting again.... \n")
		return initialize(poloModel)

orderModel = initialize(poloModel)
final = False
if isinstance(orderModel, Order):
	position = fun.findPosition(poloModel, orderModel)
	if position:
		validation = True
		# validation = fun.validatePosition(poloModel, orderModel)
		if validation:
			final = fun.finalizePosition(poloModel, orderModel)
if final:
	print("\nFully completed. Exiting program, bye!...")
else:
	print("\nExiting program, bye!...")
