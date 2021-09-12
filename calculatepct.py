import pandas as pd

#Convert to usd -> save balance 
#Convert to btc -> save balance

def calculate_pct(start_values,end_values,base):
	resp = {}
	for i in end_values.keys():
		if i in start_values.keys():
			s = pd.Series([float(start_values[i]),float(end_values[i])])
			resp[i] = [end_values[i],"{0:.2f}%".format((s.pct_change()[len(s.pct_change())-1])*100)]
		else:
			resp[i] = [end_values[i],"*N*"]
	response = []
	
	for i in sorted(resp.items(),key=lambda kv: float(kv[1][0]),reverse=True):
		if base=="USDT":
			response.append([i[0],"{0:.2f}".format(i[1][0]),i[1][1]])
		elif base=="BTC":
			response.append([i[0],"{0:.8f}".format(i[1][0]),i[1][1]])
		elif base=="ETH":
			response.append([i[0],"{0:.8f}".format(i[1][0]),i[1][1]])

	
	r = response[1:]
	r.append(response[0])
	lens = []
	for i in zip(*r):
		lens.append(max([len(v) for v in i]))
	total = []
	formatter1 = "{0:<"+str(lens[0]-1)+"}: "+"{1:<"+str(lens[1]+1)+"} "+"{2:<"+str(lens[2])+"}"
	formatter2 = "{0:<"+str(lens[0]-1)+"}: "+"{1:<"+str(lens[1]+1)+"} "+"{2:>"+str(lens[2]+1)+"}"
	for i in r:
		if '-' in i[2]:
			total.append(formatter1.format(i[0],i[1],i[2]))
		else:
			total.append(formatter2.format(i[0],i[1],i[2]))
	ret = "\n".join(total)	
	return ret

#DB Balances:
#BTC -> {asset:price}
#USDT-> {asset:price}

#Calculate pct on base
#Convert to usd current balance, get old usd balance, calculate pct -> save both usd and btc balances
#Convert to btc current balance, get old btc balance, calculate pct -> save both usd and btc balances
