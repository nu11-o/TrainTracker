from bs4 import BeautifulSoup as BS
import re
import requests
import urllib3
import json
from discord.ext import commands
from discord import app_commands
import discord
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)
tree = bot.tree

foundBoolean = 3
headcodeListClass455 = ['455705', '455712', '455716', '455717', '455721', '455727', '455732', '455860', '455908']

# function to search for an active train
def searchFunction(classNumber):
    global foundBoolean, headcodeListClass455
    headcodeList = []
    if classNumber == 455:
        headcodeList = headcodeListClass455
    foundString = f'Allocations for class {classNumber}s found.'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" "AppleWebKit/537.36 (KHTML, like Gecko)" "Chrome/120.0 Safari/537.36"}
    if len(headcodeList) > 0:
        for headcode in headcodeList:
            try:
                link = 'https://www.realtimetrains.co.uk/search/handler?qsearch=' + headcode
                response = requests.get(link, headers=headers, timeout=10, verify=False)
                soup = BS(response.text, "html.parser")
                notFoundString = soup.find_all(string=re.compile('We cannot find any allocations for that rolling stock'))
                if notFoundString:
                    foundBoolean = 0
                else:
                    foundString2 = foundString.replace(f'.', f', \nHeadcode: {headcode}, link: {link}.')
                    foundString = foundString2
                    print(f'Found! Headcode: {headcode}, link: {link}')
                    foundBoolean = 1
            except requests.exceptions.RequestException as e:
                print(headcode, "-> ERROR:", e)
    else:
        foundBoolean = 2
    if foundBoolean == 0:
        message = f'There are no current allocations for class {classNumber}s.'
    elif foundBoolean == 1:
        message = foundString
    elif foundBoolean == 2:
        message = f'My database currently does not have any headcodes for class {classNumber}s.\n\nIf you would for it to be added, please DM me on discord (@bluebananaaa) with a list of all the headcodes and a source.'
    return message

# discord stuff
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")

@tree.command(name="searchclass", description="Search for a specific train class")
@app_commands.describe(classnumber="The class number to search for")
async def SearchClass(interaction: discord.Interaction, classnumber:int):
    message = searchFunction(classnumber)
    await interaction.response.send_message(message)

bot.run(os.getenv("TOKEN"))