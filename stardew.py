import discord

CONDITION_META = {
    "sunny": {
        "emoji": "☀️",
        "label": "Sunny",
        "color": discord.Color.gold(),
        "flavor": "It'll be a fine day tomorrow. Perfect weather for tending the fields, friend!",
        "thumbnail": "https://stardewvalleywiki.com/mediawiki/images/4/44/Sunny.png",
    },
    "cloudy": {
        "emoji": "☁️",
        "label": "Cloudy",
        "color": discord.Color.light_grey(),
        "flavor": "Overcast skies roll in. A good day to visit the mines or browse Willy's wares.",
        "thumbnail": "https://stardewvalleywiki.com/mediawiki/images/7/7d/Cloudy.png",
    },
    "rainy": {
        "emoji": "🌧️",
        "label": "Rainy",
        "color": discord.Color.blue(),
        "flavor": "The crops will drink well tomorrow, friend. Best leave the watering can at home.",
        "thumbnail": "https://stardewvalleywiki.com/mediawiki/images/1/16/Rainy.png",
    },
    "snowy": {
        "emoji": "❄️",
        "label": "Snowy",
        "color": discord.Color.from_rgb(173, 216, 230),
        "flavor": "Snow drifts across the valley. Bundle up before you head out!",
        "thumbnail": "https://stardewvalleywiki.com/mediawiki/images/3/3e/Snowy.png",
    },
    "stormy": {
        "emoji": "⛈️",
        "label": "Stormy",
        "color": discord.Color.from_rgb(80, 0, 120),
        "flavor": "Lightning crackles on the horizon! Best stay indoors... or pay the Wizard a visit.",
        "thumbnail": "https://stardewvalleywiki.com/mediawiki/images/9/97/Stormy.png",
    },
}

UNKNOWN_META = {
    "emoji": "🌫️",
    "label": "Unknown",
    "color": discord.Color.greyple(),
    "flavor": "Hm... even the old farmer can't read these skies.",
    "thumbnail": None,
}


def build_embed(forecast: dict) -> discord.Embed:
    meta = CONDITION_META.get(forecast["condition"], UNKNOWN_META)

    embed = discord.Embed(
        title="📺  Pelican Town Weather Broadcast",
        description=(
            f"**Tomorrow's forecast for {forecast['location']}**\n"
            f"*\"{meta['flavor']}\"*"
        ),
        color=meta["color"],
    )

    embed.add_field(
        name=f"{meta['emoji']}  Condition",
        value=meta["label"],
        inline=True,
    )
    embed.add_field(
        name="🌡️  High",
        value=f"{forecast['high_c']}°C / {forecast['high_f']}°F",
        inline=True,
    )
    embed.add_field(
        name="🌡️  Low",
        value=f"{forecast['low_c']}°C / {forecast['low_f']}°F",
        inline=True,
    )

    embed.set_footer(text="— Your local weather gopher  •  Powered by Open-Meteo")

    if meta.get("thumbnail"):
        embed.set_thumbnail(url=meta["thumbnail"])

    return embed


def build_error_embed(message: str) -> discord.Embed:
    embed = discord.Embed(
        title="📺  Pelican Town Weather Broadcast",
        description=(
            "⚠️  *The signal from Junimo HQ is fuzzy today...*\n\n"
            f"```{message}```"
        ),
        color=discord.Color.red(),
    )
    embed.set_footer(text="Try a different location name, friend.")
    return embed
