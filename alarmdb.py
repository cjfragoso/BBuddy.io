import sqlite3
import datetime


class AlertManager():
	def __init__(self):
		self.__connect()
	def __connect(self):
		self.__connected = True
		self.__conn = sqlite3.connect("alerts/alerts.db")
		self.__c = self.__conn.cursor()
	def __disconnect(self):
		if self.__connected:
			self.__conn.close()
			self.__connected = False
	def register_user(self,phone,alert):
		date_created = str(datetime.datetime.today())
		if not self.__connected:
			self.__connect()
			self.__c.execute("insert into alert values (?,?,?,?);",(phone,alert,"done",date_created))
			self.__conn.commit()
			self.__disconnect()
		else:
			self.__c.execute("insert into alert values (?,?,?,?);",(phone,alert,"done",date_created))
			self.__conn.commit()
			self.__disconnect()
	def clear_alarm_for_user(self,phone,which_alarm):
		if not self.__connected:
			self.__connect()
			if which_alarm == "alarm1":
				self.__c.execute("update alert set alarm1='done,done' where phone=?",(phone,))
				self.__conn.commit()
				self.__disconnect()
			elif which_alarm == "alarm2":
				self.__c.execute("update alert set alarm2='done,done' where phone=?",(phone,))
				self.__conn.commit()
				self.__disconnect()
			elif which_alarm == "both":
				self.__c.execute("update alert set alarm1='done,done',alarm2='done,done' where phone=?",(phone,))
				self.__conn.commit()
				self.__disconnect()
	def register_alarm(self,phone,alert,type_alert):
		if not self.__connected:
			self.__connect()
			date_created = str(datetime.datetime.today())
			if type_alert == "alarm1":
				self.__c.execute("update alert set alarm1=?,date_created=? where phone=?",(alert,date_created,phone))
				self.__conn.commit()
				self.__disconnect()
				return True
			elif type_alert == "alarm2":
				self.__c.execute("update alert set alarm2=?,date_created=? where phone=?",(alert,date_created,phone))
				self.__conn.commit()
				self.__disconnect()

	def get_alarms_for_user(self,phone):
		try:
			user = [i for i in self.__c.execute("select alarm1,alarm2 from alert where phone=?",(phone,)).fetchone()]
			return user
		except:
			return None
	def get_alarms(self):
		if self.__connected:			
			data = [i for i in self.__c.execute("select * from alert")]
			self.__disconnect()
			if len(data) > 0:
				return (data,True)
			else:
				return ("no_data",False)
		else:
			self.__connect()
			data = [i for i in self.__c.execute("select * from alert")]
			self.__disconnect()
			if len(data) > 0:
				return (data,True)
			else:
				return ("no_data",False)


	def update_alarm(self,phone,alert):
		if not self.__connected:
			self.__connect()
			if alert == "alarm1":
				self.__c.execute("update alert set alarm1='done,done' where phone=?",(phone,))
				self.__conn.commit()
				self.__disconnect()
			else:
				self.__c.execute("update alert set alarm2='done,done' where phone=?",(phone,))
				self.__conn.commit()
				self.__disconnect()
