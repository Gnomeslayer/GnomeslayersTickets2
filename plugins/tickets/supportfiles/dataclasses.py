from dataclasses import dataclass

@dataclass
class Playerids():
    _id: int = None
    steamid: str = None
    bmid: int = None


@dataclass
class Playerstats():
    _id: int = None
    steamid: str = None
    bmid: int = None
    kills_day: int = 0
    kills_week: int = 0
    kills_two_weeks: int = 0
    deaths_day: int = 0
    deaths_week: int = 0
    deaths_two_weeks: int = 0


@dataclass
class Notes():
    _id: int = None
    noteid: int = None
    bmid: int = None
    orgid: int = None
    notemakerid: int = None
    orgname: str = None
    note: str = None
    notemakername: str = None


@dataclass
class Serverbans():
    _id: int = None
    bmid: int = None
    steamid: str = None
    bandate: str = None
    expires: str = None
    banid: int = None
    bannote: str = None
    serverid: int = None
    servername: str = None
    banner: str = None
    banreason: str = None
    uuid: str = None
    orgid: int = None


@dataclass
class Player():
    _id: int = None
    battlemetrics_id: int = None
    steam_id: int = None
    profile_url: str = None
    avatar_url: str = None
    player_name: str = None
    names: list = None
    account_created: str = None
    playtime: int = None
    playtime_training: int = None
    rustbanned: bool = None
    rustbancount: int = None
    banned_days_ago: int = None
    notes: list = None
    server_bans: list = None
    related_players: list = None
    limited: bool = None
    community_banned: bool = False
    game_ban_count: int = 0
    vac_banned: bool = False
    vacban_count: int = 0
    last_ban: int = 0
    server_id:int = 0