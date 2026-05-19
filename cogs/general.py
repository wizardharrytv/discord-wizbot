import time
import discord
from discord.ext import commands

START_TIME = time.time()


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="ping", description="Check bot latency")
    async def ping(self, ctx: discord.ApplicationContext):
        latency = round(self.bot.latency * 1000)
        await ctx.respond(f"Pong! `{latency}ms`")

    @discord.slash_command(name="uptime", description="Show how long the bot has been running")
    async def uptime(self, ctx: discord.ApplicationContext):
        elapsed = int(time.time() - START_TIME)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.respond(f"Uptime: `{hours}h {minutes}m {seconds}s`")

    @discord.slash_command(name="help", description="List available commands")
    async def help(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title="wizbot commands", color=discord.Color.blurple())
        embed.add_field(name="General", value="`/ping` `/uptime` `/help`", inline=False)
        embed.add_field(name="Fun", value="`/8ball` `/dice` `/meme`", inline=False)
        await ctx.respond(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(General(bot))
