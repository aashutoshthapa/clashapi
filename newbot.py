import discord
from discord.ext import commands
import requests
import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get tokens from environment variables
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
COC_API_TOKEN = os.getenv('COC_API_TOKEN')

# Enable the message content intent
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

# Function to get clan members
def get_clan_members(clan_tag):
    clan_tag_encoded = clan_tag.replace("#", "%23")
    url = f'https://api.clashofclans.com/v1/clans/{clan_tag_encoded}'
    headers = {'Authorization': f'Bearer {COC_API_TOKEN}'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f'Error fetching clan data: {response.status_code}')
        return None

    data = response.json()
    return data

# Function to get player name
def get_player_name(player_tag):
    player_tag_encoded = player_tag.replace("#", "%23")
    url = f'https://api.clashofclans.com/v1/players/{player_tag_encoded}'
    headers = {'Authorization': f'Bearer {COC_API_TOKEN}'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f'Error fetching player data: {response.status_code}')
        return None

    data = response.json()
    return data.get('name')

@bot.command()
async def roster(ctx, clan_tag: str, *player_tags: str):
    clan_data = get_clan_members(clan_tag)
    if clan_data is None:
        await ctx.send("Error fetching clan members.")
        return

    clan_name = clan_data.get('name', 'Unknown Clan')
    member_list = clan_data.get('memberList', [])
    member_dict = {member['tag']: member for member in member_list}

    result = []

    for i, player_tag in enumerate(player_tags, 1):
        member = member_dict.get(player_tag)
        if member:
            player_name = member['name']
            status = '✅'
        else:
            player_name = get_player_name(player_tag) or 'Unknown'
            status = '❌'

        result.append(f"{i}) **{player_name}** ({player_tag}) {status}")

    embed = discord.Embed(
        title=f"🏆 **ROSTER FOR {clan_name}** 🏆", 
        description="Here is the current roster of the clan.",
        color=discord.Color.orange()
    )

    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/805001683846823987/1269517881708773417/Untitled_Artwork.png?ex=66b05a29&is=66af08a9&hm=d6b65e6fcd05403610ad4135c4d0e43096efedfdcd12742f807f96ecb5d45bf0&")  # Replace with your server or clan icon
    embed.add_field(name="Player List", value="\n".join(result), inline=False)
    last_refreshed = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    embed.set_footer(text=f"Last Refreshed: {last_refreshed} | React with 🔄 to refresh.")

    message = await ctx.send(embed=embed)
    await message.add_reaction('🔄')

    @bot.event
    async def on_reaction_add(reaction, user):
        if user.bot:
            return

        if reaction.emoji == '🔄' and reaction.message.id == message.id:
            clan_data = get_clan_members(clan_tag)
            if clan_data is None:
                await ctx.send("Error fetching clan members.")
                return

            clan_name = clan_data.get('name', 'Unknown Clan')
            member_list = clan_data.get('memberList', [])
            member_dict = {member['tag']: member for member in member_list}

            result = []

            for i, player_tag in enumerate(player_tags, 1):
                member = member_dict.get(player_tag)
                if member:
                    player_name = member['name']
                    status = '✅'
                else:
                    player_name = get_player_name(player_tag) or 'Unknown'
                    status = '❌'

                result.append(f"{i}) **{player_name}** ({player_tag}) {status}")

            embed.clear_fields()
            embed.add_field(name="Player List", value="\n".join(result), inline=False)
            last_refreshed = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            embed.set_footer(text=f"Last Refreshed: {last_refreshed} | React with 🔄 to refresh.")

            await reaction.message.edit(embed=embed)

bot.run(TOKEN)