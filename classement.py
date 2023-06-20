import discord
from discord.ext import commands
import csv
from creation_image import *
import json
import unidecode
import asyncio
class Classement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="pr")
    @commands.has_role("Roster 1")
    async def pr(self, ctx, user, nombre):
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
                    print("a")
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
        
            



async def setup(bot):
    await bot.add_cog(Classement(bot))