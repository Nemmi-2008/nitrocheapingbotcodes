import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ID du rôle autorisé
AUTHORIZED_ROLE_ID = 1381424857526440020

def has_authorized_role():
    def predicate(interaction: discord.Interaction):
        if interaction.guild is None:
            return False

        # Vérifier si l'utilisateur a le rôle autorisé
        authorized_role = discord.utils.get(interaction.user.roles, id=AUTHORIZED_ROLE_ID)
        return authorized_role is not None

    return app_commands.check(predicate)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    # Activité personnalisée
    activity = discord.Game(name="Best Shop !")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    # Synchroniser les commandes slash
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="hello", description="Dire bonjour")
@has_authorized_role()
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hello {interaction.user.mention} !')

@bot.tree.command(name="shop", description="Afficher la boutique Nitro")
@has_authorized_role()
async def shop(interaction: discord.Interaction):
    # Créer l'embed pour la boutique
    embed = discord.Embed(
        title="🛒 NITRO CHEAPING BEST - SHOP",
        description="Découvrez nos offres Nitro à prix imbattables !",
        color=0x5865f2,  # Couleur Discord bleu
        url="https://nitrocheapingbest.sellauth.com"
    )

    # Ajouter l'image du serveur comme thumbnail
    if interaction.guild and interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

    # Ajouter les prix
    embed.add_field(
        name="💎 Nitro Basic",
        value="**Prix: 1,70€**\n• Emoji personnalisés partout\n• Taille de fichier 50MB\n• Badges de profil",
        inline=True
    )

    embed.add_field(
        name="🚀 Nitro Boost",
        value="**Prix: 2,50€**\n• Tous les avantages Basic\n• Boost de serveur\n• Qualité vidéo HD",
        inline=True
    )

    # Ajouter un champ vide pour la mise en page
    embed.add_field(
        name="\u200b",
        value="\u200b",
        inline=False
    )

    # Ajouter le lien vers la boutique
    embed.add_field(
        name="🔗 Lien de la boutique",
        value="[**Accéder au shop**](https://nitrocheapingbest.sellauth.com)",
        inline=False
    )

    # Ajouter des informations supplémentaires
    embed.add_field(
        name="✅ Garanties",
        value="• Livraison instantanée\n• Support 24/7\n• Prix les plus bas du marché",
        inline=True
    )

    embed.add_field(
        name="💳 Paiements acceptés",
        value="• PayPal\n• Par MP\n• Litecoin",
        inline=True
    )

    # Footer avec informations
    embed.set_footer(
        text="Nitro Cheaping Best • Meilleurs prix garantis",
        icon_url=bot.user.avatar.url if bot.user.avatar else None
    )

    # Timestamp
    embed.timestamp = interaction.created_at

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="info", description="Informations sur le bot")
@has_authorized_role()
async def info(interaction: discord.Interaction):
    await interaction.response.send_message('Je suis un bot créé par <@867314394831388672> pour aider les membres du serveur !')

@bot.tree.command(name="clear", description="Supprimer des messages")
@app_commands.describe(amount="Nombre de messages à supprimer")
@has_authorized_role()
async def clear(interaction: discord.Interaction, amount: int):
    # Vérifier si l'utilisateur a les permissions pour supprimer des messages
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Vous n'avez pas la permission de supprimer des messages!", ephemeral=True)
        return

    # Vérifier que le nombre est valide
    if amount <= 0:
        await interaction.response.send_message("❌ Veuillez spécifier un nombre positif de messages à supprimer!", ephemeral=True)
        return

    if amount > 100:
        await interaction.response.send_message("❌ Je ne peux pas supprimer plus de 100 messages à la fois!", ephemeral=True)
        return

    try:
        # Supprimer les messages
        deleted = await interaction.channel.purge(limit=amount)

        # Envoyer un message de confirmation
        await interaction.response.send_message(f"✅ {len(deleted)} message(s) supprimé(s)!", ephemeral=True)

    except discord.Forbidden:
        await interaction.response.send_message("❌ Je n'ai pas la permission de supprimer des messages dans ce canal!", ephemeral=True)
    except discord.HTTPException:
        await interaction.response.send_message("❌ Une erreur s'est produite lors de la suppression des messages!", ephemeral=True)

