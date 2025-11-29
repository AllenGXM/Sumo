import discord
from discord.ext import commands
import time
from datetime import datetime, timedelta

class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()  # REAL START TIME
        print("🔧 InfoCog tracking real uptime")

    def get_uptime(self):
        """Calculate REAL uptime"""
        uptime_seconds = time.time() - self.start_time
        hours, remainder = divmod(int(uptime_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def get_status_emoji(self):
        """Real status based on latency"""
        latency_ms = round(self.bot.latency * 1000)
        if latency_ms < 100:
            return "🟢 **EXCELLENT**"
        elif latency_ms < 300:
            return "🟡 **GOOD**"
        else:
            return "🟠 **SLOW**"

    @discord.app_commands.command(name="info", description="✨ Sumo Bot - Live Dashboard")
    async def info(self, interaction: discord.Interaction):
        uptime = self.get_uptime()
        latency = round(self.bot.latency * 1000)
        status = self.get_status_emoji()
        
        embed = discord.Embed(
            title="👑 **SUMO BOT**",
            description="**「 Live Performance Dashboard 」**",
            color=0xFAD5A5
        )
        
        # REAL LIVE DATA
        embed.add_field(
            name="⚡ **Status**",
            value=f"{status}\n**Latency:** `{latency}ms`",
            inline=True
        )
        embed.add_field(
            name="⏱️ **Uptime**",
            value=f"`{uptime}` **LIVE**",
            inline=True
        )
        embed.add_field(
            name="📊 **Stats**",
            value=f"**{len(self.bot.guilds)}** Servers\n**{sum(g.member_count for g in self.bot.guilds)}** Members",
            inline=True
        )
        
        # REAL Progress bar based on uptime
        uptime_percent = min((time.time() - self.start_time) / 86400 * 100, 100)  # 24h max
        bar_length = 10
        filled = int(bar_length * uptime_percent / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        embed.add_field(
            name="📈 **Session**",
            value=f"`{bar}` **{uptime_percent:.0f}%**",
            inline=False
        )
        
        embed.set_footer(text="LIVE | discord.py | /help", icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(InfoCog(bot))
    print("✅ Live Info_Cog loaded ✨")
