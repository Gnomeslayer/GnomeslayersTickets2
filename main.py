import json
from datetime import datetime

#Discord imports
from discord import Intents
from discord.ext.commands import Bot

import os
import importlib.util
import inspect

from plugins.tickets.supportfiles.database import tickets_database

with open("./json/config.json", "r") as config_file:
    config = json.load(config_file)

class MyBot(Bot):
    def __init__(self, config:dict):
        super().__init__(
            command_prefix = config['additional']['prefix'],
            intents = Intents.all()
        )
        self.config = config

    @staticmethod
    async def find_modules():
        modules = []
        base_dir = "./plugins"
        for dirpath, _, filenames in os.walk(base_dir):
            # Check if we are within the first or second level of directories
            if dirpath == base_dir or dirpath.startswith(f"{base_dir}{os.path.sep}"):
                for filename in filenames:
                    if filename.endswith('.py'):
                        module_name = os.path.splitext(filename)[0]
                        full_path = os.path.join(dirpath, filename)
                        modules.append((module_name, full_path))
        return modules
    
    @staticmethod
    async def import_class_from_module(module_path):
        module_name = os.path.splitext(os.path.basename(module_path))[0]

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Optionally, you can inspect the module to find the class or function you need
        # For example, to find the first class in the module:
        target_class = None
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name.lower() == module_name.lower():  # Adjust this condition as needed
                target_class = obj
                break

        return target_class

    async def on_ready(self):
        modules = await self.find_modules()
        for module_name, module_path in modules:
            target_class = await self.import_class_from_module(module_path)
            if target_class:
                # Perform actions with the imported class, e.g., instantiate it
                instance = target_class(bot=self, tokens=self.config)
                
                await self.add_cog(instance)

        await self.tree.sync()
        await tickets_database().create_table() #Setups the database
        print(f"[{datetime.now()}] Bot fully loaded and ready to go!")
        
# Ensure the script is being run directly, not imported as a module
if __name__ == "__main__":
    
    print("\n\n=========== BOT LOADED WITH LIVE TOKENS ===========\n\n")
    bot = MyBot(config)
    bot.run(config['tokens']['discord_token'])
