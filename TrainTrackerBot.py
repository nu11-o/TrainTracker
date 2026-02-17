from bs4 import BeautifulSoup as BS
import re
import json
from discord.ext import commands
from discord import app_commands
import discord
from dotenv import load_dotenv
import os
import aiohttp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)
tree = bot.tree

with open("trainUnitNumbers.json", "r") as f:
    unit_number_dictionary = json.load(f)

# function to search RTT for any active trains
async def searchRTT(class_number):

    results = []

    unit_number_list = get_units(class_number)

    headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/120.0 Safari/537.36"
    }

    semaphore = asyncio.Semaphore(5)

    async def limited_fetch(session, link, unit, class_number):
        async with semaphore:
            return await fetch_unit(session, link, unit, class_number)

    async with aiohttp.ClientSession(headers=headers) as session:

        tasks = [
            limited_fetch(session, f"https://www.realtimetrains.co.uk/search/handler?qsearch={unit}", unit,
                          class_number)
            for unit in unit_number_list
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response in responses:
            if isinstance(response, dict):
                results.append(response)

    return results

async def fetch_unit(session, link, unit, class_number):

    try:
        async with session.get(link, timeout=10) as response:
            text = await response.text()
            soup = BS(text, "html.parser")

            not_found = soup.find_all(
                string=re.compile('We cannot find any allocations for that rolling stock')
            )

            if not not_found:
                return {
                    'class': class_number,
                    'unit_number': unit,
                    'link': link,
                    'source': 'RTT'
                }

    except Exeption:
        return None

def get_units(class_number):
    """Return all unit numbers for a class based on ranges in JSON."""
    ranges = unit_number_dictionary.get(str(class_number), [])
    units = []
    for r in ranges:
        for i in range(r["start"], r["end"] + 1):
            units.append(f"{class_number}{i:03d}")  # zero-padded
    return units

# discord stuff
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")
    print('TESTING MODE')

@tree.command(name="searchclass", description="Search for a specific train class") # creates the / command
@app_commands.describe(classnumber="The class number to search for") # description for the / command

async def SearchClass(interaction: discord.Interaction, classnumber: int):

    results = await searchRTT(classnumber)

    if not results:
        await interaction.response.send_message(
            f"No allocations found for Class {classnumber}"
        )
    else:
        message = ""
        for r in results:
            message += (
                f"Class: {r['class']}\n"
                f"Unit Number: {r['unit_number']}\n"
                f"Link: {r['link']}\n"
                f"Source: {r['source']}\n\n"
            )

        await interaction.response.send_message(message, ephemeral=False, suppress_embeds=True)

bot.run(os.getenv("TOKEN"))