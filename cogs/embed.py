import discord
from discord.ext import commands

class EmbedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="embed", description="Simple embed (3 fields)")
    @discord.app_commands.describe(title="Embed title")
    async def embed(self, interaction: discord.Interaction, title: str):
        modal = SimpleEmbedModal(title)
        await interaction.response.send_modal(modal)

    @discord.app_commands.command(name="embed_pro", description="Advanced embed (5 fields)")
    @discord.app_commands.describe(title="Embed title")
    async def embed_pro(self, interaction: discord.Interaction, title: str):
        modal = ProEmbedModal(title)
        await interaction.response.send_modal(modal)

    @discord.app_commands.command(name="embed_preview", description="Builder guide")
    async def embed_preview(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Embed Guide", color=0xFAD5A5)
        embed.add_field(name="Simple", value="/embed \"Title\"", inline=True)
        embed.add_field(name="Pro", value="/embed_pro \"Title\"", inline=True)
        embed.add_field(name="Advanced", value="https://glitchii.github.io/embedbuilder/", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class SimpleEmbedModal(discord.ui.Modal, title="Simple Embed"):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.desc = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=False)
        self.add_item(self.desc)
        self.color = discord.ui.TextInput(label="Color", placeholder="#FAD5A5", default="#FAD5A5", max_length=7, required=False)
        self.add_item(self.color)
        self.image = discord.ui.TextInput(label="Image URL", placeholder="https://i.imgur.com/abc.png", required=False)
        self.add_item(self.image)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            color = int(self.color.value.replace("#", ""), 16)
        except:
            color = 0xFAD5A5
            
        embed = discord.Embed(title=self.title, color=color)
        if self.desc.value:
            embed.description = self.desc.value
        if self.image.value:
            embed.set_image(url=self.image.value)
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)

class ProEmbedModal(discord.ui.Modal, title="Pro Embed"):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.desc = discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=False)
        self.add_item(self.desc)
        self.color = discord.ui.TextInput(label="Color", placeholder="#FAD5A5", default="#FAD5A5", max_length=7, required=False)
        self.add_item(self.color)
        self.image = discord.ui.TextInput(label="Image URL", placeholder="https://i.imgur.com/abc.png", required=False)
        self.add_item(self.image)
        self.thumb = discord.ui.TextInput(label="Thumbnail URL", required=False)
        self.add_item(self.thumb)
        self.footer = discord.ui.TextInput(label="Footer", required=False)
        self.add_item(self.footer)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            color = int(self.color.value.replace("#", ""), 16)
        except:
            color = 0xFAD5A5
        embed = discord.Embed(title=self.title, color=color)
        if self.desc.value:
            embed.description = self.desc.value
        if self.image.value:
            embed.set_image(url=self.image.value)
        if self.thumb.value:
            embed.set_thumbnail(url=self.thumb.value)
        if self.footer.value:
            embed.set_footer(text=self.footer.value)
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(EmbedCog(bot))
    print("✅ EmbedCog: Pure embed builder!")
