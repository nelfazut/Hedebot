import discord
from utils.helpers import finaliser_pari
class PariAcceptationView(discord.ui.View):
    def __init__(self, bot, pari): # On passe directement l'objet Pari !
        super().__init__(timeout=86400)
        self.bot = bot
        self.pari = pari

    @discord.ui.button(emoji="✔️", style=discord.ButtonStyle.success)
    async def btn_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sécurité : seul l'adversaire peut accepter
        if interaction.user.id != self.pari.adversaire_id:
            return await interaction.response.send_message("Ce n'est pas ton pari !", ephemeral=True)
        # On retire les boutons et on annonce l'acceptation
        await interaction.response.edit_message(view=None)
        await interaction.followup.send(f"Pari accepté par {interaction.user.mention} ! Les mises ont été déduites.")
        
        # 1. On modifie les scores en base de données (sans déclencher l'image tout de suite)
        # Note : On utilise self.lanceur et self.adversaire (les objets discord.Member passés dans le __init__)
        classement = self.bot.get_cog("Classement")

        await classement.ajouter_pr(self.pari.lanceur_id, -self.pari.montant)
        await classement.ajouter_pr(self.pari.adversaire_id, -self.pari.montant)

class PariResolutionView(discord.ui.View):
    def __init__(self, bot, pari, vainqueur: discord.Member, perdant: discord.Member):
        super().__init__(timeout=86400)
        self.bot = bot
        self.pari = pari
        self.vainqueur = vainqueur
        self.perdant = perdant

    @discord.ui.button(emoji="✔️", style=discord.ButtonStyle.success)
    async def btn_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Seul le perdant ou un rôle Soldat.e peut valider la défaite
        soldat_role = discord.utils.get(interaction.guild.roles, name="Soldat.e")
        if interaction.user.id != self.perdant.id and soldat_role not in interaction.user.roles:
            return await interaction.response.send_message("Ce n'est pas à toi de valider ça !", ephemeral=True)

        # 1. Appel de la logique centralisée dans utils.helpers
        # Cette fonction gère l'ajout des PR, l'update couleur et la suppression du pari
        await finaliser_pari(self.bot, self.pari.id, self.vainqueur)

        # 2. Mise à jour visuelle
        await interaction.response.edit_message(view=None)
        await interaction.followup.send(
            f"MOUAHAHAHA {self.perdant.mention} a perdu et cède {self.pari.montant} PR à {self.vainqueur.mention} ! 😭😭😭"
        )

    @discord.ui.button(emoji="❌", style=discord.ButtonStyle.danger)
    async def btn_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.vainqueur.id:
            await interaction.response.send_message("Tu ne peux pas contester ta propre victoire...", ephemeral=True)
            return
        if interaction.user == self.perdant:    
            await interaction.response.edit_message(view=None)
            await interaction.followup.send("Désaccord ! Le perdant conteste. Un.e Soldat.e est demandé.e pour trancher !") 
        else:
            await interaction.followup.send("Hop hop hop mêle toi de tes affaires toi!", ephemeral=True)