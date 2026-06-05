import os
import json
import discord
import gspread
from google.oauth2.service_account import Credentials

# ======================
# ENV
# ======================
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
SHEET_NAME = os.environ["SHEET_NAME"]

# ======================
# GOOGLE CREDS (SECURE)
# ======================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS"])

creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

gs_client = gspread.authorize(creds)
sheet = gs_client.open(SHEET_NAME).sheet1

# ======================
# DISCORD
# ======================
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# ======================
# LOGIC
# ======================
def add_player(name):
    records = sheet.get_all_records()

    for i, row in enumerate(records):
        if row.get("Player") == name:
            new_reports = int(row.get("Reports", 0)) + 1
            sheet.update_cell(i + 2, 2, new_reports)
            return new_reports

    sheet.append_row([name, 1])
    return 1


def get_list():
    records = sheet.get_all_records()

    if not records:
        return "📭 Empty list"

    msg = "🚫 WoW Avoid List:\n\n"
    for r in records:
        msg += f"• {r['Player']} — {r['Reports']}\n"
    return msg


# ======================
# EVENTS
# ======================
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id != CHANNEL_ID:
        return

    content = message.content.strip()

    if content.startswith("!avoid"):
        parts = content.split()
        if len(parts) < 2:
            await message.channel.send("Usage: !avoid name")
            return

        name = parts[1]
        r = add_player(name)

        await message.channel.send(f"Added {name} ({r})")
        return

    if content == "!list":
        await message.channel.send(get_list())


client.run(DISCORD_TOKEN)
