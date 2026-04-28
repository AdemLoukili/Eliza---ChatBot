import discord
from discord import app_commands
from discord.ui import Select, View
import httpx
import os

DISCORD_TOKEN = "0"
FLASK_URL     = "http://localhost:8000/chat"
SCHOOLS_URL   = "http://localhost:8000/schools"

histories    = {}
user_context = {}  # contexte école/campus par utilisateur
MAX_HISTORY  = 8

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
tree   = app_commands.CommandTree(client)

async def fetch_schools() -> dict:
    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            r = await http.get(SCHOOLS_URL)
            return r.json()
    except Exception:
        return {}

async def ask_flask(message: str, user_id: str) -> str:
    history = histories.get(user_id, [])
    ctx     = user_context.get(user_id, {})
    try:
        async with httpx.AsyncClient(timeout=60.0) as http:
            resp = await http.post(FLASK_URL, json={
                "message": message,
                "history": history,
                "school":  ctx.get("school", ""),
                "campus":  ctx.get("campus", "")
            })
        reply = resp.json().get("reply", "⚠️ Pas de réponse.")
    except Exception as e:
        reply = f"⚠️ Erreur serveur : {e}"

    history.append({"role": "user",      "content": message})
    history.append({"role": "assistant", "content": reply})
    histories[user_id] = history[-(MAX_HISTORY * 2):]
    return reply

async def send_long(target, reply: str):
    """Envoie un message en le découpant si > 1900 chars."""
    if len(reply) > 1900:
        for i in range(0, len(reply), 1900):
            await target.channel.send(reply[i:i+1900])
    else:
        await target.reply(reply)

class CampusSelect(Select):
    def __init__(self, school: str, campus_list: list):
        self.school = school
        options = [discord.SelectOption(label=c, value=c) for c in campus_list[:25]]
        super().__init__(placeholder="Choisis un campus…", options=options)

    async def callback(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        user_context[uid] = {"school": self.school, "campus": self.values[0]}
        embed = discord.Embed(
            title="✅ Contexte mis à jour",
            description=f"**École :** {self.school}\n**Campus :** {self.values[0]}",
            color=0x5865F2
        )
        embed.set_footer(text="Mentionne-moi ou utilise /chat pour poser une question !")
        await interaction.response.edit_message(embed=embed, view=None)

class SchoolSelect(Select):
    def __init__(self, schools_data: dict):
        self.schools_data = schools_data
        options = [
            discord.SelectOption(label=s, description=data["domaine"][:50], value=s)
            for s, data in schools_data.items()
        ][:25]
        super().__init__(placeholder="Choisis une école…", options=options)

    async def callback(self, interaction: discord.Interaction):
        school      = self.values[0]
        school_data = self.schools_data.get(school, {})
        # /schools retourne campus comme liste ou dict selon le format Flask
        campus_raw  = school_data.get("campus", [])
        if isinstance(campus_raw, dict):
            campus_list = list(campus_raw.keys())
        else:
            campus_list = list(campus_raw)
        view = View(timeout=60)
        view.add_item(CampusSelect(school, campus_list))
        embed = discord.Embed(
            title=f"🏫 {school}",
            description=school_data.get("description", ""),
            color=0x5865F2
        )
        embed.set_footer(text="Maintenant choisis un campus ↓")
        await interaction.response.edit_message(embed=embed, view=view)

@tree.command(name="campus", description="Sélectionne ton école et ton campus IONIS")
async def cmd_campus(interaction: discord.Interaction):
    schools_data = await fetch_schools()
    if not schools_data:
        await interaction.response.send_message(
            "⚠️ Impossible de récupérer les écoles (Flask est-il lancé ?)", ephemeral=True
        )
        return
    view = View(timeout=60)
    view.add_item(SchoolSelect(schools_data))
    embed = discord.Embed(
        title="🎓 Sélection de ton campus",
        description="Choisis ton école pour que je personnalise mes réponses.",
        color=0x5865F2
    )
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@tree.command(name="chat", description="Pose une question à IONISBot")
@app_commands.describe(question="Ta question sur les campus IONIS")
async def cmd_chat(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)
    uid   = str(interaction.user.id)
    reply = await ask_flask(question, uid)
    ctx   = user_context.get(uid, {})

    embed = discord.Embed(description=reply[:4096], color=0x5865F2)
    if ctx:
        embed.set_footer(text=f"{ctx.get('school', '')} – {ctx.get('campus', '')}")
    await interaction.followup.send(embed=embed)

@tree.command(name="horaires", description="Affiche les horaires de ton campus")
async def cmd_horaires(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    ctx = user_context.get(uid, {})
    if not ctx:
        await interaction.response.send_message(
            "⚠️ Définis d'abord ton campus avec `/campus` !", ephemeral=True
        )
        return
    await interaction.response.defer(thinking=True)
    reply = await ask_flask(
        f"Quels sont les horaires du campus {ctx.get('school', '')} {ctx.get('campus', '')} ?", uid
    )
    embed = discord.Embed(title="🕐 Horaires", description=reply[:4096], color=0x5865F2)
    embed.set_footer(text=f"{ctx.get('school', '')} – {ctx.get('campus', '')}")
    await interaction.followup.send(embed=embed)

@tree.command(name="reset", description="Réinitialise ton historique de conversation")
async def cmd_reset(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    histories.pop(uid, None)
    user_context.pop(uid, None)
    await interaction.response.send_message("🔄 Historique et contexte réinitialisés !", ephemeral=True)

@client.event
async def on_member_join(member: discord.Member):
    for name in ("général", "general", "bienvenue", "welcome"):
        channel = discord.utils.find(
            lambda c: name in c.name.lower() and isinstance(c, discord.TextChannel),
            member.guild.channels
        )
        if channel:
            embed = discord.Embed(
                title=f"👋 Bienvenue {member.display_name} !",
                description=(
                    "Je suis **IONISBot**, ton assistant pour les campus du groupe IONIS.\n\n"
                    "**Commandes disponibles :**\n"
                    "`/campus` — Sélectionner ton école et campus\n"
                    "`/chat` — Poser une question\n"
                    "`/horaires` — Voir les horaires de ton campus\n"
                    "`/reset` — Réinitialiser la conversation\n\n"
                    "Tu peux aussi me mentionner directement dans n'importe quel salon ! 🎓"
                ),
                color=0x5865F2
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)
            break

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    is_dm        = isinstance(message.channel, discord.DMChannel)
    is_mentioned = client.user in message.mentions

    if not (is_dm or is_mentioned):
        return

    text = message.content.replace(f"<@{client.user.id}>", "").strip()
    if not text:
        await message.reply(
            "👋 Pose-moi une question, ou utilise `/campus` pour sélectionner ton école !"
        )
        return

    uid = str(message.author.id)
    async with message.channel.typing():
        reply = await ask_flask(text, uid)
    await send_long(message, reply)

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ IONISBot connecté en tant que {client.user}")
    print(f"   Commandes slash synchronisées.")

# ─── Lancement ────────────────────────────────────────────────name───────────────────
if __name__ == "__main__":
    client.run(DISCORD_TOKEN)