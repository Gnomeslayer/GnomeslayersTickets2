from discord import Interaction, TextStyle
from discord.ui import Modal, TextInput

from plugins.tickets.supportfiles.functions import ticket_functions
from plugins.tickets.supportfiles.embeds import tickets_embeds
import discord

from plugins.tickets.supportfiles.database import tickets_database
from plugins.tickets.supportfiles.buttons import PersistentViewButtons

class general_modal(Modal, title='General Ticket'):
    def __init__(self, config:dict, tokens):
        super().__init__()
        self.config:dict = config
        self.user_profile = user_profile(config=config, tokens=tokens)
        self.embed_factory = tickets_embeds(config=config)
        self.database = tickets_database()

    steam = TextInput(
        label='Steam ID or Steam Profile Link',
        style=TextStyle.short,
        required=True,
    )
    
    issue = TextInput(
        label='Describe your issue',
        style=TextStyle.long,
        required=True,
    )
    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=False)
        steam = self.steam.value
        issue = self.issue.value

        #Make sure they exist
        response = await self.user_profile.get_user_ids(steam=steam)
        if not response or not response.steamid or not response.bmid:
            try:
                await interaction.user.send("Please enter a valid steam ID or steam URL!")
            except:
                message = await interaction.channel.send(content=f"{interaction.user.mention} - Please enter a valid steam ID or steam URL!")
                await message.delete(delay=5)
            return
        
        #Give feedback ASAP
        await interaction.followup.send("Generating ticket now.", ephemeral=True)

        #Grab the category channel
        if self.config['ticket_settings']['separate_by_category']:
            category:discord.CategoryChannel = interaction.guild.get_channel(self.config['ticket_settings']['general_category'])
        else:
            category:discord.CategoryChannel = interaction.guild.get_channel(self.config['ticket_settings']['default_category'])

        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False, send_messages=False, read_message_history=False)}
        overwrites[interaction.user] = discord.PermissionOverwrite(view_channel=True, send_messages=True,read_messages=True,read_message_history=True, embed_links=True, attach_files=True)
        staff = None

        for role_id in self.config['ticket_admin_settings']['ping_roles']:
            if staff:
                staff += f",<@&{role_id}>"
            else:
                staff = f"<@&{role_id}>"
            
            if role_id not in self.config['ticket_admin_settings']['ticket_staff_roles']:
                self.config['ticket_admin_settings']['ticket_staff_roles'].append(role_id)

        for role_id in self.config['ticket_admin_settings']['ticket_staff_roles']:
            try:
                role = interaction.guild.get_role(role_id)
            except Exception as e:
                print(f"[Issue] Role: {role_id} doesn't exist..")
                continue
            
            if not role:
                print(f"Role: {role_id} doesn't exist..")
                continue
            overwrites[role] = discord.PermissionOverwrite(use_application_commands=True,
            view_channel=True, send_messages=True,
            read_messages=True, read_message_history=True,
            embed_links=True, attach_files=True)

        tickets = await self.database.get_all_tickets()

        channel = await category.create_text_channel(f"General Ticket {len(tickets)}", overwrites=overwrites)
        staff_channel = interaction.guild.get_channel(self.config['ticket_admin_settings']['admin_channel_id'])
        general_embed = await self.embed_factory.general_embed(steamid=steam, issue=issue)
        general_embed.title = f"{channel.name}"

        buttons = PersistentViewButtons(self.config)
        await self.database.add_ticket(ticket_number=len(tickets)+1, ticket_type="General", creater_discord_id=interaction.user.id, active_ticket=True, channel_id=channel.id)

        await channel.send(view=buttons, embed=general_embed, content=staff)
        await channel.send(f"Thank you {interaction.user.mention} for making a ticket, a staff member will be with you as soon as they have time. Please include any additional details.")
        profile = await self.user_profile.player_information(player_ids=steam)
        await staff_channel.send(embed=profile,content=f"General Ticket {len(tickets)} {staff} - {channel.mention}")

        
        

