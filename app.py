#!flask/bin/python
from flask import Flask, request, jsonify, abort, make_response
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

PROJECT_ROOT = os.path.abspath(os.path.dirname("__file__"))
DRIVER_BIN = os.path.join(PROJECT_ROOT, "bin/chromedriver")	

class ChatbotDriver():
	def setUp(self):	
		self.driver = webdriver.Chrome(executable_path = DRIVER_BIN)
		self.driver.get("http://118.192.65.45:8081/QASiasun/index.jsp")

	def tearDown(self):
		self.driver.close()

	def sendRequest(self, request):
		elem = self.driver.find_element_by_xpath("//input[@name='input'][@class='form-control']")
		elem.clear()
		elem.send_keys(request)
		elem.send_keys(Keys.RETURN)
		assert "No results found." not in self.driver.page_source
		return self.getReply()

	def getReply(self):
		soup = BeautifulSoup(self.driver.page_source, 'html.parser')
		soup = soup.find("div", class_="flash flash-warning panel panel-warning").find(class_='panel-heading')
		replies = soup.decode_contents(formatter="html") 
		reply = replies.split("<br/><br/>")[0]
		print(reply[3:]) 
		return jsonify({'reply': reply[3:]})

app = Flask(__name__)
driver = ChatbotDriver()

@app.route('/start', methods=['GET']) 
def start_service(): 
	driver.setUp()
	return driver.getReply()

@app.route('/close', methods=['GET']) 
def close_service(): 
	driver.tearDown()
	return "Connection is closed!"

@app.route('/food', methods=['POST'])
def get_bot_response():
    if not request.json or not 'user_request' in request.json:
        abort(400)    
    return driver.sendRequest(request.json['user_request'])
    
@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)