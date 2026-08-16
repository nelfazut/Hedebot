import discord
from discord.ext import commands, tasks
import datetime
from zoneinfo import ZoneInfo  

TZ_FRANCE = ZoneInfo("Europe/Paris")
class Streaks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rappel_streak.start()

    def cog_unload(self):
        self.rappel_streak.cancel()
        
    @property
    def guild(self):
        return self.bot.get_guild(self.bot.config["GUILD_ID"])
        
    @property
    def default_channel(self):
        if self.guild:
            return self.guild.get_channel(self.bot.config["DEFAULT_CHANNEL"])
        return None

    @tasks.loop(time=[datetime.time(hour=h, minute=0, second=0, tzinfo=TZ_FRANCE) for h in range(18, 24)])
    async def rappel_streak(self):
        now = datetime.datetime.now(TZ_FRANCE)
        current_hour = now.hour
        
        users_to_ping = self.bot.streak_mgr.get_users_to_remind(current_hour)
        if not users_to_ping:
            return
            
        channel = self.bot.get_channel(self.bot.config["STREAK_CHANNEL_ID"])
        if channel:
            pings = " ".join([f"<@{uid}>" for uid in users_to_ping])
            await channel.send(
                f"**Rappel de Streak !**\n{pings}\n"
                f"N'oublie pas de faire votre streak aujourd'hui !"
            )

    @rappel_streak.before_loop
    async def before_rappel(self):
        await self.bot.wait_until_ready()

    @commands.command(name="streak")
    async def streak(self, ctx, user: discord.Member = commands.parameter(default=None, description="Le membre dont on veut voir la streak (laisser vide pour soi-même)")):
        """affiche la streak de l'auteur ou du membre ciblé, avec ses gels"""
        cible = user if user else ctx.author
        streak_val = self.bot.streak_mgr.get_user_streak(cible.id)
        freezes = self.bot.streak_mgr.get_user_freezes(cible.id)
        played_today = self.bot.streak_mgr.played_today(cible.id)
        if user is None:
            msg = f"Vous avez joué {streak_val} jours de suite."
        else:
            nom = cible.nick if cible.nick else cible.display_name
            msg = f"{nom} a joué {streak_val} jours de suite."
        if not played_today:
            msg += f"\nPas joué ajourd'hui."
        if freezes > 0:
            msg += f"\n**Gels de série disponibles :** {freezes}"
            
        await ctx.send(msg)
        
    @commands.command(name="bstreak")
    async def best_streak(self, ctx, user: discord.Member = commands.parameter(default=None, description="Un utilisateur dont on veut voir la meilleure")):
        """Donne la meilleure streak de l'auteur ou du membre ciblé"""
        if user is None:
            await ctx.send(f"Votre meilleure streak de tous les temps est {self.bot.streak_mgr.get_user_best_streak(ctx.author.id)}")
        else:
            nom = user.nick if user.nick else user.display_name
            await ctx.send(f"La meilleur streak de tous les temps de {nom} est {self.bot.streak_mgr.get_user_best_streak(user.id)}")
    
    @commands.command(name="soat")
    async def soat(self, ctx):
        """renvoie la meilleure streak all time de la guilde"""
        id_max, valeur_max = self.bot.streak_mgr.best_streak()
        if not id_max:
            return await ctx.send("Personne n'a de streak enregistrée pour le moment.")
        
        membre = await self.guild.fetch_member(id_max)
        nom = membre.nick if membre and membre.nick else membre.display_name if membre else f"Utilisateur inconnu ({id_max})"
        await ctx.send(f"La meilleure streak de tous les temps de cette guilde est {valeur_max}, réalisée par {nom}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Jeu des streaks"""
        if message.author.bot:
            return
        channel_id = self.bot.config["STREAK_CHANNEL_ID"]
        if message.channel.id == channel_id:
            streak_updated, freeze_gained = self.bot.streak_mgr.trigger_streak(message.author.id)
            await message.add_reaction(await message.guild.fetch_emoji(self.bot.config["STREAK_EMOJI_ID"]))
            if streak_updated:
                current_streak = self.bot.streak_mgr.get_user_streak(message.author.id)
                
                # Si le joueur a gagné un gel de série aujourd'hui
                if freeze_gained:
                    await self.default_channel.send(
                        f"{message.author.mention} ! Tu viens d'atteindre {current_streak} jours de suite dans {(await self.bot.fetch_channel(channel_id)).mention} et tu gagnes un **Gel de série** !\n"
                        f"Il sauvera automatiquement ta streak si tu oublies de jouer un jour."
                    )
                
                for jours, pr in self.bot.config["STREAK_DAY_PR"]: 
                    if current_streak == jours:
                        await self.default_channel.send(f"Pour avoir joué {jours} jours dans {message.channel.mention}, {message.author.mention} gagne {pr} pr!")
                        
                        # On récupère le cog Classement pour ajouter les PR
                        classement_cog = self.bot.get_cog("Classement")
                        if classement_cog:
                            await classement_cog.ajouter_pr(message.author, pr)
                        break 

async def setup(bot):
    await bot.add_cog(Streaks(bot))