class Order:
	UP_TREND = 'u'
	DOWN_TREND = 'd'

	def __init__(self, market, amount, trend, fb_amount, fb_amount_extra, win_limit, loss_limit, timeslot):
		self.market = market
		self.amount = amount
		self.trend = trend
		self.fb_amount = fb_amount
		self.fb_amount_extra = fb_amount_extra
		self.win_limit = win_limit
		self.loss_limit = loss_limit
		self.timeslot = timeslot
		self.treshold = Order.calculateTreshold(fb_amount, fb_amount_extra, trend)
		self.order_number = 0
		self.order_date = ''
		self.position = 0
		self.closedAt = 0
		self.position_trades = []
		self.result_trades = []

	def confirmation(self):
		print("\n CONFIRMATION, PLEASE CHECK CAREFULLY: \n")
		print("BTC market:"+"\t "+str(self.market))
		print("Order amount:"+"\t "+str(self.amount))
		print("Market trend:"+"\t "+str(Order.trendToString(self.trend)))
		print("FB amount:"+"\t "+str(self.fb_amount))
		print("FB extra:"+"\t "+str(self.fb_amount_extra)+"%")
		print("FB treshold:"+"\t "+str(self.treshold))
		print("Win limit:"+"\t "+str(self.win_limit))
		print("Loss limit:"+"\t "+str(self.loss_limit))
		print("Timeslot:"+"\t "+str(self.timeslot)+"m")
		command = raw_input("\n Is this information correct? (y)es or (n)o... \n")
		if command == 'y':
			return True
		elif command == 'n':
			return False
		else:
			return self.confirmation()

	@staticmethod
	def trendToString(trend):
		if trend == Order.UP_TREND:
			return 'UP'
		else:
			return 'DOWN'

	@staticmethod
	def calculateTreshold(amount, extra, trend):
		# When trend is up, the treshold should be a little above the FB line
		# When trend is down, the treshold should be a little under the FB line
		if trend == Order.UP_TREND:
			return "{:.8f}".format(float(float(amount) * (float(1) + (float(extra)/float(100)))))
		else:
			return "{:.8f}".format(float(float(amount) * (float(1) - (float(extra)/float(100)))))

	
		