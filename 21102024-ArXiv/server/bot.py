# This example requires the 'members' and 'message_content' privileged intents to function.

import discord
from discord.ext import commands
from discord import app_commands # should add later
import random
from dotenv import load_dotenv
import os
from rcs import Pinnacle, RcsFunctionalities
import re
import arxiv
import asyncio
import boto3
import tarfile
import io
import PyPDF2
from openai import OpenAI
import feedparser

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', description=description, intents=intents)

client = Pinnacle(
    api_key="9db05d1b-d965-4fae-9b30-06a0326f282b",
)

def normalize_phone_number(number: str) -> str:
    """Normalize phone number to E.164 format, assuming US numbers."""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', number)
    
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    else:
        raise ValueError(f"Invalid phone number format. Please provide a 10-digit US number: {digits}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


# http://arxiv.org/abs/2410.13857v1

def ai_rss():
  # RSS feed URL
  rss_url = 'http://export.arxiv.org/rss/cs.ai'  # Replace with your desired feed
  rss_file = 'sample_feed.xml'

  # Parse the RSS feed
  feed = feedparser.parse(rss_url)

  # Display feed title
  print(f"Feed Title: {feed['feed']['title']}")

  # Display entries (papers) in the feed
  for entry in feed.entries[:5]:  # Limiting to 5 papers
      print(f"\nTitle: {entry.title}")
      print(f"Published: {entry.published}")
      print(f"Summary: {entry.summary}")
      print(f"Link: {entry.link}")

ai_rss()

def get_ai_summary(metadata: dict):
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

    prompt = f"""
    Based on the following metadata of a recent AI research paper:
    
    Title: {metadata['title']}
    Authors: {', '.join(metadata['authors'])}
    Abstract: {metadata['abstract']}
    Published Date: {metadata['published_date']}
    
    Please provide:
    1. A brief background on this type of research
    2. What's new or notable about this paper in the context of AI research this year
    3. Suggestions for 2-3 other related papers and their authors that might be good to check out with links to the papers
    
    Keep your response concise but informative.
    """

    messages = [
        {
            "role": "system",
            "content": "You are an AI research assistant specializing in summarizing and contextualizing recent AI papers.",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")

    response = client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
    )

    return response.choices[0].message.content

@bot.command()
async def ai(ctx):
    """Returns the most recent AI paper from arXiv with its AI-generated summary"""
    search = arxiv.Search(
        query="cat:cs.AI",
        max_results=1,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    result = next(search.results())
    
    # Extract the arXiv ID from the entry_id
    arxiv_id = result.entry_id.split('/')[-1]
    
    # Generate the PDF link
    pdf_link = f"http://arxiv.org/pdf/{arxiv_id}"
    
    # Get AI summary
    summary = get_ai_summary({
        'title': result.title,
        'authors': [author.name for author in result.authors],
        'abstract': result.summary,
        'published_date': result.published.strftime('%Y-%m-%d')
    })
    
    # Prepare response
    response = f"Here's the most recent AI paper from ArXiv:\n\n"
    response += f"**Title:** {result.title}\n\n"
    response += f"**Authors:** {', '.join(author.name for author in result.authors)}\n\n"
    response += f"**Published:** {result.published.strftime('%Y-%m-%d')}\n\n"
    response += f"**AI Summary:**\n{summary[:1500]}...\n\n"  # Truncate to fit Discord's character limit
    response += f"**ArXiv page:** {result.entry_id}\n\n"
    response += f"**PDF link:** {pdf_link}\n\n"

    await ctx.send(response)
    
    def check(m):
        return m.reference and m.reference.message_id == ctx.message.id and re.match(r'^\+\d{11}$', m.content)
    
    try:
        reply = await bot.wait_for('message', check=check, timeout=60.0)
        await reply.reply(f"Hi there! Thanks for your interest. The number {reply.content} has been noted.")
    except asyncio.TimeoutError:
        pass  # No valid reply within 60 seconds, do nothing

@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)

@bot.command()
async def readme(ctx: commands.Context):
  await ctx.send("""Hi! I'm Rosie the Raccoon! 
                 
If you want to try sending your first RCS message, try /send <10 digit number> or /send <10 digit number> invite (invite only works if you're tagged Pinnacle).
                 
/send +16287261512 invite
/send "+1 (628) 726 -1512" invite <- need quotes
/send "+1 (628) 726 -1512" invite <- need quotes
/send "(628) 726-1512" invite <- need quotes
/send "(628) 726-1512" invite <- need quotes""")

# Admin only
@bot.command()
async def send(ctx: commands.Context, number: str, *, invite: str = None):
    """Sends an RCS message (Pinnacle role only). Use 'invite' to send as an invitation."""
    pinnacle_role = discord.utils.get(ctx.guild.roles, name="Pinnacle")
    if pinnacle_role not in ctx.author.roles:
        await ctx.send("This command can only be used by members with the Pinnacle role.", ephemeral=True)
        return

    if ctx.channel.name != 'rcs-demo':
        await ctx.send("This command can only be used in the 'rcs-demo' channel.", ephemeral=True)
        return
    
    normalized_number = normalize_phone_number(number)
    
    # Check if the number is in valid E.164 format
    if not normalized_number.startswith('+') or not normalized_number[1:].isdigit():
        await ctx.send("Please provide a valid phone number (e.g., +1234567890 or (914) 826-7757).", ephemeral=True)
        return

    functionality: RcsFunctionalities = client.get_rcs_functionality(phone_number=normalized_number)
    if functionality.is_enabled:
        await ctx.send(f"RCS is enabled on {normalized_number}!")
        try:
            title = (f"{ctx.author.display_name} invited you to check out Pinnacle's RCS API!"
                     if invite and invite.lower() == "invite" else
                     f"Hi {ctx.author.display_name}! It's Rosie 🦝 from Pinnacle - Thanks for checking out our API")

            client.send.rcs(
                from_="test",
                to=normalized_number,
                cards=[
                    {
                        "title": title,
                        "subtitle": "You can check out our docs and join our community below",
                        "mediaUrl": "https://i.ibb.co/gvZ0XvC/IMG-3248.jpg",
                        "buttons": [
                            {
                                "title": "Docs",
                                "type": "openUrl",
                                "payload": "https://docs.trypinnacle.app"
                            },
                            {
                                "title": "Community",
                                "type": "openUrl",
                                "payload": "https://discord.gg/tT3n4Gmf"
                            }
                        ]
                    }
                ]
            )
            await ctx.send("Special Pinnacle RCS message sent successfully!")
        except Exception as e:
            await ctx.send(f"Error sending RCS message: {str(e)}")
    else:
        await ctx.send(f"RCS isn't enabled on {normalized_number}.")

@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f'Welcome, {member.name}! Feel free to explore our discord here or check out the docs here: https://docs.trypinnacle.app')

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
token = os.getenv('DISCORD_TOKEN')

# Use the token from the environment variable
bot.run(token)
