import json
import os
import discord
from discord.ext import commands

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
APPROVAL_CHANNEL_ID = int(os.environ["DISCORD_APPROVAL_CHANNEL_ID"])
PUBLISH_CHANNEL_ID = int(os.environ["DISCORD_PUBLISH_CHANNEL_ID"])

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

pending_path = "pending.json"
approved = []

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    channel = bot.get_channel(APPROVAL_CHANNEL_ID)

    with open(pending_path) as f:
        items = json.load(f)

    for item in items:
        embed = discord.Embed(
            title=item["title"],
            url=item["url"],
            description=item["summary"][:200] + "...",
            color=discord.Color.blue()
        )
        msg = await channel.send(embed=embed)
        await msg.add_reaction("✅")

    print("All news sent for approval.")
    await bot.close()

@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name != "✅":
        return

    if payload.channel_id != APPROVAL_CHANNEL_ID:
        return

    channel = bot.get_channel(APPROVAL_CHANNEL_ID)
    msg = await channel.fetch_message(payload.message_id)

    if not msg.embeds:
        return

    embed = msg.embeds[0]
    publish_channel = bot.get_channel(PUBLISH_CHANNEL_ID)
    await publish_channel.send(embed=embed)

    print("Approved message sent to publish channel.")
