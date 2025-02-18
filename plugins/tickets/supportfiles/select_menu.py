import plugins.tickets.supportfiles.ticket_modals as modal_manager

import discord
import json

from plugins.tickets.supportfiles.database import tickets_database

class dropdown_menu_setup(discord.ui.Select):
    def __init__(self, options, config, tokens):
        self.config = config
        self.tokens = tokens
        self.database = tickets_database()

        super().__init__(
            placeholder="Select an option",
            max_values=1,min_values=1,
            options=options, custom_id="ticket_maker_menu")

    async def callback(self, interaction: discord.Interaction):
        
        selected_option = self.values[0]

        #Reset the menu
        options=self.load_options_from_json()
        await interaction.message.edit(view=dropdown_menu_view(config=self.config, tokens=self.tokens,options=options))
        
        #Check to see if the user has an active ticket already.
        active_ticket = await self.database.get_active_ticket_for_user(interaction.user.id)
        if active_ticket:
            await interaction.response.send_message(f"You already have an active ticket.. It's right here: <#{active_ticket['channel_id']}>", ephemeral=True)
            return

        selected_option = selected_option.lower()
        if selected_option == "general":            
            modal = modal_manager.general_modal(config=self.config, tokens=self.tokens)
            await interaction.response.send_modal(modal)
        elif selected_option == "ban appeal":
            modal = modal_manager.ban_appeal_modal(config=self.config, tokens=self.tokens)
            await interaction.response.send_modal(modal)
        elif selected_option == "report a cheater":
            modal = modal_manager.report_cheater_modal(config=self.config, tokens=self.tokens)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message(f"Something isn't working. Please contact staff. You have selected: `{selected_option}`", ephemeral=True)

    def load_options_from_json(self):
        with open('./plugins/tickets/select_menu_options.json', 'r', encoding="utf-16") as f:
            select_menu_options = json.load(f)
        return [discord.SelectOption(label=option["label"], emoji=option['emoji'], description=option["description"]) for option in select_menu_options]

class dropdown_menu_view(discord.ui.View):
    def __init__(self, *, timeout = None, options, config, tokens):
        super().__init__(timeout=timeout)
        self.add_item(dropdown_menu_setup(options, config, tokens))