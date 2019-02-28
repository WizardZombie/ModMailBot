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
activeMails = []

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)