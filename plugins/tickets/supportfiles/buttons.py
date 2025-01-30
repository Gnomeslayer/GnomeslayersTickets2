from plugins.tickets.supportfiles.database import tickets_database

from discord.ui import View,Button,button
from discord import ButtonStyle, Interaction
import chat_exporter
import os
import asyncio
import discord

class PersistentViewButtons(View):
    def __init__(self, config):
        super().__init__(timeout=None)
        self.database = tickets_database()
        self.config = config

    @button(label='Close', style=ButtonStyle.green, custom_id='persistent_view:green')
    async def green(self, interaction: Interaction, button: Button):
        print("This was pressed..")
        user_roles = interaction.user.roles
        allowed_roles = self.config['ticket_admin_settings']['ticket_staff_roles']


        allowed_to_press = False
        for role in user_roles:
            if role.id in allowed_roles:
                allowed_to_press = True
                break
        
        if not allowed_to_press:
            return
        
        
        
        await self.database.update_ticket_status(channel_id=interaction.channel.id)
        transcript = await chat_exporter.export(interaction.channel)
        transcripts_channel = interaction.guild.get_channel(self.config['ticket_admin_settings']['transcripts_channel_id'])
        
        file_path = f"./logs/html/transcript_{interaction.channel.name}.html"
        
        try:
            with open(file_path, "w",encoding="utf-8") as f:
                f.write(transcript)
        except Exception as e:
            print(f"There was an error creating the transcript.\n {e}")
        
        await transcripts_channel.send(
                content=f"Application transcript log for (Channel ID: {interaction.channel.id})",
                file=discord.File(file_path, filename=f"./logs/html/transcript_{interaction.channel.name}.html")
            )
        
        await interaction.response.send_message("Deleting channel in 3 seconds.")
        await asyncio.sleep(3) #This is in seconds right?
        await interaction.channel.delete()
        
        os.remove(file_path)
        