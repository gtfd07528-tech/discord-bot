import discord
from discord import app_commands
import random
import asyncio
import time
import json
import os


# ============================================================
# BOT TOKEN
# ============================================================
# IMPORTANT:
# Put your NEW regenerated Discord bot token here.
# Do NOT use the old token that was previously exposed.

TOKEN = "paste token here""


# ============================================================
# DISCORD SETUP
# ============================================================

intents = discord.Intents.default()

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)


# ============================================================
# LEVEL DATA
# ============================================================

LEVELS = {

    1: {
        "name": "Ready",
        "emoji": "🍎",
        "fruits": ["🍎"],
        "copies": 3,
        "bombs": 1,
        "timer": None,
        "mistakes": None
    },

    2: {
        "name": "Rookie",
        "emoji": "🍌",
        "fruits": ["🍎", "🍌"],
        "copies": 2,
        "bombs": 2,
        "timer": None,
        "mistakes": None
    },

    3: {
        "name": "Hunter",
        "emoji": "🍇",
        "fruits": ["🍎", "🍌", "🍇"],
        "copies": 2,
        "bombs": 2,
        "timer": None,
        "mistakes": None
    },

    4: {
        "name": "Fighter",
        "emoji": "🥝",
        "fruits": [
            "🍎",
            "🍌",
            "🍇",
            "🥝",
            "🍓"
        ],
        "copies": 2,
        "bombs": 3,
        "timer": None,
        "mistakes": None
    },

    5: {
        "name": "Master",
        "emoji": "🍍",
        "fruits": [
            "🍎",
            "🍌",
            "🍇",
            "🥝",
            "🍓",
            "🍍"
        ],
        "copies": 2,
        "bombs": 4,
        "timer": None,
        "mistakes": None
    },

    6: {
        "name": "Legend",
        "emoji": "🍉",
        "fruits": [
            "🍎",
            "🍌",
            "🍇",
            "🥝",
            "🍓",
            "🍍"
        ],
        "copies": 3,
        "bombs": 6,
        "timer": 180,
        "mistakes": None
    },

    7: {
        "name": "Immortal",
        "emoji": "👑",
        "fruits": [
            "🍎",
            "🍌",
            "🍇",
            "🥝",
            "🍓",
            "🍍",
            "🍉"
        ],
        "copies": 3,
        "bombs": 7,
        "timer": 120,
        "mistakes": 3
    },

    8: {
        "name": "Demon",
        "emoji": "💀",
        "fruits": [
            "🍎",
            "🍌",
            "🍇",
            "🥝",
            "🍓",
            "🍍",
            "🍉",
            "🍒"
        ],
        "copies": 4,
        "bombs": 9,
        "timer": None,
        "mistakes": None
    },

    9: {
        "name": "Immortal God",
        "emoji": "👑🔥",
        "fruits": [
            "🍎",
            "🍌",
            "🍇",
            "🥝",
            "🍓",
            "🍍",
            "🍉",
            "🍒"
        ],
        "copies": 4,
        "bombs": 12,
        "timer": None,
        "mistakes": None
    }
}


# ============================================================
# PLAYER PROGRESS
# ============================================================

PROGRESS_FILE = "fruit_progress.json"

if os.path.exists(PROGRESS_FILE):

    try:

        with open(PROGRESS_FILE, "r") as f:
            unlocked_levels = json.load(f)

        unlocked_levels = {
            int(user_id): int(level)
            for user_id, level in unlocked_levels.items()
        }

    except Exception:

        unlocked_levels = {}

else:

    unlocked_levels = {}


def save_progress():

    try:

        with open(PROGRESS_FILE, "w") as f:
            json.dump(unlocked_levels, f)

    except Exception as e:

        print("Progress save error:", e)


def get_unlocked_level(user_id):

    return unlocked_levels.get(user_id, 1)


def unlock_next_level(user_id, current_level):

    current_unlocked = get_unlocked_level(user_id)

    if current_level < 9 and current_level >= current_unlocked:

        unlocked_levels[user_id] = current_level + 1

        save_progress()


# ============================================================
# COOLDOWNS
# ============================================================

cooldowns = {}

COOLDOWN_SECONDS = 5 * 60


