import discord
from discord.ext import commands

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="help", description="Show all commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📚 Sumo Bot Commands", color=0x0099ff)
        embed.add_field(
            name="Info",
            value="`/info` `/avatar` `/server`",
            inline=False
        )
        embed.add_field(
            name="Utility", 
            value="`/help` `/ping` `/clear`",
            inline=False
        )
        embed.add_field(
            name="Fun",
            value="Coming soon! 🎉",
            inline=False
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command(name="clear", description="Delete messages (Admin only)")
    @discord.app_commands.describe(amount="Number of messages (1-100)")
    async def clear(self, interaction: discord.Interaction, amount: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Admin only!", ephemeral=True)
            return
        if amount > 100 or amount < 1:
            await interaction.response.send_message("❌ 1-100 messages only!", ephemeral=True)
            return
        
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🗑️ Deleted {len(deleted)} messages", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
