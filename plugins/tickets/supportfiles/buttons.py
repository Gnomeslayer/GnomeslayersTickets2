from plugins.tickets.supportfiles.database import tickets_database
from plugins.tickets.supportfiles.embeds import tickets_embeds

from discord.ui import View,Button,button
from discord import ButtonStyle, Interaction
import chat_exporter
import os
import asyncio
import discord

class CloseButtons(View):
    def __init__(self, config):
        super().__init__(timeout=None)
        self.database = tickets_database()
        self.config = config
        self.embed_factory = tickets_embeds(config=config)
        self.ticket_number = 0
        self.creator_steam = None
        self.creator = None

    @button(label='Close', style=ButtonStyle.green, custom_id='persistent_view:green')
    async def green(self, interaction: Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        user_roles = interaction.user.roles
        allowed_roles = self.config['ticket_admin_settings']['ticket_staff_roles']


        allowed_to_press = False
        for role in user_roles:
            if role.id in allowed_roles:
                allowed_to_press = True
                break
        
        if not allowed_to_press:
            return
        
        await interaction.followup.send("Deleting channel in 3 seconds.")
        
        transcript = await chat_exporter.export(interaction.channel)
        transcripts_channel = interaction.guild.get_channel(self.config['ticket_admin_settings']['transcripts_channel_id'])
        
        file_path = f"./logs/html/transcript_{interaction.channel.name}.html"
        
        try:
            with open(file_path, "w",encoding="utf-8") as f:
                f.write(transcript)
        except Exception as e:
            print(f"There was an error creating the transcript.\n {e}")
        
        if not self.creator:
            creator_discord_id = await self.database.get_active_ticket_by_channel(channel_id=interaction.channel.id)
            self.creator = interaction.guild.get_member(int(creator_discord_id['creater_discord_id']))

        embed = await self.embed_factory.ticket_transcript_embed(ticket_number=self.ticket_number, creator=self.creator, creators_steam=self.creator_steam, closed_by=interaction.user)

        await transcripts_channel.send(
                embed=embed,
                file=discord.File(file_path, filename=f"./logs/html/transcript_{interaction.channel.name}.html")
            )
        
        
        await asyncio.sleep(3) #This is in seconds right?
        await interaction.channel.delete()
        await self.database.update_ticket_status(channel_id=interaction.channel.id)
        
        os.remove(file_path)
        