def cooldown_remaining(user_id, level):

    key = (user_id, level)

    if key not in cooldowns:
        return 0

    remaining = cooldowns[key] - time.time()

    if remaining <= 0:

        del cooldowns[key]

        return 0

    return int(remaining)


def start_cooldown(user_id, level):

    if level in (6, 7):

        cooldowns[(user_id, level)] = (
            time.time() + COOLDOWN_SECONDS
        )


# ============================================================
# LEVEL SELECT
# ============================================================

class LevelSelect(discord.ui.Select):

    def __init__(self, player_id):

        self.player_id = player_id

        unlocked = get_unlocked_level(player_id)

        options = []

        for level in range(1, 10):

            data = LEVELS[level]

            if level <= unlocked:

                options.append(
                    discord.SelectOption(
                        label=f"Level {level} — {data['name']}",
                        description=f"Play {data['name']} level",
                        emoji=data["emoji"],
                        value=str(level)
                    )
                )

            else:

                options.append(
                    discord.SelectOption(
                        label=f"Level {level} — LOCKED",
                        description="Complete the previous level first",
                        emoji="🔒",
                        value=str(level)
                    )
                )

        super().__init__(
            placeholder="🎮 Choose a level...",
            min_values=1,
            max_values=1,
            options=options
        )


    async def callback(self, interaction: discord.Interaction):

        if interaction.user.id != self.player_id:

            await interaction.response.send_message(
                "❌ Ye level menu tumhara nahi hai!",
                ephemeral=True
            )

            return

        level = int(self.values[0])

        unlocked = get_unlocked_level(
            self.player_id
        )

        if level > unlocked:

            await interaction.response.send_message(
                "🔒 Ye level abhi locked hai!",
                ephemeral=True
            )

            return

        remaining = cooldown_remaining(
            self.player_id,
            level
        )

        if remaining > 0:

            minutes = remaining // 60
            seconds = remaining % 60

            await interaction.response.send_message(
                f"⏳ Level {level} cooldown active!\n"
                f"Try again in **{minutes}m {seconds}s**.",
                ephemeral=True
            )

            return

        game = FruitGame(
            self.player_id,
            level
        )

        await interaction.response.edit_message(
            content=game.start_message(),
            view=game
        )

        game.message = interaction.message

        if LEVELS[level]["timer"]:

            asyncio.create_task(
                game.start_timer()
            )


# ============================================================
# LEVEL MENU
# ============================================================

class LevelMenu(discord.ui.View):

    def __init__(self, player_id):

        super().__init__(timeout=180)

        self.add_item(
            LevelSelect(player_id)
        )


# ============================================================
# FRUIT GAME
# ============================================================

