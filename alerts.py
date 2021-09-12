import socket
import sys
from binance.websockets import BinanceSocketManager
from binance.client import Client
import handle_data
from alarmdb import AlertManager as manager
server_address = "./uds_socket"
client = Client('API_KEYS','API_SECRET')
bm = BinanceSocketManager(client)
key = bm.start_ticker_socket(handle_data.response)
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.bind(server_address)
sock.listen()
bm.start()
while True:
	# Wait for a connection
	connection, client_address = sock.accept()
	try:
		
	# Receive the data in small chunks and retransmit it
		while True:
			data = connection.recv(1024)
			if data:
				d = data.decode('utf-8').split(',')
				resp,state = handle_data.handle_alarm(d)
				if resp != "set" and resp != None:
					user_alarms = resp.encode('utf-8')
					connection.sendall(user_alarms)
				elif resp is None:
					connection.sendall(b'None')
				elif state:
					connection.sendall(b'valid')
				else:
					connection.sendall(b'invalid')
			else:
				break
	finally:
		# Clean up the connection
		connection.close()
