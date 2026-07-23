from discord import app_commands
from discord.ext import commands
import discord
from random import *
import re
import numpy as np
from module1 import *


class des(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # adding a bot attribute for easier access
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
                problemes = str(self.analyse_commande(message.content)).replace("'","")
                problemes = problemes.replace("[", "")
                problemes = problemes.replace("]", "")
                await message.channel.send(f"```md\n#{problemes}```")
            elif message.content == 'h!pnj':
                await message.channel.send(f"```md\n# {self.analyse_commande(message.content)}```")

            elif "d" not in message.content and "D" not in message.content and "e" not in message.content and "E" not in message.content:
                await message.channel.send(f"```md\n#  {str(self.analyse_commande(message.content)[0][0])}\n{message.content[1:]}```")
            elif message.content[0:2] == 'h!':
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

async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(des(bot=bot))