import asyncio
import random
from importlib.resources import contents
from typing import Any
import os
import json
from pathlib import Path

import discord
import dotenv
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

import random
import discord
from discord.ext import commands
from discord import app_commands


class DisguiseCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ================================
    # UTILITY COMMANDS
    # ================================

    @app_commands.command(name="ping", description="Check bot latency.")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latency: `{latency}ms`")

    @app_commands.command(name="serverinfo", description="Displays information about the current server.")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Server ID", value=str(guild.id), inline=True)
        embed.add_field(name="Owner", value=str(guild.owner), inline=True)
        embed.add_field(name="Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
        embed.set_footer(text=f"Created at {guild.created_at.strftime('%Y-%m-%d')}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Get information about a user.")
    @app_commands.describe(member="The member to inspect (defaults to you)")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        embed = discord.Embed(title=f"User Info - {target.name}", color=discord.Color.green())
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="ID", value=str(target.id), inline=True)
        embed.add_field(name="Display Name", value=target.display_name, inline=True)

        joined_str = target.joined_at.strftime("%Y-%m-%d") if hasattr(target,
                                                                      "joined_at") and target.joined_at else "Unknown"
        embed.add_field(name="Joined Server", value=joined_str, inline=True)
        embed.add_field(name="Account Created", value=target.created_at.strftime("%Y-%m-%d"), inline=True)

        if hasattr(target, "top_role"):
            embed.add_field(name="Top Role", value=target.top_role.mention, inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Show user's profile avatar.")
    @app_commands.describe(member="The member whose avatar you want to view")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        embed = discord.Embed(title=f"{target.name}'s Avatar", color=discord.Color.purple())
        embed.set_image(url=target.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ================================
    # MODERATION COMMANDS
    # ================================

    @app_commands.command(name="purge", description="Bulk delete messages.")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int = 5):
        if amount > 100 or amount < 1:
            await interaction.response.send_message("Please specify a number between 1 and 100.", ephemeral=True)
            return

        # Defer answer because channel.purge takes a moment
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)

    @app_commands.command(name="slowmode", description="Set channel slowmode delay.")
    @app_commands.describe(seconds="Delay in seconds (0 to disable)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int = 0):
        await interaction.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await interaction.response.send_message("Slowmode disabled.")
        else:
            await interaction.response.send_message(f"Slowmode set to {seconds} seconds.")

    # ================================
    # FUN & INTERACTION COMMANDS
    # ================================

    @app_commands.command(name="roll", description="Roll a dice (e.g. 1d20 or 100).")
    @app_commands.describe(dice="Dice specification like '100' or '2d6'")
    async def roll(self, interaction: discord.Interaction, dice: str = "100"):
        try:
            if "d" in dice.lower():
                rolls, limit = map(int, dice.lower().split("d"))
                results = [random.randint(1, limit) for _ in range(rolls)]
                await interaction.response.send_message(
                    f"🎲 Rolled: {', '.join(map(str, results))} (Total: {sum(results)})")
            else:
                result = random.randint(1, int(dice))
                await interaction.response.send_message(f"🎲 Rolled: **{result}** (1-{dice})")
        except Exception:
            await interaction.response.send_message("Invalid format! Use `100` or `2d6`.", ephemeral=True)

    @app_commands.command(name="coinflip", description="Flips a coin.")
    async def coinflip(self, interaction: discord.Interaction):
        outcome = random.choice(["Heads 🪙", "Tails 🪙"])
        await interaction.response.send_message(f"Result: **{outcome}**")

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question.")
    @app_commands.describe(question="Your question for the 8-ball")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = [
            "It is certain.", "Without a doubt.", "You may rely on it.",
            "Ask again later.", "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "Very doubtful."
        ]
        answer = random.choice(responses)
        await interaction.response.send_message(f"🎱 **Question:** {question}\n**Answer:** {answer}")

    @app_commands.command(name="poll", description="Create a simple yes/no poll.")
    @app_commands.describe(question="The question to poll")
    async def poll(self, interaction: discord.Interaction, question: str):
        embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.gold())
        embed.set_footer(text=f"Asked by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

        # Fetch the sent message to add reactions
        msg = await interaction.original_response()
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    # ================================
    # GAMES & TRIVIA
    # ================================

    @app_commands.command(name="trivia", description="Play a quick trivia question!")
    async def trivia(self, interaction: discord.Interaction):
        questions = [
            {"q": "What is the capital of Japan?", "a": "tokyo"},
            {"q": "How many keys does a standard piano have?", "a": "88"},
            {"q": "Which element has the chemical symbol 'Au'?", "a": "gold"},
            {"q": "What year did the original iPhone release?", "a": "2007"},
        ]
        item = random.choice(questions)
        await interaction.response.send_message(f"❓ **Trivia:** {item['q']}\n*(You have 15 seconds to reply in chat!)*")

        def check(m):
            return m.channel == interaction.channel and m.content.lower().strip() == item["a"]

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=15.0)
            await interaction.channel.send(
                f"🎉 Correct, {msg.author.mention}! The answer was **{item['a'].capitalize()}**.")
        except Exception:
            await interaction.channel.send(f"⏰ Time's up! The correct answer was **{item['a'].capitalize()}**.")

    @app_commands.command(name="rps", description="Play Rock, Paper, Scissors against the bot.")
    @app_commands.choices(choice=[
        app_commands.Choice(name="Rock", value="rock"),
        app_commands.Choice(name="Paper", value="paper"),
        app_commands.Choice(name="Scissors", value="scissors"),
    ])
    async def rps(self, interaction: discord.Interaction, choice: app_commands.Choice[str]):
        user_choice = choice.value
        bot_choice = random.choice(["rock", "paper", "scissors"])
        win_map = {"rock": "scissors", "paper": "rock", "scissors": "paper"}

        if user_choice == bot_choice:
            result = "It's a tie! 🤝"
        elif win_map[user_choice] == bot_choice:
            result = "You win! 🎉"
        else:
            result = "I win! 🤖"

        await interaction.response.send_message(f"You chose **{user_choice}**, I chose **{bot_choice}**. {result}")

    @app_commands.command(name="rate", description="Rates anything out of 10.")
    @app_commands.describe(thing="What would you like me to rate?")
    async def rate(self, interaction: discord.Interaction, thing: str):
        score = random.randint(0, 10)
        await interaction.response.send_message(f"⭐ I rate **{thing}** a **{score}/10**!")

    # ================================
    # TEXT MODIFIERS & FUN UTILS
    # ================================

    @app_commands.command(name="mock", description="mOcKiNg tExT GeNeRaToR")
    @app_commands.describe(text="The text to mock")
    async def mock(self, interaction: discord.Interaction, text: str):
        mocked = "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))
        await interaction.response.send_message(f"🤡 {mocked}")

    @app_commands.command(name="reverse", description="Reverses any text provided.")
    @app_commands.describe(text="Text to reverse")
    async def reverse(self, interaction: discord.Interaction, text: str):
        await interaction.response.send_message(f"🔄 {text[::-1]}")

    @app_commands.command(name="clap", description="Adds 👏 clap 👏 emojis 👏 between 👏 words.")
    @app_commands.describe(text="Text to clapify")
    async def clap(self, interaction: discord.Interaction, text: str):
        clapped = " 👏 ".join(text.split())
        await interaction.response.send_message(f"👏 {clapped} 👏")

    # ================================
    # INTERACTION & SOCIAL COMMANDS
    # ================================

    @app_commands.command(name="ship", description="Calculate compatibility between two users.")
    @app_commands.describe(user1="First user", user2="Second user (defaults to you)")
    async def ship(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member = None):
        target2 = user2 or interaction.user
        score = random.randint(0, 100)

        if score > 80:
            bar = "██████████"
            message = "A match made in heaven! 💕"
        elif score > 50:
            bar = "█████▒▒▒▒▒"
            message = "Looking pretty solid! 👍"
        else:
            bar = "██▒▒▒▒▒▒▒▒"
            message = "Maybe stay as friends... 😅"

        embed = discord.Embed(title="❤️ Compatibility Meter", color=discord.Color.magenta())
        embed.add_field(name="Coupling", value=f"{user1.mention} + {target2.mention}", inline=False)
        embed.add_field(name="Score", value=f"**{score}%**\n`[{bar}]`", inline=False)
        embed.set_footer(text=message)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hug", description="Send a virtual hug to someone!")
    @app_commands.describe(member="Person to hug")
    async def hug(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"🤗 {interaction.user.mention} gave {member.mention} a big warm hug!")

    @app_commands.command(name="slap", description="Slap someone with a trout!")
    @app_commands.describe(member="Person to slap")
    async def slap(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(
            f"🐟 {interaction.user.mention} slapped {member.mention} with a giant smelly trout!")


class DiscordScraper(commands.Bot):
    def __init__(self, channel_id: int, server_id: int, auto_close: bool = False):
        intents = discord.Intents.default()
        intents.message_content = True
        self._channel_id = channel_id
        self._server_id = server_id

        self.auto_close = auto_close

        super().__init__(command_prefix="!", intents=intents)


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    async def setup_hook(self) -> None:
        await self.add_cog(DisguiseCog(self))

        guild = discord.Object(id=self._server_id)

        self.tree.copy_global_to(guild=guild)

        self.tree.clear_commands(guild=None)
        await self.tree.sync()

        synced = await self.tree.sync(guild=guild)
        print(f"Synced {len(synced)} command(s) to Guild {self._server_id}!")

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user}")

        await self.get_all_messages(self._channel_id)

        if self.auto_close:
            await self.close()

    async def get_all_messages(self, channel_id: int) -> Any:
        channel = self.get_channel(channel_id) or await self.fetch_channel(channel_id)

        data_path = Path(f"../data/{channel_id}.json")
        data_path.parent.mkdir(parents=True, exist_ok=True)

        messages = {}
        if data_path.exists():
            try:
                messages = json.loads(data_path.read_text(encoding="utf-8"))
                print(f"Resuming from existing file with {len(messages)} messages already saved.")
            except json.JSONDecodeError:
                print("Existing file corrupted or empty, starting fresh.")

        last_message_id = None
        if messages:
            last_message_id = min(int(msg_id) for msg_id in messages.keys())

        total_scraped = len(messages)
        batch_count = 0

        while True:
            before_obj = discord.Object(id=last_message_id) if last_message_id else None
            fetched_in_batch = 0

            try:
                async for message in channel.history(limit=100, before=before_obj):
                    messages[str(message.id)] = {
                        "author": str(message.author),
                        "content": message.content,
                        "mentions": [str(u) for u in message.mentions],
                        "attachments": [a.url for a in message.attachments],
                        "created_at": message.created_at.isoformat(),
                        "jump_url": message.jump_url,
                    }
                    last_message_id = message.id
                    fetched_in_batch += 1

                if fetched_in_batch == 0:
                    print("Reached the beginning of the channel history!")
                    break

                total_scraped += fetched_in_batch
                batch_count += 1
                print(f"Fetched {total_scraped} total messages...")

                if batch_count % 10 == 0:
                    data_path.write_text(json.dumps(messages, indent=4), encoding="utf-8")
                    print("--> Progress saved to disk.")

                await asyncio.sleep(0.2)

            except (discord.DiscordServerError, discord.HTTPException) as e:
                print(f"API Error encountered: {e}. Waiting 10 seconds before resuming...")
                await asyncio.sleep(10)
                continue

        data_path.write_text(json.dumps(messages, indent=4), encoding="utf-8")
        print(f"Scrape complete! Total messages saved: {len(messages)}")

ds = DiscordScraper(1530222266611404872, 1530222265851973772)
ds.run(os.getenv("DISCORD_TOKEN"))
