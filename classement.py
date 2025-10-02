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
class Classement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="pr")
    @commands.has_role("Soldat.e")
    async def pr(self, ctx, user, nombre):
        if user == "<@444044042716577803>" or user == "<@476812132852432936>":
            return
        user = discord.utils.get(ctx.guild.members, id = int(user[2:-1]))
        roles = [y.name.lower() for y in user.roles]

        with open("classement.csv", "r", newline = "") as classement:
            membres = list(csv.reader(classement, quotechar="\n", delimiter=";"))
        if user.id not in [int(element[3]) for element in membres]:
            pseudo = unidecode.unidecode(user.display_name)
            print(pseudo)
            if "roster 1" in roles:
                couleur = "#0077d3"
            elif "soldat.e" in roles:
                couleur = "#ff8ff6"
            elif "collaborateur.ice coalisé.e" in roles:
                couleur = "#d60e0e"
            elif "collaborateur.ice ordonné.e" in roles:
                couleur = "#1cb81f"
            else:
                couleur = "#ffb000"
            membres.append([pseudo, couleur, nombre, user.id])
        else:
            for i,k in enumerate(membres):
                if int(k[3]) == user.id:
                    if "roster 1" in roles:
                        membres[i][1] = "#0077d3"
                    elif "soldat.e" in roles:
                        membres[i][1] = "#ff8ff6"
                    elif "collaborateur.ice coalisé.e" in roles:
                        membres[i][1] = "#d60e0e"
                    elif "collaborateur.ice ordonné.e" in roles:
                        membres[i][1] = "#1cb81f"
                    else:
                        membres[i][1] = "#ffb000"
                    membres[i][2] = str(int(membres[i][2])+int(nombre))
        membres.sort(reverse = True, key = lambda x : int(x[2]))
        await asyncio.sleep(1)
        with open("classement.csv", "w", newline="") as classement:
            writer = csv.writer(classement, delimiter=";")
            writer.writerows(membres)
        await self.update(ctx)

    async def update(self, ctx):
        with open("classement.csv", "r", newline = "") as classement:
            membres = list(csv.reader(classement, quotechar="\n", delimiter=";"))
        with open("classement.json", "r", encoding = "utf8") as file:
            liste_json = json.load(file)
            channel = discord.utils.get(ctx.guild.channels, id = liste_json[0])
            id_messages = liste_json[1]
            messages = [await channel.fetch_message(k) for k in id_messages]
        for i in messages:
            await i.delete()
        liste_messages = []
        for i,k in enumerate(self.decouper_liste(membres, 12)):
            image = await generate_scoreboard(k,i)
            image.save("image.png")
            with open('image.png', 'rb') as f:
                image = discord.File(f)
            message = await channel.send(file=image)
            liste_messages.append(message.id)
            with open("classement.json", "w", encoding = "utf8") as f:
                json.dump([channel.id,liste_messages],f)


    def decouper_liste(self, liste, n):
        result = []
        for i in range(0, len(liste), n):
            result.append(liste[i:i+n])
        return result    
    @commands.command(name="nomclassement")
    async def nomblassement(self, ctx, *, phrase):
        with open("classement.csv", "r", newline = "") as f:
            membres = list(csv.reader(f, quotechar="\n", delimiter=";"))
        for i,k in enumerate(membres):
            if k[3] == str(ctx.author.id):
                membres[i][0] = phrase
        with open("classement.csv", "w", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerows(membres)
        with open("classement.json", "r", encoding = "utf8") as file:
            liste_json = json.load(file)
            channel = discord.utils.get(ctx.guild.channels, id = liste_json[0])
            id_messages = liste_json[1]
            messages = [await channel.fetch_message(k) for k in id_messages]
        for i in messages:
            await i.delete()
        liste_messages = []
        for i,k in enumerate(self.decouper_liste(membres, 12)):
            image = await generate_scoreboard(k,i)
            image.save("image.png")
            with open('image.png', 'rb') as f:
                image = discord.File(f)
            message = await channel.send(file=image)
            liste_messages.append(message.id)
            with open("classement.json", "w", encoding = "utf8") as f:
                json.dump([channel.id,liste_messages],f)
    @commands.command(name="remove")
    async def remove(self, ctx, ping):
        with open("classement.csv", "r", newline="") as f:
            membres = list(csv.reader(f, quotechar="\n", delimiter=";"))
        for i,k in enumerate(membres):
            if k[3] == ping[2:-1]:
                membres.pop(i)
        with open("classement.csv", "w", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerows(membres)
        await self.update(ctx)
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
        no.callback = no_callback
        view.add_item(yes)
        view.add_item(no)
        await ctx.send(f"<@{i[1]}>",embed = embed, view = view)
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if str(ctx.channel.id) == "1206703716481245255":
            jouractuel = int((time.time()+7200)/86400)

            with open("streaks.json", "r", encoding="utf8") as f:
                streaks = json.load(f)
            streaksavant = streaks.copy()
            if (str(ctx.author.id) in streaks):
                if streaks[(str(ctx.author.id))][0] == jouractuel-1:
                    streaks[(str(ctx.author.id))][0] = jouractuel
                    streaks[(str(ctx.author.id))][1] += 1
                    if streaks[str(ctx.author.id)][1] in [i[0] for i in [[30,5],[50,15],[100,50],[200,115], [365,220], [500, 320]]]:
                        etape = [i for i in [[30,5],[50,15],[100,50],[200,115], [365,220], [500, 320]] if i[0] == streaks[str(ctx.author.id)][1]][0]
                        await ctx.channel.send(f"<@{ctx.author.id}>, pour avoir joué {etape[0]} jours, voici {etape[1]} PRs, fais en bon usage!")
                        await self.pr(ctx, f"<@{ctx.author.id}>", etape[1])
                elif streaks[(str(ctx.author.id))][0] != jouractuel:
                    streaks[(str(ctx.author.id))][0] = jouractuel
                    streaks[(str(ctx.author.id))][1] = 1 
            else:
                streaks[str(ctx.author.id)] = [jouractuel, 1]
            with open("streaks.json", "w", encoding= "utf8") as f:
                json.dump(streaks, f)
    @commands.command(name="streak")
    async def streak(self, ctx):
        with open("streaks.json", "r", encoding="utf8") as f:
            streaks = json.load(f)
        if str(ctx.author.id) in streaks:
            await ctx.send(f" vous avez joué pendant {streaks[str(ctx.author.id)][1]} jours consecutifs")
        else:
            await ctx.send("vous n'avez pas encore participé ou perdu votre streak, triste...")
async def setup(bot):
    await bot.add_cog(Classement(bot))
