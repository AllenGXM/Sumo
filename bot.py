import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN: print("❌ No token!"); exit(1)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    print("🔧 Loading cogs...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            ext_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(ext_name)
                print(f"✅ Loaded: {ext_name}")
            except Exception as e:
                print(f"❌ Failed {ext_name}: {e}")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("✅ PingCog ready")
    
    # GLOBAL SYNC - appears in ALL servers
    try:
        synced = await bot.tree.sync()  # No guild parameter = GLOBAL
        print(f"🌍 GLOBAL SYNC: {len(synced)} commands!")
        print(f"📋 Commands: {[cmd.name for cmd in bot.tree.get_commands()]}")
    except Exception as e:
        print(f"❌ Global sync failed: {e}")


async def main():
    await load_cogs()  # ← THIS WAS MISSING!
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
