import os
import discord
import health
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents)

COGS = ["cogs.general", "cogs.fun"]


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await health.run(bot)
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="slash commands | /help"
    ))


async def main():
    for cog in COGS:
        bot.load_extension(cog)
        print(f"Loaded {cog}")

    await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down.")
