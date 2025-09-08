import os
import json
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

if not TOKEN or not GUILD_ID:
    raise ValueError("❌ TOKEN or GUILD_ID is missing in environment variables!")

GUILD_ID = int(GUILD_ID)

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

STORAGE_FILE = "storage.json"

# ---- Helpers ----
def load_storage():
    if not os.path.exists(STORAGE_FILE):
        return {"autoroles": {}, "setups": {}}
    with open(STORAGE_FILE, "r") as f:
        return json.load(f)

def save_storage(data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

storage = load_storage()


# ---- Persistent Autorole Button ----
class AutoroleButton(discord.ui.Button):
    def __init__(self, role_id: int):
        super().__init__(style=discord.ButtonStyle.primary, label=f"Get Role {role_id}", custom_id=f"autorole-{role_id}")
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ Role not found.", ephemeral=True)
            return

        member = interaction.user
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"❌ Removed {role.name}.", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"✅ You got {role.name}!", ephemeral=True)


# ---- Persistent Multi-role Dropdown ----
class RoleSelect(discord.ui.Select):
    def __init__(self, roles):
        options = [discord.SelectOption(label=role.name, value=str(role.id)) for role in roles]
        super().__init__(
            placeholder="Choose your roles...",
            min_values=1,
            max_values=len(options),
            options=options,
            custom_id="role_selector"
        )
        self.roles = roles

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        added, removed = [], []

        for role_id in self.values:
            role = interaction.guild.get_role(int(role_id))
            if role not in member.roles:
                await member.add_roles(role)
                added.append(role.name)

        for role in self.roles:
            if str(role.id) not in self.values and role in member.roles:
                await member.remove_roles(role)
                removed.append(role.name)

        msg = ""
        if added:
            msg += f"✅ Added: {', '.join(added)}\n"
        if removed:
            msg += f"❌ Removed: {', '.join(removed)}"
        if not msg:
            msg = "ℹ️ No changes."

        await interaction.response.send_message(msg, ephemeral=True)


class RoleView(discord.ui.View):
    def __init__(self, roles):
        super().__init__(timeout=None)
        self.add_item(RoleSelect(roles))


# ---- Bot Ready ----
@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))

    # Re-attach persistent views
    for msg_id, data in storage["autoroles"].items():
        channel = bot.get_channel(data["channel_id"])
        if channel:
            view = discord.ui.View(timeout=None)
            view.add_item(AutoroleButton(data["role_id"]))
            bot.add_view(view, message_id=int(msg_id))

    for msg_id, data in storage["setups"].items():
        channel = bot.get_channel(data["channel_id"])
        if channel:
            roles = [channel.guild.get_role(rid) for rid in data["role_ids"] if channel.guild.get_role(rid)]
            if roles:
                bot.add_view(RoleView(roles), message_id=int(msg_id))

    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")


# ---- Embed Command ----
@bot.tree.command(name="embed", description="Create a custom embed", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(administrator=True)
async def embed(interaction: discord.Interaction, title: str, description: str):
    embed = discord.Embed(title=title, description=description, color=discord.Color.random())
    await interaction.response.send_message(embed=embed)


# ---- Autorole Command ----
@bot.tree.command(name="autorole", description="Send an auto role message", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(administrator=True)
async def autorole(interaction: discord.Interaction, role: discord.Role):
    button = AutoroleButton(role.id)
    view = discord.ui.View(timeout=None)
    view.add_item(button)
    msg = await interaction.channel.send(
        content=f"Click below to get the **{role.name}** role:",
        view=view
    )
    await interaction.response.send_message("✅ Autorole message created.", ephemeral=True)

    storage["autoroles"][str(msg.id)] = {"channel_id": interaction.channel.id, "role_id": role.id}
    save_storage(storage)


# ---- Setup Command ----
@bot.tree.command(name="setup", description="Create a multi-role selector", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction, roles: str):
    role_mentions = roles.replace(" ", "").split(",")
    role_objects = []
    for mention in role_mentions:
        if mention.startswith("<@&") and mention.endswith(">"):
            role_id = int(mention[3:-1])
            role = interaction.guild.get_role(role_id)
            if role:
                role_objects.append(role)

    if not role_objects:
        await interaction.response.send_message("❌ No valid roles found.", ephemeral=True)
        return

    view = RoleView(role_objects)
    msg = await interaction.channel.send("📌 Select your roles below:", view=view)
    await interaction.response.send_message("✅ Setup message created.", ephemeral=True)

    storage["setups"][str(msg.id)] = {"channel_id": interaction.channel.id, "role_ids": [r.id for r in role_objects]}
    save_storage(storage)


# ---- Error Handling ----
@embed.error
@autorole.error
@setup.error
async def permissions_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You must be an **Administrator** to use this command.", ephemeral=True)


bot.run(TOKEN)
