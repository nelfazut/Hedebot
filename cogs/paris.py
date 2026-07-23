import discord
from discord.ext import commands
from cogs.views.pari_view import PariAcceptationView

class ParisCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pari")
    async def pari(self, ctx, adversaire: discord.Member, montant: int, *, objet: str):

        nouveau_pari = self.bot.bet_manager.create_bet(
            ctx.author.id, 
            adversaire.id, 
            objet, 
            montant
        )

        # 2. On prépare l'interface
        embed = discord.Embed(
            title="Nouveau Pari !", 
            description=f"{adversaire.mention}, tu as été défié par {ctx.author.mention} !"
        )
        embed.add_field(name="Enjeu", value=nouveau_pari.objet)
        embed.add_field(name="Mise", value=f"{nouveau_pari.montant} PR")

        # 3. On envoie la Vue
        view = PariAcceptationView(self.bot, nouveau_pari)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ParisCog(bot))