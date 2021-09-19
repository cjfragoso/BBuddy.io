import api_keys
from Brokers import Broker_P
import sys
c = Broker_P("whatsapp:+PHONE",api_keys.api_key,api_keys.api_secret)
def show_data():
	print("Balance USDT\n")
	print(c.process_command(['balance'])[0])
	print("\n")
	print("Balance BTC")
	print(c.process_command(['balance','btc'])[0])
	print("\n")
	print("Balance ETH")
	print(c.process_command(['balance','ETH'])[0])

if __name__ == '__main__':
	if len(sys.argv) > 1:

		if sys.argv[1] == 'show':
			show_data()
	else:
		print("No args, available args =[show]")
