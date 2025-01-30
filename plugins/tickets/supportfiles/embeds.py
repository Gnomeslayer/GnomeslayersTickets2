from discord import Embed
import plugins.tickets.supportfiles.dataclasses as dataclass
import json

class tickets_embeds():
    def __init__(self, config):
        self.config = config

    with open('./plugins/tickets/embeds.json', 'r') as f:
        config_embed_settings = json.load(f)
    
    async def auto_response(self, content:str):
        embed_settings = self.config_embed_settings['auto_response']

        embed = Embed(title=embed_settings['title'],
                      description=f"```{content}```",
                      color=int(embed_settings['color'], base=16))
        #embed.add_field(name="Auto Response Message", value=f"```{content}```", inline=False)
        #embed.set_thumbnail(url=embed_settings['thumbnail_image'])
        embed.set_footer(text=embed_settings['footer_text'], icon_url=embed_settings['footer_image'])

        return embed
    
    async def ticket_maker(self):
        embed_settings = self.config_embed_settings['ticket_maker']

        description = "".join(embed_settings['description'])

        embed = Embed(title=embed_settings['title'],
                      description=description,
                      color=int(embed_settings['color'], base=16))
        #embed.add_field(name="Auto Response Message", value=f"```{content}```", inline=False)
        embed.set_thumbnail(url=embed_settings['thumbnail_image'])
        embed.set_footer(text=embed_settings['footer_text'], icon_url=embed_settings['footer_image'])

        return embed
    

    async def player_info_embed(self, profile:dataclass.Player, stats:dataclass.Playerstats, bancount,serverbans, player_ids:dataclass.Playerids, note_count, official_bans):
        embed_settings = self.config_embed_settings['auto_response']
        embed = Embed(title=embed_settings['title'],
                              description=f"# {profile.player_name}\nSteam ID: [{player_ids.steamid}]({profile.profile_url})", color=int(embed_settings['color'], base=16)) 
        embed.set_footer(text=embed_settings['footer_text'], icon_url=embed_settings['footer_image'])
        embed.set_thumbnail(url=embed_settings['thumbnail_image'])
        embed.add_field(
            name="Hours", value=f"Total Time Played: {profile.playtime}\nTraining time:{profile.playtime_training}\nActual Servers: {profile.playtime - profile.playtime_training}",
            inline=True)

        embed.add_field(name="Notes", value=f"There are {note_count}(s) on profile.",
                        inline=True)
        
        embed.add_field(name="Stats (1 week period)",
                        value=f"Total kills/deaths today: {stats.kills_day}/{stats.deaths_day}\nTotal kills/deaths this week: {stats.kills_week}/{stats.deaths_week}",
                        inline=False)
        
        embed.add_field(name="Limited",
                        value=f"```{profile.limited}```", inline=False)
        
        embed.add_field(name=f"Server Bans - Total: {bancount}, Showing: {bancount}",
                                value=f"{serverbans}", inline=False)
        
        embed.add_field(name="Rustbans, community bans and other bans",
                        value=f"{official_bans}", inline=False)
        
        return embed
    

    async def general_embed(self, steamid, issue) -> Embed:
        embed_settings = self.config_embed_settings['general_ticket']
        embed = Embed(title="General Embed", color=int(embed_settings['color'], base=16))
        embed.add_field(name="Describe your issue", value=f"```{issue}```", inline=False)
        embed.add_field(name="Steam ID or Profile Link", value=f"```{steamid}```", inline=False)
        
        embed.set_footer(text=embed_settings['footer_text'], icon_url=embed_settings['footer_image'])

        return embed
    
    async def report_embed(self, maker_steamid, cheater_steamid, info, proof) -> Embed:
        embed_settings = self.config_embed_settings['report_ticket']
        embed = Embed(title="Report Embed", color=int(embed_settings['color'], base=16))
        embed.add_field(name="Your Steam ID or Profile Link", value=f"````{maker_steamid}```", inline=False)
        embed.add_field(name="Cheater's Steam ID or Profile Link", value=f"```{cheater_steamid}```", inline=False)
        embed.add_field(name="Information", value=f"```{info}```", inline=False)
        embed.add_field(name="Proof", value=f"```{proof}```", inline=False)
        
        embed.set_footer(text=embed_settings['footer_text'], icon_url=embed_settings['footer_image'])

        return embed
    
    async def ban_appeal_embed(self, steamid, reason) -> Embed:
        embed_settings = self.config_embed_settings['ban_appeal_ticket']
        embed = Embed(title="Ban Appeal Embed", color=int(embed_settings['color'], base=16))
        embed.add_field(name="Why should you be unbanned?", value=f"```{reason}```", inline=False)
        embed.add_field(name="Your Steam ID or Profile Link", value=f"````{steamid}```", inline=False)
        embed.set_footer(text=embed_settings['footer_text'], icon_url=embed_settings['footer_image'])

        return embed
    

    async def ticket_transcript_embed(self, ticket_number, creator, creators_steam, closed_by):
        embed_settings = self.config_embed_settings['transcripts']
        embed = Embed(title="Ticket Transcript", description="A transcript has been generated for a closed ticket.", color=int(embed_settings['color'], base=16))

        embed.add_field(name="Ticket Number", value=f"#{ticket_number}", inline=False)
        embed.add_field(name="Ticket Creator", value=f"{creator.mention}", inline=False)
        embed.add_field(name="Creator's SteamID/Profile", value=creators_steam, inline=False)
        embed.add_field(name="Creator's Discord ID", value=creator.id, inline=False)

        embed.add_field(name="Closed By", value=closed_by.mention, inline=False)

        embed.set_footer(text=embed_settings['footer_text'], icon_url=embed_settings['footer_image'])

        return embed