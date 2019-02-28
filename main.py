import discord
from discord.ext import commands
import asyncio
import logging
import json
import io
from datetime import datetime, date, time
import utils.config as config
import utils.checks as checks

token = config.getToken()
guildID = config.getGuildID()
inboxID = config.getInboxID()
modRoleID = config.getModRoleID()
activeMails = []

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = discord.Bot(command_prefix='>', description="ModMail Bot. DM to contact Staff")

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	load_active()
	if guildID == None:
		await bot.change_presence(activity=discord.Game(name='Requires setup. See README'), status=discord.Status.dnd)
	else:
		await bot.change_presence(activity=discord.Game(name='DM to contact staff'))

@bot.event
async def on_message(msg):
	if msg.author.bot:
		return
	elif isinstance(msg.channel, discord.DMChannel):
		if guildID == None:
			await msg.channel.send('Bot not setup. Contact server administrators.')
		else:
			await process_report(msg)
	else:
		bot.process_commands(msg)

async def on_command_error(ctx, err):
	if isinstance(err, commands.CheckFailure):
		pass
	elif isinstance(err, commands.CommandNotFound):
		pass
	else:
		print(err)

async def on_raw_reaction_add(payload):
	pass

async def on_raw_reaction_remove(payload):
	pass

async def process_report(msg):
	pass

def load_active():
	try:
		with open('utils/activeMails.txt') as data_file:
			data = json.load(data_file)
			for item in data:
				mailItem = data[item]
				mail = Object()
				mail.ticketID = mailItem['id']
				mail.botMsgID = mailItem['botMsgID']
				activeMails.append(mail)
	except FileNotFoundError:
		pass

def save_active():
	mails = {}
	for item in activeMails:
		mail = {'id': item.mailID, 'botMsgID':item.botMsgID}
		mails[item.mailID] = mail
	with io.open('utils/activeMails.txt', 'w', encoding='utf-8') as f:
		f.write(json.dumps(mails, sort_keys=True, indent=4, ensure_ascii=False))

@bot.command()
async def setup(ctx, roleID):
	"""Sets up the bot, requires ID of Moderator role. Use command in channel you want reports to be sent to"""
	global guildID, inboxID, modRoleID
	#setup goes here
	await bot.change_presence(activity=discord.Game(name='DM to contact staff'), status=discord.Status.online)

bot.run(token)