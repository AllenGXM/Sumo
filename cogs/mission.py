import discord
from discord.ext import commands
from discord import app_commands, Interaction
from discord.ui import Modal, TextInput
from database import database  # your async SQLite DB instance


class MissionModal(Modal):
    def __init__(self, *, default_color):
        super().__init__(title="Create a Mission")

        self.title_input = TextInput(
            label="Mission Title",
            style=discord.TextStyle.short,
            placeholder="Enter the mission title",
            max_length=100
        )
        self.description_input = TextInput(
            label="Mission Description",
            style=discord.TextStyle.paragraph,
            placeholder="Describe the mission details",
            max_length=1000
        )
        self.color_input = TextInput(
            label="Embed Color (Hex, optional)",
            style=discord.TextStyle.short,
            placeholder=f"Default is {hex(default_color)}",
            required=False,
            max_length=7
        )

        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.add_item(self.color_input)

        self.default_color = default_color
        self.response = None

    async def on_submit(self, interaction: Interaction):
        self.response = {
            "title": self.title_input.value,
            "description": self.description_input.value,
            "color": self.color_input.value or hex(self.default_color)
        }
        await interaction.response.send_message("Mission details received! Creating mission...", ephemeral=True)
        self.stop()


class Missions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mission", description="Create a mission with XP and target channel")
    @app_commands.describe(xp="XP reward for completing this mission", channel="Channel to post the mission")
    async def mission(self, interaction: Interaction, xp: int, channel: discord.TextChannel):
        # Permission check
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        default_color = 0xFFD700

        modal = MissionModal(default_color=default_color)
        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.response:
            return

        mission_info = modal.response

        # Parse color safely
        try:
            color_str = mission_info["color"]
            if color_str.startswith("#"):
                mission_color = int(color_str[1:], 16)
            elif color_str.startswith("0x"):
                mission_color = int(color_str, 16)
            else:
                mission_color = int(color_str, 16)
        except Exception:
            mission_color = default_color

        # Create embed for mission announcement
        embed = discord.Embed(
            title=mission_info["title"],
            description=mission_info["description"],
            color=mission_color
        )
        embed.set_footer(text=f"Earn {xp} XP by completing this mission!")

        mission_message = await channel.send(embed=embed)

        # Create thread for mission submissions
        thread = await mission_message.create_thread(
            name=f"Mission Thread: {mission_info['title'][:50]}",
            auto_archive_duration=1440  # Archive after 24 hours
        )

        # Store mission thread and XP in DB
        await database.add_mission_thread(thread.id, xp)

        await channel.send(f"Thread created for mission '{mission_info['title']}' with {xp} XP reward!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            # Debug print
            print(f"[DEBUG] Reaction {payload.emoji} added by user {payload.user_id} in channel {payload.channel_id}")

            # We only care about ✅ reactions
            if str(payload.emoji) != "✅":
                return

            channel = self.bot.get_channel(payload.channel_id)
            if not channel or not isinstance(channel, discord.Thread):
                return

            # Get XP configured for this mission thread
            xp = await database.get_mission_xp(channel.id)
            if xp is None:
                return

            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return

            member = guild.get_member(payload.user_id)
            if not member:
                return

            # Only allow XP awarding if reactor has manage_messages permission (mods/admins)
            if not any(role.permissions.manage_messages for role in member.roles):
                return

            try:
                message = await channel.fetch_message(payload.message_id)
            except discord.NotFound:
                print(f"[WARN] Message {payload.message_id} not found in channel {channel.id}")
                return

            # Prevent duplicate XP grants for same message
            if await database.is_message_awarded(message.id):
                return

            # Retrieve the XP cog and award XP async
            xp_cog = self.bot.get_cog("XPCog")
            if not xp_cog:
                await channel.send("⚠️ XP Cog not loaded. Please load it.")
                return

            leveled_up = await xp_cog.add_xp(guild.id, message.author.id, xp)
            
            # Mark message as awarded in DB
            await database.add_awarded_message(message.id)

            # Confirmation message
            confirmation = f"{message.author.mention} has been awarded {xp} XP for completing the mission!"
            if leveled_up:
                confirmation += " 🎉 They leveled up!"

            await channel.send(confirmation)

        except Exception as e:
            print(f"[ERROR] Exception in reaction handler: {e}")


async def setup(bot):
    await bot.add_cog(Missions(bot))
