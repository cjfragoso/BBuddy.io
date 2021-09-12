#Calculate command

#3 btc to usdt
#4 knc to usdt

#data = {'symbol': 'BNBBTC', 'quoteAssetName': 'Bitcoin','baseAsset': 'BNB','close': '0.0022715', 'quoteAsset': 'BTC',}
#determine base and quote by argument position 1 base 3 quote
#calculate 2 btc to usdt

def process(client,argument):
	data = argument.split(' ')
	if len(data) != 4:
		return ("Missing arguments",0)
	else:
		try:
			qty = float(data[0])
		except:
			return ("Invalid qty",0)
		base = data[1]
		quote = data[3]

		return calc(client,qty,base,quote)

def calc(client,qty,base,quote):
	data = client.get_products()['data']
	p = []
	for i in data:
		try:
			if base.lower() in i['b'].lower() and quote.lower() in i['q'].lower():
				if quote.lower() == 'usdt':
					f = "{:.2f}"
				else:
					f = "{:.8f}"
				return ("{} {} = {} {}".format(qty,base.upper(),f.format((float(i['c'])*qty)),quote.upper()),0)
			elif base.lower() in i['q'].lower() and quote.lower() in i['b'].lower():
				if quote.lower() == 'usdt':
					f = "{:.2f}"
				else:
					f = "{:.8f}"

				return ("{} {} = {} {}".format(qty, base.upper(),f.format((qty/float(i['c']))),quote.upper()),0)
		except Exception as e:
			return (str(e),0) 
	else:
		return ("Unable to calculate",0)
