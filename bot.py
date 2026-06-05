import os
import discord
import gspread
from google.oauth2.service_account import Credentials

# =========================
# ENV VARIABLES (RENDER)
# =========================
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
SHEET_NAME = os.environ["SHEET_NAME"]

# =========================
# GOOGLE SHEETS SETUP
# =========================
GOOGLE_CREDS_FILE = "wow-avoid-bot-e0cddd94f409.json"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=scope)
gs_client = gspread.authorize(creds)

sheet = gs_client.open(SHEET_NAME).sheet1

# =========================
# DISCORD SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# =========================
# FUNCTIONS
# =========================
def add_player(name: str):
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
        return "📭 Avoid list is empty"

    msg = "🚫 **WoW Avoid List:**\n\n"
    for row in records:
        msg += f"• {row.get('Player')} — {row.get('Reports')} reports\n"

    return msg


# =========================
# EVENTS
# =========================
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

    # ADD PLAYER
    if content.startswith("!avoid"):
        parts = content.split()

        if len(parts) < 2:
            await message.channel.send("❌ Usage: !avoid PlayerName")
            return

        name = parts[1]
        reports = add_player(name)

        await message.channel.send(f"✅ {name} added ({reports} reports)")
        return

    # SHOW LIST
    if content == "!list":
        await message.channel.send(get_list())
        return


# =========================
# RUN BOT
# =========================
client.run(DISCORD_TOKEN)