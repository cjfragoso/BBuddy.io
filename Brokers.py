import re
import difflib
import datetime
import time
import os
import requests
import random
import operator
import socket
from binance.client import Client
from pandas.plotting import register_matplotlib_converters
from UserManagement.UserManagement import UserManagement as manager
from UserManagement.UserManagement import Admin
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.dates import DateFormatter, MinuteLocator
import matplotlib.dates as dates
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.ticker import FixedLocator, FormatStrFormatter
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib import style
import calculatepct
import calculator
import qrcode
style.use('dark_background')
register_matplotlib_converters()
account_sid = 'TWILIO ACCOUNT_SID'
auth_token = 'TWILIO AUTH_TOKEN'
class Base_Broker():
	def __init__(self,phone,api_key,api_secret):
		self.ohlc_image_path = "{}"
		self.pie_image_path = "{}"
		self.client = Client(api_key,api_secret)
		self.phone = phone
		self.assets_usd = {}
		self.assets_btc = {}
		self.assets_eth = {}
		self.asset_matches = []
		#self.get_accounts()
		#self.get_exchange_info()
		#self.get_tickers()
		#self.convert_to_usd()
		#self.convert_to_btc()
	def get_prices(self,ask):
		ask = ask.upper()
		f = open('logf.txt','w')
		f.write(ask)
		try:
			price = self.prices[ask]
			f.write(str(price))
			f.close()	
			if "USDT" in ask:
				return (re.sub(' +',' ',"*{m}:* {t}".format(m=ask,t="{0:10.6f}".format(float(price)))),0)
			else:
				return ("*{m}:* {t}".format(m=ask,t="{0:10.8f}".format(float(price))),0)
		except:
			return ("Invalid symbol {s}".format(s=ask),0)
	def get_accounts(self):
		accounts = self.client.get_account()['balances']
		self.accounts = []
		for acc in accounts:
			self.asset_matches.append(acc['asset'].lower())
			if float(acc['free']) > 0 or float(acc['locked']) > 0:
				self.accounts.append(acc)
	def get_exchange_info(self):
		base_quota = self.client.get_exchange_info()['symbols']
		self.base_quota = {i['baseAsset']:i['quoteAsset'] for i in base_quota}
		
	def get_tickers(self):
		tickers = self.client.get_all_tickers()
		self.symbol_matches = [i['symbol'] for i in tickers]
		self.prices = {i['symbol']:float(i['price']) for i in tickers}
		self.btc_prices = {i['symbol'][:-3]:i['price'] for i in tickers if i['symbol'][-3:] == "BTC"}
		self.btc_prices['BTC'] = 1
		self.eth_prices = {i['symbol'][:-3]:i['price'] for i in tickers if i['symbol'][-3:] == "ETH"}
		self.usd_prices = {i['symbol'][:-4]:i['price'] for i in tickers if i['symbol'][-4:] == "USDT"}
		self.xrp_prices = {i['symbol'][:-3]:i['price'] for i in tickers if i['symbol'][-3:] == "XRP"}
		self.pax_prices = {i['symbol'][:-3]:i['price'] for i in tickers if i['symbol'][-3:] == "PAX"}
		self.usdc_prices = {i['symbol'][:-4]:i['price'] for i in tickers if i['symbol'][-4:] == "USDC"}
		self.bnb_prices = {i['symbol'][:-3]:i['price'] for i in tickers if i['symbol'][-3:] == "BNB"}
		self.tusd_prices = {i['symbol'][:-4]:i['price'] for i in tickers if i['symbol'][-4:] == "TUSD"}
		self.bases = {"BTC":self.btc_prices,"ETH":self.eth_prices,"USDT":self.usd_prices,"XRP":self.xrp_prices,"PAX":self.pax_prices,"USDC":self.usdc_prices,"BNB":self.bnb_prices,"TUSD":self.tusd_prices}
	def convert_to_usd(self):
		for asset in self.accounts:
			if asset['asset'] == "USDT":
				self.assets_usd[asset['asset']] = "{0:.2f}".format(float(asset['free']) + float(asset['locked']))
			if asset['asset'] in self.usd_prices.keys():
				self.assets_usd[asset['asset']] = '{0:.2f}'.format(float(self.usd_prices[asset['asset']]) * (float(asset['free']) + float(asset['locked'])))
			else:
				try:
					self.assets_usd[asset['asset']] = "{0:.2f}".format((float(self.bases[self.base_quota[asset['asset']]][asset['asset']])*(float(asset['free'])+float(asset['locked'])))*float(self.usd_prices[self.base_quota[asset['asset']]]))
				except:
					try:
						price = float(self.client.get_ticker(symbol=asset['asset']+"USDT")['lastPrice'])
						self.assets_usd[asset['asset']] = "{0:.2f}".format((price) * (float(asset['free']) + float(asset['locked'])))
					except:
						pass
	def convert_to_btc(self):
		for asset in self.accounts:
			if asset['asset'] in self.btc_prices.keys():
				self.assets_btc[asset['asset']] = '{0:.8f}'.format(float(self.btc_prices[asset['asset']]) * (float(asset['free']) + float(asset['locked'])))
			else:
				try:
					self.assets_btc[asset['asset']] = (float(self.bases[self.base_quota[asset['asset']]][asset['asset']])*(float(asset['free'])+float(asset['locked'])))*float(self.btc_prices[self.base_quota[asset['asset']]])
				except:
					try:
						price = float(self.client.get_ticker(symbol=asset['asset']+"BTC")['lastPrice'])
						self.assets_btc[asset['asset']] = price * (float(asset['free']) + float(asset['locked']))
					except:
						if asset['asset'] == "USDT":
							self.assets_btc["USDT"] = '{0:.8f}'.format((float(asset['locked'])+float(asset['free']))/float(self.usd_prices['BTC']))
						else:
							pass
	def convert_to_eth(self):
		for asset in self.accounts:
			if asset['asset'] in self.eth_prices.keys():
				self.assets_eth[asset['asset']] = "{0:.8f}".format(float(self.eth_prices[asset['asset']]) * (float(asset['free']) + float(asset['locked'])))
			else:
				try:
					self.assets_eth[asset['asset']] = (float(self.bases[self.base_quota[asset['asset']]][asset['asset']])*(float(asset['free'])+float(asset['locked'])))*float(self.eth_prices[self.base_quota[asset['asset']]])
				except:
					try:
						price = float(self.client.get_ticker(symbol=asset['asset']+"ETH")['lastPrice'])
						self.assets_eth[asset['asset']] = price * (float(asset['free']) + float(asset['locked']))
					except:
						if asset['asset'] == "USDT":
							self.assets_eth["USDT"] = '{0:.8f}'.format((float(asset['locked'])+float(asset['free']))/float(self.usd_prices['ETH']))
						else:
							pass
		
	def response_balances(self,asset):
		self.get_accounts()
		self.get_tickers()
		self.get_exchange_info()
		self.convert_to_usd()
		self.convert_to_btc()
		self.convert_to_eth()
		curr = {"BTC":self.assets_btc,"USDT":self.assets_usd,"ETH":self.assets_eth}
		text_btc = {}
		text_usdt = {}
		text_eth = {}
		total_btc = []
		total_usdt = []
		total_eth = []
		for i in sorted(curr["BTC"].items(), key=lambda kv: float(kv[1]),reverse=True):
			total_btc.append(float(i[1]))
			if float(i[1]) > 0.000001:
				text_btc[i[0]] = float(i[1])
		text_btc['Total'] = sum(total_btc)
		for i in sorted(curr["USDT"].items(),key=lambda kv: float(kv[1]),reverse=True):
			total_usdt.append(float(i[1]))
			if float(i[1]) > 0.01:
				text_usdt[i[0]] = float(i[1])
		text_usdt['Total'] = sum(total_usdt)
		for i in sorted(curr["ETH"].items(), key=lambda kv: float(kv[1]),reverse=True):
			total_eth.append(float(i[1]))
			if float(i[1]) > 0.000001:
				text_eth[i[0]] = float(i[1])
		text_eth['Total'] = sum(total_eth)
		
		m = manager()
		if asset=="USDT":
			old_balance = m.get_old_balance(phone=self.phone,base=asset)
			pct = calculatepct.calculate_pct(old_balance,text_usdt,asset)
			res = ["*Balance USDT* ðŸ’°",pct]
			m.register_balances(self.phone,str(text_usdt),"USDT")
			return "\n".join(res)
		elif asset=="BTC":
			old_balance = m.get_old_balance(phone=self.phone,base=asset)
			pct = calculatepct.calculate_pct(old_balance,text_btc,asset)
			res = ["*Balance BTC* ðŸ’°",pct]
			m.register_balances(self.phone,str(text_btc),"BTC")
			return "\n".join(res)
		elif asset=="ETH":
			old_balance = m.get_old_balance(phone=self.phone,base=asset)
			pct = calculatepct.calculate_pct(old_balance,text_eth,asset)
			res = ["*Balance ETH* ðŸ’°",pct]
			m.register_balances(self.phone,str(text_eth),"ETH")
			return "\n".join(res)
	def response_assets(self):
		self.get_accounts()
		text = []
		text.append("*Asset Qty* ðŸ“")
		if len(self.accounts) > 0:

			for i in self.accounts:
				text.append("{s}: {p}".format(s=i['asset'],p="{0:.8f}".format(float(i['free']) + float(i['locked']))))
			resp = "\n".join(text)
			return resp
		else:
			return "You have no assets"

	def process_command(self,pool):
		matches = ["balance","price","asset","help","?","chart","orders"]
		try:
			command = difflib.get_close_matches(re.sub(' +',' ',pool[0].lower()),matches)[0]
		except:
			 return ("Invalid command\nType *?* for help",0)
		if command == "price":
			try:
				self.get_tickers()
				f = open('logt.txt','w+')
				f.write(command)
				resp = self.get_prices(difflib.get_close_matches(pool[1].upper(),self.symbol_matches)[0])
				f.close()
				return resp
			except:
				return ("Invalid command {s}".format(s="".join(pool)),0)
		elif command == "balance":
			return ("This command is for premium memebers",0)
		elif command == "asset":
			resp = self.response_assets()
			return (resp,0)
			
		else:
			return ("Invalid command",0)

