import discord
from discord.ext import commands
from discord.ui import Button, View, UserSelect
from discord import app_commands
import asyncio
import os
os.system("pip install --upgrade ezcord")
os.system("pip install --upgrade chat_exporter")
import ezcord
import chat_exporter
import io

class CloseModal(discord.ui.Modal):
    def __init__(self, bot):
        super().__init__(title="Close")
        self.bot = bot

    reason = discord.ui.TextInput(label="Reason", required=True, style=discord.TextStyle.paragraph, placeholder='Reason for closing the ticket, e.g. "Resolved"', max_length=1024)

    async def on_submit(self, interaction: discord.Interaction):
        creator = await interaction.client.fetch_user(interaction.channel.topic)
        ### Logs

        transcript = await chat_exporter.export(
            interaction.channel,
            limit=1000,
            bot=self.bot,
            tz_info="Europe/Berlin",
        )

        file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{interaction.channel.topic}.html"
        )
        logchannelid = 1193675262823518330
        logchannel = self.bot.get_channel(logchannelid)

        msg = await logchannel.send(f"Transcript von User <@{interaction.channel.topic}>", file=file)
        link = await chat_exporter.link(msg)
        
        

        ### Close ticket
        await interaction.response.send_message(f"Das ticket wird **jeden moment** geschloßen!")
        await asyncio.sleep(5)
        await interaction.channel.delete()

        ### Confirmation message

        embed = discord.Embed(
            title="⛄ Paradise ✘ Studio | Ticket",
            description=f"Your ticket has been closed.",
            colour=0xCCC48B,
        )
        embed.add_field(name="📜 - Transcript", value=f"[Transcript Link]({link})")
        embed.add_field(name="📚 - Reason:", value=f"{self.reason}")
        embed.add_field(name="🚀 - Staff", value=f"{interaction.user}", inline=False)
        embed.add_field(name="❗ - Info",
                        value="If you find this is a Mistake please Open another Ticket! \n(<#1107010351146467487>)",
                        inline=False)
        embed.set_footer(text="⛄ Paradise ✘ Studio", icon_url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")

        await creator.send(embed=embed)


class TDHOpen(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label="Click to open!", style=discord.ButtonStyle.primary, emoji="<:Ticket:1151540222669107271>", custom_id="ticket_open")
    async def button_callback1(self, interaction: discord.Interaction, button: discord.Button):

        ### Authorizations for the new ticket channel

        staff_role = interaction.guild.get_role(1107010350441832507)
        username = interaction.user.name
        category = interaction.guild.get_channel(1109800047517909103)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        ### Ticket message in the new ticket channel

        embed = discord.Embed(
            title="⛄ Paradise ✘ Studio | New Ticket",
            description=f"{interaction.user.mention} has created a new ticket.\n\nI have informed the staff team!",
            color=0xCCC48B,
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")

        embed.set_footer(text="Please wait until a team member responds.", icon_url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")

        ### Create ticket channel

        ticket_channel = await interaction.guild.create_text_channel(f"ticket-{username}", topic=interaction.user.id, category=category, overwrites=overwrites)
        embed2 = discord.Embed(
            title="⛄ Paradise ✘ Studio | Ticket",
            description=f"Your ticket has been created: {ticket_channel.mention}",
            color=0xCCC48B,
        )
        embed2.set_footer(text="⛄ Paradise ✘ Studio", icon_url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")
        embed2.set_thumbnail(url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")

        await interaction.response.send_message(embed=embed2, ephemeral=True)
        t_message = await ticket_channel.send("@everyone")
        await t_message.delete()
        await asyncio.sleep(0.5)
        await ticket_channel.send(embed=embed, view=TDHClose(self.bot))


class TDHClose(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label="Close ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_close")
    async def button_callback1(self, interaction: discord.Interaction, button: discord.Button):

        staff_role = interaction.guild.get_role(1107010350441832507)
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("Du hast keine Berechtigung, um dieses Ticket zu schließen.", ephemeral=True)
            return
        await interaction.response.send_modal(CloseModal(self.bot))

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.primary, emoji="🤚", custom_id="ticket_claim")
    async def button_callback2(self, interaction: discord.Interaction, button: discord.Button):

        ### Authorizations for the new ticket channel

        staff_role = interaction.guild.get_role(1107010350441832507)
        username = interaction.user.name
        category = interaction.guild.get_channel(1191541742114177144)
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("You do not have permission to claim this ticket.", ephemeral=True)
            return
        embed = discord.Embed(
            title="⛄ Paradise ✘ Studio | Claimed Ticket",
            description=f"Your Ticket Now will be handled by our Staff {interaction.user.mention}",
            colour=0xCCC48B,
        )
        embed.set_footer(text="⛄ Paradise ✘ Studio", icon_url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")

        embed2 = discord.Embed(
            title="⛄ Paradise ✘ Studio | New Ticket",
            description=f"<@{interaction.channel.topic}> has created a new ticket.\n\nI have informed the staff team!",
            color=0xCCC48B,
        )
        embed2.set_thumbnail(url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")

        embed2.set_footer(text="Please wait until a team member responds.", icon_url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")

        await interaction.response.send_message(embed=embed)
        button.disabled = True
        await interaction.message.edit(embed=embed2, view=self)

    @discord.ui.button(label="Add User", style=discord.ButtonStyle.primary, emoji="👤", custom_id="add_user")
    async def button_callback3(self, interaction: discord.Interaction, button: discord.Button):

        staff_role = interaction.guild.get_role(1107010350441832507)
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("You do not have permission to add Users to this ticket.", ephemeral=True)
            return
        embed = discord.Embed(
            title = "⛄ Paradise ✘ Studio | Add User",
            description = "Select the user you would like to add to the ticket below",
            color=0xCCC48B,
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")

        embed.set_footer(text="⛄ Paradise ✘ Studio", icon_url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")
        view = View()
        select = discord.ui.UserSelect(placeholder="Users", min_values=1, max_values=1, custom_id="users")

        async def callback(interaction: discord.Interaction):
            creator = await interaction.client.fetch_user(interaction.channel.topic)
            selected_user = select.values[0]
            await interaction.channel.send_message(f"I added {select.values[0].mention} to ticket **Successful**.", ephemeral=True)
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                select.values[0]: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                creator: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
                
            channel = interaction.channel
            await channel.edit(overwrites=overwrites)
            embed2 = discord.Embed(
                title = f"⛄ Paradise ✘ Studio | User Added",
                description = f"I have successfully added User {select.values[0].mention} to the ticket.",
                colour=0xCCC48B,
            )
            embed2.set_thumbnail(url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")

            embed2.set_footer(text="⛄ Paradise ✘ Studio", icon_url="https://cdn.discordapp.com/icons/1107010349993033780/5e31b2269bf8506a513bb5366ae4a420.png?size=1024")
            await channel.send(embed=embed2)


        select.callback = callback
        view.add_item(select)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)




class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# Ticket System

    @app_commands.command(name="ticket", description="Create a new ticket.")
    @commands.guild_only()
    async def ticket(self, ctx: discord.Interaction):
        if ctx.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="Open a ticket!",
                description="<:Info:1151540150128611471> Click the button to open a ticket.\n\n\n<:ChristmasBell:1175395784515129424> __Want to report someone?__\n\nJust send their Username + Tag, a Photo/Video\n showing proof, and why you want to report them!\n The same thing applies to staff reports.\n\n\n<:booster:1131565918460321824> __Want to claim a giveaway?__\n\nJust ping the giveaway host and we will give the \nprize! In case of a sponsor, we will add them to the \nticket. If you want to sponsor a giveaway, just tell \nour staff in the ticket.\n\n\nPlease be aware that it may come to delays from \n8PM to 5AM.",
                color=0xCCC48B,
            )
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1039974403733200979/1113862407673106512/briefkasten__1_-removebg-preview.png?ex=65a94db4&is=6596d8b4&hm=cbf06b2f9aa8acb27f6d6bccde91199c5d70825752e7c42c5e52764261200a11&=&format=webp&quality=lossless")
            embed.set_image(url="https://media.discordapp.net/attachments/1039974403733200979/1113854023716585482/INFORMATION.png?ex=65a945e5&is=6596d0e5&hm=875e4ef33eaa28bcc830c8a05bc4a3d16f30d2e06df828291783580d12029f63&=&format=webp&quality=lossless")
            embed.set_footer(text="Ticket Devlivery is fast!")

            view = TDHOpen(self.bot)
            await ctx.response.send_message("ERFOLGREICH!", ephemeral=True)
            await ctx.channel.send(embed=embed, view=view)
        else:
            await ctx.response.send_message("You have no permissions to use the Command.", ephemeral=True)
            return

async def setup(bot):
    await bot.add_cog(Ticket(bot))
    await on_ready(bot)

async def on_ready(bot):
    bot.add_view(TDHOpen(bot))
    bot.add_view(TDHClose(bot))
