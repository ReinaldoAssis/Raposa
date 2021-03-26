#import discord
#from discord import File
#import requests
from discord.ext import commands
import os
#from bs4 import BeautifulSoup
#import asyncio
#import random
from keep_alive import keep_alive
#from replit import db
#from googleapiclient.discovery import build

client = commands.Bot(command_prefix="+")

from brincadeiras import Brincadeiras
from utilidades import Utilidades

client.add_cog(Brincadeiras(client))
client.add_cog(Utilidades(client))
# client.loop.create_task(Utilidades.entrou())
keep_alive()
client.run(os.getenv("DISCORD_TOKEN"))