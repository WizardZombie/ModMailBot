import io
import json

token = None
guildID = None
inboxID = None
modRoleID = None

def _setup():
	data = {}
	print('Config file not found! Creating ...')
    while userInput == "":
    	userInput = input('Please enter bot token: \n')
    data['token'] = userInput
    data['guildID'] = None
	inboxID = data['inboxID']
	modRoleID = data['modRoleID']
    _save_data()
    return data

def _save_data():
	data = {
		"token":token,
		"guildID":guildID,
		"inboxID":inboxID,
		"modRoleID":modRoleID
	}
	with io.open('utils/config.txt', 'w', encoding='utf-8') as f:
		f.write(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False))

def _load_data():
	try:
		with open('utils/config.txt') as data_file:
			data = json.load(data_file)
	except FileNotFoundError:
		data = _setup()
	return data

data = _load_data()
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

def setConfig(serverID, channelID, roleID):
	guildID = serverID
	inboxID = channelID
	modRoleID = roleID
	_save_data()