class FruitGame(discord.ui.View):

    # --------------------------------------------------------
    # Discord allows max 25 components in one View.
    # We use 20 cards + navigation buttons.
    # --------------------------------------------------------

    PAGE_SIZE = 20


    def __init__(self, player_id, level):

        super().__init__(
            timeout=LEVELS[level]["timer"] or 600
        )

        self.player_id = player_id

        self.level = level

        self.data = LEVELS[level]

        self.finished = False

        self.message = None

        self.current_page = 0

        self.revealed = set()

        self.completed_groups = set()

        self.mistakes = 0

        self.start_time = time.time()

        # ----------------------------------------------------
        # CREATE CARDS
        # ----------------------------------------------------

        self.cards = []

        for fruit in self.data["fruits"]:

            for _ in range(self.data["copies"]):

                self.cards.append(fruit)

        # Add bombs

        for _ in range(self.data["bombs"]):

            self.cards.append("💣")

        random.shuffle(self.cards)

        self.total_pages = (
            len(self.cards) + self.PAGE_SIZE - 1
        ) // self.PAGE_SIZE

        self.build_page()


    # ========================================================
    # BUILD PAGE
    # ========================================================

    def build_page(self):

        self.clear_items()

        start = (
            self.current_page *
            self.PAGE_SIZE
        )

        end = min(
            start + self.PAGE_SIZE,
            len(self.cards)
        )

        for index in range(start, end):

            button = discord.ui.Button(
                label=(
                    self.cards[index]
                    if index in self.revealed
                    else "❓"
                ),
                style=(
                    discord.ButtonStyle.secondary
                    if index in self.revealed
                    else discord.ButtonStyle.primary
                ),
                row=(index - start) // 5
            )

            button.callback = self.make_callback(
                index
            )

            self.add_item(button)

        # ----------------------------------------------------
        # NAVIGATION
        # ----------------------------------------------------

        navigation_row = 4

        if self.current_page > 0:

            previous_button = discord.ui.Button(
                label="Previous",
                emoji="⬅️",
                style=discord.ButtonStyle.secondary,
                row=navigation_row
            )

            previous_button.callback = (
                self.previous_page
            )

            self.add_item(previous_button)

        if self.current_page < self.total_pages - 1:

            next_button = discord.ui.Button(
                label="Next",
                emoji="➡️",
                style=discord.ButtonStyle.success,
                row=navigation_row
            )

            next_button.callback = (
                self.next_page
            )

            self.add_item(next_button)

        exit_button = discord.ui.Button(
            label="EXIT",
            emoji="❌",
            style=discord.ButtonStyle.danger,
            row=navigation_row
        )

        exit_button.callback = self.exit_game

        self.add_item(exit_button)


    # ========================================================
    # START MESSAGE
    # ========================================================

    def start_message(self):

        title = self.data["name"]

        fruit_count = len(
            self.data["fruits"]
        )

        copies = self.data["copies"]

        total = len(self.cards)

        message = (

            f"{self.data['emoji']} "
            f"**LEVEL {self.level} — "
            f"{title.upper()}**\n\n"

            f"🎴 Cards: **{total}**\n"

            f"🍎 Matching fruit groups: "
            f"**{fruit_count}**\n"

            f"🔢 Find **{copies} matching fruits** "
            f"of each type\n"

            f"💣 Bombs: "
            f"**{self.data['bombs']}**\n\n"
        )

        if self.data["timer"]:

            minutes = self.data["timer"] // 60

            message += (
                f"⏱️ **TIME LIMIT: "
                f"{minutes} MINUTES**\n\n"
            )

        if self.data["mistakes"]:

            message += (
                f"❤️ Mistakes allowed: "
                f"**{self.data['mistakes']}**\n\n"
            )

        message += (
            f"📄 Board **1/{self.total_pages}**\n\n"
            "👇 Choose the cards!"
        )

        return message


    # ========================================================
    # CARD CALLBACK
    # ========================================================

    def make_callback(self, index):

        async def callback(
            interaction: discord.Interaction
        ):

            # ------------------------------------------------
            # PLAYER CHECK
            # ------------------------------------------------

            if interaction.user.id != self.player_id:

                await interaction.response.send_message(
                    "❌ Ye game tumhara nahi hai!",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # FINISHED CHECK
            # ------------------------------------------------

            if self.finished:

                await interaction.response.send_message(
                    "❌ Game already finished!",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # ALREADY REVEALED
            # ------------------------------------------------

            if index in self.revealed:

                await interaction.response.send_message(
                    "⚠️ Ye card already reveal ho chuka hai!",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # TIMER CHECK
            # ------------------------------------------------

            timer = self.data["timer"]

            if timer:

                elapsed = (
                    time.time() -
                    self.start_time
                )

                if elapsed >= timer:

                    await self.fail_game(
                        interaction,
                        "⏰ **TIME'S UP!**"
                    )

                    return

            # ------------------------------------------------
            # REVEAL CARD
            # ------------------------------------------------

            self.revealed.add(index)

            card = self.cards[index]

            # ------------------------------------------------
            # BOMB
            # ------------------------------------------------

            if card == "💣":

                await self.fail_game(
                    interaction,
                    "💥 **BOOM!**\n\n"
                    "You clicked a bomb!"
                )

                return

            # ------------------------------------------------
            # CHECK GROUP
            # ------------------------------------------------

            matching_indexes = [

                i for i in self.revealed

                if self.cards[i] == card

            ]

            required = self.data["copies"]

            # ------------------------------------------------
            # COMPLETE GROUP
            # ------------------------------------------------

            if len(matching_indexes) == required:

                self.completed_groups.add(card)

            # ------------------------------------------------
            # LEVEL 7 MISTAKES
            # ------------------------------------------------

            if self.level == 7:

                if len(matching_indexes) < required:

                    self.mistakes += 1

                    if (
                        self.mistakes >
                        self.data["mistakes"]
                    ):

                        await self.fail_game(
                            interaction,
                            "💀 **TOO MANY MISTAKES!**"
                        )

                        return

            # ------------------------------------------------
            # WIN CHECK
            # ------------------------------------------------

            if (
                len(self.completed_groups) ==
                len(self.data["fruits"])
            ):

                await self.complete_game(
                    interaction
                )

                return

            # ------------------------------------------------
            # UPDATE PAGE
            # ------------------------------------------------

            self.build_page()

            remaining_groups = (
                len(self.data["fruits"]) -
                len(self.completed_groups)
            )

            await interaction.response.edit_message(

                content=(

                    f"{self.data['emoji']} "
                    f"**LEVEL {self.level} — "
                    f"{self.data['name'].upper()}**\n\n"

                    f"🏆 Groups complete: "
                    f"**{len(self.completed_groups)}/"
                    f"{len(self.data['fruits'])}**\n"

                    f"🎯 Groups remaining: "
                    f"**{remaining_groups}**\n"

                    f"💣 Avoid the bombs!\n"

                    f"📄 Board "
                    f"**{self.current_page + 1}/"
                    f"{self.total_pages}**"
                ),

                view=self
            )

        return callback


    # ========================================================
    # NEXT PAGE
    # ========================================================

    async def next_page(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.player_id:

            await interaction.response.send_message(
                "❌ Ye game tumhara nahi hai!",
                ephemeral=True
            )

            return

        if self.finished:

            await interaction.response.send_message(
                "❌ Game already finished!",
                ephemeral=True
            )

            return

        if (
            self.current_page <
            self.total_pages - 1
        ):

            self.current_page += 1

        self.build_page()

        await interaction.response.edit_message(
            content=self.game_status(),
            view=self
        )


    # ========================================================
    # PREVIOUS PAGE
    # ========================================================

    async def previous_page(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.player_id:

            await interaction.response.send_message(
                "❌ Ye game tumhara nahi hai!",
                ephemeral=True
            )

            return

        if self.finished:

            await interaction.response.send_message(
                "❌ Game already finished!",
                ephemeral=True
            )

            return

        if self.current_page > 0:

            self.current_page -= 1

        self.build_page()

        await interaction.response.edit_message(
            content=self.game_status(),
            view=self
        )


    # ========================================================
    # GAME STATUS
    # ========================================================

    def game_status(self):

        status = (

            f"{self.data['emoji']} "
            f"**LEVEL {self.level} — "
            f"{self.data['name'].upper()}**\n\n"

            f"🏆 Groups complete: "
            f"**{len(self.completed_groups)}/"
            f"{len(self.data['fruits'])}**\n"

            f"💣 Bombs remaining hidden!\n"

            f"📄 Board "
            f"**{self.current_page + 1}/"
            f"{self.total_pages}**"
        )

        if self.level == 7:

            status += (

                f"\n❤️ Mistakes: "
                f"**{self.mistakes}/"
                f"{self.data['mistakes']}**"
            )

        return status


    # ========================================================
    # COMPLETE LEVEL
    # ========================================================

    async def complete_game(
        self,
        interaction: discord.Interaction
    ):

        self.finished = True

        unlock_next_level(
            self.player_id,
            self.level
        )

        self.clear_items()

        if self.level == 9:

            content = (

                "👑🔥 **IMMORTAL GOD LEVEL COMPLETE!** 🔥👑\n\n"

                "🏆 You have conquered all 9 levels!\n\n"

                "🌟 **YOU ARE THE IMMORTAL GOD!**"
            )

        else:

            next_level = self.level + 1

            next_name = LEVELS[
                next_level
            ]["name"]

            content = (

                f"🎉 **LEVEL {self.level} COMPLETE!**\n\n"

                f"🏆 Rank: "
                f"**{self.data['name']}**\n\n"

                f"🔓 **LEVEL {next_level} — "
                f"{next_name} UNLOCKED!**\n\n"

                "Use `/fruits` to choose your "
                "next level."
            )

        await interaction.response.edit_message(
            content=content,
            view=self
        )


    # ========================================================
    # FAIL GAME
    # ========================================================

    async def fail_game(
        self,
        interaction,
        reason
    ):

        self.finished = True

        start_cooldown(
            self.player_id,
            self.level
        )

        self.clear_items()

        cooldown_text = ""

        if self.level in (6, 7):

            cooldown_text = (

                "\n\n⏳ You cannot replay this level "
                "for **5 minutes**."
            )

        await interaction.response.edit_message(

            content=(

                f"{reason}\n\n"

                f"❌ **LEVEL {self.level} FAILED!**"

                f"{cooldown_text}\n\n"

                "Use `/fruits` to try an available level."
            ),

            view=self
        )


    # ========================================================
    # TIMER
    # ========================================================

    async def start_timer(self):

        timer = self.data["timer"]

        if not timer:
            return

        await asyncio.sleep(timer)

        if self.finished:
            return

        self.finished = True

        start_cooldown(
            self.player_id,
            self.level
        )

        self.clear_items()

        if self.message is None:
            return

        try:

            await self.message.edit(

                content=(

                    "⏰ **TIME'S UP!**\n\n"

                    f"❌ **LEVEL {self.level} FAILED!**\n\n"

                    "⏳ You cannot replay this level "
                    "for **5 minutes**."
                ),

                view=self
            )

        except Exception as e:

            print("Timer message error:", e)


    # ========================================================
    # EXIT
    # ========================================================

    async def exit_game(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.player_id:

            await interaction.response.send_message(
                "❌ Ye game tumhara nahi hai!",
                ephemeral=True
            )

            return

        self.finished = True

        self.clear_items()

        await interaction.response.edit_message(
            content="👋 **Game ended!**",
            view=self
        )


    # ========================================================
    # VIEW TIMEOUT
    # ========================================================

    async def on_timeout(self):

        if self.finished:
            return

        self.finished = True

        self.clear_items()

        if self.message is None:
            return

        try:

            await self.message.edit(
                content="⌛ **Game session expired!**",
                view=self
            )

        except Exception:

            pass


# ============================================================
# /FRUITS COMMAND
# ============================================================

@tree.command(
    name="fruits",
    description="Open the Fruit Match level selection!"
)
async def fruits(
    interaction: discord.Interaction
):

    unlocked = get_unlocked_level(
        interaction.user.id
    )

    embed = discord.Embed(

        title="🍎🍌 FRUIT MATCH 🍇🥝",

        description=(

            "🎮 **Choose your level!**\n\n"

            f"🔓 Your highest unlocked level: "
            f"**{unlocked}/9**\n\n"

            "Complete a level to unlock "
            "the next one!"
        )
    )

    view = LevelMenu(
        interaction.user.id
    )

    await interaction.response.send_message(
        embed=embed,
        view=view
    )


# ============================================================
# /FRUITPROGRESS COMMAND
# ============================================================

@tree.command(
    name="fruitprogress",
    description="Check your Fruit Match progress!"
)
async def fruitprogress(
    interaction: discord.Interaction
):

    unlocked = get_unlocked_level(
        interaction.user.id
    )

    if unlocked >= 9:

        status = (
            "👑 **IMMORTAL GOD UNLOCKED!**"
        )

    else:

        next_level = unlocked + 1

        next_name = LEVELS[
            next_level
        ]["name"]

        status = (

            f"🔓 Highest unlocked: "
            f"**Level {unlocked}/9**\n\n"

            f"🎯 Next goal: "
            f"**Level {next_level} — "
            f"{next_name}**"
        )

    await interaction.response.send_message(

        f"🍎 **FRUIT MATCH PROGRESS** 🍎\n\n"
        f"{status}\n\n"
        "Use `/fruits` to play!"
    )


# ============================================================
# BOT READY
# ============================================================

@client.event
async def on_ready():

    try:

        await tree.sync()

        print(
            f"✅ Logged in as {client.user}"
        )

        print(
            "🍎 Fruit Match Bot is ONLINE!"
        )

        print(
            "🎮 Slash commands synced!"
        )

    except Exception as e:

        print(
            "❌ Command sync error:",
            e
        )


# ============================================================
# START BOT
# ============================================================

if TOKEN == "PASTE_NEW_TOKEN_HERE":

    print(
        "❌ ERROR: Please put your NEW Discord bot token "
        "inside TOKEN."
    )

else:

    client.run(TOKEN)    