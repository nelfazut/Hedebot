from discord.ext import commands
from discord import app_commands
import asyncio
import json
import discord
class reactionrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def anwser_to_data(self, answer : list):
        emojis = answer[1].split(" ")
        roles = answer[2].split(" ")
        roles = [int(k) for k in roles]
        c_id = int(answer[3][2:-1])
        channel =  self.bot.get_channel(c_id)
        return emojis, roles, channel

    @commands.command(name="reactionrole")
    @commands.has_role('Soldat.e')
    async def self_role(self, ctx, envoyer = None):
        await ctx.send("Répondez a ces questions dans les deux minutes qui suivent")
        if envoyer is None:
            questions = ["ID du message: ", "Emoji(s): ", "ID du (des) rôle(s)", "Salon: "]
        else:
            questions = ["Message a envoyer: ", "Emoji(s): ", "ID du (des) rôle(s)", "Salon: "]
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

        emojis, roles, channel = self.anwser_to_data(answers)
        if len(emojis) != len(roles):
            await ctx.send("Vous devez spécifier autant de roles que d'émojios.")
        if envoyer is None:
            msg = await channel.fetch_message(int(answers[0]))
        else:
            msg = await channel.send(answers[0])
        self.bot.reaction_mgr.add_reaction(msg.id, emojis, roles)
        for emoji in emojis:
            await msg.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Ajoute le role assoccié si il existe quand on ajoute une réaction a un message"""
        msg_id = payload.message_id
        infos = self.bot.reaction_mgr.get_message_info(msg_id)

        if payload.member.bot:
            return
        
        if not infos is None:
            emojis = infos["emojis"]
            roles = infos["roles"]

            guild = self.bot.get_guild(payload.guild_id)

            for i in range(len(emojis)):
                choosed_emoji = str(payload.emoji)
                if choosed_emoji == emojis[i]:
                    selected_role = roles[i]
                    role = self.bot.get_guild(payload.guild_id).get_role(selected_role)
                    await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        msg_id = payload.message_id
        infos = self.bot.reaction_mgr.get_message_info(msg_id)

        if infos is not None:
            emojis = infos["emojis"]
            roles = infos["roles"]

            guild = self.bot.get_guild(payload.guild_id)

            for i in range(len(emojis)):
                choosed_emoji = str(payload.emoji)
                if choosed_emoji == emojis[i]:
                    selected_role = roles[i]
                    role = self.bot.get_guild(payload.guild_id).get_role(selected_role)

                    await guild.get_member(payload.user_id).remove_roles(role)

async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(reactionrole(bot=bot))