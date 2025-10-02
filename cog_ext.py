from discord import app_commands
from discord.ext import commands
import asyncio
import discord
import random
import time
import json
import numpy as np
import re
from module1 import *
from random import choice
# all cogs inherit from this base class
class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # adding a bot attribute for easier access
    srlist = []
    # adding a command to the cog
    @commands.command(name="purge")
    @commands.has_role('Soldat.e')
    async def purge(self, ctx, amount):
        amount = int(amount)
        if amount > 1000:
            await ctx.send(f"trop de message selectionnés ({amount}/1000)")
        else:
            count_members = {}
            messages = [m async for m in ctx.channel.history(limit=amount)]#await ctx.channel.history(limit=amount).flatten()
            for message in messages:
                if str(message.author) in count_members:
                    count_members[str(message.author)] += 1 
                else:
                    count_members[str(message.author)] = 1 
            new_string = []
            messages_deleted = 0 
            for author, message_deleted in list(count_members.items()):
                new_string.append(f'**{author}**: {message_deleted}')
                messages_deleted += message_deleted
            final_string ='\n'.join(new_string)
            await ctx.channel.purge(limit=amount+1 )
            msg = await ctx.send(f'{messages_deleted} message are removed \n\n{final_string}')
            await asyncio.sleep(2)
            await msg.delete()
    
    # adding a slash command to the cog (make sure to sync this!)
    @commands.command(name="rappel")
    async def remind(self, ctx):
        await ctx.send("Répondez a ces questions dans les cinq minutes qui suivent")

        questions = ["Message", "Temps"]
        answers = []

        def check(user):
            return user.author == ctx.author and user.channel == ctx.channel
        
        for question in questions:
            await ctx.send(question)

            try:
                msg = await self.bot.wait_for('message', timeout=300.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Soyez plus rapide la prochaine fois 😉")
                return
            else:
                answers.append(msg.content)
        if not answers[1].find('s') == -1:
            var=int(answers[1].find('s'))
            await ctx.channel.send('Quête acceptée!')
            aled = await asyncio.sleep(int(answers[1][0:var]))
            await ctx.channel.send(answers[0]+' <@'+str(ctx.author.id)+'>')
        elif not answers[1].find('m') == -1:
            var=int(answers[1].find('m'))
            await ctx.channel.send('Quête acceptée!')
            aled = await asyncio.sleep(int(float(answers[1][0:var])*60))
            await ctx.channel.send(answers[0]+' <@'+str(ctx.author.id)+'>')
        elif not answers[1].find('h') == -1:
            var=int(answers[1].find('h'))
            await ctx.channel.send('Quête acceptée!')
            aled = await asyncio.sleep(int(float(answers[1][0:var])*3600))
            await ctx.channel.send(answers[0]+' <@'+str(ctx.author.id)+'>')
        elif not answers[1].find('j') == -1:
            var=int(answers[1].find('j'))
            await ctx.channel.send('Quête acceptée!')
            aled = await asyncio.sleep(int(float(answers[1][0:var])*86400))
            await ctx.channel.send(answers[0]+' <@'+str(ctx.author.id)+'>')
        else:
            await ctx.channel.send("érreur dans l'écriture du temps (ne sont acceptés que les durées données en décimales de secondes(s), de minutes(m), d'heures(h), et de jours(j)) ex : 30s")

    # adding an event listener to the cog
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.text_channels, name="canal-de-discussion")
        embed = discord.Embed(title="**Bienvenue dans la guilde!**", description= "Bienvenue dans la Guilde, jeune Adorateur.ice ! "
    "Passe voir le maître de compétences dans le <#585151108465426442> et gagne des points de réputation grâce à ton <#627854418473123871>."
    "Les mises à jours apparaissent dans les <#589082158174306330>."
    "Attention cependant à respecter la sacro-sainte Charte placardée dans les <#582101378474835978>."
    "Tu peux également visiter ton QG, rendez-vous à l'<#903739233079025705>!", color=0x3f8402)
        embed.set_thumbnail(url = "https://media.discordapp.net/attachments/582101378474835978/990245258753368084/Embleme_pixel_fucked__TEXTE_SD.png")
        await channel.send(f'<@{member.id}>', embed = embed)
        role = discord.utils.get(member.guild.roles, id=int(585146028106448906))
        await member.add_roles(role)
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = discord.utils.get(member.guild.text_channels, name="canal-de-discussion")
        embed = discord.Embed(title="**Au revoir**", description= f"**{member.name}** est parti.e", color=0x3f8402)
        embed.set_thumbnail(url = "https://media.discordapp.net/attachments/582101378474835978/990245258753368084/Embleme_pixel_fucked__TEXTE_SD.png")
        await channel.send(f'<@{member.id}>', embed = embed)

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")
    @commands.command(name="reactionrole")
    @commands.has_role('Soldat.e')
    async def self_role(self, ctx, envoyer = None):
        await ctx.send("Répondez a ces questions dans les deux minutes qui suivent")
        if envoyer is None:
            questions = ["ID du message: ", "Emojis: ", "Id du rôle", "Salon: "]
        else:
            questions = ["Message a envoyer: ", "Emojis: ", "ID du rôle", "Salon: "]
        answers = []

        def check(user):
            return user.author == ctx.author and user.channel == ctx.channel
        
        for question in questions:
            await ctx.send(question)

            try:
                msg = await self.bot.wait_for('message', timeout=120.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Soyez plus rapide la prochaine fois :wink:")
                return
            else:
                answers.append(msg.content)

        emojis = answers[1].split(" ")
        roles = answers[2].split(";")
        roles = [int(k) for k in roles]
        c_id = int(answers[3][2:-1])
        channel =  self.bot.get_channel(c_id)
        if envoyer is None:
            msg = await channel.fetch_message(int(answers[0]))
        else:
            msg = await channel.send(answers[0])
        with open("selfrole.json", "r") as f:
            self_roles = json.load(f)
        try:
            self_roles[str(msg.id)]
        except KeyError:
            self_roles[str(msg.id)] = {}
            self_roles[str(msg.id)]["emojis"] = emojis
            self_roles[str(msg.id)]["roles"] = roles
        else: 
            self_roles[str(msg.id)]["emojis"] += emojis
            self_roles[str(msg.id)]["roles"] += roles

        with open("selfrole.json", "w") as f:
            json.dump(self_roles, f)

        for emoji in emojis:
            await msg.add_reaction(emoji)
    @commands.command(name="activator")
    async def activator(self, ctx):
        self.Hedera = ctx
    @commands.command(name = 'aled')
    async def aled(self, ctx):
        if str(ctx.channel.type) == "private":
            def check(user):
                return user.author == ctx.author and user.channel == ctx.channel
            await ctx.channel.send("Envoie le message que tu shouaite voir apparaitre")
            try:
                msg = await self.bot.wait_for('message', timeout=120.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Soyez plus rapide la prochaine fois :wink:")
                return
            embed = discord.Embed(title="un membre a besoin d'aide!", description=msg.content, color=0x3f8402)
            await self.Hedera.channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        print("reel")
        msg_id = payload.message_id

        with open("selfrole.json", "r") as f:
            self_roles = json.load(f)

        if payload.member.bot:
            return
        
        if str(msg_id) in self_roles:
            print("réel²")
            emojis = []
            roles = []

            for emoji in self_roles[str(msg_id)]['emojis']:
                emojis.append(emoji)

            for role in self_roles[str(msg_id)]['roles']:
                roles.append(role)
            
            guild = self.bot.get_guild(payload.guild_id)

            for i in range(len(emojis)):
                choosed_emoji = str(payload.emoji)
                if choosed_emoji == emojis[i]:
                    selected_role = roles[i]
                    print(selected_role)
                    role = discord.utils.get(guild.roles, id=selected_role)

                    await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        msg_id = payload.message_id

        with open("selfrole.json", "r") as f:
            self_roles = json.load(f)
        
        if str(msg_id) in self_roles:
            emojis = []
            roles = []

            for emoji in self_roles[str(msg_id)]['emojis']:
                emojis.append(
                    emoji)

            for role in self_roles[str(msg_id)]['roles']:
                roles.append(role)
            
            guild = self.bot.get_guild(payload.guild_id)

            for i in range(len(emojis)):
                choosed_emoji = str(payload.emoji)
                if choosed_emoji == emojis[i]:
                    selected_role = roles[i]

                    role = discord.utils.get(guild.roles, id=selected_role)

                    member = await(guild.fetch_member(payload.user_id))
                    if member is not None:
                        await member.remove_roles(role)
    @commands.command(name = "parle")
    @commands.has_role('Soldat.e')
    async def parler_cmd(self, ctx, salon, *, phrase):
        
        answers = []

        def check(user):
            return user.author == ctx.author and user.channel == ctx.channel
        
        await ctx.send('Salon :')

        try:
            msg = await self.bot.wait_for('message', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Soyez plus rapide la prochaine fois :wink:")
            return
        else:
            answers.append(msg.content)
        await ctx.send('message:')
        msg = await self.bot.wait_for('message', check=check)
        msg = msg.content
        if msg == 'stop':
            ctx.send("commande annulée")
        else:
            print(answers)
            channel = self.bot.get_channel(int(answers[0][2:-1]))
            print(channel)
            await channel.send(msg)

    srlist = []
    #s'occupe de nettoyer et garder l'essentiel (mettre en minuscule...ect)# balb-*- coding:utf-16 -*-
    def nettoyage(self, token:str) -> str:
        token = token.replace(" ", "")
        token = token.lower()
        token = token[1:]
        
        return token

    def analyse_l(self, commande:str):
        phrases = re.search("(?<=l\[).+(?=\])", commande)
        phrases = re.split("[,;]", phrases.group())

        nombre_fois = int(commande[:commande.find("l")])

        if nombre_fois < 1:
            return "Commande invalide, le nombre d'élément choisis est invalide"
        elif not phrases:
            return "Commande invalide, aucun élément n'est présent"
        
        choix = []
        for i in range(nombre_fois):
            choix.append(choice(phrases))
            
        return choix

    def analyse_u(self, commande:str):
        phrases = re.search("(?<=u\[).+(?=\])", commande)
        phrases = re.split("[,;]", phrases.group())

        nombre_fois = int(commande[:commande.find("u")])
        if nombre_fois > len(phrases):
            return "Commande invalide, le nombre d'élément choisis est supérieur au nombre de choix possible"
        elif nombre_fois < 1:
            return "Commande invalide, le nombre d'élément choisis est invalide"
        elif not phrases:
            return "Commande invalide, aucun élément n'est présent"
        
        choix = []
        for i in range(nombre_fois):
            index = randint(0, len(phrases)-1)
            choix.append(phrases[index])
            del phrases[index]

        return choix

    def appliquer_resultat_if(self, somme_modifiee, lancer_des_if, si, nombre):
        if nombre and si[2] == '+':
            lancer_des_if.append(nombre)
            somme_modifiee += nombre
            
        elif nombre and si[1] == '-':
            lancer_des_if.append(nombre)
            somme_modifiee -= nombre
            
        else:
            des = self.analyse_commande(si)

            lancer_des_if += des[1]
            somme_modifiee += des[0]

        return somme_modifiee, lancer_des_if
    feur = []
    def analyse_token_regex(self, token:str):
        somme = 0
        nombre_des = re.search("\d+(?=(d|e|s))", token)
        if nombre_des:
            nombre_des = int(nombre_des.group())
        else:
            nombre_des = 1

        nombre_face = int(re.search("(?<=(d|e))\d+", token).group())
        self.feur.append(int(nombre_face))
        #Explode et Dice
        lancer_de_des = np.random.randint(1, nombre_face+1, nombre_des, np.int16)
        
        if 'e' in token and nombre_face > 1:
            lancer_des_total = list(lancer_de_des)
            
            while nombre_face in lancer_de_des:
                lancer_de_des= np.random.randint(1, nombre_face+1, sum(lancer_de_des==nombre_face), np.int16)
                somme += sum(lancer_de_des)
                lancer_des_total += list(lancer_de_des)
                
            lancer_de_des = np.array(lancer_des_total)

        #Keep
        #Keep Lower

        nombre_a_garder = re.search("(?<=k)\d+", token)
        nombre_minimum_a_garder = re.search("(?<=kl)\d+", token)

        if nombre_a_garder != None:
            nombre_a_garder = int(nombre_a_garder.group())

            lancer_de_des = sorted(lancer_de_des,reverse=True)
            lancer_de_des = lancer_de_des[:nombre_a_garder]

        elif nombre_minimum_a_garder != None:
            nombre_minimum_a_garder = int(nombre_minimum_a_garder.group())

            lancer_de_des = sorted(lancer_de_des)
            lancer_de_des = lancer_de_des[:nombre_minimum_a_garder]
            
        #Map
        action_map = re.search("(?<=m)\{.\d+", token)

        if action_map != None:
            lancer_de_des = np.array((lancer_de_des))
            
            action_map = action_map.group()
            dictionnaire_action = {"+":(lambda n:lancer_de_des+n),
                                "-":(lambda n:lancer_de_des-n),
                                "=":(lambda n:lancer_de_des==n),
                                "!":(lambda n:lancer_de_des!=n),
                                "<":(lambda n:lancer_de_des<n),
                                ">":(lambda n:lancer_de_des>n)}

            lancer_de_des = dictionnaire_action[action_map[1]](int(action_map[2:]))
        #If
        somme_modifiee = 0
        lancer_des_if = []
        
        if 'i' in token:
                
            condition = re.search("(?<=i\[)\W\d+(?=\])", token).group()
            operateur = condition[0]
            condition_nombre = int(condition[1:])

            si_vrai = '!0' + str(re.search("(?<=\]\[).+(?=\])", token).group())
            nombre_si_vrai = int(si_vrai[2:]) if si_vrai[3:].isdigit() else None

            si_faux = re.search("(?<=\]\{).+(?=\})", token)
            nombre_si_faux = None

            if si_faux:
                si_faux = '!0' + str(si_faux.group())
                nombre_si_faux = int(si_vrai[3:]) if si_vrai[3:].isdigit() else None

            if operateur in ("=","!",">","<"):
                lancer_de_des = np.array((lancer_de_des))
                
                dictionnaire_action = {"=":(lambda n:lancer_de_des==n),
                                "!":(lambda n:lancer_de_des!=n),
                                "<":(lambda n:lancer_de_des<n),
                                ">":(lambda n:lancer_de_des>n)}

                des_respecte_condition = dictionnaire_action[operateur].__call__(condition_nombre)
                
                for respecte in des_respecte_condition:
                    if respecte:
                        somme_modifiee, lancer_des_if = self.appliquer_resultat_if(
                            somme_modifiee, lancer_des_if, si_vrai, nombre=nombre_si_vrai)
                        
                    elif si_faux:
                        somme_modifiee, lancer_des_if = self.appliquer_resultat_if(
                            somme_modifiee, lancer_des_if, si_faux, nombre=nombre_si_faux)
        #Sort
        if "s" in token:
            lancer_de_des = sorted(lancer_de_des)
        
        return (sum(lancer_de_des)+somme_modifiee, list(lancer_de_des)+lancer_des_if)

    def trouver_operations_calcul(self, commande:str):
        return re.findall("(\-|\+)(?!.+\})", commande)

    def analyse_commande(self, commande:str):
        commande = commande.lower()
        commande = commande[2:]
        operation = False
        if re.search("(\-|\+)(?!.+\})", commande):
            commande = commande.replace(" ", "")
            
            tokens = re.split("(\-|\+)(?!.+\})", commande)

            for token in tokens[:]:
                if token in ('+','-'):
                    tokens.remove(token)
            
            operations = iter(self.trouver_operations_calcul(commande))
                
            somme = 0
            lancer_des = []

            for i,token in enumerate(tokens):
                
                if token.isdigit():
                    somme_resultat = int(token)
                    operation = True
                else:
                    somme_resultat,des = self.analyse_token_regex(token)
                    lancer_des += list(des)
                    
                if i > 0 :
                    try:
                        operation_actuel = next(operations)
                        somme = eval(str(somme)+operation_actuel+str(somme_resultat))
                        
                    except StopIteration:
                        somme = somme+somme_resultat
                        
                else:
                    somme += somme_resultat
            return (somme, lancer_des), operation
        
        elif commande == "pnj":
            return pnj_shadowrun()
            
        elif "l[" in commande:
            return self.analyse_l(commande)

        elif "u[" in commande:
            return self.analyse_u(commande)

        elif not commande.isdigit():
            commande = commande.replace(" ", "")
            return self.analyse_token_regex(commande), operation
                
    @commands.Cog.listener()
    async def on_message(self, message):
        self.feur = []
        if message.content.startswith("h!"):
            if message.content =="h!sr":
                if self.srlist.count(message.author) == 0:
                    self.srlist.append(message.author)
                    emoji = discord.utils.get(message.guild.emojis, name='Tenshirock2')
                    await message.add_reaction(emoji)
                    
                elif self.srlist.count(message.author) != 0:
                    self.srlist.remove(message.author)
                    emoji = discord.utils.get(message.guild.emojis, name='Tenshirock2')
                    await message.add_reaction(emoji)
            elif ("l[" in message.content or 'u[' in message.content or 'U[' in message.content or 'L[' in message.content) and message.content[0:2] == "h!":
                print("mort")
                problemes = str(self.analyse_commande(message.content)).replace("'","")
                problemes = problemes.replace("[", "")
                problemes = problemes.replace("]", "")
                await message.channel.send(f"```md\n#{problemes}```")
            elif message.content == 'h!pnj':
                print("mort2")
                await message.channel.send(f"```md\n# {self.analyse_commande(message.content)}```")

            elif "d" not in message.content and "D" not in message.content and "e" not in message.content and "E" not in message.content:
                print("mort3")
                await message.channel.send(f"```md\n#  {str(self.analyse_commande(message.content)[0][0])}\n{message.content[1:]}```")
            elif message.content[0:2] == 'h!':
                print("mort4")
                func = self.analyse_commande(message.content)
                if message.author in self.srlist and len(set(self.feur)) == 1 and self.feur[0] == 6 and func[1] == False:
                    nbr_6 = 0
                    nbr_reussites = 0
                    nbr_1 = 0
                    for des in func[0][1]:
                        if des == 6:
                            nbr_6 += 1
                            nbr_reussites +=1
                        elif des == 5:
                            nbr_reussites +=1
                        elif des == 1:
                            nbr_1 += 1
                    await message.channel.send(f"```md\n# nombre de réussites: {str(nbr_reussites)}\nNombre de 6: {nbr_6}\nNombre de 1: {nbr_1}```")
                    return
                await message.channel.send(f"```md\n# {str(func[0][0])}\n{message.content[2:]} ({str(func[0][1])[1:-1]})```")
        elif self.bot.user.mentioned_in(message) and message.author != self.bot.user and discord.utils.get(message.guild.roles, name="Soldat.e") in message.author.roles: 
            await message.channel.send("Que les témoins prennent acte!!")
        print(message.author.roles)
# usually you’d use cogs in extensions
# you would then define a global async function named 'setup', and it would take 'bot' as its only parameter
async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(ExampleCog(bot=bot))