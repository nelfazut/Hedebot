from discord.ext import commands
from discord import app_commands
import asyncio
import json
import discord

class reactionrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def anwser_to_data(self, answer: list):
        emojis = answer[1].split(" ")
        roles = answer[2].split(" ")
        roles = [int(k) for k in roles]
        c_id = int(answer[3][2:-1])
        channel = self.bot.get_channel(c_id)
        return emojis, roles, channel

    @commands.command(name="reactionrole")
    @commands.has_role('Soldat.e')
    async def self_role(
        self, 
        ctx, 
        envoyer: str = commands.parameter(
            default=None, 
            description="Laissez vide pour utiliser un message existant, ou tapez n'importe quoi pour créer un nouveau message"
        )
    ):
        """Configure un système pour donner des rôles via des réactions"""
        await ctx.send("Répondez à ces questions dans les deux minutes qui suivent")
        
        if envoyer is None:
            questions = ["ID du message: ", "Emoji(s): ", "ID du (des) rôle(s): ", "Salon: "]
        else:
            questions = ["Message à envoyer: ", "Emoji(s): ", "ID du (des) rôle(s): ", "Salon: "]
            
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
            return await ctx.send("Vous devez spécifier autant de rôles que d'émojis.")
            
        if envoyer is None:
            msg = await channel.fetch_message(int(answers[0]))
        else:
            msg = await channel.send(answers[0])
            
        self.bot.reaction_mgr.add_reaction(msg.id, emojis, roles)
        
        for emoji in emojis:
            await msg.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Ajoute le rôle associé s'il existe quand on ajoute une réaction à un message"""
        msg_id = payload.message_id
        infos = self.bot.reaction_mgr.get_message_info(msg_id)

        if payload.member.bot:
            return
        
        if infos is not None:
            emojis = infos["emojis"]
            roles = infos["roles"]

            guild = self.bot.get_guild(payload.guild_id)

            for i in range(len(emojis)):
                choosed_emoji = str(payload.emoji)
                if choosed_emoji == emojis[i]:
                    selected_role = roles[i]
                    role = guild.get_role(selected_role)

                    if role:
                        await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Retire le rôle associé quand on enlève sa réaction"""
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
                    role = guild.get_role(selected_role)
    
                    if role:
                        member = guild.get_member(payload.user_id)
                        if member:
                            await member.remove_roles(role)

async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(reactionrole(bot=bot))