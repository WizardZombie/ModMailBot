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
guildObj = None
inboxChnl = None

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix='>', description="ModMail Bot. DM to contact Staff")

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
		global guildObj, inboxChnl
		await bot.change_presence(activity=discord.Game(name='DM to contact staff'))
		guildObj = bot.get_guild(guildID)
		inboxChnl = guildObj.get_channel(inboxID)

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

@bot.event
async def on_raw_reaction_add(payload):
	user = guildObj.get_member(payload.user_id)
	if user.bot:
		return
	elif payload.channel_id == inboxID:
		for item in activeMails:
			if payload.message_id == item.botMsgID:
				msg = await inboxChnl.get_message(payload.message_id)
				if payload.emoji.name == '\U0001F50D':
					await assign_mail(msg, item.mailID, user)
				elif payload.emoji.name == '\u2705':
					await close_mail(msg, item.mailID, user)
				else:
					for reaction in msg.reactions:
						if payload.emoji.name == '\U0001F50D' or payload.emoji.name == '\u2705':
							pass
						else:
							await reaction.remove(user)
				return
			else:
				pass
	else:
		pass

@bot.event
async def on_raw_reaction_remove(payload):
	user = await bot.get_user_info(payload.user_id)
	for item in activeMails:
		if payload.message_id == item.botMsgID:
			mail = get_mail(item.mailID)
			if mail['status'] == 1:
				if payload.emoji.name == '\u2705':
					msg = await inboxChnl.get_message(payload.message_id)
					await msg.add_reaction(payload.emoji.name)
					return
				else:
					pass
			else:
				if payload.emoji.name == '\U0001F50D' or payload.emoji.name == '\u2705':
					msg = await inboxChnl.get_message(payload.message_id)
					await msg.add_reaction(payload.emoji.name)
					return
				else:
					pass
		else:
			pass

async def process_mail(msg):
	recievedAt = datetime.utcnow()
	mail = {}
	mail['id'] = msg.id
	mail['senderID'] = msg.author.id
	mail['mailContent'] = msg.content
	mail['status'] = 0
	mail['staff_member'] = None
	mail['recievedAt'] = {
		'year':recievedAt.year,
		'month':recievedAt.month,
		'day':recievedAt.day,
		'hour':recievedAt.hour,
		'minute':recievedAt.minute,
		'second':recievedAt.second
	}
	with io.open('mails/' + str(msg.id) + '.txt', 'w', encoding='utf-8') as f:
		f.write(json.dumps(mail, sort_keys=True, indent=4, ensure_ascii=False))
	em = discord.Embed(title="**__ModMail Recieved__**", colour=0xe74c3c)
	em.add_field(name="**Sender**", value=msg.author.mention, inline=False)
	em.add_field(name="**Message**", value=msg.content, inline=False)
	em.add_field(name="**Status**", value="Open", inline=True)
	em.add_field(name="**Staff Member**", value="None", inline=True)
	em.timestamp = recievedAt
	em.set_footer(text='ID: ' + str(msg.id))
	botMsg = await inboxChnl.send(embed=em)
	await botMsg.add_reaction('\N{LEFT-POINTING MAGNIFYING GLASS}')
	await botMsg.add_reaction('\N{WHITE HEAVY CHECK MARK}')
	newMail = Object()
	newMail.mailID = msg.id
	newMail.botMsgID = botMsg.id
	activeMails.append(newMail)
	save_active()
	await msg.channel.send('Your mail (ID: ' + str(msg.id) + ') has been sent')

async def assign_mail(msg, mailID, user):
	mail = get_mail(mailID)
	if mail['status'] == 1:
		for reaction in msg.reactions:
			try:
				await reaction.remove(user)
			except discord.NotFound:
				pass
		return
	else:
		pass
	senderID = mail['senderID']
	sender = await bot.get_user_info(senderID)
	em = discord.Embed(title="**__ModMail Recieved__**", colour=0xff9d00)
	em.add_field(name="**Sender**", value=sender.mention, inline=False)
	em.add_field(name="**Message**", value=mail['mailContent'], inline=False)
	em.add_field(name="**Status**", value="Assigned", inline=True)
	em.add_field(name="**Staff Member**", value=user.mention, inline=True)
	recievedAt = mail['recievedAt']
	em.timestamp = datetime(recievedAt['year'], recievedAt['month'], recievedAt['day'], recievedAt['hour'], recievedAt['minute'], recievedAt['second'])
	em.set_footer(text='ID: ' + str(mail['id']))
	mail['status'] = 1
	mail['staff_member'] = user.id
	save_mail(mail)
	await msg.edit(embed=em)
	await msg.clear_reactions()
	await msg.add_reaction('\N{WHITE HEAVY CHECK MARK}')

