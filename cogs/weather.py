import discord
from discord.ext import commands

from weather import fetch_tomorrow, WeatherError
from stardew import build_embed, build_error_embed


class Weather(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="weather", description="Get tomorrow's Stardew Valley-style forecast for any location")
    async def weather_slash(
        self,
        ctx: discord.ApplicationContext,
        location: discord.Option(str, "City, region, or country name", required=True),
    ):
        await ctx.defer()
        try:
            forecast = await fetch_tomorrow(location)
            embed = build_embed(forecast)
        except WeatherError as e:
            embed = build_error_embed(str(e))
        except Exception:
            embed = build_error_embed("Unexpected error reaching the forecast tower. Try again shortly.")
        await ctx.respond(embed=embed)

    @commands.command(name="weather", help="Get tomorrow's Stardew Valley-style forecast — !weather <location>")
    async def weather_prefix(self, ctx: commands.Context, *, location: str = None):
        if not location:
            await ctx.reply("Usage: `!weather <location>` — e.g. `!weather London`")
            return

        async with ctx.typing():
            try:
                forecast = await fetch_tomorrow(location)
                embed = build_embed(forecast)
            except WeatherError as e:
                embed = build_error_embed(str(e))
            except Exception:
                embed = build_error_embed("Unexpected error reaching the forecast tower. Try again shortly.")

        await ctx.reply(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Weather(bot))
