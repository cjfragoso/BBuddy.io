import os
import time
from UserManagement.UserManagement import UserManagement
from Brokers import *
import re
import difflib
from allowed_commands import *


def validate_intent(phone,message):
	pool = []
	user_data = ""
	user_type = ""
	user_broker = ""
	user_api_key = ""
	user_api_secret = ""
	message = re.sub(' +',' ',message)
	try:
		for i in message.split(' '):
			pool.append(i)
	except:
		pool.append(message)
	
	manager = UserManagement()
	try:
	
		user_data = manager.select(phone)
		user_type = user_data[0]
	except:
		valid = manager.is_limited(phone)
		f = open('limited.log','a')
		f.write(str(valid))
		f.close()
		if valid:
			print("User is limited")
			f = open('limited.log','a')
			f.write("{}:Limited".format(phone))
			f.close()
		else:
			manager.limit_user(phone)
			return ("Welcome to *BBuddy.io*\nTo register go to the website https://BBuddy.io/register",0)
	try:
		if pool[0] == "?" or difflib.get_close_matches(pool[0],allowed_commands[user_type])[0] == "help":
			return(help_message[user_type],0)
	except:
		pass
	if user_type =="Premium" or user_type=="Free":
		if user_data[1] != '' and user_data[2] != '': 
			user_api_key= user_data[1]
			user_api_secret = user_data[2]
			instance = classes[user_type](phone,user_api_key,user_api_secret)
			resp = instance.process_command(pool)
			manager.update_usage(phone)
			return resp
		else:
			return ("Oops!\n Seems like you're missing your\n*api keys and secret* go to\nhttps://bbuddy.io/members/api-keys\nand register your credentials.",0)
		
	elif user_type == "Beta1" and user_data[1] =="n":
		#register api key for user
		print("first loop")
		beta_register(phone,["/apikey","s"])
		return ("*BBuddy.io*\nWelcome to the closed Beta!\nSend your api key with the following command\n/apikey *yourapikey*",0)
	elif user_type == "Beta1" and user_data[1] =="s":
		if pool[0] == "/apikey":
			beta_register(phone,pool)
			return ("Now send /apisecret *yourapisecret*",0)
		else:
			return ("/apikey *yourapikey*",0)

	
	elif user_type == "Beta2" and pool[0] =="/apisecret":
		beta_register(phone,pool)
		return (allowed_beta["Premium"][1],0)
	elif user_type == "Beta2" and user_data[2] =="s":
		if pool[0] == "/apisecret":
			beta_register(phone,pool)
			user_type = manager.select(phone)
			return (allowed_beta[user_type][1],0)
		else:
			return ("/apisecret *yourapisecret*",0)
		
	
def beta_register(phone,pool):
	manager = UserManagement()
	if pool[0].lower() == "/apikey":
		return manager.beta_register(phone,"api_key",pool[1])
	elif pool[0].lower() == "/apisecret":
		return manager.beta_register(phone,"api_secret",pool[1])
