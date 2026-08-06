import discord
from discord.ext import commands
from services.creation_image import *
from io import BytesIO
from utils.helpers import get_user_color, decouper_liste
from typing import Union

class Classement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ajouter_pr(self, user_input: Union[discord.Member, int], nombre: int, leaderboard_mgr = None, gui=True):
        """mécanisme principal d'ajout de pr"""
        if not leaderboard_mgr:
            leaderboard_mgr = self.bot.leaderboard_mgr
        excluded = self.bot.config["EXCLUDED_IDS"]
        
        user_id = user_input.id if isinstance(user_input, discord.Member) else user_input

        if user_id in excluded:
            return

        # Récupération du membre via la config
        if not isinstance(user_input, discord.Member):
            guild = self.bot.get_guild(self.bot.config["GUILD_ID"])
            user = guild.get_member(user_id) if guild else None
        else:
            user = user_input
            
        # 2. Gestion de la couleur et du nom
        if user:
            color = get_user_color(user.roles)
            display_name = user.display_name
        else:
            old_data = mgr.get_player(user_id) # Note: 'mgr' semble ne pas être défini ici, c'est peut-être un oubli dans ton code original
            color = old_data.color if old_data else "#ffb000"
            display_name = old_data.nom if old_data else f"Joueur {user_id}"
            
        # 3. Mise à jour via le manager
        leaderboard_mgr.add_pr(user_id, display_name, color, nombre)
        if gui:
            await self.update_classement()

    @commands.command(name="prtemp")
    @commands.has_role("Soldat.e")
    async def prtemp(
        self, 
        ctx, 
        user: discord.Member = commands.parameter(description="Le membre à qui ajouter les PR"), 
        nombre: int = commands.parameter(description="Le nombre de PR à ajouter")
    ):
        """ajoute des pr au classement temporaire"""
        await self.ajouter_pr(user, nombre, self.bot.leaderboard_mgr_tmp, gui=False)

    @commands.command(name="classementtemp")
    @commands.has_role("Soldat.e")
    async def afficher_classement_temp(self, ctx):
        """renvoie le classement temporaire en format texte"""
        await ctx.send(str(self.bot.leaderboard_mgr_tmp))
    
    @commands.command(name="fusion")
    @commands.has_role("Soldat.e")
    async def fusion_classement(self, ctx):
        """Fusionne le classement temporaire et le classement normal dans le classement normal"""
        for user in self.bot.leaderboard_mgr_tmp.get_all_players():
            await self.ajouter_pr(user.id, user.pr, self.bot.leaderboard_mgr)
        self.bot.leaderboard_mgr_tmp.reset()

    @commands.command(name="pr")
    @commands.has_role("Soldat.e")
    async def pr(
        self, 
        ctx, 
        user: discord.Member = commands.parameter(description="Le membre à qui ajouter les PR"), 
        nombre: int = commands.parameter(description="Le nombre de PR à lui donner")
    ):
        """Ajoute des prs au membre"""
        await self.ajouter_pr(user, nombre, self.bot.leaderboard_mgr)
        
    async def update_classement(self):
        """Met à jour les images du classement sur discord en se basant sur l'état en mémoire"""
        channel_id = self.bot.config["RANKING_CHANNEL"]
            
        channel = self.bot.get_channel(channel_id)
        if not channel:
            return 

        for m_id in self.bot.leaderboard_mgr.get_ui_messages():
            try:
                msg = await channel.fetch_message(m_id)
                await msg.delete()
            except discord.NotFound:
                pass 
                
        membres = self.bot.leaderboard_mgr.get_all_players()
        new_messages = []
        for i, k in enumerate(decouper_liste(membres, 12)):
            image = await generate_scoreboard(k, i)
            with BytesIO() as f:
                image.save(f, format="PNG")
                f.seek(0)
                discord_file = discord.File(f, filename="classement.png")

            message = await channel.send(file=discord_file)
            new_messages.append(message.id)
        self.bot.leaderboard_mgr.save_ui_messages(new_messages)

    @commands.command(name="nomclassement")
    async def nomclassement(
        self, 
        ctx, 
        *, 
        phrase: str = commands.parameter(description="Le nouveau nom à afficher sur le classement")
    ):
        """Change le nom de l'utilisateur au classement"""
        await self.fnomclassement(ctx, ctx.author, phrase=phrase)

    @commands.command(name="fnomclassement")
    @commands.has_role("Soldat.e")
    async def fnomclassement(
        self, 
        ctx, 
        user: discord.Member = commands.parameter(description="Le membre dont on veut changer le nom"), 
        *, 
        phrase: str = commands.parameter(description="Le nouveau nom à afficher")
    ):
        """force le changement de nom de l'utilisateur ciblé au classement"""
        if ("\n" in phrase or ";" in phrase):
            await ctx.send("nom invalide")
            return
        if self.bot.leaderboard_mgr.rename_player(user.id, phrase):
            await self.update_classement()
            return
        if user.id == ctx.author.id:
            await ctx.send("Vous n'appartenez pas au classement")
        else:
            await ctx.send("Il n'appartient pas au classement...")

    @commands.has_role("Soldat.e")
    @commands.command(name="remove")
    async def remove(
        self, 
        ctx, 
        user: discord.Member = commands.parameter(description="Le membre à retirer du classement")
    ):
        """retire un utilisateur du classement"""
        self.bot.leaderboard_mgr.remove_player(user.id)
        await self.update_classement()

    async def renvoyer_paris_actifs(self, ctx):
        paris_actifs = self.bot.bet_manager.get_user_bets(ctx.author.id)
        if not paris_actifs:
            return await ctx.send("Tu n'as aucun pari en cours.")

        embed = discord.Embed(title="Tes paris actifs :", color=0x3f8402)
        for p in paris_actifs:
            role_txt = "lancé par toi" if p.lanceur_id == ctx.author.id else "reçu"
            embed.add_field(
                name=f"Pari #{p.id} ({role_txt})", 
                value=f"Adversaire : <@{p.adversaire_id if p.lanceur_id == ctx.author.id else p.lanceur_id}>\nObjet : {p.objet}\nMise : {p.montant} PR",
                inline=False
            )
        return await ctx.send(embed=embed)
    
    @commands.command(name="pari")
    async def pari(
        self, 
        ctx, 
        adversaire: discord.Member = commands.parameter(default=None, description="Le membre que vous souhaitez défier"), 
        montant: int = commands.parameter(default=None, description="La mise en PR (multiple de 5)"), 
        *, 
        objet: str = commands.parameter(default=None, description="L'enjeu ou la description du pari")
    ):
        """Lance un défi à un autre joueur ou affiche les paris en cours."""
        
        # 1. CAS : Affichage des paris en cours (si aucun argument n'est fourni)
        if adversaire is None and montant is None:
            return await self.renvoyer_paris_actifs(ctx)

        # 2. CAS : Lancement d'un nouveau pari
        # Vérification des arguments
        if not montant or not objet or not adversaire:
            return await ctx.send("Usage: `h!pari @user [montant] [objet]`")

        if not montant % 5 == 0:
            return await ctx.send("EH C'EST QUOI CE MONTANT????? NAN MAIS OH TU CROIS QUE TU VAS T'ECHAPPER DES MULTIPLES DE 5PR COMME CA? JE CROIS PAS NON. Parie un multiple de 5.")
            
        # Vérification du solde PR
        # On récupère les données des deux joueurs
        p1 = self.bot.leaderboard_mgr.get_player(ctx.author.id)
        p2 = self.bot.leaderboard_mgr.get_player(adversaire.id)

        if (not p1 or p1.pr < montant or not p2 or p2.id < montant) and not (ctx.author.id in self.bot.config["EXCLUDED_IDS"] or adversaire.id in self.bot.config["EXCLUDED_IDS"]):
            return await ctx.send("Alors comme ça on est trop pauvre? bouuuuhhhh retente quand tu pourra assumer ta défaite")

        # Création du pari via le manager (renvoie un objet Pari)
        nouveau_pari = self.bot.bet_manager.create_bet(ctx.author.id, adversaire.id, objet, montant)

        # Envoi de la vue d'acceptation
        from cogs.views.pari_view import PariAcceptationView
        embed = discord.Embed(
            title="Un pari a été lancé !!!", 
            color=0xFF0000, 
            description=f"{adversaire.mention}, {ctx.author.display_name} te lance un défi !"
        )
        embed.add_field(name="Objet", value=nouveau_pari.objet)
        embed.add_field(name="Mise", value=f"{nouveau_pari.montant} PR")

        view = PariAcceptationView(self.bot, nouveau_pari)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="rendlargent")
    async def rendlargent(
        self, 
        ctx, 
        pari_id: int = commands.parameter(description="L'identifiant du pari à résoudre")
    ):
        """Déclenche la phase de résolution d'un pari spécifique."""
        
        # Récupération du pari par son ID unique
        pari = self.bot.bet_manager.get_bet_by_id(pari_id)
        
        if not pari:
            return await ctx.send(f"Le pari #{pari_id} n'existe pas ou a déjà été résolu.")

        if ctx.author.id != pari.lanceur_id and ctx.author.id != pari.adversaire_id:
            return await ctx.send("Tu n'es pas concerné par ce pari.")

        # Déterminer qui est le vainqueur auto-proclamé et qui est le perdant
        vainqueur = ctx.author
        perdant_id = pari.adversaire_id if ctx.author.id == pari.lanceur_id else pari.lanceur_id
        perdant = ctx.guild.get_member(perdant_id)

        if not perdant:
            return await ctx.send("Le perdant semble avoir quitté le serveur.")

        from cogs.views.pari_view import PariResolutionView
        embed = discord.Embed(
            title="Le pari prend fin", 
            color=0x3f8402, 
            description=f"{vainqueur.display_name} affirme avoir gagné le pari suivant : **{pari.objet}**.\n\n{perdant.mention}, es-tu d'accord avec ce résultat ?"
        )
        
        view = PariResolutionView(self.bot, pari, vainqueur, perdant)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="annuler_pari")
    @commands.has_role("Soldat.e")
    async def annuler_pari(
        self, 
        ctx, 
        id: int = commands.parameter(description="L'identifiant du pari à annuler")
    ):
        """annule un pari"""
        self.bot.bet_manager.remove_bet(id)
        await ctx.send("pari annulé")

    @commands.command(name="streak")
    async def streak(
        self, 
        ctx, 
        user: discord.Member = commands.parameter(default=None, description="Le membre dont on veut voir la streak (laisser vide pour soi-même)")
    ):
        """affiche la streak de l'auteur ou du membre ciblé"""
        if user == None:
            await ctx.send(f"Vous avez joué {self.bot.streak_mgr.get_user_streak(ctx.author.id)} jours")
        else:
            await ctx.send(f"{user.nick} a joué {self.bot.streak_mgr.get_user_streak(user.id)} jours")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Jeu des streaks"""
        if message.channel.id == self.bot.config["STREAK_CHANNEL_ID"]:
            streak_updated = self.bot.streak_mgr.trigger_streak(message.author.id)
            if streak_updated:
                current_streak = self.bot.streak_mgr.get_user_streak(message.author.id)
                
                for jours, pr in self.bot.config["STREAK_DAY_PR"]: 
                    if current_streak == jours:
                        await message.channel.send(f"Pour avoir joué {jours} jours, {message.author.mention} gagne {pr} pr!")
                        await self.ajouter_pr(message.author, pr)
                        break 

async def setup(bot):
    await bot.add_cog(Classement(bot))