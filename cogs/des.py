from discord import app_commands
from discord.ext import commands
import discord
from libs.diceio.src.run_cmd import run_cmd


class Des(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # adding a bot attribute for easier access
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith(self.bot.config["BOT_PREFIX"]):
            command = message.content.removeprefix(self.bot.config["BOT_PREFIX"])
            if command.split(maxsplit=1)[0] not in [command.name for command in self.bot.commands]:
                await message.channel.send(f"```md\n{run_cmd(command, message.author.id)}```")

async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(Des(bot=bot))