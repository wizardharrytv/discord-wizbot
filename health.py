import os
import aiohttp
import discord
from discord.ext import commands

PASS = "\033[92m PASS\033[0m"
FAIL = "\033[91m FAIL\033[0m"
WARN = "\033[93m WARN\033[0m"


def _row(label: str, ok: bool | None, detail: str = "") -> str:
    status = PASS if ok is True else (WARN if ok is None else FAIL)
    detail_str = f"  ({detail})" if detail else ""
    return f"  [{status}] {label}{detail_str}"


async def run(bot: commands.Bot) -> bool:
    print("\n─── Health Check ───────────────────────────────")
    results = []
    all_passed = True

    # 1. Token env var
    token_set = bool(os.getenv("DISCORD_TOKEN"))
    results.append(_row("DISCORD_TOKEN set", token_set))
    if not token_set:
        all_passed = False

    # 2. Bot identity
    identity_ok = bot.user is not None
    results.append(_row("Bot identity", identity_ok, str(bot.user) if identity_ok else "bot.user is None"))
    if not identity_ok:
        all_passed = False

    # 3. WebSocket latency
    latency_ms = round(bot.latency * 1000)
    latency_ok = bot.latency < 1.0  # under 1s = healthy
    results.append(_row("WebSocket latency", latency_ok, f"{latency_ms}ms"))
    if not latency_ok:
        all_passed = False

    # 4. Cogs loaded
    expected_cogs = ["cogs.general", "cogs.fun"]
    for cog in expected_cogs:
        loaded = cog in bot.extensions
        results.append(_row(f"Cog: {cog}", loaded))
        if not loaded:
            all_passed = False

    # 5. Slash commands registered
    cmd_count = len(bot.pending_application_commands)
    cmds_ok = cmd_count > 0
    results.append(_row("Slash commands pending sync", cmds_ok, f"{cmd_count} commands"))
    if not cmds_ok:
        all_passed = False

    # 6. Meme API reachable (meme command dependency)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://meme-api.com/gimme",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                meme_ok = resp.status == 200
    except Exception as e:
        meme_ok = False
        results.append(_row("Meme API (/meme)", False, str(e)))
    else:
        results.append(_row("Meme API (/meme)", meme_ok, f"HTTP {resp.status}" if not meme_ok else "reachable"))

    if not meme_ok:
        all_passed = False

    for row in results:
        print(row)

    summary = "\033[92mAll checks passed.\033[0m" if all_passed else "\033[91mSome checks failed — see above.\033[0m"
    print(f"\n  {summary}")
    print("────────────────────────────────────────────────\n")

    return all_passed
