from twilio.rest import Client
import sqlite3
import sys
account_sid = 'TWILIO ACCOUNT_SID'
auth_token = 'TWILIO AUTH_TOKEN'
client = Client(account_sid,auth_token)

conn = sqlite3.connect("UserManagement/clients.db")
c = conn.cursor()
clients = c.execute("select phone from clients;").fetchall()
numbers = []
for i in clients:
	numbers.append(i[0])

mantenimiento = "*----*"
welcome = "-----"
if __name__=='__main__':
	if sys.argv[1] == "welcome":
		for i in numbers:
			message = client.messages.create(body=welcome,from_='whatsapp:+TWILIO_NUMBER',to=i)
			print(message)
		print("Done")
	else:
		for i in numbers:
			message = client.messsages.create(body=mantenimiento,from_='whatsapp:+TWILIO_NUMBER',to=i)
			print(message)
		print("done")
