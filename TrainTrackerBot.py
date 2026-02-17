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

with open("trainUnitNumbers.json", "r") as f:
    unitNumberDictionary = json.load(f)

foundBoolean = 3

# function to search for an active train
def searchFunction(classNumber):
    global foundBoolean
    foundBoolean = 0
    unitNumberList = []
    try:
        unitNumberList = unitNumberDictionary[f'Class {classNumber}']
    except KeyError:
        foundBoolean = 2
    foundString = f'Allocations for Class no. {classNumber} have been found '
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" "AppleWebKit/537.36 (KHTML, like Gecko)" "Chrome/120.0 Safari/537.36"}
    if len(unitNumberList) > 0:
        for unitNumber in unitNumberList:
            try:
                link = 'https://www.realtimetrains.co.uk/search/handler?qsearch=' + unitNumber
                response = requests.get(link, headers=headers, timeout=10, verify=False)
                soup = BS(response.text, "html.parser")
                notFoundString = soup.find_all(string=re.compile('We cannot find any allocations for that rolling stock'))
                if notFoundString:
                    continue
                else:
                    foundString2 = foundString.replace(f' ', f', \nUnit Number: {unitNumber}, link: {link} ')
                    foundString = foundString2
                    print(f'Found! Unit Number: {unitNumber}, link: {link}')
                    foundBoolean = 1
            except requests.exceptions.RequestException as e:
                print(unitNumber, "-> ERROR:", e)
    else:
        foundBoolean = 2
    if foundBoolean == 0:
        message = f'There are no current allocations for Class no. {classNumber}'
    elif foundBoolean == 1:
        message = foundString
    elif foundBoolean == 2:
        message = f'My database currently does not have any unit numbers for Class no. {classNumber}\n\nIf you would like for it to be added, please DM me on discord (@bluebananaaa) with a list of all the unit numbers and a source'
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