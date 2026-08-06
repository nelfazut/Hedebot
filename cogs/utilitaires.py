from discord import app_commands
from discord.ext import commands
import asyncio
import discord
import re
from collections import Counter

# all cogs inherit from this base class
class Utilitaires(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # adding a bot attribute for easier access
        self.demarrage = 0
        self.aled_messages = []
    
    @property
    def guild(self):
        return self.bot.get_guild(self.bot.config["GUILD_ID"])
        
    @property
    def help_channel(self):
        if self.guild:
            return self.guild.get_channel(self.bot.config["HELP_CHANNEL"])
        return None
        
    @commands.command(name="purge")
    @commands.has_role('Soldat.e')
    async def purge(
        self, 
        ctx, 
        amount: int = commands.parameter(description="Le nombre de messages à supprimer (max 1000)")
    ):
        """Supprime un certain nombre de messages dans le salon actuel"""
        if amount > 1000:
            return await ctx.send(f"Trop de messages sélectionnés ({amount}/1000)")
        deleted = await ctx.channel.purge(limit=amount + 1)
        deleted_msgs = [m for m in deleted if m.id != ctx.message.id]
        counts = Counter(str(m.author) for m in deleted_msgs)
        summary = '\n'.join([f"**{author}**: {count}" for author, count in counts.items()])
        await ctx.send(f"{len(deleted_msgs)} messages ont été supprimés\n\n{summary}", delete_after=2.0)
    
    @commands.command(name="rappel")
    async def remind(
        self, 
        ctx, 
        temps: str = commands.parameter(description="Le délai (ex: 1h30m, 2j, 45s) sans espaces"), 
        *, 
        message: str = commands.parameter(description="Le texte du rappel à envoyer")
    ):
        """Crée un rappel personnalisé après un certain temps"""
        matches = re.findall(r'(\d+(?:\.\d+)?)([smhj])', temps.lower())
        if not matches:
            await ctx.send("Format de temps invalide. Utilisez `s`, `m`, `h`, `j` **sans espaces** (ex: `ht!rappel 1h30m prendre la bastille`).")
            return    

        total_secondes = 0
        multiplicateurs = {'s': 1, 'm': 60, 'h': 3600, 'j': 86400}

        for valeur, unite in matches:
            total_secondes += float(valeur) * multiplicateurs[unite]
            
        if total_secondes <= 0:
            await ctx.send("Le temps doit être supérieur à 0.")
            return

        await ctx.send(f'Quête acceptée !')
        
        await asyncio.sleep(total_secondes)
        
        await ctx.send(f"{message} {ctx.author.mention}")
        
    @remind.error
    async def remind_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Il manque des arguments. Utilisation : `ht!rappel <temps> <message>`")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Détecte si le bot est mentionné pour prendre les témoins à partie"""
        if not self.demarrage and str(message.channel.type) != "private":
            self.aled_salon = await message.guild.fetch_channel(self.bot.config["HELP_CHANNEL"])
            
        if self.bot.user.mentioned_in(message) and message.author != self.bot.user and discord.utils.get(message.guild.roles, name="Soldat.e") in message.author.roles: 
            await message.channel.send("Que les témoins prennent acte!!")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Souhaite la bienvenue aux nouveaux arrivants"""
        channel = member.guild.get_channel(self.bot.config["DEFAULT_CHANNEL"])
        embed = discord.Embed(
            title="**Bienvenue dans la guilde!**",
            description=self.bot.config["ARRIVAL_MESSAGE"], 
            color=0x3f8402
        )
        embed.set_thumbnail(url=self.bot.config["LOGO_LINK"])
        await channel.send(f'<@{member.id}>', embed=embed)
        
        role = member.guild.get_role(self.bot.config["DEFAULT_ROLE"])
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Signale le départ d'un membre"""
        channel = member.guild.get_channel(self.bot.config["DEFAULT_CHANNEL"])
        embed = discord.Embed(
            title="**Au revoir**", 
            description=f"**{member.name}** est parti.e", 
            color=0x3f8402
        )
        embed.set_thumbnail(url=self.bot.config["LOGO_LINK"])
        await channel.send(f'{member.mention}', embed=embed)

    @commands.command(name='aled')
    async def aled(self, ctx):
        """Permet d'envoyer un appel anonyme à la modération (à utiliser en message privé)"""
        if ctx.channel.type == discord.ChannelType.private:
            def check(user):
                return user.author == ctx.author and user.channel == ctx.channel
                
            await ctx.channel.send("Envoie le message que tu souhaites voir apparaitre")
            
            try:
                msg = await self.bot.wait_for('message', timeout=120.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Soyez plus rapide la prochaine fois :wink:")
                return
                
            embed = discord.Embed(title="Un membre a besoin d'aide !", description=msg.content, color=0x3f8402)
            self.aled_messages.append([(await self.help_channel.send(embed=embed)).id, embed])
            await ctx.send("Message bien envoyé")
            
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Empêche la suppression des messages d'aide (aled)"""
        for aled_message in self.aled_messages:
            if aled_message[0] == message.id:
                new_msg = await message.channel.send(embed=aled_message[1])
                aled_message[0] = new_msg.id
                
    @commands.command(name="parle")
    @commands.has_role('Soldat.e')
    async def parler_cmd(
        self, 
        ctx, 
        channel: discord.TextChannel = commands.parameter(description="Le salon où le bot doit parler"), 
        *, 
        message: str = commands.parameter(description="Le texte que le bot va envoyer")
    ):
        """Fait parler le bot dans un salon spécifique"""
        await channel.send(message)
    @commands.command(name="steak")
    async def steak(self, ctx):
        """Si on se trompe de commande"""
        await ctx.send("végétal et à point, j'espère")
async def setup(bot):
    await bot.add_cog(Utilitaires(bot=bot))