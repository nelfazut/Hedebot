import discord
from discord.ext import commands
TOKEN = open("TOKEN.txt").read()
print((TOKEN))
class ExampleBot(commands.Bot):
    def __init__(self):
        # initialise l'objet bot
        # ici on prend les intents all au cas ou on en ai besoin
        super().__init__( 
            command_prefix="h!",
            intents=discord.Intents.all()
        )
    
    async def setup_hook(self): # on crée une méthode pour charger les extensions
        await self.load_extension("classement")
        await self.load_extension("utilitaires")
        await self.load_extension("des")
        await self.load_extension("reactionrole")

ExampleBot().run(TOKEN) # on lance le bot