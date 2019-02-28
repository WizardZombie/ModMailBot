import io
import json

token = None
guildID = None

def setup():
	data = {}
	print('Config file not found! Creating ...')
    while userInput == "":
    	userInput = input('Please enter bot token: \n')
    data['token'] = userInput
    data['guildID'] = None
	inboxID = data['inboxID']
	modRoleID = data['modRoleID']
    save_data(data)
    return data

def save_data(data):
	with io.open('utils/config.txt', 'w', encoding='utf-8') as f:
		f.write(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False))

def load_data():
	try:
		with open('utils/config.txt') as data_file:
			data = json.load(data_file)
	except FileNotFoundError:
		data = setup()
	return data

data = load_data()
token = data['token']
guildID = data['guildID']
inboxID = data['inboxID']
modRoleID = data['modRoleID']

def getToken():
	return token

def getGuildID():
	return guildID

def getInboxID():
	return inboxID

def getModRoleID():
	return modRoleID

