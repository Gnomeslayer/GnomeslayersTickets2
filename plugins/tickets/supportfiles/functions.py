# Third-party imports
import asyncio
import aiohttp
import json
import validators

import plugins.tickets.supportfiles.dataclasses as dataclass
# Standard library imports
from datetime import datetime, timezone, timedelta

from battlemetrics import Battlemetrics

with open("./json/config.json", "r") as config_file:
    config = json.load(config_file)

class ticket_functions():
    def __init__(self, config, tokens):
        self.config = config
        self.api = Battlemetrics(api_key=tokens['tokens']['battlemetrics_token'])



    async def get_player_info(self, player_id):
        
        player = await self.api.player.info(player_id)
        if not player:
            return
        player = await self.sort_player(player)
        await asyncio.sleep(0.1)  # Slight sleep so we don't get rate limited.
        player_notes = await self.api.notes.list(player_id=player_id)
        if player_notes:
            if player_notes['data']:
                player.notes = await self.sort_notes(player_notes)
        else:
            player.notes = None
        await asyncio.sleep(0.1)  # Slight sleep so we don't get rate limited.
        
        player_server_bans = await self.api.bans.search(player_id=player_id)
        if player_server_bans:
            if player_server_bans.get('meta'):
                if player_server_bans['meta']['total']:
                    player.server_bans = await self.sort_server_bans(player_server_bans)
            else:
                player.server_bans = None
        else:
            player.server_bans = None
        
        player_session = await self.api.player.session_history(player_id=player_id)
        if player_session:
            if player_session['data']:
                player.server_id = await self.sort_session(player_session)

        # for name in player.names:
        #    await db.save_name(bmid=player.battlemetrics_id, playername=name)

        return player

    async def sort_session(self, player_session:dict) -> int:
        return player_session['data'][0]['relationships']['server']['data']['id']

    async def sort_server_bans(self, player_server_bans: dict) -> list:
        server_bans = []

        for data in player_server_bans['data']:
            if str(data['relationships']['organization']['data']['id']) == str(config['additional']['organization_id']):
                server_ban = dataclass.Serverbans()
                server_ban.bandate = data['attributes']['timestamp']
                server_ban.banid = data['id']
                server_ban.bannote = data['attributes']['note']
                server_ban.banreason = data['attributes']['reason']
                server_ban.bmid = data['relationships']['player']['data']['id']
                if data['relationships'].get('server'):
                    server_ban.serverid = data['relationships']['server']['data']['id']
                else:
                    server_ban.serverid = 0

                server_ban.orgid = data['relationships']['organization']['data']['id']
                server_ban.uuid = data['attributes']['uid']
                if data['attributes']['expires']:
                    server_ban.expires = data['attributes']['expires']
                else:
                    server_ban.expires = "Never"
                banner_id = 0
                if data['relationships'].get('user'):
                    banner_id = data['relationships']['user']['data']['id']
                else:
                    server_ban.banner = "Server Ban"
                for identifier in data['attributes']['identifiers']:
                    if identifier['type'] == "steamID":
                        if identifier.get('metadata'):
                            server_ban.steamid = identifier['metadata']['profile']['steamid']
                        else:
                            server_ban.steamid = identifier['identifier']

                for included in player_server_bans['included']:
                    if included['type'] == "server":
                        if included['id'] == server_ban.serverid:
                            server_ban.servername = included['attributes']['name']
                    if included['type'] == "user":
                        if included['id'] == banner_id:
                            server_ban.banner = included['attributes']['nickname']
                server_bans.append(server_ban)
        return server_bans


    async def sort_notes(self, player_notes: dict) -> list:
        notes = []
        for data in player_notes['data']:
            if data['relationships'].get('user'):
                note = dataclass.Notes(
                    noteid=data['id'],
                    bmid=data['relationships']['player']['data']['id'],
                    orgid=data['relationships']['organization']['data']['id'],
                    notemakerid=data['relationships']['user']['data']['id'],
                    note=data['attributes']['note'],
                    notemakername="Unknown"
                )
            else:
                note = dataclass.Notes(
                    noteid=data['id'],
                    bmid=data['relationships']['player']['data']['id'],
                    orgid=data['relationships']['organization']['data']['id'],
                    notemakerid=data['relationships']['organization']['data']['id'],
                    note=data['attributes']['note'],
                    notemakername="Unknown"
                )
            for included in player_notes['included']:
                if included['type'] == "user":
                    if included['id'] == note.notemakerid:

                        note.notemakername = included['attributes']['nickname']
                if included['type'] == "organization":
                    if included['id'] == note.orgid:
                        note.orgname = included['attributes']['name']
            
            notes.append(note)
        return notes

    async def sort_player(self, player: dict) -> dataclass.Player:
        player_data = {}
        player_data['battlemetrics_id'] = player['data']['id']
        player_data['player_name'] = player['data']['attributes']['name']
        player_data['playtime'] = 0
        player_data['playtime_training'] = 0
        player_data['names'] = []

        vacban_count = 0
        vac_banned = False
        last_ban = 0
        community_banned = False
        game_ban_count = 0

        for included in player['included']:
            if included['type'] == "identifier":
                if included['attributes']['type'] == "steamID":
                    player_data['steam_id'] = included['attributes']['identifier']
                    if included['attributes'].get('metadata'):
                        if included['attributes']['metadata'].get('profile'):
                            player_data['avatar_url'] = included['attributes']['metadata']['profile']['avatarfull']
                            # player_data['account_created'] = included['attributes']['metadata']['profile']['timecreated']
                            player_data['limited'] = False
                            if included['attributes']['metadata']['profile'].get('isLimitedAccount'):
                                player_data['limited'] = included['attributes']['metadata']['profile']['isLimitedAccount']
                            player_data['profile_url'] = included['attributes']['metadata']['profile']['profileurl']
                        if included['attributes']['metadata'].get('rustBans'):
                            player_data['rustbanned'] = included['attributes']['metadata']['rustBans']['banned']
                            player_data['rustbancount'] = included['attributes']['metadata']['rustBans']['count']
                            given_time = datetime.strptime(
                                f"{included['attributes']['metadata']['rustBans']['lastBan']}", "%Y-%m-%dT%H:%M:%S.%fZ")
                            current_time = datetime.utcnow()
                            player_data['banned_days_ago'] = (
                                current_time - given_time).days

                if included['attributes']['type'] == "name":
                    player_data['names'].append(
                        included['attributes']['identifier'])

            if included['type'] == "server":
                training_names = ["rtg", "aim", "ukn", "arena",
                                "combattag", "training", "aimtrain", "train", "arcade", "bedwar", "bekermelk", "escape from rust"]
                for name in training_names:
                    if name in included['attributes']['name']:
                        player_data['playtime_training'] += included['meta']['timePlayed']
                player_data['playtime'] += included['meta']['timePlayed']
        player_data['playtime'] = player_data['playtime'] / 3600
        player_data['playtime'] = round(player_data['playtime'], 2)
        player_data['playtime_training'] = player_data['playtime_training'] / 3600
        player_data['playtime_training'] = round(
            player_data['playtime_training'], 2)
        player_data['last_ban'] = last_ban
        player_data['community_banned'] = community_banned
        player_data['game_ban_count'] = game_ban_count
        player_data['vac_banned'] = vac_banned
        player_data['vacban_count'] = vacban_count
        myplayer = dataclass.Player(**player_data)
        return myplayer

    async def get_id_from_steam(self, url: str) -> int:
        """Takes the URL (well part of it) and returns a steam ID"""
        url = (
            f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?format=json&"
            f"key={config['tokens']['steam_token']}&vanityurl={url}&url_type=1"
        )
        async with aiohttp.ClientSession(
            headers={"Authorization": config['tokens']['steam_token']}
        ) as session:
            async with session.get(url=url) as r:
                response = await r.json()
        if response['response'].get('steamid'):
            return response["response"]["steamid"] if response["response"]["steamid"] else 0
        else:
            return 0


    async def get_player_ids(self, submittedtext: str) -> dataclass.Playerids:
        steamid = 0
        playerids = dataclass.Playerids()

        if validators.url(submittedtext):
            mysplit = submittedtext.split("/")
            if mysplit[3] == "id":
                steamid = await self.get_id_from_steam(mysplit[4])
            if mysplit[3] == "profiles":
                steamid = mysplit[4]
        else:
            if len(submittedtext) != 17:
                return None
            steamid = submittedtext

        if not steamid:
            return playerids
        
        if steamid:
            playerids.steamid = steamid
            results = await self.api.player.match_identifiers(identifier=steamid,identifier_type="steamID")
            if results.get('data'):
                playerids.bmid = results['data'][0]['relationships']['player']['data']['id']
            else:
                playerids.bmid = 0

        return playerids

    async def kda_two_weeks(self, bmid: int) -> dict:
        weekago = datetime.now(
            timezone.utc) - timedelta(hours=168)
        weekago = str(weekago).replace("+00:00", "Z:")
        weekago = weekago.replace(" ", "T")
        url = "https://api.battlemetrics.com/activity"
        params = {
            "version": "^0.1.0",
            "tagTypeMode": "and",
            "filter[timestamp]": str(weekago),
            "filter[types][whitelist]": "rustLog:playerDeath:PVP",
            "filter[players]": f"{bmid}",
            "include": "organization,user",
            "page[size]": "100"
        }
        return await self.api.helpers._make_request(method="GET", url=url, data=params)

    async def kda_day(self, bmid: int) -> dict:
        weekago = datetime.now(
            timezone.utc) - timedelta(hours=24)
        weekago = str(weekago).replace("+00:00", "Z:")
        weekago = weekago.replace(" ", "T")
        url = "https://api.battlemetrics.com/activity"
        params = {
            "version": "^0.1.0",
            "tagTypeMode": "and",
            "filter[timestamp]": str(weekago),
            "filter[types][whitelist]": "rustLog:playerDeath:PVP",
            "filter[players]": f"{bmid}",
            "include": "organization,user",
            "page[size]": "100"
        }
        
        return await self.api.helpers._make_request(method="GET", url=url, params=params)


    async def player_stats(self, bmid: int) -> dataclass.Playerstats:
        kda_results = await self.kda_day(bmid)
        stats = dataclass.Playerstats()
        if kda_results:
            if kda_results.get('data'):
                for stat in kda_results['data']:
                    mytimestamp = stat['attributes']['timestamp'][:10]
                    mytimestamp = datetime.strptime(mytimestamp, '%Y-%m-%d')
                    days_ago = (datetime.now() - mytimestamp).days
                    if stat['attributes']['data'].get('killer_id'):
                        if stat['attributes']['data']['killer_id'] == int(bmid):
                            if days_ago <= 1:
                                stats.kills_day += 1
                            if days_ago <= 7:
                                stats.kills_week += 1
                            if days_ago <= 14:
                                stats.kills_two_weeks += 1
                        else:
                            if days_ago <= 1:
                                stats.deaths_day += 1
                            if days_ago <= 7:
                                stats.deaths_week += 1
                            if days_ago <= 14:
                                stats.deaths_two_weeks += 1
        if kda_results:
            if kda_results.get('links'):
                while kda_results["links"].get("next"):
                    myextension = kda_results["links"]["next"]
                    kda_results = await self.api.helpers._make_request(method="GET", url=myextension)
                    if kda_results:
                        for stat in kda_results['data']:
                            mytimestamp = stat['attributes']['timestamp'][:10]
                            mytimestamp = datetime.strptime(
                                mytimestamp, '%Y-%m-%d')
                            days_ago = (datetime.now() - mytimestamp).days
                            if stat['attributes']['data'].get('killer_id'):
                                if stat['attributes']['data']['killer_id'] == int(bmid):
                                    if days_ago <= 1:
                                        stats.kills_day += 1
                                    if days_ago <= 7:
                                        stats.kills_week += 1
                                    if days_ago <= 14:
                                        stats.kills_two_weeks += 1
                                else:
                                    if days_ago <= 1:
                                        stats.deaths_day += 1
                                    if days_ago <= 7:
                                        stats.deaths_week += 1
                                    if days_ago <= 14:
                                        stats.deaths_two_weeks += 1
        return stats


    async def activity_logs(self, steamid:str, server_id:str):
        combatlog = None
        teaminfo = None
        combatlog = await self.api.server.console_command(server_id=server_id, command=f"combatlog {steamid}")
                
        if combatlog.get('errors'):
            combatlog = None
        elif not combatlog.get('data'):
            combatlog = None
        else:
            combatlog = combatlog['data']['attributes']['result']
            if 'invalid player' in combatlog.lower():
                combatlog = None
        
        teaminfo = await self.api.server.console_command(server_id=server_id, command=f"teaminfo {steamid}")
        if teaminfo.get('errors'):
            teaminfo = None
        elif not teaminfo.get('data'):
            teaminfo = None
        else:
            teaminfo = teaminfo['data']['attributes']['result']
                
        response = {}
        response['combatlog'] = combatlog
        response['teaminfo'] = teaminfo
        return response


    async def activity_logs_search(self, search:str):
        return await self.api.activity_logs(filter_search=search)
    

    async def save_button(self, button_id):
        with open('./plugins/tickets/interactions.json', 'r') as f:
            button_data:list = json.load(f)
        
        button_data.append(button_id)

        with open('./plugins/tickets/interactions.json', 'w') as f:
            f.write(json.dumps(button_data, indent=4))