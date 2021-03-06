import os
import sys
from time import sleep

import discord
from tabulate import tabulate
from dotenv import load_dotenv

from sql import SQL

load_dotenv()
client = discord.Client()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

db = None
history_channel = None

# TODO: Add all the teams here
# Make sure they are in order
team_names = [
    'The Boys',
    'MCDT',
    "Fluffy's 3 Heads",
    'Mario & the other guy',
    'www.',
    'The Intrepids',
    'Detty pigs',
    'The Invincibles',
    'Goal Diggers ',
    'HoynaHoyna',
    'El',
    'Theen Bacche',
    'Tesseract',
    'XD',
    'Ombani',
    'Impostors',
    'God particle',
    'kryptomaniax ',
    'Oreo Sheikhs',
    'Sons of pitches',
    'Strawberry Beans',
]

# admin role ID
ADMIN_ID = 767717031318782003
HISTORY_CHANNEL_ID = 768235871223676948


def help():
    """
    Shows help message
    """
    help_msg = """
```
Commands (prepend `!si` to all the commands):

update <teamA> <teamB> <score>: Transfer `score` points FROM teamA TO teamB
                    scoreboard: Display the scoreboard
```
"""

    return help_msg


def print_scoreboard():
    """
    Returns the scoreboard as a string
    """
    data = db.get_scoreboard()
    headers = ["Team #", "Name", "Score"]
    content = tabulate(data, headers)

    return "```\n" + content + "\n```"


def update_score(from_team_id, to_team_id, score_delta):
    """
    Updates the score
    If successful, returns the new scoreboard otherwise nothing
    """
    if db.update_score(from_team_id, to_team_id, score_delta):
        return print_scoreboard()

    return None


# TODO: ADD ALL THE UPDATES TO READ-ONLY HISTORY CHANNEL
async def add_to_history(message):
    global history_channel

    if history_channel is None:
        history_channel = client.get_channel(HISTORY_CHANNEL_ID)

    await history_channel.send(message)


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!\n")
    guild = discord.utils.get(client.guilds, name=GUILD)

    print(
        f"{client.user} is connected to the following guild:\n"
        f"{guild.name}(id: {guild.id})"
    )


@client.event
async def on_message(message):
    msg = "A valid command plox"
    cntnt = message.content.lower()

    # Check bot prefix
    if (cntnt.split()[0] != "!si") or message.author.bot:
        return

    # Check if the author is an admin
    if ADMIN_ID not in [i.id for i in message.author.roles]:
        await message.channel.send("Only admins allowed")
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
        _, from_team_id, to_team_id, delta = cntnt.split()

        if int(delta) < 0:
            msg = "Only positive score can be transferred.\nCheck !si.help"
        else:
            logs = f"{message.author} requested for transferring {delta} points from {from_team_id} to {to_team_id}"
            msg = update_score(int(from_team_id), int(to_team_id), int(delta))

            if msg is None:
                msg = "Failed to update score"
                logs += "\n\nStatus: FAILED"
            else:
                logs += "\n\nStatus: Successful"

            await add_to_history(logs)

    await message.channel.send(msg)


def main():
    global db
    # setup database and tables
    db = SQL()
    db.setup_table()

    if db.count_rows() == 0:
        db.populate_table(team_names)

    client.run(TOKEN)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(e)
            sleep(10)
