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

bot = commands.Bot(command_prefix='>', description="ModMail Bot. DM to contact Staff")

guildObj = bot.get_guild(guildID)
inboxChnl = guildObj.get_channel(inboxID)

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
			await process_mail(msg)
	else:
		await bot.process_commands(msg)

@bot.event
async def on_command_error(ctx, err):
	if isinstance(err, commands.CheckFailure):
		pass
	elif isinstance(err, commands.MissingRequiredArgument):
		await _delete_msg(ctx.message)
		param = err.param
		await _wait_delete(await ctx.channel.send(f'Missing {param}. Please check parameters and try again.'), 10)
	elif isinstance(err, commands.CommandNotFound):
		pass
	else:
		print(err)

async def on_raw_reaction_add(payload):
	pass

async def on_raw_reaction_remove(payload):
	pass

async def process_mail(msg):
	mail = {}
	mail['sender'] = msg.author.id
	mail['mailContent'] = msg.content
	mail['status'] = 0
	mail['staff_member'] = None
	with io.open('utils/' + str(msg.id) + '.txt', 'w', encoding='utf-8') as f:
		f.write(json.dumps(mail, sort_keys=True, indent=4, ensure_ascii=False))
	em = discord.Embed(title="**__ModMail Recieved__**")
	em.add_field(name="**Sender**", value=msg.author.mention)
	em.add_field(name="**Message**", value=msg.content)
	em.add_field(name="**Status**", value="Open")
	em.add_field(name="**Staff Member**", value="None")
	botMsg = await inboxChnl.send(embed=em)
	await botMsg.add_reaction('\N{LEFT-POINTING MAGNIFYING GLASS}')
	await botMsg.add_reaction('\N{WHITE HEAVY CHECK MARK}')

async def _delete_msg(msg):
	await msg.delete()

async def _wait_delete(msg, time):
	await asyncio.sleep(time)
	await _delete_msg(msg)

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
async def setup(ctx, roleTag):
	"""Sets up the bot, requires ID of Moderator role. Use command in channel you want reports to be sent to"""
	await _delete_msg(ctx.message)
	roleList = ctx.message.role_mentions
	if len(roleList) > 1:
		await ctx.channel.send('Please only mention 1 role!')
		return
	else:
		global guildID, inboxID, modRoleID
		guildID = ctx.guild.id
		inboxID = ctx.channel.id
		modRole = None
		for role in roleList:
			modRole = role
			modRoleID = role.id
		config.setConfig(guildID, inboxID, modRoleID)
		await bot.change_presence(activity=discord.Game(name='DM to contact staff'), status=discord.Status.online)
		await _wait_delete(await ctx.channel.send('This channel now set as inbox. ' + modRole.name + " set as moderator role."), 10)

bot.run(token)