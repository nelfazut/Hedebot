import discord
from discord.ext import commands
from data.managers.leaderboard import LeaderboardManager
from data.managers.bets import BetManager
from data.managers.react_emojis import ReactionroleManager
from data.managers.streaks import StreakMgr
import json

with open("config.json") as f:
    config = json.load(f)

class Hedebot(commands.Bot):
    def __init__(self, config):
        self.config = config

        super().__init__( 
            command_prefix=self.config["BOT_PREFIX"],
            intents=discord.Intents.all()      
        )
        
    async def setup_hook(self): # on crée une méthode pour charger les extensions
        self.leaderboard_mgr = LeaderboardManager()
        self.leaderboard_mgr_tmp = LeaderboardManager(file_path="data/classement_tmp.csv", ui_path="data/classement_tmp.json")
        self.streak_mgr = StreakMgr()
        self.reaction_mgr = ReactionroleManager()
        self.bet_manager = BetManager("data/paris.json")
        await self.load_extension("cogs.classement")
        await self.load_extension("cogs.utilitaires")
        await self.load_extension("cogs.des")
        await self.load_extension("cogs.reactionrole")
        await self.load_extension("cogs.honeypot")
    
Hedebot(config).run(config["TOKEN"]) # on lance le bot