class Broker_P(Base_Broker):
	def __init__(self,phone,api_key,api_secret):
		super().__init__(phone,api_key,api_secret)
	def transfer_dust(self):
		self.get_accounts()
		self.get_tickers()
		self.get_exchange_info()
		self.convert_to_usd()
		try:
			self.dust = [i for i in self.assets_usd.keys() if i !="BNB" and float(self.assets_usd[i]) < 1]
			if len(self.dust) > 1:
				self.assets_to_dust = ",".join(self.dust)
			elif len(self.dust) == 1:
				self.assets_to_dust = "".join(self.dust)
			else:
				return ("No assets available for dust transfer",0)
			try:

				r = self.client.transfer_dust(asset=self.assets_to_dust)
				dust_assets = []
				dust_assets.append("*Dust Log*")
				for i in r['transferResult']:
					dust_assets.append("{} -> {}".format(i['fromAsset'],i['transferedAmount']))
				dust_assets.append("Service Charge: {}".format(r['totalServiceCharge']))
				dust_assets.append("Total Transfered: {}".format(r['totalTransfered']))
				res = "\n".join(dust_assets)
				return (res,0)
			except:
				return ("You can transfer dust every 24 Hours",0)
		except:
			return ("Error trying to transfer dust",0)
	def get_open_orders(self):
		self.open_orders = self.client.get_open_orders()
		if len(self.open_orders) > 0:
			orders = []
			for i in self.open_orders:
				orders.append([i['side'],i['origQty'],i['symbol'],i['price'],i['orderId']])
			
			text = []
			text.append("\U0001f535Buy   \U0001f534Sell   ")
			for i in orders:
				if i[0] == "BUY":
					if float(i[1]) < 1:
						text.append("\U0001f535 {0:.8f} *{1:}* *{2:}* ID: {3:}".format(float(i[1]),i[2],i[3],i[4]))
					else:
						text.append("\U0001f535 {0:.2f} *{1:}* *{2:}* ID: {3:}".format(float(i[1]),i[2],i[3],i[4]))
				else:
					if float(i[1]) < 1:
						text.append("\U0001f534 {0:.8f} *{1:}* *{2:}* ID: {3:}".format(float(i[1]),i[2],i[3],i[4]))
					else:
						text.append("\U0001f534 {0:.2f} *{1:}* *{2:}* ID: {3:}".format(float(i[1]),i[2],i[3],i[4]))
			ret = "\n".join(text)
			return (ret,0)
		else:
			return ("No open orders!",0)
	def get_orders(self,symbol):
		self.orders = self.client.get_all_orders(symbol=symbol)
		
		
		try:
			self.orders = self.orders[-19:]
			
		except:
			self.orders = self.orders
		if len(self.orders) > 0:
			data = {'side':[i['side'] for i in self.orders],'qty':[i['origQty'] for i in self.orders],'price':[i['price'] for i in self.orders],'status':[i['status'] for i in self.orders],'date':[datetime.datetime.fromtimestamp(i['time']/1000).strftime("%b %d %H:%m") for i in self.orders]}
			resp = []
			#resp.append("\U0001f535Buy   \U0001f534Sell  *{}*\n".format(symbol))
			for i in range(len(data['side'])):
				if data['status'][i] != "CANCELED":
					if data['side'][i] == 'BUY':
						if data['status'][i] == 'FILLED':
							status = "*F*"
						else:
							status = "*N*"
						qty = float(data['qty'][i])
						if qty.is_integer():
							qty = str(qty.as_integer_ratio()[0])
						resp.append(['\U0001f535',str(qty),str(data['price'][i]),status,str("\n\t\t*"+data['date'][i]+"*")])
					elif data['side'][i] == 'SELL':
						if data['status'][i] == 'FILLED':
							status = "*F*"
						else:
							status = "*N*"
						qty = float(data['qty'][i])
						if qty.is_integer():
							qty = str(qty.as_integer_ratio()[0])
						resp.append(['\U0001f534',str(qty),str(data['price'][i]),status,str("\n\t\t*"+data['date'][i]+"*")])
			if len(resp) > 0:
				lens = []
				for col in zip(*resp):
					lens.append(max([len(v) for v in col]))
				formater = " ".join(["{: <" + str(l) + "}" for l in lens])
				final = []
				final.append("\U0001f535Buy   \U0001f534Sell  *{}* ðŸ—‚ \n".format(symbol))
				for i in resp:
					final.append(formater.format(*i))
				ret = "\n".join(final)
			
				return (ret,0)
			else:
				return ("No orders for {}".format(symbol),0)
		else:
			return ("No orders for {}".format(symbol),0)
	def get_ohlc_values(self,symbol,frec,frame,now="now"):
		today = now + " UTC"
		candle_width = {"1h":.01,"1d":.2,"1w":.4,"30m":.01,"15m":0.003,"1m":0.0003,"5m":0.0005,"2h":0.02,"4h":0.1}
		xformatter = {"1h":"%H:%M","1d":"%m/%d","1w":"%m/%d","30m":"%H:%M","15m":"%H:%M","1m":"%M","5m":"%M","2h":"%H:%M","4h":"%H:%M"}
		xformatter_limit = {"1h":24,"15m":93,"1w":4,"30m":48,"1m":60,"4h":6,"2h":12,"5m":12}
		if frec == "1h" and int(frame) > xformatter_limit[frec]:
			xformatter[frec] = "%d\n%H:%M"
		elif frec == "1w" and int(frame) > xformatter_limit[frec]:
			xformatter[frec] = "%m/%d"
		elif frec == "15m" and int(frame) > xformatter_limit[frec]:
			xformatter[frec] = "%d\n%H:%M"
		elif frec == "30m" and int(frame) > xformatter_limit[frec]:
			xformatter[frec] = "%d\n%H:%M"
		elif frec == "1m" and int(frame) > xformatter_limit[frec]:
			xformatter[frec] = "%H:%M"
		elif frec == "4h" and int(frame) > xformatter_limit[frec]:
			xformatter[frec] = "\n%H:%M"
		elif frec == "5m" and int(frame) > xformatter_limit[frec]:
			xformatter[frec] = "%H:%M"
		
		months = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sept",10:"Oct",11:"Nov",12:"Dec"}
		if frame != 1:
			minutes = int(frame)*30
			minutesf = int(frame)*15
			hours2 = int(frame)*2
			hours4 = int(frame)*4
			minutes5 = int(frame)*5
		else:
			return "Ivalid frame {}".format(frame)
		period = {"5m":"{m} minutes ago UTC".format(m=minutes5),"4h":"{h} hours ago UTC".format(h=hours4),"2h":"{h} hours ago UTC".format(h=hours2),"1m":"{m} minutes ago UTC".format(m=frame),"15m":'{minutesf} minutes ago UTC'.format(minutesf=minutesf),"1h":'{frame} hours ago UTC'.format(frame=frame),"30m":'{minutes} minutes ago UTC'.format(minutes=minutes),"1w":'{frame} weeks ago UTC'.format(frame=frame),"1d":'{frame} days ago UTC'.format(frame=frame)}
		ohlc = self.client.get_historical_klines(symbol,frec,period[frec],today)
		data = []
		for i in ohlc:
			data.append(i[:5])
		d = {"Date":[datetime.datetime.fromtimestamp(i[0]/1000) for i in data],"Open":[float(i[1]) for i in data],"High":[float(i[2]) for i in data],"Low":[float(i[3]) for i in data],"Close":[float(i[4]) for i in data]}
		dataframe = pd.DataFrame(d)
		dataframe.Date = mdates.date2num(dataframe.Date.dt.to_pydatetime())
		dataframe.set_index('Date')
		trace = dataframe[['Date','Open','High','Low','Close']].copy()
		fig = plt.figure(frameon=False,figsize=(15.0,11.0),dpi=80)
		if frec == "1h":
			fig.suptitle("{s} {t} {n}".format(s=symbol,t="Hourly",n="{} Hours".format(len(trace['Low']))), fontsize=30, fontweight='bold')
		elif frec == "1d":
			fig.suptitle("{s} {t} {n}".format(s=symbol,t="Daily",n="{} Days".format(len(trace['Low']))), fontsize=30, fontweight='bold')
		elif frec == "1m":
			fig.suptitle("{s} {t} {n}".format(s=symbol,t=frec,n="{} Minutes".format(len(trace['Low']))), fontsize=30, fontweight='bold')
		else:
			fig.suptitle("{s} {t} {n}".format(s=symbol,t=frec,n="{} bars".format(len(trace['Low']))), fontsize=30, fontweight='bold')
		ax1 = plt.subplot2grid((7,1),(0,0),rowspan=5,colspan=1)
		plt.axhline(y=min(trace['Low']),color='g',linestyle='-',label="Low")
		plt.axhline(y=max(trace['High']),color='r',linestyle='-',label="High")
		plt.axhline(y=trace['Close'].__array__()[-1],alpha=0.6,color='white',linestyle='--',label="Price Line")
		form = "{0:.2f}"
		if min(trace['Low']) < 1:
			form = "{0:.8f}"
			
		ax1.text(trace.Date[trace.index[trace.Low == min(trace.Low)][0]],min(trace['Low']),form.format(min(trace.Low)),fontsize=20)
		ax1.text(trace.Date.__array__()[-1],trace['Close'].__array__()[-1],form.format(trace.Close.__array__()[-1]),fontsize=20)
		ax1.text(trace.Date[trace.index[trace.High == max(trace.High)][0]],max(trace['High']),form.format(max(trace.High)),fontsize=20)
		ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),fancybox=False,ncol=5,prop={'size':30})
		ax1.xaxis.set_major_formatter(DateFormatter(xformatter[frec]))
		ax1.grid(True,linestyle="-.",alpha=0.4)
		ax1.tick_params(labelcolor='white', labelsize=20.0, width=1.5)
		for label in list(range(len(ax1.get_xticklabels()))):
			if label !=0 and label != len(ax1.get_xticklabels()):
				ax1.get_xticklabels()[label].set_visible = False
		candlestick_ohlc(ax1,trace.values,width=candle_width[frec],colorup='g')
		img = '{p}{r}ohlc.png'.format(p=self.phone,r=random.randint(111,999))
		plt.savefig(self.ohlc_image_path.format(img))
		return img
	def get_pie_chart(self,base="USDT"):
		self.get_accounts()
		self.get_tickers()
		self.get_exchange_info()
		self.convert_to_usd()
		curr = {"BTC":[self.assets_btc,"{0:0.8f}"],"USDT":[self.assets_usd,"{0:0.2f}"]}
		labels = []
		values = []
		explode_mayor = []
		filter_value = 0
		if base == "USDT":
			filter_value = 0.2
		else:
			filter_value = 0.0001
		for key in curr[base][0].keys():
			if float(curr[base][0][key]) > filter_value:
				labels.append(key)
				values.append(curr[base][1].format(float(curr[base][0][key])))
				explode_mayor.append([float(curr[base][0][key]),0.20])
		if len(labels) == 0:
			for key in curr[base][0].keys():
				labels.append(key)
				values.append(curr[base][1].format(float(curr[base][0][key])))
				explode_mayor.append([float(curr[base][0][key]),0])
		try:
			explode_mayor[explode_mayor.index(max(explode_mayor, key = lambda i : i[0]))] = (explode_mayor[explode_mayor.index(max(explode_mayor, key = lambda i : i[0]))][0],0)
			explode = tuple([i[1] for i in explode_mayor])
		except:
			explode = tuple([0.09 for i in labels])
			
		fig,ax = plt.subplots()
		centre_circle = plt.Circle((0,0),0.65,fc='black')
		label = ax.annotate("BBuddy", xy=(0, 0),color="white", fontsize=20, ha="center")
		fig = plt.gcf()
		fig.gca().add_artist(centre_circle)
		colors = ["#003f5c","#ff6361","#2f4b7c","#FF6347","#06364A","#009DAB","#EE5F2D"]
		ax.pie(values,labels=labels,autopct="%1.1f%%",colors=colors,explode=explode,shadow=False,startangle=90,pctdistance=0.85)
		ax.axis('equal')
		plt.tight_layout()
		img = '{s}{r}piechart.png'.format(s=self.phone,r=random.randint(9999,999999))
		plt.savefig(self.pie_image_path.format(img))
		return img
	def get_prices(self,ask):
		ask = ask.upper()
		try:
			changes = self.client.get_ticker(symbol=ask)
			price_change = changes['priceChange']
			price_pct = changes['priceChangePercent']
			high = changes['highPrice']
			low = changes['lowPrice']
			volume = float(changes['volume'])
			quoteVolume = float(changes['quoteVolume'])
			price = self.prices[ask]
			if '-' in price_pct:

				price_pct = "\U0001F534 {}".format(price_pct)
			else:
				price_pct = "\U0001F7E2 {}".format(price_pct)
			if "USDT" in ask:
				if float(price) < 1 and len(str(price)) > 2:
					form = '{:10.'+str(len(str(price)))+'f}'
				else:
					form = '{:10.2f}'
				return (re.sub(' +',' ',"*{m} {p}%*\n*P: {t}*\nH: {h}\nL: {l}\nBase Vol: {v}\nQuote Vol: {q}".format(m=ask,t=form.format(float(price)),p=price_pct,h=form.format(float(high)),l=form.format(float(low)),v='{0:,.2f}'.format(volume),q='{:,.2f}'.format(quoteVolume))),0)
			else:
				return ("*{m} {p}%*\n*P: {t}*\nH: {h}\nL: {l}\nBase Vol: {v}\nQuote Vol: {qv}".format(m=ask,t="{0:10.8f}".format(float(price)),p=price_pct,h=high,l=low,v='{:,.2f}'.format(volume),qv='{:,.2f}'.format(quoteVolume)),0)
		except:
			return ("Invalid symbol {s}".format(s=ask),0)

	def alarm_info(self):
		msg = []
		alarms=""
		try:
			sock = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
			sock.connect('./uds_socket')
			sock.sendall('{phone},info'.format(phone=self.phone).encode('utf-8'))
			alarms = sock.recv(1024).decode('utf-8')
			sock.close()
		except:
			return ("Oops\nWe're having trouble with alerts at this moment\nplease try again later",0)
		
		text = ""
		if alarms !='None':
			text = "Alerts:"
			msg.append(text)
			user_data = alarms.split(' ')
			total_alarms = [i.split(',') for i in user_data]
			for i in range(len(total_alarms)):
				if total_alarms[i][0] != "done":
					if total_alarms[i][0] == 'up':
						sym = '\u2B06'
					else:
						sym = '\u2B07'
					msg.append("{} - {} {} {}".format(i+1,total_alarms[i][1].upper(),sym,total_alarms[i][2]))
			if len(msg) > 1:
				response = "\n".join(msg)
				return (response,0)
			else:
				return ("No alarms set!",0)
		else:
			return ("No alarms set!",0)

	def set_alarm(self,symbol,reach):
		try:
			self.get_tickers()
			symbol = difflib.get_close_matches(symbol.upper(),self.symbol_matches)[0]
			arg_send = ""
			price = float(self.get_prices(symbol)[0].split('\n')[1].strip("*").split(" ")[1])
			reach = reach.replace(',','')
			if float(reach) > price:
				arg_send = "up"
			elif float(reach) < price:
				arg_send = "down"
			sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
			sock.connect('./uds_socket')
			sock.sendall('{phone},{alarm},{symbol},{price}'.format(phone=self.phone,alarm=arg_send,symbol=symbol,price=reach).encode('utf-8'))
			valid = sock.recv(1024).decode('utf-8')
			sock.close()
			direction = ""
			if arg_send == "down":
				direction = '\u2B07'
			elif arg_send == "up":
				direction = '\u2B06'
			if valid == 'valid':
				return ("\u2757Alert set for *{}* {} {}".format(symbol,direction,reach),0)
			else:
				return (" All alerts set!",0)
		except Exception as e:
			f = open("ex.log","w")
			f.write(str(e))
			f.close()
			return ("We're having problems setting up your alert\ntry again later",0)
	def clear_alarm(self,num):
		try:
			info,extra = self.alarm_info()
			if info == "No alerts set!":
				return (info,extra)
			else:
				sock = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
				sock.connect('./uds_socket')
				sock.sendall('{},clear,{}'.format(self.phone,num).encode('utf-8'))
				resp = sock.recv(1024).decode('utf-8')
				if resp == "valid":
					return ("Alert {} deleted".format(num),0)
				else:
					return ("We're having problems deleting your alert!\ntry again later",0)
		except:
			return ("Oops! We're having problems deliting your alert\ntry again later",0)
	def gen_qrcode(self,phone,asset):
		assets = self.client.get_asset_details()['assetDetail']
		self.valid_assets_for_deposit = [i for i in assets.keys() if assets[i]['depositStatus']]
		try:
			valid = difflib.get_close_matches(asset.upper(),self.valid_assets_for_deposit)[0]
		except:
			return ("Invalid Asset {}".format(asset.upper()),0)
		if valid == "BNB":
			return ("Sorry, we're unable to generate BNB QR Address at the moment",0)
		elif valid == "BTC":
			qr = "bitcoin:"
		else:
			qr = "ethereum:"
		data = self.client.get_deposit_address(asset=valid)['address']
		img = qrcode.make(qr+data)
		imname = phone.split("+")[1]+valid+".png"
		img.save('{}'.format(imname))
		return ("*{} address* - {}".format(valid,data),imname)
	def limit_buy(self,symbol,qty,price):
		try:
			qty = float(qty)
			
		except:
			return ("Invalid qty!",0)
		
		try:
			order = self.client.order_limit_buy(symbol=symbol,quantity=qty,price=price)
			if order['status'] == "FILLED":
				return ("\U0001f535 {} {} *@* {} *executed!*\nOrder ID:{}".format(qty,symbol,price,order['orderId']),0)
			else:
				return ("\U0001f535 {} {} *@* {} *placed!*\nOrder ID:{}".format(qty,symbol,price,order['orderId']),0)
		except:
			status = self.client.get_system_status()['msg']
			if status == "System maintenance.":
				return ("Unable to process command due to Broker System Maintenance",0)
			else:
				return ("Insufficient balance!",0)
	def limit_sell(self,symbol,qty,price):
		try:
			order = self.client.order_limit_sell(symbol=symbol,quantity=float(qty),price=price)
			if order['status'] == "FILLED":
				return ("\U0001f534 {} {} *@* {} *executed!*\nOrder ID:{}".format(qty,symbol,price,order['orderId']),0)
			else:
				return ("\U0001f534 {} {} *@* {} *placed!*\nOrder ID:{}".format(qty,symbol,price,order['orderId']),0)
		except:
			status = self.client.get_system_status()['msg']
			if status == "System maintenance.":
				return ("Unable to process command due to Broker System Maintenance",0)
			else:
				return ("Insufficient balance!",0)
	def cancel_order(self,symbol,order_id):
		try:
			l = open('cancel.log','a')
			l.write("{} {}\n".format(symbol,order_id))
			l.close()
			order = self.client.cancel_order(symbol=symbol,orderId=int(order_id))
			return ("Order {} {} canceled!‘ ".format(symbol.upper(),order_id),0)
		except:
			return ("Unknown order!",0)
	def process_command(self,pool):
		matches = ["deposit","cleardust","buy","sell","cancel","request","balance","alarm","alert","price","pie","asset","help","?","chart","orders","support"]
		infos = ["info","clear"]
		bases = ['SC','BTC', 'ETH', 'BNB', 'BCC', 'NEO', 'LTC', 'QTUM', 'ADA', 'XRP', 'EOS', 'TUSD', 'IOTA', 'XLM', 'ONT', 'TRX', 'ETC', 'ICX', 'VEN', 'NULS', 'VET', 'PAX', 'BCHABC', 'BCHSV', 'USDC', 'LINK', 'WAVES', 'BTT', 'USDS', 'ONG', 'HOT', 'ZIL', 'ZRX', 'FET', 'BAT', 'XMR', 'ZEC', 'IOST', 'CELR', 'DASH', 'NANO', 'OMG', 'THETA', 'ENJ', 'MITH', 'MATIC', 'ATOM', 'TFUEL', 'ONE', 'FTM', 'ALGO', 'USDSB', 'GTO', 'ERD', 'DOGE', 'DUSK', 'ANKR', 'WIN', 'COS', 'NPXS', 'COCOS', 'MTL', 'TOMO', 'PERL', 'DENT', 'MFT', 'KEY', 'STORM', 'DOCK', 'WAN', 'FUN', 'CVC', 'CHZ', 'BAND', 'BUSD', 'BEAM', 'XTZ', 'REN', 'RVN', 'HC', 'HBAR', 'NKN', 'STX', 'KAVA', 'ARPA']
		symbols = open('all_symbols.txt','r')
		all_symbols = symbols.read()
		symbols.close()
		all_symbols = eval(all_symbols)
		admin_phones = "whatsapp:{}"
		if self.phone == admin_phones  and "stat" in pool[0].lower():
			from twilio.rest import Client
			client = Client(account_sid,auth_token)
			bal = client.balance.fetch()
			
			return ("*Credit remaining*\n{}: {}".format(bal.currency,bal.balance),0)
		elif self.phone == admin_phones and "users" in pool[0].lower():
			import sqlite3
			c = sqlite3.connect("database.sqlite")
			cursor = c.cursor()
			data = cursor.execute("select name from users;")
			data = [i[0] for i in data]
			c.close()
			return ("\n".join(data),0)
		try:
			command = difflib.get_close_matches(re.sub(' +',' ',pool[0].lower()),matches)[0]
			
		except:
			return ("Invalid command\nType *?* for help",0)

		if command == "cleardust":
			return self.transfer_dust()
		if command == "buy" and len(pool) == 4:
				return self.limit_buy(pool[1].upper(),pool[2],pool[3])
		elif command == "buy" and len(pool) !=4:
				return ("Missing arguments in command\n*buy <symbol> <qty> <price>*",0)
		if command == "sell" and len(pool) == 4:
				return self.limit_sell(pool[1].upper(),pool[2],pool[3])
		elif command == "sell" and len(pool) != 4:
				return ("Missing arguments in command\n*sell <symbol> <qty> <price>*",0)
		if command == "cancel" and len(pool) == 3:
				return self.cancel_order(pool[1].upper(),pool[2])
		elif command == "cancel" and len(pool) != 3:
				return ("Missing arguments in command\n*cancel <symbol> <orderId>*",0)
		if command == "request" and len(pool) > 1 or command == "deposit" and len(pool) > 1:
			return self.gen_qrcode(self.phone,pool[1])
		elif command == "request" and len(pool) ==1 or command == "deposit" and len(pool) == 1:
			return ("Missing asset name, type ? for help",0)
		if command == "alert" or command == "alarm":
			try:
				if len(pool) == 1:
					return self.alarm_info()
				elif "info" in difflib.get_close_matches(pool[1].lower(),infos):
					return self.alarm_info()
				elif "clear" in difflib.get_close_matches(pool[1].lower(),infos):
					return self.clear_alarm(pool[2])
				else:
					return self.set_alarm(pool[1],pool[2])
			except:
				return ("Type ? or help",0)
		elif command == "balance" and len(pool) == 1:
			resp = self.response_balances("USDT")
			return (resp,0)
		elif command == "balance" and len(pool) > 1:
			try:
				if "btc" in difflib.get_close_matches(pool[1].lower(),["btc","eth"])[0]:

					resp = self.response_balances("BTC")
					return (resp,0)
				elif "eth" in difflib.get_close_matches(pool[1].lower(),["eth"])[0]:
					resp = self.response_balances("ETH")
					return (resp,0)
			except:
				resp = self.response_balances("BTC")
				return (resp,0)
		elif command == "asset":
			resp = self.response_assets()
			return (resp,0)
		elif command == "pie":
			filename = self.get_pie_chart()
			return ("Piechart",filename)
		elif command == "chart":
			try:
				f_values = ["1h","1d","1w","30m","15m","1m","5m","2h","4h"]
				if len(pool) == 3 and pool[2] not in f_values:
					frame_value = "1d"
				frame_value = ""
				if len(pool) == 3:
					frame_value = pool[2].lower()
				elif len(pool) == 2:
					frame_value = "1d"
				self.get_tickers()
				try:
					if len(pool[1]) <=5:
						chart = difflib.get_close_matches(pool[1].upper(),bases)[0]+"USDT"
					else:
						chart = difflib.get_close_matches(pool[1].upper(),self.symbol_matches)[0]
				except:
					pass
				if len(pool) == 3 and pool[2].lower() not in f_values:
					try:
						file_name = self.get_ohlc_values(chart,"1d",pool[2])
					except:
						return ("Invalid Time Frame!",0)
				elif len(pool) == 3 and pool[2].lower() == "1h":
					file_name = self.get_ohlc_values(chart,pool[2].lower(),"24")
				elif len(pool) == 3 and pool[2].lower() == "15m":
					file_name = self.get_ohlc_values(chart,pool[2].lower(),"96")
				elif len(pool) == 3 and pool[2].lower() == "1m":
					file_name = self.get_ohlc_values(chart,pool[2].lower(),"60")
				elif len(pool) == 3 and pool[2].lower() == "30m":
					file_name = self.get_ohlc_values(chart,pool[2].lower(),"48")
				elif len(pool) == 3 and pool[2].lower() == "5m":
					file_name = self.get_ohlc_values(chart,pool[2].lower(),"288")
				elif len(pool) == 3 and pool[2].lower() =="2h":
					file_name = self.get_ohlc_values(chart,pool[2].lower(),"12")
				elif len(pool) == 3:
					file_name = self.get_ohlc_values(chart,pool[2].lower(),"24")
				elif len(pool) == 2:
					file_name = self.get_ohlc_values(chart,"1d","30")
				else:
					file_name = self.get_ohlc_values(chart,pool[2].lower(),pool[3])
				if "png" in file_name:
					if frame_value != "":

						return ("*Chart {} {}*".format(chart,frame_value),file_name)
					else:
						return ("*Chart {}*".format(chart),file_name)
				else:
					return (file_name,1)
			except Exception as e:
				f = open('charterror.log','w')
				f.write(str(e)+str(datetime.datetime.today()))
				f.close()
				try:
					return ("Invalid symbol {s}".format(s=pool[1].upper()),0)
				except:
					return ("Invalid Command, type ?/help for help",0)
			
		elif command == "price":
			try:
				self.get_tickers()
				if pool[1].upper() in bases:
					return self.get_prices(pool[1].upper()+"USDT")
				else:
					return self.get_prices(difflib.get_close_matches(pool[1].upper(),self.symbol_matches)[0])
			except:
				return ("Invalid command {s}".format(s=" ".join(pool)),0)
		elif command == "orders" and len(pool) == 2:
			self.get_tickers()
			return self.get_orders(difflib.get_close_matches(pool[1].upper(),self.symbol_matches)[0])
		elif command == "orders" and len(pool) == 1:
			return self.get_open_orders()
		elif command == "support":
			f = open('support.log','a')
			f.write("{}|{}\n".format(self.phone," ".join(pool)))
			f.close()
			return ("We received your message!\nif necessary, our team will contact you asap!",0)
		else:
			return ("Invalid command!",0)

classes = {"Premium":Broker_P,"Free":Base_Broker}
