import discord
from discord.ext import commands
import json
import os
import math

class XPCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_data = {}
        self.load_xp()

    def xp_file(self):
        return f"xp_{self.bot.user.id}.json"

    def load_xp(self):
        try:
            if os.path.exists(self.xp_file()):
                with open(self.xp_file(), 'r') as f:
                    self.xp_data = json.load(f)
        except:
            self.xp_data = {}

    def save_xp(self):
        try:
            with open(self.xp_file(), 'w') as f:
                json.dump(self.xp_data, f)
        except:
            pass

    def get_xp(self, guild_id, user_id):
        guild = str(guild_id)
        user = str(user_id)
        if guild not in self.xp_data:
            self.xp_data[guild] = {}
        if user not in self.xp_data[guild]:
            self.xp_data[guild][user] = {"xp": 0, "level": 1}
        return self.xp_data[guild][user]

    def add_xp(self, guild_id, user_id, amount):
        data = self.get_xp(guild_id, user_id)
        old_level = data["level"]
        data["xp"] += amount
        
        # XP Formula: 100 * level^2
        new_level = 1
        for level in range(1, 100):
            if data["xp"] < 100 * level * level:
                new_level = level
                break
        data["level"] = new_level
        self.save_xp()
        return new_level > old_level

    def xp_to_next_level(self, level):
        return 100 * level * level

    def get_progress_bar(self, current_xp, level):
        next_level_xp = self.xp_to_next_level(level)
        progress = min(current_xp / next_level_xp * 20, 20)
        bar = "█" * int(progress) + "░" * (20 - int(progress))
        percent = int((current_xp / next_level_xp) * 100)
        return f"`[{bar}] {percent}%`"

    @discord.app_commands.command(name="userinfo", description="User XP & Level")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        data = self.get_xp(interaction.guild.id, user.id)
        
        embed = discord.Embed(title=f"{user.display_name} Profile", color=0xFAD5A5)
        embed.add_field(name="⭐ Level", value=f"**{data['level']}**", inline=True)
        embed.add_field(name="⚡ XP", value=f"**{data['xp']}**", inline=True)
        embed.add_field(name="📈 Progress to L{data['level']+1}", value=self.get_progress_bar(data['xp'], data['level']), inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(XPCog(bot))
    print("✅ XP_Cog loaded - Mission system ready!")
