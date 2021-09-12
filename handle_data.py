from alarmdb import AlertManager as manager
from twilio.rest import Client
account_sid = 'TWILIO ACCOUNT_SID'
auth_token = 'TWILIO AUTH_TOKEN'
alert_manager = manager()
client = Client(account_sid,auth_token)
clients = {}
def build_up_client():
	datac,state = alert_manager.get_alarms()
	if state:
		for i in range(len(datac)):
			clients[datac[i][0]] = [datac[i][1].split(','),datac[i][2].split(',')]
	else:
		pass

build_up_client()
def handle_alarm(d):
	if d[1].lower() == "info" and d[0] in clients.keys():
		build_up_client()
		datas = clients[d[0]]
		return (" ".join([",".join(datas[0])] +  [",".join(datas[1])]),True)
	elif d[1].lower() == "info" and d[0] not in clients.keys():
		return (None,True)
	elif d[1].lower() == "clear" and len(d) > 2:
		if d[2] == '1':
			alert_manager.clear_alarm_for_user(d[0],"alarm1")
			build_up_client()
			return ("set",True)
		elif d[2] == '2':
			alert_manager.clear_alarm_for_user(d[0],"alarm2")
			build_up_client()
			return ("set",True)
		else:
			return("set",False)
	elif len(clients) > 0 and d[0] in clients.keys():
		if clients[d[0]][0][0] != "done" and clients[d[0]][1][0] !="done":
			return ("set",False)
		else:
			for i in clients.keys():
				if d[0] == i:
					if "done" in clients[i][0][0]:
						alert_manager.register_alarm(i,",".join([d[1],d[2],d[3]]),"alarm1")
						build_up_client()
						return ("set",True)
					elif "done" in clients[i][1][0]:
						alert_manager.register_alarm(i,",".join([d[1],d[2],d[3]]),"alarm2")
						build_up_client()
						return ("set",True)
	else:
		alert_manager.register_user(d[0],",".join([d[1],d[2],d[3]]))
		build_up_client()
		return ("set",True)


def send_message(phone,msg):
	message = client.messages.create(body=msg,from_='whatsapp:+',to=phone)


def response(msg):
	data = {i['s']:i['c'] for i in msg}
	log = open('log.txt','w')
	log.write(str(data))
	log.close()
	
	if len(clients) > 0:
		for i in clients.keys():
			for v in range(len(clients[i])):
				alerts = clients[i][v]
				if alerts[0].lower() == "up":
					try:
						if float(data[alerts[1]]) > 1:
							formatt = "{:,.2f}"
						else:
							formatt = "{:."+str(len(data[alerts[1]]))+"f}"
						if float(data[alerts[1]]) >= float(alerts[2]):
							if v == 0:
								alert_manager.update_alarm(i,"alarm1")
								send_message(i,"  Alert! Your alert for symbol {} {} has reached {}".format(alerts[1].upper(),alerts[2],formatt.format(float(data[alerts[1]]))))
								build_up_client()
							elif v == 1:
								alert_manager.update_alarm(i,"alarm2")
								send_message(i,"  Alert! Your alert for symbol {} {} has reached {}".format(alerts[1].upper(),alerts[2],formatt.format(float(data[alerts[1]]))))
								build_up_client()
					except Exception as e:
						alertlog = open('alertlogs.txt','w+')
						alertlog.write(str(e)+"\n")
						alertlog.close()
				elif alerts[0].lower() == "down":
					try:
						if float(data[alerts[1]]) > 1:
							formatt = "{:,.2f}"
						else:
							formatt = "{:."+str(len(data[alerts[1]]))+"f}"
						if float(data[alerts[1]]) <= float(alerts[2]):
							if v == 0:
								alert_manager.update_alarm(i,"alarm1")
								send_message(i,"  Alert! Your alert for symbol {} {} has reached {}".format(alerts[1].upper(),alerts[2],formatt.format(float(data[alerts[1]]))))
								build_up_client()
							elif v ==1:
								alert_manager.update_alarm(i,"alarm2")
								send_message(i,"  Alert! Your alert for symbol {} {} has reached {}".format(alerts[1].upper(),alerts[2],formatt.format(float(data[alerts[1]]))))
								build_up_client()
					except Exception as e:
						alertlog = open('alertlogs.txt','w+')
						alertlog.write(str(e)+"\n")
						alertlog.close()
