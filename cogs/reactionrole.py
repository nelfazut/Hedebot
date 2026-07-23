from discord.ext import commands
from discord import app_commands
import asyncio
import json
import discord
class reactionrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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

async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(reactionrole(bot=bot))