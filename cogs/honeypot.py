import discord
from discord.ext import commands, tasks
import random
class HoneyPot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot # adding a bot attribute for easier access
        self.honey_id = self.bot.config["HONEYPOT_CHANNEL"]
        self.nom_salons = honeypot_channels_explicites = [
            "pas-pour-ecrire",
            "ne-pas-ecrire",
            "ne-rien-ecrire",
            "ne-pas-parler",
            "ne-rien-dire",
            "ne-pas-poster",
            "ne-rien-poster",
            "ne-pas-envoyer",
            "ne-rien-envoyer",
            "ne-pas-taper",
            "ne-rien-taper",
            "ne-pas-commenter",
            "ne-rien-commenter",
            "ne-pas-interagir",
            "ne-rien-publier",
            "ne-pas-publier",
            "ne-rien-rediger",
            "ne-pas-rediger",
            "ne-pas-discuter",
            "ne-pas-tchatter",            
            "interdit-d-ecrire",
            "ecriture-interdite",
            "interdiction-d-ecrire",
            "interdit-de-parler",
            "parole-interdite",
            "interdiction-de-parler",
            "interdit-de-poster",
            "post-interdit",
            "interdiction-de-poster",
            "interdit-d-envoyer",
            "envoi-interdit",
            "interdit-de-commenter",
            "commentaire-interdit",
            "interdit-de-discuter",
            "discussion-interdite",
            "chat-interdit",
            "messages-interdits",
            "texte-interdit",
            "interdiction-absolue-d-ecrire",
            "strictement-interdit-d-ecrire",
            "lecture-seule",
            "uniquement-pour-lire",
            "juste-pour-lire",
            "lecture-uniquement",
            "que-pour-la-lecture",
            "lire-seulement",
            "salon-en-lecture-seule",
            "mode-lecture",
            "lecture-exclusivement",
            "espace-de-lecture",
            "regarder-sans-ecrire",
            "lire-sans-ecrire",
            "consultation-seulement",
            "consultation-uniquement",
            "lecture-autorisee-ecriture-interdite",
            "pas-de-messages",
            "aucun-message",
            "pas-de-texte",
            "aucun-texte",
            "pas-de-discussion",
            "aucune-discussion",
            "pas-de-commentaires",
            "aucun-commentaire",
            "pas-de-parole",
            "pas-de-chat",
            "pas-de-tchat",
            "pas-d-ecriture",
            "aucune-ecriture",
            "pas-d-envoi",
            "aucun-envoi-possible",
            "zero-message",
            "zero-texte",
            "zero-discussion",
            "aucune-saisie",
            "saisie-interdite",
            "silence",
            "silence-svp",
            "silence-obligatoire",
            "silence-requis",
            "salon-silencieux",
            "zone-silencieuse",
            "espace-silencieux",
            "muet",
            "salon-muet",
            "zone-muette",
            "rester-muet",
            "gardez-le-silence",
            "merci-de-garder-le-silence",
            "mode-silencieux",
            "merci-de-ne-pas-ecrire",
            "priere-de-ne-pas-ecrire",
            "ecriture-egale-ban",
            "ban-si-ecriture",
            "message-egale-bannissement",
            "ban-si-message",
            "ne-pas-ecrire-sous-peine-de-ban",
            "ecrire-provoque-un-ban",
            "exclusion-si-message",
            "ban-automatique-si-ecriture",
            "ne-pas-ecrire-ou-ban",
            "ecrire-ici-est-un-ban"
        ]
        self.change_channel_name.start()

    @tasks.loop(hours=5)
    async def change_channel_name(self):
        channel = self.bot.get_channel(self.honey_id)
        nouveau_nom = random.choice(self.nom_salons)
        if channel is not None:
            try:
                await channel.edit(name=nouveau_nom)
            except discord.Forbidden:
                print("❌ [Honeypot Cog] Erreur : Permission 'Gérer les salons' manquante.")
            except discord.HTTPException as e:
                print(f"❌ [Honeypot Cog] Erreur Discord : {e}")
        else:
            print(f"❌ [Honeypot Cog] Erreur : Salon introuvable.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.honey_id:
            await message.author.kick(reason="Message envoyé dans le slaon interdit")
    
    @change_channel_name.before_loop
    async def before_changer_nom_salon(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(HoneyPot(bot))