async def close_mail(msg, mailID, user):
	mail = get_mail(mailID)
	if mail['status'] == 1:
		if user.id == mail['staff_member'] or user.permissions_in(inboxChnl).administrator:
			pass
		else:
			for reaction in msg.reactions:
				try:
					await reaction.remove(user)
				except discord.NotFound:
					pass
			return
	else:
		pass
	sender = await bot.get_user_info(mail['senderID'])
	em = discord.Embed(title="**__ModMail Recieved__**", colour=0x2ecc71)
	em.add_field(name="**Sender**", value=sender.mention, inline=False)
	em.add_field(name="**Message**", value=mail['mailContent'], inline=False)
	em.add_field(name="**Status**", value="Resolved", inline=True)
	em.add_field(name="**Staff Member**", value=user.mention, inline=True)
	recievedAt = mail['recievedAt']
	em.timestamp = datetime(recievedAt['year'], recievedAt['month'], recievedAt['day'], recievedAt['hour'], recievedAt['minute'], recievedAt['second'])
	em.set_footer(text='ID: ' + str(mail['id']))
	mail['status'] = 2
	mail['staff_member'] = user.id
	save_mail(mail)
	await msg.edit(embed=em)
	await msg.clear_reactions()

def get_mail(mailID):
	try:
		with open('mails/' + str(mailID) + '.txt') as data_file:
			data = json.load(data_file)
			return data
	except FileNotFoundError:
		return None

def save_mail(data):
	with io.open('mails/' + str(data['id']) + '.txt', 'w', encoding='utf-8') as f:
		f.write(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False))

async def _delete_msg(msg):
	await msg.delete()

async def _wait_delete(msg, time):
	await asyncio.sleep(time)
	await _delete_msg(msg)

def load_active():
	try:
		with open('mails/activeMails.txt') as data_file:
			data = json.load(data_file)
			for item in data:
				mailItem = data[item]
				mail = Object()
				mail.mailID = mailItem['id']
				mail.botMsgID = mailItem['botMsgID']
				activeMails.append(mail)
	except FileNotFoundError:
		pass

def save_active():
	mails = {}
	for item in activeMails:
		mail = {'id': item.mailID, 'botMsgID':item.botMsgID}
		mails[item.mailID] = mail
	with io.open('mails/activeMails.txt', 'w', encoding='utf-8') as f:
		f.write(json.dumps(mails, sort_keys=True, indent=4, ensure_ascii=False))

@bot.command()
@checks.isAdmin()
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

@bot.command()
@checks.isMod()
async def retrieve(ctx, mailID):
	await _delete_msg(ctx.message)
	mail = get_mail(mailID)
	sender = await bot.get_user_info(mail['senderID'])
	staff = await bot.get_user_info(mail['staff_member'])
	em = discord.Embed(title="**__ModMail " + str(mail['id']) + "__**", colour=0x000000)
	em.add_field(name="**Sender**", value=sender.mention, inline=False)
	em.add_field(name="**Message**", value=mail['mailContent'], inline=False)
	if mail['status'] == 2:
		em.colour = 0x2ecc71
		em.add_field(name="**Status**", value="Resolved", inline=True)
	elif mail['status'] == 2:
		em.colour = 0xff9d00
		em.add_field(name="**Status**", value="Assigned", inline=True)
	else:
		em.colour = 0xe74c3c
		em.add_field(name="**Status**", value="Open", inline=True)
	em.add_field(name="**Staff Member**", value=staff.mention, inline=True)
	recievedAt = mail['recievedAt']
	em.timestamp = datetime(recievedAt['year'], recievedAt['month'], recievedAt['day'], recievedAt['hour'], recievedAt['minute'], recievedAt['second'])
	em.set_footer(text='ID: ' + str(mail['id']))
	await _wait_delete(await ctx.channel.send(embed=em), 30)

class Object(object):
	pass

bot.run(token)