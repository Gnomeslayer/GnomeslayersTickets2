import json
from typing import List

from discord.ext.commands import Bot, Cog
from discord import app_commands, Interaction
from discord.app_commands import guild_only, Choice

from plugins.tickets.supportfiles.embeds import tickets_embeds
from plugins.tickets.supportfiles.buttons import CloseButtons 
from plugins.tickets.supportfiles.functions import ticket_functions

class tickets_commands(Cog):
    def __init__(self, bot: Bot, tokens:dict):
        print("[Cog] Tickets Commands has been initiated")
        self.bot = bot
        self.tokens = tokens
        self.embed_factory = None
        self.functions = None
        
    with open('./plugins/tickets/settings.json', 'r') as f:
        config = json.load(f)

    with open('./plugins/tickets/auto_responses.json', 'r') as f:
        auto_responses = json.load(f)

    
    
    roles = config['ticket_admin_settings']['ticket_staff_roles']

    async def cog_load(self):
        self.config['steam_token'] = self.tokens['tokens']['steam_token']
        self.embed_factory = tickets_embeds(config=self.config)
        self.bot.add_view(CloseButtons(self.config))
        self.functions = ticket_functions(config=self.config, tokens=self.tokens)
    
    #Autocompletes inputs for premade responses
    async def autocomplete(self, _: Interaction, current: str) -> List[Choice[str]]:
        
        choicelist = [response for response in self.auto_responses][:20]

        if current:
            choicelist = [response for response in self.auto_responses if current.lower() in response['name'].lower()][:20]
            return [Choice(name=c['name'], value=c['message']) for c in choicelist]
        else:
            #default = ["Start typing!"]
            return [Choice(name=c['name'], value=c['message']) for c in choicelist]


    @app_commands.command(name="auto_response", description="Auto replies to the ticket")
    @ app_commands.checks.has_any_role(*roles)
    @guild_only()
    @app_commands.autocomplete(response=autocomplete)
    async def auto_response(self, interaction:Interaction, response:str):
        await interaction.response.defer(ephemeral=False)

        embed = await self.embed_factory.auto_response(content=response)
        await interaction.followup.send(embed=embed, ephemeral=False)


    #Ensuring the user has the roles and they're told so. It's important!
    @auto_response.error
    async def auto_response_error_handler(self, ctx:Interaction, error):
        if isinstance(error, app_commands.MissingAnyRole):
            roles = []
            for role in self.config['allowed_roles']:
               guild = self.bot.guilds[0]
               the_role = guild.get_role(role)
               roles.append(the_role.mention)
            error = f"You do not have any of the required roles: {roles}"
            await ctx.response.send_message(error, ephemeral=True)
        else:
            await ctx.response.send_message(error, ephemeral=True)