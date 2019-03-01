ModMailBot
===
ModMail Bot for Discord

## This bot is designed to act as a ModMail system for your Discord server. Simply place the files in this repo on a server, and run the main.py file. 

Initial setup will require the token for the bot user you wish to use on your server (entered through console, prompts on startup), then simply go to the text channel you wish to designate as the Mail Inbox, and type >setup <@ModRoleTag>.

### Functions
* Recieves ModMail messages via Direct Message, and posts to an inbox channel on your server
* Actioning of these mails via reactions
  * Invetigate - Allows a staff member to assign a mail to themselves if it requires further investigation
  * Close - Once handled, a mail can be closed. This can be done from both Open and Assigned states. If ModMail is assigned, bot will check to ensure the assigned staff member, or an admin, is closing, to prevent accidental closure of a ticket.
* Permanant storage of Mails for archival purposes

### Commands
* \>setup <@ModRoleTag> - Use to set the inbox channel and the moderator role of the server
* \>retrieve \<mailID> - Use to view information on a ModMail
