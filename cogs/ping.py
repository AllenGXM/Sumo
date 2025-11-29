import discord
from discord.ext import commands

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("🔧 PingCog created")

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ PingCog ready")

    @discord.app_commands.command(name="ping", description="Check if bot is alive")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong! 🏓")

async def setup(bot):
    print("🔧 PingCog setup...")
    await bot.add_cog(PingCog(bot))
    print("✅ Ping_Cog setup complete")