class ban_appeal_modal(Modal, title='Ban Appeal'):
    def __init__(self, config, tokens):
        super().__init__()
        self.config = config
        self.user_profile = user_profile(config=config, tokens=tokens)
        self.embed_factory = tickets_embeds(config=config)
        self.database = tickets_database()

    steam = TextInput(
        label='Steam ID or Steam Profile Link',
        style=TextStyle.short,
        required=True,
    )
    
    reason = TextInput(
        label='Why should you be unbanned?',
        style=TextStyle.long,
        required=True,
    )
    async def on_submit(self, interaction: Interaction):
        #self.config = dict(self.config[0])
        await interaction.response.defer(ephemeral=False)
        steam = self.steam.value
        reason = self.reason.value

        response = await self.user_profile.get_user_ids(steam=steam)
        if not response or not response.steamid or not response.bmid:
            try:
                await interaction.user.send("Please enter a valid steam ID or steam URL!")
            except:
                message = await interaction.channel.send(content=f"{interaction.user.mention} - Please enter a valid steam ID or steam URL!")
                await message.delete(delay=5)
            return
        
        await interaction.followup.send("Generating ticket now.", ephemeral=True)

        if self.config['ticket_settings']['separate_by_category']:
            category:discord.CategoryChannel = interaction.guild.get_channel(self.config['ticket_settings']['ban_appeal_category'])
        else:
            category:discord.CategoryChannel = interaction.guild.get_channel(self.config['ticket_settings']['default_category'])

        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False, send_messages=False, read_message_history=False)}
        overwrites[interaction.user] = discord.PermissionOverwrite(view_channel=True, send_messages=True,read_messages=True,read_message_history=True, embed_links=True, attach_files=True)
        staff = None
        for role_id in self.config['ticket_admin_settings']['ticket_staff_roles']:
            if staff:
                staff += f",<@&{role_id}>"
            else:
                staff = f"<@&{role_id}>"
            role = interaction.guild.get_role(role_id)

            overwrites[role] = discord.PermissionOverwrite(use_application_commands=True,
            view_channel=True, send_messages=True,
            read_messages=True, read_message_history=True,
            embed_links=True, attach_files=True)

        tickets = await self.database.get_all_tickets()
        channel = await category.create_text_channel(f"Appeal Ticket {len(tickets)}", overwrites=overwrites)
        staff_channel = interaction.guild.get_channel(self.config['ticket_admin_settings']['admin_channel_id'])

        
        ban_appeal_embed = await self.embed_factory.ban_appeal_embed(steamid=steam,reason=reason)
        ban_appeal_embed.title = f"{channel.name}"

        buttons = PersistentViewButtons(self.config)

        await self.database.add_ticket(ticket_number=len(tickets)+1, ticket_type="Ban Appeal", creater_discord_id=interaction.user.id, active_ticket=True, channel_id=channel.id)
        
        await channel.send(view=buttons,embed=ban_appeal_embed, content=staff)
        await channel.send(f"Thank you {interaction.user.mention} for making a ticket, a staff member will be with you as soon as they have time. Please include any additional details.")
        
        profile = await self.user_profile.player_information(player_ids=steam)
        await staff_channel.send(embed=profile,content=f"Ban Appeal Ticket {len(tickets)} {staff} - {channel.mention}")
        

class report_cheater_modal(Modal, title='Report a cheater'):
    def __init__(self, config, tokens):
        super().__init__()
        self.config = config
        self.user_profile = user_profile(config=config, tokens=tokens)
        self.embed_factory = tickets_embeds(config=config)
        self.database = tickets_database()

    creater_steam = TextInput(
        label='Your Steam ID or Steam Profile Link',
        style=TextStyle.short,
        required=True,
    )

    cheater_steam = TextInput(
        label='Cheaters Steam ID or Steam Profile Link',
        style=TextStyle.short,
        required=True,
    )
    
    information = TextInput(
        label='Information we need to know',
        style=TextStyle.long,
        required=True,
    )

    proof = TextInput(
        label='Proof',
        style=TextStyle.long,
        placeholder="You can provide images in the ticket.",
        required=True,
    )
    async def on_submit(self, interaction: Interaction):
        #self.config = dict(self.config[0])
        creater_steam = self.creater_steam.value
        cheater_steam = self.cheater_steam.value
        information = self.information.value
        proof = self.proof.value

        response = await self.user_profile.get_user_ids(steam=cheater_steam)
        if not response or not response.steamid or not response.bmid:
            try:
                await interaction.user.send("Please enter a valid steam ID or steam URL!")
            except:
                message = await interaction.channel.send(content=f"{interaction.user.mention} - Please enter a valid steam ID or steam URL!")
                await message.delete(delay=5)
            return
        
        await interaction.followup.send("Generating ticket now.", ephemeral=True)

        if self.config['ticket_settings']['separate_by_category']:
            category:discord.CategoryChannel = interaction.guild.get_channel(channel_id=self.config['ticket_settings']['report_category'])
        else:
            category:discord.CategoryChannel = interaction.guild.get_channel(channel_id=self.config['ticket_settings']['default_category'])

        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False, send_messages=False, read_message_history=False)}
        overwrites[interaction.user] = discord.PermissionOverwrite(view_channel=True, send_messages=True,read_messages=True,read_message_history=True, embed_links=True, attach_files=True)
        staff = None
        for role_id in self.config['ticket_admin_settings']['ticket_staff_roles']:
            if staff:
                staff += f",<@&{role_id}>"
            else:
                staff = f"<@&{role_id}>"
            role = interaction.guild.get_role(role_id)

            overwrites[role] = discord.PermissionOverwrite(use_application_commands=True,
            view_channel=True, send_messages=True,
            read_messages=True, read_message_history=True,
            embed_links=True, attach_files=True)

        tickets = await self.database.get_all_tickets()

        channel = await category.create_text_channel(f"Report Ticket {len(tickets)}", overwrites=overwrites)
        staff_channel = interaction.guild.get_channel(self.config['ticket_admin_settings']['admin_channel_id'])

        
        report_embed = await self.embed_factory.report_embed(maker_steamid=creater_steam,cheater_steamid=cheater_steam,info=information,proof=proof)
        report_embed.title = f"{channel.name}"

        buttons = PersistentViewButtons(self.config)
        await self.database.add_ticket(ticket_number=len(tickets)+1, ticket_type="Report", creater_discord_id=interaction.user.id, active_ticket=True, channel_id=channel.id)
        await channel.send(view=buttons,embed=report_embed, content=staff)
        await channel.send(f"Thank you {interaction.user.mention} for making a ticket, a staff member will be with you as soon as they have time. Please include any additional details.")
        
        profile = await self.user_profile.player_information(player_ids=cheater_steam)
        await staff_channel.send(embed=profile,content=f"Report a cheater ticket {len(tickets)} {staff} - {channel.mention}")


