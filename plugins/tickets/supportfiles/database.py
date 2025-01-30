import aiosqlite

class tickets_database():
    def __init__(self):
        self.database_location = "./plugins/tickets/supportfiles/database.db"

    async def create_table(self) -> None:
        async with aiosqlite.connect(self.database_location) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY,
                    ticket_number TEXT,
                    ticket_type TEXT,
                    creater_discord_id TEXT,
                    active_ticket boolean,
                    channel_id TEXT
                )
            ''')

            await db.commit()

    
    async def get_all_tickets(self) -> list[dict]:
        query = "SELECT * FROM tickets"
        tickets = []
        async with aiosqlite.connect(self.database_location) as db:
            response = await db.execute(query)
            response = await response.fetchall()
            for ticket in response:
                tickets.append({
                    'ticket_number': ticket[1],
                    'ticket_type': ticket[2],
                    'creater_discord_id': ticket[3],
                    'active_ticket': ticket[4],
                    'channel_id': ticket[5]
                    })
        
        return tickets
    
    async def add_ticket(self, ticket_number, ticket_type, creater_discord_id, active_ticket, channel_id) -> None:

        query = """INSERT INTO tickets (ticket_number, ticket_type, creater_discord_id, active_ticket, channel_id) 
        VALUES (:ticket_number, :ticket_type, :creater_discord_id, :active_ticket, :channel_id)"""
        params = {
            'ticket_number': ticket_number,
            'ticket_type': ticket_type,
            'creater_discord_id': creater_discord_id,
            'active_ticket': active_ticket,
            'channel_id': channel_id
        }
        async with aiosqlite.connect(self.database_location) as db:
            await db.execute(query, params)
            await db.commit()
        
        return True

    
    async def update_ticket_status(self, channel_id) -> None:
        active = False
        query = f"UPDATE tickets SET active_ticket = {active} WHERE channel_id = :channel_id"
        params = {'channel_id': channel_id}

        async with aiosqlite.connect(self.database_location) as db:
            await db.execute(query, params)
            await db.commit()
        
        return


    async def get_active_ticket_for_user(self, discord_id:str) -> dict:
        active = True
        query = f"SELECT * FROM tickets where creater_discord_id = :creater_discord_id and active_ticket = {active}"
        params = {'creater_discord_id': discord_id}

        ticket = {}
        async with aiosqlite.connect(self.database_location) as db:
            async with db.execute(query, params) as cursor:
                response = await cursor.fetchone()
                if response:
                    ticket = {
                    'ticket_number': response[1],
                    'ticket_type': response[2],
                    'creater_discord_id': response[3],
                    'active_ticket': response[4],
                    'channel_id': response[5]
                    }
        
        return ticket