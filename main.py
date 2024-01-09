import os
os.system("pip install --upgrade discord.py")
import discord
import config
import asyncio
import random
from discord.ext import commands
import datetime


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="?", intents=discord.Intents.all())


bot = Client()
bot.remove_command('help')


@bot.event
async def on_ready():
    info = "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰"
    print("\033[0;31m" + f"{info}")

    # Liste der Ordner, die Sie laden möchten
    folders = ['events', 'commands']

    for folder in folders:
        for filename in os.listdir(f'./{folder}'):
            if filename.endswith('.py'):
                await bot.load_extension(f'{folder}.{filename[:-3]}')
                print("\033[0;35m" + f"[Cog Loaded] " + "\033[1;37m" + f"  {folder}.{filename[:-3]}")

    await bot.tree.sync()
    print("\033[0;31m" + f"{info}")
    print("\033[0;32m" + "Online!")
    await update_status()


async def update_status():
    while True:
        try:
            member_count = len(bot.guilds[
                                   0].members)  # Hier wird die Anzahl der Mitglieder im ersten Server des Bots genommen. Passe dies an, wenn dein Bot auf mehreren Servern ist.

            # Aktualisiere den Status
            await bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.listening, name=f"Unity"))
            await asyncio.sleep(3)
            await bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name="Über den Server"))
            await asyncio.sleep(3)
        except (discord.ConnectionClosed, asyncio.CancelledError):
            print("Connection was closed. Retrying in 5 seconds...")
            await asyncio.sleep(5)


@bot.event
async def on_command_error(ctx, error):
    print(f"{error}")


bot.run(config.TOKEN)