class user_profile():
    def __init__(self, config, tokens):
        self.config = config
        self.functions = ticket_functions(config=self.config, tokens=tokens)
        self.embed_factory = tickets_embeds(config=config)

    async def get_user_ids(self, steam:str):
        player_ids = await self.functions.get_player_ids(steam)

        return player_ids

    def filter_reasons(self, reasons:str):
        reason = reasons.replace("}", "")
        reason = reason.replace("{", "")
        reason = reason.replace("]", "")
        reason = reason.replace("[", "")
        reason = reason.replace("|", "")
        reason = reason.replace("discord.gg", "discordlink")
        reason = reason.replace("https://", "")
        reason = reason.replace("http://", "")
        return reason


    async def player_information(self, player_ids):
        user_ids = await self.get_user_ids(steam=player_ids)

        if not user_ids.bmid:
            return
        
        player_profile = await self.functions.get_player_info(player_id=user_ids.bmid)
        player_stats = await self.functions.player_stats(bmid=user_ids.bmid)
        bancount = 0
        serverbans = None
        rustbanned_msg = "Rustbans: Not rustbanned."
        community_msg = "Community bans: No community Bans"
        vac_msg = "VAC Bans: No VAC bans"
        lastban = "Days since last non rust ban: Never"
        
        if player_profile.rustbanned:
            rustbanned_msg = f"Rustbans: {player_profile.rustbancount} | {player_profile.banned_days_ago} days ago"
        
        
        if player_profile.server_bans:
            for serverban in player_profile.server_bans:
                serverban.banreason = self.filter_reasons(serverban.banreason)
                if bancount <= 5:
                    if serverbans:
                        serverbans += f"\n➣ [{serverban.banreason}](https://www.battlemetrics.com/rcon/bans/edit/{serverban.banid})"
                        bancount += 1
                    else:
                        serverbans = f"➣ [{serverban.banreason}](https://www.battlemetrics.com/rcon/bans/edit/{serverban.banid})"
                        bancount += 1
                else:
                    break
        
        if player_profile.rustbanned:
            rustbanned_msg = f"Rustbans: {player_profile.rustbancount} | {player_profile.banned_days_ago} days ago"

        if player_profile.community_banned:
            community_msg = f"Community Bans: {player_profile.game_ban_count}"

        if player_profile.vac_banned:
            vac_msg = f"VAC Bans: {player_profile.vacban_count}"
            
        if player_profile.vac_banned or player_profile.community_banned:
            lastban = f"Days since last non rust ban: {player_profile.last_ban}"
                
        official_bans = f"{rustbanned_msg}\n{community_msg}\n{vac_msg}\n{lastban}"
        note_count = 0
        if player_profile.notes:
            note_count = len(player_profile.notes)
        embed = await self.embed_factory.player_info_embed(profile=player_profile,
                                                           stats=player_stats,
                                                           bancount=bancount,
                                                           serverbans=serverbans,
                                                           player_ids=user_ids,
                                                           official_bans=official_bans,
                                                           note_count=note_count)
        
        return embed