@bot.tree.command(name="avis", description="Laisser un avis sur la boutique")
@app_commands.describe(
    etoiles="Nombre d'étoiles (1-5)",
    commentaire="Votre commentaire"
)
@has_authorized_role()
async def avis(interaction: discord.Interaction, etoiles: int, commentaire: str):
    # Vérifier que le nombre d'étoiles est valide (1 à 5)
    if etoiles < 1 or etoiles > 5:
        await interaction.response.send_message("❌ Le nombre d'étoiles doit être entre 1 et 5!", ephemeral=True)
        return

    # Vérifier que le commentaire n'est pas trop long
    if len(commentaire) > 500:
        await interaction.response.send_message("❌ Le commentaire ne peut pas dépasser 500 caractères!", ephemeral=True)
        return

    # Créer l'affichage des étoiles
    etoiles_affichage = "⭐" * etoiles + "☆" * (5 - etoiles)

    # Créer l'embed pour l'avis
    embed = discord.Embed(
        title="⭐ NOUVEL AVIS ⭐",
        description=f"**Note:** {etoiles_affichage} ({etoiles}/5)\n\n**Commentaire:**\n{commentaire}",
        color=0xffd700 if etoiles >= 4 else 0xff8c00 if etoiles >= 3 else 0xff4500
    )

    # Ajouter les informations de l'utilisateur
    embed.set_author(
        name=f"{interaction.user.display_name}",
        icon_url=interaction.user.avatar.url if interaction.user.avatar else None
    )

    embed.add_field(
        name="👤 Utilisateur", 
        value=interaction.user.mention, 
        inline=True
    )

    embed.add_field(
        name="📅 Date", 
        value=f"<t:{int(interaction.created_at.timestamp())}:F>", 
        inline=True
    )

    embed.set_footer(text="Merci pour votre avis! 💙")

    # Envoyer l'avis
    await interaction.response.send_message(embed=embed)

    # Ajouter des réactions pour indiquer si l'avis est utile
    message = await interaction.original_response()
    await message.add_reaction("👍")
    await message.add_reaction("👎")

    # Message de confirmation en DM
    try:
        dm_embed = discord.Embed(
            title="✅ Avis publié avec succès!",
            description=f"Votre avis de {etoiles} étoiles a été publié sur le serveur.\n\nMerci pour votre retour!",
            color=0x00ff00
        )
        await interaction.user.send(embed=dm_embed)
    except discord.Forbidden:
        # Si les DM sont fermés, on ignore
        pass

@bot.tree.command(name="voir_avis", description="Voir les avis d'un utilisateur")
@app_commands.describe(utilisateur="Utilisateur dont voir les avis (optionnel)")
@has_authorized_role()
async def voir_avis(interaction: discord.Interaction, utilisateur: discord.Member = None):
    if utilisateur:
        # Rechercher les avis de cet utilisateur dans les messages récents
        avis_count = 0
        messages_checked = 0

        # Vérifier les 100 derniers messages du canal
        async for message in interaction.channel.history(limit=100):
            messages_checked += 1
            if (message.author == bot.user and 
                message.embeds and 
                "NOUVEL AVIS" in message.embeds[0].title and
                utilisateur.mention in message.embeds[0].fields[0].value):
                avis_count += 1

        embed = discord.Embed(
            title=f"📊 Avis de {utilisateur.display_name}",
            description=f"**Nombre d'avis trouvés:** {avis_count}\n**Messages vérifiés:** {messages_checked}",
            color=0x0099ff
        )
        embed.set_thumbnail(url=utilisateur.avatar.url if utilisateur.avatar else None)

    else:
        # Afficher des conseils pour laisser un avis
        embed = discord.Embed(
            title="⭐ Système d'Avis",
            description="Laissez votre avis sur notre boutique!",
            color=0xffd700
        )
        embed.add_field(
            name="📝 Comment laisser un avis",
            value="Utilisez la commande: `/avis <étoiles> <commentaire>`\n**Exemple:** `/avis 5 Excellent service!`",
            inline=False
        )
        embed.add_field(
            name="⭐ Système d'étoiles",
            value="• 1 ⭐ = Très mauvais\n• 2 ⭐⭐ = Mauvais\n• 3 ⭐⭐⭐ = Moyen\n• 4 ⭐⭐⭐⭐ = Bon\n• 5 ⭐⭐⭐⭐⭐ = Excellent",
            inline=False
        )
        embed.add_field(
            name="🛍️ Notre boutique",
            value="[Visitez notre shop](https://nitrocheapingbest.sellauth.com)",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="giveaway", description="Lancer un giveaway")
