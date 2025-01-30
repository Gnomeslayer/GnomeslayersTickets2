import json

import discord
from discord.ext.commands import Bot, Cog

from plugins.tickets.supportfiles.embeds import tickets_embeds
from plugins.tickets.supportfiles.dropdown_menu import dropdown_menu_view
from plugins.tickets.supportfiles.functions import ticket_functions



class tickets_controller(Cog):
    def __init__(self, bot: Bot, tokens:dict):
        print("[Cog] Tickets Controller has been initiated")
        self.bot = bot
        self.tokens = tokens
        self.embed_factory = None
        self.functions = None
        
    with open('./plugins/tickets/settings.json', 'r', encoding="utf-8") as f:
        config = json.load(f)

    with open('./plugins/tickets/auto_responses.json', 'r') as f:
        auto_responses = json.load(f)

    
    roles = config['ticket_admin_settings']['ticket_staff_roles']

    async def cog_load(self):
        self.config['steam_token'] = self.tokens['tokens']['steam_token']
        self.embed_factory = tickets_embeds(config=self.config)

        self.functions = ticket_functions(config=self.config, tokens=self.tokens)
        
        
        channel,send_maker = await self.clear_channel()

        embed = await self.embed_factory.ticket_maker()
        options = self.load_options_from_json()

        menu = dropdown_menu_view(options=options,config=self.config, tokens=self.tokens)
        self.bot.add_view(menu)
        if send_maker:
            await channel.send(embed=embed, view=menu)
    
    async def clear_channel(self):
        guild = self.bot.get_guild(self.config['ticket_settings']['guild_id'])
        channel = guild.get_channel(self.config['ticket_settings']['ticket_maker_channel'])
        messages = channel.history(limit=None)

        messages = []
        async for message in channel.history(limit=None):
            messages.append(message)

        if len(messages) > 1:
            await channel.purge(limit=None)
            return channel, True
        
        if len(messages) == 1:
            if messages[0].author.bot:
                return channel, False
            else:
                await channel.purge(limit=None)
                return channel, True
        
        if len(messages) == 0:
            return channel, True
    
    def load_options_from_json(self):
        with open('./plugins/tickets/select_menu_options.json', 'r', encoding="utf-16") as f:
            select_menu_options = json.load(f)
        return [discord.SelectOption(label=option["label"], emoji=option['emoji'], description=option["description"]) for option in select_menu_options]
    