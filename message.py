from flask import Flask, request, send_file, abort
from twilio.twiml.messaging_response import MessagingResponse, Message
from twilio.rest import Client
from twilio.request_validator import RequestValidator
import datetime
import time
import request_handler as handler
import hashlib
import hmac
import base64
import logging
from logging.handlers import RotatingFileHandler
import pytz
import sqlite3
account_sid = 'TWILIO ACCOUNT_SID' 
auth_token = 'TWILIO AUTH_TOKEN' 
client = Client(account_sid, auth_token)
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
handler_log = RotatingFileHandler('bot.log', maxBytes=100000, backupCount=3)
logger = logging.getLogger('tdm')
logger.setLevel(logging.ERROR)
logger.addHandler(handler_log)
@app.route("/",methods=['POST','GET'])
def gateway():
	url ="yourpage.*"
	params = {}
	for i in request.form:
		params[i] = request.form.get(i)
	validator = RequestValidator(auth_token)
	if 'X-Twilio-Signature' not in request.headers:
		return abort(403)
	signature = request.headers['X-Twilio-Signature']
	res = validator.validate(url, params, signature)
	if res:
		phone = request.form.get('From')
		message = request.form.get('Body')
		
		
		#dat = d.localize(n)
		
		record = sqlite3.connect('sent.db')
		c = record.cursor()
		r = MessagingResponse()
		response = handler.validate_intent(phone,message)
		
		try:
			msg = r.message(response[0])
		except:
			return abort(403)
		try:
			c.execute("insert into messages values (?,?,?,?);",(phone,message,response[0].replace('\n','').replace(' ',''),str(n)))
			record.commit()
			record.close()
		except:
			logger.error("-------------------{} {} {} {}".format(phone,message,response[0],str(n)))
		if response[0] == "Piechart":
			msg.media("/{e}".format(e=response[1]))
		#	msg.media("https://youtu.be/AiYZi9YfCiY")
		elif type(response[1]) != int:
			msg.media("/{s}".format(s=response[1]))
		try:	
			return str(r)
		except:
			return abort(403)
	else:
		return abort(403)
@app.route("/",methods=['POST','GET'])
def process():
	try:
		data = request.form.to_dict()
		stat = sqlite3.connect('status.db')
		s = stat.cursor()
		data = request.form.to_dict()
		#SmsStatus string, EventType string, From_n string, to_n string, msgid string)
		s.execute("insert into stat values (?,?,?,?,?);",(data['SmsStatus'],data['MessageStatus'],data['From'],data['To'],data['SmsSid']))
		stat.commit()
		stat.close()
		f = open('status.txt','a')
		f.write(str(data))
		f.close()
		return "200"
	except:
		return abort(404)

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response
if __name__ == "__main__":
	app.run(host='127.0.0.1',port=80)