@app_commands.describe(
    temps="Durée en minutes",
    prix="Prix du giveaway"
)
@has_authorized_role()
async def giveaway(interaction: discord.Interaction, temps: int, prix: str):
    import asyncio
    import random

    # Vérifier les permissions
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Vous n'avez pas la permission de lancer un giveaway!", ephemeral=True)
        return

    # Vérifier que le temps est valide
    if temps <= 0:
        await interaction.response.send_message("❌ Le temps doit être positif!", ephemeral=True)
        return

    if temps > 1440:  # Plus de 24h
        await interaction.response.send_message("❌ Le giveaway ne peut pas durer plus de 24 heures!", ephemeral=True)
        return

    # Créer l'embed du giveaway
    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"**Prix:** {prix}\n**Temps:** {temps} minutes\n**Pour participer:** Réagissez avec 🎉",
        color=0x00ff00
    )
    embed.add_field(name="Lancé par", value=interaction.user.mention, inline=True)
    embed.set_footer(text=f"Se termine dans {temps} minutes")

    # Envoyer le message du giveaway
    await interaction.response.send_message("@everyone", embed=embed)
    giveaway_msg = await interaction.original_response()
    await giveaway_msg.add_reaction("🎉")

    # Attendre la fin du giveaway
    await asyncio.sleep(temps * 60)

    # Récupérer le message mis à jour
    giveaway_msg = await interaction.channel.fetch_message(giveaway_msg.id)

    # Trouver la réaction 🎉
    reaction = None
    for r in giveaway_msg.reactions:
        if str(r.emoji) == "🎉":
            reaction = r
            break

    if not reaction or reaction.count <= 1:  # Compte le bot aussi
        # Aucun participant
        embed_end = discord.Embed(
            title="🎉 GIVEAWAY TERMINÉ 🎉",
            description=f"**Prix:** {prix}\n**Gagnant:** Aucun participant 😢",
            color=0xff0000
        )
        await giveaway_msg.edit(embed=embed_end)
        return

    # Récupérer les participants (exclure le bot)
    participants = []
    async for user in reaction.users():
        if not user.bot:
            participants.append(user)

    if not participants:
        embed_end = discord.Embed(
            title="🎉 GIVEAWAY TERMINÉ 🎉",
            description=f"**Prix:** {prix}\n**Gagnant:** Aucun participant valide 😢",
            color=0xff0000
        )
        await giveaway_msg.edit(embed=embed_end)
        return

    # Choisir un gagnant aléatoire
    winner = random.choice(participants)

    # Créer l'embed de fin
    embed_end = discord.Embed(
        title="🎉 GIVEAWAY TERMINÉ 🎉",
        description=f"**Prix:** {prix}\n**Gagnant:** {winner.mention}\n**Participants:** {len(participants)}",
        color=0xffd700
    )
    embed_end.set_footer(text="Félicitations au gagnant!")

    # Mettre à jour le message et annoncer le gagnant
    await giveaway_msg.edit(embed=embed_end)
    await interaction.followup.send(f"🎉 Félicitations {winner.mention}! Vous avez gagné **{prix}**!")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ Vous n'avez pas l'autorisation d'utiliser cette commande!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Vous n'avez pas l'autorisation d'utiliser cette commande!", ephemeral=True)
    else:
        # Autres erreurs
        print(f"Erreur: {error}")

@bot.tree.command(name="ban", description="Bannir un utilisateur")
@app_commands.describe(utilisateur="Utilisateur à bannir", raison="Raison du bannissement")
@has_authorized_role()
async def ban(interaction: discord.Interaction, utilisateur: discord.Member, raison: str = "Aucune raison fournie"):
    # Vérifier si l'utilisateur a les permissions pour bannir
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Vous n'avez pas la permission de bannir des membres!", ephemeral=True)
        return

    try:
        # Bannir l'utilisateur
        await interaction.guild.ban(user=utilisateur, reason=raison)
        await interaction.response.send_message(f"✅ {utilisateur.mention} a été banni avec succès! Raison: {raison}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ Je n'ai pas la permission de bannir cet utilisateur!", ephemeral=True)
    except discord.HTTPException:
        await interaction.response.send_message("❌ Une erreur s'est produite lors du bannissement!", ephemeral=True)

# Replace 'YOUR_TOKEN_HERE' with your actual bot token
bot.run('YOUR-TOKEN-HERE')