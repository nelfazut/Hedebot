import discord
from discord.ext import commands
import csv
from creation_image import *
import json
import unidecode
import asyncio
from discord.ui import Button, View
import time
import math
from io import BytesIO
from utils.helpers import get_user_color, decouper_liste
class Classement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ajouter_pr(self, user: discord.Member, nombre: int):
        if user.id == 444044042716577803 or user.id == 476812132852432936:
            return
        
        color = get_user_color(user.roles)

        self.bot.leaderboard_mgr.add_pr(user.id, user.nick, color, nombre)

        await self.update_classement()


    @commands.command(name="pr")
    @commands.has_role("Soldat.e")
    async def pr(self, ctx, user : discord.Member , nombre : int):
        await self.ajouter_pr(user, nombre)

    async def update_classement(self):
        """Met à jour les images du classement sur discord en se basant sur l'état en mémoire"""
        
        channel_id = self.bot.leaderboard_mgr.get_ui_channel()
        
        if not channel_id:
            channel_id = 620004242966577208
            
        channel = self.bot.get_channel(channel_id)
        if not channel:
            return # Sécurité au cas où le bot n'a pas accès au salon

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

        self.bot.leaderboard_mgr.save_ui_state(channel_id, new_messages)
    @commands.command(name="nomclassement")
    async def nomclassement(self, ctx, *, phrase):
        """Change le nom de l'utilisateur au classement"""
        self.fnomclassement(ctx.author, phrase)

    @commands.command(name="fnomclassement")
    @commands.has_role("Soldat.e")
    async def fnomclassement(self, ctx, user, *, phrase):
        """force le changement de nom de l'utilisateur ciblé au classement"""
        if ("\n" in phrase or ";" in phrase):
            ctx.send("nom invalide")
            return
        if self.bot.leaderboard_mgr.rename_player(user.id, phrase):
            self.update_classement()
            return
        if user.id == ctx.author.id:
            ctx.send("Vous n'appartenez pas au classement")
        else:
            ctx.send("Il n'appartient pas au classement...")

    @commands.command(name="remove")
    async def remove(self, ctx, user):
        """retire un utilisateur du classement"""
        self.bot.leaderboard_mgr.remove_player(user.id)
        self.update_classement


    @commands.command(name="pari")
    async def pari(self,ctx, user = None, number = None, *, objet = None):
        with open("paris.json", "r", encoding="utf8") as f:
            liste_paris = json.load(f)
        with open("classement.csv", "r", newline="") as f:
            classement = list(csv.reader(f, quotechar = "\n", delimiter=";"))
        pr_membres = []
        if not user is None:
            for k in classement:
                if k[3] == str(ctx.author.id) or k[3] == user[2:-1]:
                    pr_membres.append(k[2])
        if user is None and number is None and objet is None:
            embed = discord.Embed(title=f"Paris actifs:", colour = 0x3f8402)
            for pari in liste_paris[str(ctx.author.id)]:
                embed.add_field(name = pari[0], value=f"adversaire : <@{pari[1]}>, objet : {pari[2]}, {pari[3]}")
            await ctx.send(embed=embed)
        elif int(pr_membres[0]) >= int(number) and int(pr_membres[1]) >= int(number):
            
            embed = discord.Embed(title="Un pari a été lancé!!!", colour = 0xFF0000, description= f"{user}, {ctx.author.nick} vous lance le pari suivant!")
            embed.add_field(name= objet, value = f"pour {number} PR!")
            view = View()
            yes = Button(emoji="✔️")
            no = Button(emoji="❌")
            view.add_item(yes)
            view.add_item(no)
            async def yes_callback(interaction):
                if interaction.user.id == int(user[2:-1]):
                    print(liste_paris)
                    liste_paris["IDs"] += 1
                    if str(ctx.author.id) in liste_paris:
                        liste_paris[str(ctx.author.id)].append([liste_paris["IDs"], user[2:-1], objet, "lancé par vous", number])
                    else:
                        liste_paris[str(ctx.author.id)] = [[liste_paris["IDs"], user[2:-1], objet, "lancé par vous", number]]
                    if user[2:-1] in liste_paris:
                        liste_paris[user[2:-1]].append([liste_paris["IDs"], str(ctx.author.id), objet, "lancé par lui meme", number])
                    else:
                        liste_paris[user[2:-1]] = [[liste_paris["IDs"], str(ctx.author.id), objet, "lancé par lui meme", number]]
                    with open("paris.json", "w", encoding="utf8") as f:
                        json.dump(liste_paris, f)
                    await ctx.send("pari accepté.")
                    await interaction.response.edit_message(view = View())
                    await self.pr(ctx, f"<@{ctx.author.id}>", str(-int(number)))
                    asyncio.sleep(1)
                    self.pr(ctx, user, str(0-int(number)))

                    liste = {
                        "userid" : [["id", "adversaire", "objet", "lanceur", "pr"]]
                    }
                else: 
                    await interaction.response.send_message("Hey c'est pas a toi de dire oui ou non!", ephemeral=True)
            async def no_callback(interaction):
                if interaction.user.id == int(user[2:-1]):
                    await interaction.response.send_message("pari refusé.")
                else:
                    await interaction.response.send_message("Hey c'est pas a toi de dire oui ou non!", ephemeral=True)
            yes.callback = yes_callback
            no.callback = no_callback
            await ctx.send(embed = embed, view = view)

        else: 
            await ctx.send("le pari n'a pas pu se faire. Soit car toutes les informations n'ont pas été remplies, soit par ce qu'un(e) des concerné(e)s n'a pas sufisemment de PR.")
    @commands.command(name="rendlargent")
    async def aboule(self, ctx, id):
        with open("paris.json", "r", encoding="utf8") as f:
            dico_paris = json.load(f)
        for i in dico_paris[str(ctx.author.id)]:
            if i[0] == int(id):
                pari = i
        embed = discord.Embed(colour = 0x3f8402, title="Le pari prend fin", description= f"{ctx.author.nick} affirme avoir gagné le pari suivant : {pari[2]} {pari[3]}. Êtes-vous d'accord avec ce résultat?")
        view = View()
        yes = Button(emoji="✔️")
        no = Button(emoji="❌")
        valide = False
        async def yes_callback(interaction):
            nonlocal embed
            soldat = discord.utils.get(ctx.guild.roles, name="Soldat.e")
            if interaction.user.id == int(i[1]) or soldat in interaction.user.roles:
                await interaction.response.edit_message(embed=embed, view = View())
                await ctx.send(f"MOUAHAHAHA <@{i[1]}> tu as HONTEUSEMENT perdu le pari. Te voilà forcé a donner {i[4]} PR a ton adversaire. C'est triste" )
                await ctx.send("😭😭😭")
                for k in dico_paris[str(ctx.author.id)]:
                    if k[0] == int(id):
                        dico_paris[str(ctx.author.id)].remove(k)
                for k in dico_paris[str(i[1])]:
                    if k[0] == int(id):
                        dico_paris[str(i[1])].remove(k)
                with open("paris.json", "w", encoding = "utf8") as f:
                    json.dump(dico_paris, f)
                await self.pr(ctx, f"<@{ctx.author.id}>", 2*i[4])

            else:
                await interaction.response.send_message("nan mais oh depuis quand c'est toi qui choisis?", ephemeral = True)
        async def no_callback(interaction):
            if interaction.user == ctx.author:
                await interaction.response.send_message("ET c'est un NON! VOILA UN RETOURNEMENT DE SITUATUION ABRACADABRANT!!!!!!!!!! (plus serieusemet, si il y a un conflit, demandez a un soldat de le résoudre.)")
            else:
                await interaction.response.send_message("nan mais oh depuis quand c'est toi qui choisis?", ephemeral = True)
        yes.callback = yes_callback
        no.callback = no_caclassement.py
    @commands.command(name="streak")
    async def streak(self, ctx, user : discord.Member = None):
        if user == None:
            await ctx.send(f"Vous avez joué {self.bot.leaderboard_mgr.get_user_streak(ctx.author.id)} jours")
        else:
            await ctx.send(f"{user.nick} a joué {self.bot.leaderboard_mgr.get_user_streak(user.id)} jours")
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 1206703716481245255:
            streak_updated = self.bot.leaderboard_mgr.trigger_streak(message.author.id)
            if streak_updated:
                streak_pr = [(30,5), (50,15), (100,50), (200,115), (365,220), (500,320), (1000,1100), (2000,2300)]
                current_streak = self.bot.leaderboard_mgr.get_user_streak(message.author.id)
                
                for jours, pr in streak_pr: 
                    if current_streak == jours:
                        await self.ajouter_pr(message.author, pr)
                        break 

async def setup(bot):
    await bot.add_cog(Classement(bot))
    