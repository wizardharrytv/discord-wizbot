import random
import aiohttp
import discord
from discord.ext import commands

EIGHT_BALL_RESPONSES = [
    "It is certain.", "It is decidedly so.", "Without a doubt.",
    "Yes, definitely.", "You may rely on it.", "As I see it, yes.",
    "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
    "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
    "Cannot predict now.", "Concentrate and ask again.",
    "Don't count on it.", "My reply is no.", "My sources say no.",
    "Outlook not so good.", "Very doubtful.",
]


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="8ball", description="Ask the magic 8-ball a question")
    async def eightball(
        self,
        ctx: discord.ApplicationContext,
        question: discord.Option(str, "Your question", required=True),
    ):
        response = random.choice(EIGHT_BALL_RESPONSES)
        embed = discord.Embed(color=discord.Color.dark_purple())
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=f"🎱 {response}", inline=False)
        await ctx.respond(embed=embed)

    @discord.slash_command(name="dice", description="Roll dice — e.g. 2d6")
    async def dice(
        self,
        ctx: discord.ApplicationContext,
        notation: discord.Option(str, "Dice notation like 1d6, 2d20 (default: 1d6)", required=False, default="1d6"),
    ):
        try:
            count_str, sides_str = notation.lower().split("d")
            count = int(count_str) if count_str else 1
            sides = int(sides_str)
            if not (1 <= count <= 20 and 2 <= sides <= 100):
                raise ValueError
        except ValueError:
            await ctx.respond("Bad notation. Use `NdS` format, e.g. `2d6`. Max 20 dice, max 100 sides.", ephemeral=True)
            return

        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        rolls_str = ", ".join(str(r) for r in rolls)
        result = f"**Total: {total}**" if count > 1 else f"**{total}**"
        await ctx.respond(f"🎲 Rolling `{notation}`: [{rolls_str}] → {result}")

    @discord.slash_command(name="meme", description="Get a random meme")
    async def meme(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        url = "https://meme-api.com/gimme"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    if resp.status != 200:
                        raise ValueError(f"HTTP {resp.status}")
                    data = await resp.json()

            if data.get("nsfw"):
                await ctx.respond("Got an NSFW meme — skipped. Try again.", ephemeral=True)
                return

            embed = discord.Embed(title=data["title"], color=discord.Color.orange())
            embed.set_image(url=data["url"])
            embed.set_footer(text=f"r/{data['subreddit']} • 👍 {data['ups']}")
            await ctx.respond(embed=embed)

        except Exception as e:
            await ctx.respond(f"Couldn't fetch meme: `{e}`", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
