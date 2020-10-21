import os
import sys

import discord
from tabulate import tabulate
from dotenv import load_dotenv

from sql import SQL

load_dotenv()
client = discord.Client()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

db = None

# TODO: Add all the teams here
# Make sure they are in order
team_names = [
    "The Boys",
    "MCDT",
    "Fluffy's 3 Heads",
    "Mario & the other guy",
    "www.",
    "The Intrepids",
]

# admin role ID
admin_id = 767717031318782003

# Help info
def help():
    help_msg = """
```
Commands (prepend `!si` to all the commands):

update <team_no> <score>: Increase/decrease the score of team `team_no` by `score`. Write the score as negative to decrease it
              scoreboard: Display the scoreboard
                 history: Show history
```
"""

    return help_msg


# Print scoreboard
def print_scoreboard():
    """
    Returns the scoreboard as a string
    """
    data = db.get_scoreboard()
    headers = ["Team #", "Name", "Score"]
    content = tabulate(data, headers, tablefmt="fancy_grid")

    return "```\n" + content + "\n```"


# Update team scores
def update_score(team_id, score_delta):
    """
    Updates the score
    If successful, returns the new scoreboard otherwise an error message
    """
    if db.update_score(team_id, score_delta):
        return print_scoreboard()

    return "Failed to update score"


# TODO: ADD ALL THE UPDATES TO READ-ONLY HISTORY CHANNEL
# def add_to_history(message):
# print(client)
# print(client.guilds.channels)


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
    if admin_id not in [i.id for i in message.author.roles]:
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
        _, team_id, delta = cntnt.split()
        msg = update_score(int(team_id), int(delta))
        # add_to_history(stuff)
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
    main()
