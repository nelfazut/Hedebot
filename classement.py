import asyncio
import csv
import discord
import json
import math
import unidecode
import time

from creation_image import generate_scoreboard
from datetime import date, timedelta
from discord.ext import commands
from discord.ui import Button, View
from user import *
from zoneinfo import ZoneInfo

# Admins are banned from the ranking system
admin_ids = [
    444044042716577803,
    476812132852432936,
]


class Classement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def role_color(user: discord.Member) -> str:
        """
        Returns the hex value of the color related to the role
        using hardcoded ids of the Hedera roles

        Args:
            userid: int
        Returns:
            str: the color related to the role id
        """
        roles_id = [u.name for u in user.roles]
        special_roles = [
            ("roster 1", "#0077d3"),
            ("soldat.e", "#ff8ff6"),
            ("collaborateur.ice coalisé.e", "#d60e0e"),
            ("collaborateur.ice ordonné.e", "#1cb81f"),
        ]

        for sp_role, sp_color in special_roles:
            if sp_role in roles_id:
                return sp_color

        return "#ffb000"  # couleur jaune Empire par défaut si pas de rôle spécial

    @commands.command(name="pr")
    @commands.has_role("Soldat.e")
    async def pr(
        self, ctx: discord.ext.commands.Context, user: discord.Member, number: int
    ):
        """This method is only meant to be used from Discord. It checks if everything is alright
        in the command for its execution then adds a certain number of points to the ranking of the pinged user
        Args:
            user: discord.Member
            number: int
        """
        if user == None:
            ctx.send("l'utilisateur n'est pas présent sur le serveur")
        else:
            user = get_user(user.id)
            user.total_pr += number
            update_users([user])
            await self.update_leaderboard(ctx.guild)
            await ctx.message.add_reaction("👍")

    async def update_leaderboard(self, guild):
        """This option updates the ranking display in the dedicated discord channel"""
        users = [user if user.discord_id not admin_ids for user in get_all()]

        with open(
            "classement.json", "r", encoding="utf8"
        ) as file:  # Loads the json containing previously sent messages [guild_id[message1_id,message2_id]] A passer en dict
            liste_json = json.load(file)
        # At first we delete the messages
        channel = guild.get_channel(liste_json[0])
        id_messages = liste_json[1]
        for i in id_messages:
            await (await channel.fetch_message(i)).delete()

        # Then we send new messages
        liste_messages = []
        subsets = [users[i : i + n] for i in range(0, len(users), 12)]
        for i, k in enumerate(subsets):
            # We cut the list so the image isn't too large for a good display in a discord channel
            image = await generate_scoreboard(k, i)
            image.save("image.png")
            with open("image.png", "rb") as f:
                image = discord.File(f)
            message = await channel.send(file=image)
            liste_messages.append(message.id)

    # ________________________________________________
    @commands.command(name="nomclassement")
    async def edit_nick(self, ctx, *, new_nick):
        user_id = ctx.author.id
        user = get_user(user_id)
        user.display_name = new_nick
        update_users([user])
        self.update_leaderboard(ctx.guild)

    @commands.command(name="remove")
    async def remove(self, ctx: discord.ext.commands.Context, user: discord.Member):
        user = get_user(user.id)
        if user:
            delete_users([user])
        else:
            await ctx.send("Cet utilisateur n'est pas dans le classement.")
        self.update_leaderboard(ctx.guild)

    @commands.command(name="pari")
    async def pari(self, user=None, number=None, *, objet=None):
        ctx = self.context
        with open("paris.json", "r", encoding="utf8") as f:
            liste_paris = json.load(f)
        with open("classement.csv", "r", newline="") as f:
            classement = list(csv.reader(f, quotechar="\n", delimiter=";"))
        pr_membres = []
        if not user is None:
            for k in classement:
                if k[3] == str(ctx.author.id) or k[3] == user[2:-1]:
                    pr_membres.append(k[2])
        if user is None and number is None and objet is None:
            embed = discord.Embed(title=f"Paris actifs:", colour=0x3F8402)
            for pari in liste_paris[str(ctx.author.id)]:
                embed.add_field(
                    name=pari[0],
                    value=f"adversaire : <@{pari[1]}>, objet : {pari[2]}, {pari[3]}",
                )
            await ctx.send(embed=embed)
        elif int(pr_membres[0]) >= int(number) and int(pr_membres[1]) >= int(number):
            embed = discord.Embed(
                title="Un pari a été lancé!!!",
                colour=0xFF0000,
                description=f"{user}, {ctx.author.nick} vous lance le pari suivant!",
            )
            embed.add_field(name=objet, value=f"pour {number} PR!")
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
                        liste_paris[str(ctx.author.id)].append(
                            [
                                liste_paris["IDs"],
                                user[2:-1],
                                objet,
                                "lancé par vous",
                                number,
                            ]
                        )
                    else:
                        liste_paris[str(ctx.author.id)] = [
                            [
                                liste_paris["IDs"],
                                user[2:-1],
                                objet,
                                "lancé par vous",
                                number,
                            ]
                        ]
                    if user[2:-1] in liste_paris:
                        liste_paris[user[2:-1]].append(
                            [
                                liste_paris["IDs"],
                                str(ctx.author.id),
                                objet,
                                "lancé par lui meme",
                                number,
                            ]
                        )
                    else:
                        liste_paris[user[2:-1]] = [
                            [
                                liste_paris["IDs"],
                                str(ctx.author.id),
                                objet,
                                "lancé par lui meme",
                                number,
                            ]
                        ]
                    with open("paris.json", "w", encoding="utf8") as f:
                        json.dump(liste_paris, f)
                    await ctx.send("pari accepté.")
                    await interaction.response.edit_message(view=View())
                    await self.pr(ctx, ctx.author, str(-int(number)))
                    asyncio.sleep(1)
                    self.pr(ctx, user, str(0 - int(number)))

                    liste = {"userid": [["id", "adversaire", "objet", "lanceur", "pr"]]}
                else:
                    await interaction.response.send_message(
                        "Hey c'est pas a toi de dire oui ou non!", ephemeral=True
                    )

            async def no_callback(interaction):
                if interaction.user.id == int(user[2:-1]):
                    await interaction.response.send_message("pari refusé.")
                else:
                    await interaction.response.send_message(
                        "Hey c'est pas a toi de dire oui ou non!", ephemeral=True
                    )

            yes.callback = yes_callback
            no.callback = no_callback
            await ctx.send(embed=embed, view=view)

        else:
            await ctx.send(
                "le pari n'a pas pu se faire. Soit car toutes les informations n'ont pas été remplies, soit par ce qu'un(e) des concerné(e)s n'a pas sufisemment de PR."
            )

    @commands.command(name="rendlargent")
    async def aboule(self, ctx, id):
        with open("paris.json", "r", encoding="utf8") as f:
            dico_paris = json.load(f)
        for i in dico_paris[str(ctx.author.id)]:
            if i[0] == int(id):
                pari = i
        embed = discord.Embed(
            colour=0x3F8402,
            title="Le pari prend fin",
            description=f"{ctx.author.nick} affirme avoir gagné le pari suivant : {pari[2]} {pari[3]}. Êtes-vous d'accord avec ce résultat?",
        )
        view = View()
        yes = Button(emoji="✔️")
        no = Button(emoji="❌")
        valide = False

        async def yes_callback(interaction):
            nonlocal embed
            soldat = discord.utils.get(ctx.guild.roles, name="Soldat.e")
            if interaction.user.id == int(i[1]) or soldat in interaction.user.roles:
                await interaction.response.edit_message(embed=embed, view=View())
                await ctx.send(
                    f"MOUAHAHAHA <@{i[1]}> tu as HONTEUSEMENT perdu le pari. Te voilà forcé a donner {i[4]} PR a ton adversaire. C'est triste"
                )
                await ctx.send("😭😭😭")
                for k in dico_paris[str(ctx.author.id)]:
                    if k[0] == int(id):
                        dico_paris[str(ctx.author.id)].remove(k)
                for k in dico_paris[str(i[1])]:
                    if k[0] == int(id):
                        dico_paris[str(i[1])].remove(k)
                with open("paris.json", "w", encoding="utf8") as f:
                    json.dump(dico_paris, f)
                await self.pr(ctx, f"<@{ctx.author.id}>", 2 * i[4])

            else:
                await interaction.response.send_message(
                    "nan mais oh depuis quand c'est toi qui choisis?", ephemeral=True
                )

        async def no_callback(interaction):
            if interaction.user == ctx.author:
                await interaction.response.send_message(
                    "ET c'est un NON! VOILA UN RETOURNEMENT DE SITUATUION ABRACADABRANT!!!!!!!!!! (plus serieusemet, si il y a un conflit, demandez a un soldat de le résoudre.)"
                )
            else:
                await interaction.response.send_message(
                    "nan mais oh depuis quand c'est toi qui choisis?", ephemeral=True
                )

        yes.callback = yes_callback
        no.callback = no_callback
        view.add_item(yes)
        view.add_item(no)
        await ctx.send(f"<@{i[1]}>", embed=embed, view=view)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.channel.id == 1206703716481245255:  # ID du thread ":Hedera:"
            user_id = str(ctx.author.id)
            message = self.update_streak(user_id)
            if message != "":
                await ctx.channel.send(message)

    @staticmethod
    def update_streak(user: ctx.author) -> str:
        message = ""
        user_id = user.id
        td = date.today()
        streak_breakpoints = [
            (30, 5),
            (50, 15),
            (100, 50),
            (200, 115),
            (365, 220),
            (500, 320),
        ]

        user = get_user(user_id)
        if user is None:
            user = User(
                discord_id=user_id,
                display_name=user.nick,
                display_color=self.role_color(user),
            )
            add_users([user])

        if user.last_played == td - timedelta(days=1):
            user.streak += 1
        else:
            user.streak = 1
        user.last_played = td

        # On vérifie si le nouveau streak donne droit à un cadeau
        for days, points in streak_breakpoints:
            if user.streak == days:
                user.total_pr += points
                message = f"<@{user_id}>, pour avoir joué {jours} jours, voici {points} PRs, fais-en bon usage !"
                break
        # On sauvegarde tout ça
        update_users([user])
        return message

    @commands.command(name="streak")
    async def streak(self, ctx):
        user_id = ctx.author.id
        user = get_user(user_id)
        if user:
            last_played = user.last_played
            if last_played < date.today() - timedelta(days=1):
                user.streak = 0
                update_users([user])
                message = "Vous avez perdu votre streak, triste..."

            streak = user.streak
            if streak != 0:
                message = f" Vous avez joué pendant {streak} jours consécutifs."
        else:
            message = "Vous n'avez pas encore participé."

        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(Classement(bot))
