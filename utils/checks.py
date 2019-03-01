from discord.ext import commands
import discord.utils
import utils.config as config

def _is_mod_or_admin(ctx):
	author = ctx.message.author
	mod_role_id = config.getModRoleID()
	if mod_role_id in [y.id for y in author.roles]:
		return True
	else:
		return _is_admin_check(ctx)

def _is_admin_check(ctx):
	return ctx.message.author.permissions_in(ctx.channel.id).administrator

def isMod():
	return commands.check(_is_mod_or_admin)

def isAdmin():
	return commands.check(_is_admin_check)