import discord
from discord.ext import commands
from data.managers.leaderboard import LeaderboardManager
from data.managers.bets import BetManager
import json
TOKEN = open("TOKEN.txt").read()
print((TOKEN))
class ExampleBot(commands.Bot):
    def __init__(self):
        with open("config.json") as f:
            self.config = json.load(f) 
        # initialise l'objet bot
        # ici on prend les intents all au cas ou on en ai besoin
        super().__init__( 
            command_prefix=self.config["BOT_PREFIX"],
            intents=discord.Intents.all()      
        )
        
    async def setup_hook(self): # on crée une méthode pour charger les extensions
        self.leaderboard_mgr = LeaderboardManager()
        self.bet_manager = BetManager("data/paris.json")
        await self.load_extension("cogs.classement")
        await self.load_extension("cogs.utilitaires")
        await self.load_extension("cogs.des")
        await self.load_extension("cogs.reactionrole")
    
ExampleBot().run(TOKEN) # on lance le bot