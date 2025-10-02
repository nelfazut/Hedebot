from discord import app_commands
from discord.ext import commands
import asyncio
import discord
from module1 import *
# all cogs inherit from this base class
class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # adding a bot attribute for easier access
        self.demarrage = 0
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
    async def on_message(self, ctx):
        if not self.demarrage and str(ctx.channel.type) != "private":
            self.aled_salon = await ctx.guild.fetch_channel(1089639136866086923)
    
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
            await self.aled_salon.send(embed = embed)
    @commands.command(name = "parle")
    @commands.has_role('Soldat.e')
    async def parler_cmd(self, ctx):
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
# usually you’d use cogs in extensions
# you would then define a global async function named 'setup', and it would take 'bot' as its only parameter
async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(ExampleCog(bot=bot))