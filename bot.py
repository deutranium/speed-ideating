import os
import discord
from tabulate import tabulate
from dotenv import load_dotenv

load_dotenv()
client = discord.Client()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


# TODO: Add all the teams here
scoreboard = [
	["1", "The Boys", 20],
	["2", "MCDT", 20],
	["3", "Fluffy's 3 Heads", 20],
	["4", "Mario & the other guy", 20],
	["5", "www.", 20],
	["6", "The Intrepids", 20]
]

# Help info
def help():
	help_msg = """```Commands (prepend `!si` to all the commands):

	update <team_no> <+/-score>: Increase/decrease the score of team `team_no` by `score` on +/-
	scoreboard:                     Display the scoreboard
	history:                        Show history
	```
	"""

	return help_msg

# Print scoreboard
def print_scoreboard():
	data = scoreboard
	headers = ["Team #", "Name", "Score"]
	content = tabulate(data, headers, tablefmt="fancy_grid")
	
	return ("```\n" + content + "\n```")

# Update team scores
def update_score(team, score):
	initial = scoreboard[team - 1][2]
	scoreboard[team - 1][2] = initial + score

# TODO: ADD ALL THE UPDATES TO READ-ONLY HISTORY CHANNEL
# def add_to_history(message):
	# print(client)
	# print(client.guilds.channels)


@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!\n')
	guild = discord.utils.get(client.guilds, name=GUILD)

	print(
		f'{client.user} is connected to the following guild:\n'
		f'{guild.name}(id: {guild.id})'
	)

@client.event
async def on_message(message):
	msg = "A valid command plox"
	cntnt = message.content.lower()

	# Check bot prefix
	if (cntnt.split()[0] != "!si")  or message.author.bot:
		return

	# remove the prefix
	cntnt = " ".join(cntnt.split()[1:])

	# help
	if cntnt == "help":
		msg = help()

	# display scoreboard
	elif cntnt == "scoreboard":
		msg = print_scoreboard()

	# update team score
	elif cntnt.split()[0] == "update":
		stuff = cntnt.split()
		update_score(int(stuff[1]), int(stuff[2]))
		# add_to_history(stuff)
		msg = print_scoreboard()
	await message.channel.send(msg)

client.run(TOKEN)
