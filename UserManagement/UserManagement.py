import uuid
import os
import hashlib
import sqlite3
import datetime
import getpass
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Admin():
	def __init__(self):
		self.__connect()
	def __connect(self):
		self.__connected = True
		self.__conn = sqlite3.connect("/Users/CJFSantoni/Desktop/BBuddy/UserManagement/clients.db")
		self.__c = self.__conn.cursor()
	def __disconnect(self):
		if self.__connected:
			self.__conn.close()
			self.__connected = False
	def get_n_calls(self):
		if self.__connected:
			n_calls = self.__c.execute("select n_calls from clients;").fetchall()
			n_calls = [i[0] for i in n_calls]
			self.__conn.close()
			self.__connected = False
			data = str(sum(n_calls)*0.005)
			return "Total calls US $ {}\nTotal calls {}".format(data,str(sum(n_calls)))
		else:
			self.__connect()
			self.get_n_calls()

class UserManagement():

	def __init__(self):
		self.__connect()

	def __connect(self):
		self.__connected = True
		self.__conn = sqlite3.connect("/Users/CJFSantoni/Desktop/BBuddy/UserManagement/clients.db")
		self.__c = self.__conn.cursor()
	def __disconnect(self):
		if self.__connected:
			self.__conn.close()
			self.__connected = False
	def register_balances(self,phone,balance,base):
		if not self.__connected:
			self.__connect()
		if base=="BTC":
			self.__c.execute("update clients set balance_btc=? where phone=?",(balance,phone))
			self.__conn.commit()
			self.__disconnect()
		elif base=="USDT":
			self.__c.execute("update clients set balance_usdt=? where phone=?",(balance,phone))
			self.__conn.commit()
			self.__disconnect()
		elif base=="ETH":
			self.__c.execute("update clients set balance_eth=? where phone=?",(balance,phone))
			self.__conn.commit()
			self.__disconnect()

	def get_old_balance(self,phone,base):
		if not self.__connected:
			self.__connect()
		if base=="USDT":
			val = self.__c.execute("select balance_usdt from clients where phone=?",(phone,)).fetchone()
			vals = eval(val[0])
			return vals
		elif base=="BTC":
			val = self.__c.execute("select balance_btc from clients where phone=?",(phone,)).fetchone()
			vals = eval(val[0])
			return vals
		elif base=="ETH":
			val = self.__c.execute("select balance_eth from clients where phone=?",(phone,)).fetchone()
			vals = eval(val[0])
			return vals
	def select(self,value=None):
		if value != None:
			obj = self.__c.execute("select type,api_key,api_secret from clients where phone=?;",(value,)).fetchone()
			return obj
		else:
			obj = self.__c.execute("select * from clients;")
			return obj



	def select_update(self,phone):
		self.__connect()
		user_data = self.__c.execute("select n_calls from clients where phone=?",(phone,)).fetchone()
		return user_data
	
	def update_usage(self,phone):
		fphone=phone.strip("whatsapp:+1")
		
		bot_init = self.__c.execute('select n_calls from clients where phone=?;',(phone,)).fetchone()[0]
		chat_ready = sqlite3.connect("/home/CJFS/bbuddy-website/database/database.sqlite")
		c = chat_ready.cursor()
		val = c.execute("select chat_ready from users where telephone=?;",(fphone,)).fetchone()
		if val[0] == None:
			os.system('/usr/bin/php7.2 /home/CJFS/bbuddy-website/artisan bbuddy:chatready {}'.format(fphone))
			chat_ready.close()
		else:
			#os.system('/usr/bin/php7.2 /home/CJFS/bbuddy-website/artisan bbuddy:chatready {}'.format(fphone))
			chat_ready.close()
			pass
		user_data = self.select_update(phone)
		last_call = str(datetime.datetime.today().strftime("%d/%m %I:%M %p"))
		n_calls = int(user_data[0])
		#print("*************************************************{}".format(n_calls))
		n_calls += 1
		self.__c.execute("update clients set last_call=?, n_calls=? where phone=?",(last_call,str(n_calls),phone))
		self.__conn.commit()
		self.__disconnect()
		return True

	

	def beta_register(self,phone,intent,value):
		self.__connect()
		if intent == "api_key" and value =="s":
			self.__c.execute("update clients set api_key=? where phone=?",(value,phone))
			self.__conn.commit()
			self.__disconnect()
			return True
		elif intent == "api_key" and value !="s":
			self.__c.execute("update clients set type='Beta2', api_key=? where phone=?",(value,phone))
			self.__conn.commit()
			self.__disconnect()
			return True
		elif intent == "api_secret" and value =="s":
			self.__c.execute("update clients set api_secret=? where phone=?",(value,phone))
			self.__conn.commit()
			self.__disconnect()
			return True
		elif intent == "api_secret" and value !="s":
			self.__c.execute("update clients set type='Premium', api_secret=? where phone=?",(value,phone))
			self.__conn.commit()
			self.__disconnect()
			return True
		else:
			return False

	def __validate_email(self,email):
		obj = self.select(email).fetchall()
		if len(obj) > 0:
			for i in obj:
				if email in obj[0]:
					return False
				else:
					return True
		else:
			return True
		
	def make_user(self,phone,email,password):
		if not self.__connected:
			self.__connect()
		valid = self.__validate_email(email)
		if not valid:
			return "Email already registered, choose another email address"
		else:

			vals = (phone,email,self.__hash_password(passwd))
			self.__c.execute("insert into clients values (?,?,?);",vals)
			self.__conn.commit()
			self.__disconnect()
			return "Please verify your email"

	def __hash_password(self,password):
	
		salt = uuid.uuid4().hex
		retval = hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ":" + salt
		return retval

	def __check_password(self,user_pass,password):
		passwd, salt = user_pass.split(":")
		return passwd == hashlib.sha256(salt.encode() + password.encode()).hexdigest()

	def login(self,email):
		if not self.__connected:
			self.__connect()
		vals = (username,)
		query = self.__c.execute("select * from clients where username=?;",vals).fetchone()
		if query != None:

			if self.__check_password(query[2],password):
				self.__disconnect()
			else:
				print("Wrong username and password combination")
				self.__disconnect()
		else:
			print("No info")
	def limit_user(self,phone):
		if not self.__connected:
			self.__connect()
			self.__c.execute("insert into first_time_users values (?,?);",(phone,str(datetime.datetime.today())))
			self.__conn.commit()
			f = open('write.log','a')
			f.write("limited {}\n".format(phone))
			f.close()
			self.__disconnect()
		else:
			self.__c.execute("insert into first_time_users values (?,?);",(phone, str(datetime.datetime.today())))
			self.__conn.commit()
			self.__disconnect()
	def is_limited(self,phone):
		if not self.__connected:
			self.__connect()
			user = self.__c.execute("select * from first_time_users where phone=?;",(phone,)).fetchone()
			
			if user == None:
				self.__disconnect()
				return False
			else:
				self.__disconnect()
				return True
		else:
			user = self.__c.execute("select * from first_time_users where phone=?;",(phone,)).fetchone()
			if user == None:
				self.__disconnect()
				return False
			else:
				self.__disconnect()
				return True
