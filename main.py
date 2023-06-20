import discord
from discord.ext import commands
TOKEN = "OTgzODE4MTQwMjA1MDgwNTc2.GF3lhb.bKPNk6CXU-LHiwrFnxOLpWYjb3kkYGBH42dfug"
class ExampleBot(commands.Bot):
    def __init__(self):
        # initialise l'objet bot
        # ici on prend les intents all au cas ou on en ai besoin
        super().__init__( 
            command_prefix="h!",
            intents=discord.Intents.all()
        )
    
    async def setup_hook(self): # on crée une fonction pour charger les extensions
        await self.load_extension("classement") # on charge l'extension bjorgus.py
        await self.load_extension("utilitaires")
        await self.load_extension("des")
        await self.load_extension("reactionrole")

ExampleBot().run(TOKEN) # on lance le bot