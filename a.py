import discord
from discord.ext import commands, tasks
import random
import json
import os
from dotenv import load_dotenv

load_dotenv(".env")
TOKEN = os.getenv('BOT_TOKEN')
GUILD = os.getenv('GUILD')

intents = discord.Intents.all()
intents.members = True
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

CATEGORY_ID = 1245417060989927424

if not os.path.exists("economy.json"):
    with open("economy.json", "w") as f:
        json.dump({}, f)

with open("economy.json", "r") as f:
    economy_data = json.load(f)

def save_economy():
    with open("economy.json", "w") as f:
        json.dump(economy_data, f)

@bot.command(name="balance")
async def balance(ctx):
    user_id = str(ctx.author.id)
    candies = economy_data.get(user_id, {}).get("candies", 0)
    points = economy_data.get(user_id, {}).get("points", 0)

    embed = discord.Embed(title=f"{ctx.author.name}'s Balance", color=discord.Color.purple())
    embed.add_field(name="Candies", value=candies, inline=True)
    embed.add_field(name="Points", value=points, inline=True)
    await ctx.send(embed=embed)

class HalloweenGames(discord.ui.View):  
    def __init__(self, invoker):  
        super().__init__(timeout=180)  
        self.invoker = invoker  

    @discord.ui.select(  
        placeholder="Choose a game",  
        min_values=1,  
        max_values=1,  
        options=[  
            discord.SelectOption(label="Pumpkin Smash", description="Rock-Paper-Scissors with a Halloween twist"),  
            discord.SelectOption(label="Ghost Guess", description="Guess where the ghost is hiding"),  
            discord.SelectOption(label="Witch's Coin Flip", description="Flip a cursed coin"),  
            discord.SelectOption(label="Skeleton Dice Roll", description="Roll against a skeleton"),  
            discord.SelectOption(label="Vampire Card Draw", description="Draw from Dracula's deck"),  
            discord.SelectOption(label="Monster Battle", description="Higher or Lower battle"),  
            discord.SelectOption(label="Zombie Trivia", description="Answer Halloween trivia"),  
            discord.SelectOption(label="Cauldron Math", description="Solve spooky math problems"),  
            discord.SelectOption(label="Memory of the Dead", description="Match creepy items"),  
            discord.SelectOption(label="Spooky Word Scramble", description="Unscramble a Halloween word"),  
        ]  
    )  
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):  
        if interaction.user and self.invoker.id != interaction.user.id:  
            await interaction.response.send_message("You can't play this game. Only the person who invoked can play.", ephemeral=True)  
            return

        selected_game = select.values[0]

        if selected_game == "Pumpkin Smash":
            await self.pumpkin_smash(interaction)
        elif selected_game == "Ghost Guess":
            await self.ghost_guess(interaction)
        elif selected_game == "Witch's Coin Flip":
            await self.coin_flip(interaction)
        elif selected_game == "Skeleton Dice Roll":
            await self.dice_roll(interaction)
        elif selected_game == "Vampire Card Draw":
            await self.card_draw(interaction)
        elif selected_game == "Monster Battle":
            await self.monster_battle(interaction)
        elif selected_game == "Zombie Trivia":
            await self.zombie_trivia(interaction)
        elif selected_game == "Cauldron Math":
            await self.cauldron_math(interaction)
        elif selected_game == "Memory of the Dead":
            await self.memory_of_the_dead(interaction)
        elif selected_game == "Spooky Word Scramble":
            await self.word_scramble(interaction)

    async def pumpkin_smash(self, interaction):
        choices = ["pumpkin", "witch", "ghost"]
        bot_choice = random.choice(choices)

        def check_winner(user_choice, bot_choice):
            if user_choice == bot_choice:
                return "It's a tie!"
            elif (user_choice == "pumpkin" and bot_choice == "ghost") or \
                 (user_choice == "witch" and bot_choice == "pumpkin") or \
                 (user_choice == "ghost" and bot_choice == "witch"):
                return "You win!"
            else:
                return "You lose!"

        await interaction.response.send_message(f"Choose: pumpkin, witch, or ghost.")

        try:
            msg = await bot.wait_for(
                "message",
                check=lambda message: message.author == interaction.user and message.content.lower() in choices,
                timeout=20.0
            )
            user_choice = msg.content.lower()
            result = check_winner(user_choice, bot_choice)

            reward = random.randint(1, 10) if result == "You win!" else random.randint(1, 5)
            user_id = str(interaction.user.id)
            economy_data[user_id]["candies"] += reward
            save_economy()

            embed = discord.Embed(title="Pumpkin Smash", color=discord.Color.orange())
            embed.add_field(name="Your choice", value=user_choice, inline=True)
            embed.add_field(name="Bot's choice", value=bot_choice, inline=True)
            embed.add_field(name="Result", value=result, inline=False)
            embed.add_field(name="Candies earned", value=reward, inline=False)

            await interaction.channel.send(embed=embed)

        except discord.ext.commands.errors.CommandInvokeError:
            await interaction.response.send_message(f"Timed out! Please respond faster next time.")

    async def ghost_guess(self, interaction):
        await interaction.response.send_message("Guess which haunted house the ghost is hiding in (1-5).")

        ghost_house = random.randint(1, 5)

        def check_winner(user_guess, ghost_house):
            return "You found the ghost!" if user_guess == ghost_house else "Wrong guess! The ghost wasn't there."

        try:
            msg = await bot.wait_for(
                "message",
                check=lambda message: message.author == interaction.user and message.content.isdigit(),
                timeout=20.0
            )
            user_guess = int(msg.content)
            result = check_winner(user_guess, ghost_house)

            reward = random.randint(5, 15) if result == "You found the ghost!" else 0
            user_id = str(interaction.user.id)
            economy_data[user_id]["candies"] += reward
            save_economy()

            embed = discord.Embed(title="Ghost Guess", color=discord.Color.purple())
            embed.add_field(name="Your guess", value=user_guess, inline=True)
            embed.add_field(name="Ghost's house", value=ghost_house, inline=True)
            embed.add_field(name="Result", value=result, inline=False)
            embed.add_field(name="Candies earned", value=reward, inline=False)
            await interaction.channel.send(embed=embed)

        except discord.ext.commands.errors.CommandInvokeError:
            await interaction.response.send_message(f"Timed out! Please respond faster next time.")

    async def coin_flip(self, interaction):
        outcome = random.choice(["heads", "tails"])

        def check_winner(user_choice, outcome):
            return "You guessed correctly!" if user_choice == outcome else "You guessed wrong!"

        await interaction.response.send_message(f"Choose: heads or tails.")

        try:
            msg = await bot.wait_for(
                "message",
                check=lambda message: message.author == interaction.user and message.content.lower() in ["heads", "tails"],
                timeout=20.0
            )
            user_choice = msg.content.lower()
            result = check_winner(user_choice, outcome)

            reward = random.randint(5, 10) if result == "You guessed correctly!" else 0
            user_id = str(interaction.user.id)
            economy_data[user_id]["candies"] += reward
            save_economy()

            embed = discord.Embed(title="Witch's Coin Flip", color=discord.Color.dark_gold())
            embed.add_field(name="Your choice", value=user_choice, inline=True)
            embed.add_field(name="Coin outcome", value=outcome, inline=True)
            embed.add_field(name="Result", value=result, inline=False)
            embed.add_field(name="Candies earned", value=reward, inline=False)
            await interaction.channel.send(embed=embed)

        except discord.ext.commands.errors.CommandInvokeError:
            await interaction.response.send_message(f"Timed out! Please respond faster next time.")

    async def dice_roll(self, interaction):
        await interaction.response.send_message("Roll a die against the skeleton. Type `roll`.")

        skeleton_roll = random.randint(1, 6)

        try:
            msg = await bot.wait_for(
                "message",
                check=lambda message: message.author == interaction.user and message.content.lower() == "roll",
                timeout=20.0
            )
            user_roll = random.randint(1, 6)

            result = "You win!" if user_roll > skeleton_roll else "You lose!"
            reward = random.randint(5, 15) if user_roll > skeleton_roll else 0
            user_id = str(interaction.user.id)
            economy_data[user_id]["candies"] += reward
            save_economy()

            embed = discord.Embed(title="Skeleton Dice Roll", color=discord.Color.red())
            embed.add_field(name="Your roll", value=user_roll, inline=True)
            embed.add_field(name="Skeleton's roll", value=skeleton_roll, inline=True)
            embed.add_field(name="Result", value=result, inline=False)
            embed.add_field(name="Candies earned", value=reward, inline=False)
            await interaction.channel.send(embed=embed)

        except discord.ext.commands.errors.CommandInvokeError:
            await interaction.response.send_message(f"Timed out! Please respond faster next time.")

async def card_draw(self, interaction):
    await interaction.response.send_message("Draw a card from Dracula's deck (1-10).")

    vampire_card = random.randint(1, 10)

    try:
        msg = await bot.wait_for(
            "message",
            check=lambda message: message.author == interaction.user and message.content.isdigit(),
            timeout=20.0
        )
        user_card = int(msg.content)

        result = "You win!" if user_card > vampire_card else "You lose!"
        reward = random.randint(10, 20) if user_card > vampire_card else 0
        user_id = str(interaction.user.id)
        economy_data[user_id]["candies"] += reward
        save_economy()

        embed = discord.Embed(title="Vampire Card Draw", color=discord.Color.dark_red())
        embed.add_field(name="Your card", value=user_card, inline=True)
        embed.add_field(name="Vampire's card", value=vampire_card, inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        embed.add_field(name="Candies earned", value=reward, inline=False)
        await interaction.channel.send(embed=embed)

    except discord.ext.commands.errors.CommandInvokeError:
        await interaction.response.send_message(f"Timed out! Please respond faster next time.")

async def monster_battle(self, interaction):
    await interaction.response.send_message("Guess if the next number is higher or lower (1-10).")

    monster_number = random.randint(1, 10)

    try:
        msg = await bot.wait_for(
            "message",
            check=lambda message: message.author == interaction.user and message.content.isdigit(),
            timeout=20.0
        )
        user_guess = int(msg.content)

        next_monster_number = random.randint(1, 10)
        result = "You guessed correctly!" if (user_guess < next_monster_number) else "You guessed wrong!"
        reward = random.randint(5, 15) if result == "You guessed correctly!" else 0
        user_id = str(interaction.user.id)
        economy_data[user_id]["candies"] += reward
        save_economy()

        embed = discord.Embed(title="Monster Battle", color=discord.Color.green())
        embed.add_field(name="Your guess", value=user_guess, inline=True)
        embed.add_field(name="Next monster number", value=next_monster_number, inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        embed.add_field(name="Candies earned", value=reward, inline=False)
        await interaction.channel.send(embed=embed)

    except discord.ext.commands.errors.CommandInvokeError:
        await interaction.response.send_message(f"Timed out! Please respond faster next time.")

async def zombie_trivia(self, interaction):
    questions = {
        "What do zombies eat?": ["brains", "people", "flesh"],
        "What is the most famous zombie movie?": ["Night of the Living Dead", "Zombieland", "World War Z"],
        "How do you kill a zombie?": ["headshot", "fire", "dismemberment"]
    }

    question, answers = random.choice(list(questions.items()))
    correct_answer = answers[0]

    await interaction.response.send_message(f"Trivia Question: {question}\nOptions: {', '.join(answers)}")

    try:
        msg = await bot.wait_for(
            "message",
            check=lambda message: message.author == interaction.user and message.content in answers,
            timeout=20.0
        )
        user_answer = msg.content

        result = "Correct!" if user_answer == correct_answer else "Wrong answer!"
        reward = 10 if user_answer == correct_answer else 0
        user_id = str(interaction.user.id)
        economy_data[user_id]["candies"] += reward
        save_economy()

        embed = discord.Embed(title="Zombie Trivia", color=discord.Color.green())
        embed.add_field(name="Your answer", value=user_answer, inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        embed.add_field(name="Candies earned", value=reward, inline=False)
        await interaction.channel.send(embed=embed)

    except discord.ext.commands.errors.CommandInvokeError:
        await interaction.response.send_message(f"Timed out! Please respond faster next time.")

async def cauldron_math(self, interaction):
    num1, num2 = random.randint(1, 10), random.randint(1, 10)
    correct_answer = num1 + num2

    await interaction.response.send_message(f"What is {num1} + {num2}?")

    try:
        msg = await bot.wait_for(
            "message",
            check=lambda message: message.author == interaction.user and message.content.isdigit(),
            timeout=20.0
        )
        user_answer = int(msg.content)

        result = "Correct!" if user_answer == correct_answer else "Wrong answer!"
        reward = 10 if user_answer == correct_answer else 0
        user_id = str(interaction.user.id)
        economy_data[user_id]["candies"] += reward
        save_economy()

        embed = discord.Embed(title="Cauldron Math", color=discord.Color.blue())
        embed.add_field(name="Your answer", value=user_answer, inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        embed.add_field(name="Candies earned", value=reward, inline=False)
        await interaction.channel.send(embed=embed)

    except discord.ext.commands.errors.CommandInvokeError:
        await interaction.response.send_message(f"Timed out! Please respond faster next time.")

async def memory_of_the_dead(self, interaction):
    items = ["bat", "witch", "ghost", "pumpkin", "skeleton", "zombie"]
    random_items = random.sample(items, 2) * 2
    random.shuffle(random_items)

    await interaction.response.send_message("Memorize these items: " + ", ".join(random_items))

    await discord.utils.sleep(10)

    await interaction.followup.send("Now, guess the first item!")

    try:
        msg = await bot.wait_for(
            "message",
            check=lambda message: message.author == interaction.user and message.content in items,
            timeout=20.0
        )
        user_guess = msg.content

        if user_guess in random_items:
            reward = 10
            user_id = str(interaction.user.id)
            economy_data[user_id]["candies"] += reward
            save_economy()
            result = "Correct!"
        else:
            reward = 0
            result = "Wrong guess!"

        embed = discord.Embed(title="Memory of the Dead", color=discord.Color.yellow())
        embed.add_field(name="Your guess", value=user_guess, inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        embed.add_field(name="Candies earned", value=reward, inline=False)
        await interaction.channel.send(embed=embed)

    except discord.ext.commands.errors.CommandInvokeError:
        await interaction.response.send_message(f"Timed out! Please respond faster next time.")

async def word_scramble(self, interaction):
    words = ["pumpkin", "skeleton", "ghost", "vampire", "zombie"]
    chosen_word = random.choice(words)
    scrambled_word = ''.join(random.sample(chosen_word, len(chosen_word)))

    await interaction.response.send_message(f"Unscramble the word: {scrambled_word}")

    try:
        msg = await bot.wait_for(
            "message",
            check=lambda message: message.author == interaction.user and message.content == chosen_word,
            timeout=20.0
        )

        user_answer = msg.content
        reward = 10
        user_id = str(interaction.user.id)
        economy_data[user_id]["candies"] += reward
        save_economy()

        embed = discord.Embed(title="Spooky Word Scramble", color=discord.Color.pink())
        embed.add_field(name="Your answer", value=user_answer, inline=True)
        embed.add_field(name="Result", value="Correct!", inline=False)
        embed.add_field(name="Candies earned", value=reward, inline=False)
        await interaction.channel.send(embed=embed)

    except discord.ext.commands.errors.CommandInvokeError:
        await interaction.response.send_message(f"Timed out! Please respond faster next time.")

@bot.command(name="playgame")
async def playgame(ctx):
    user_id = str(ctx.author.id)

    if user_id not in economy_data:
        economy_data[user_id] = {"candies": 0, "points": 0}

    await ctx.send("Choose a Halloween game to play!", view=HalloweenGames(ctx.author))

async def spawn_trick_or_treat():
    guilds = bot.guilds
    for guild in guilds:
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)
        if category:
            channels = [channel for channel in category.text_channels if channel.permissions_for(guild.me).send_messages]
            if channels:
                channel = random.choice(channels)

                class TrickOrTreatButton(discord.ui.View):
                    @discord.ui.button(label="Trick or Treat!", style=discord.ButtonStyle.green)
                    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
                        user_id = str(interaction.user.id)

                        if user_id not in economy_data:
                            economy_data[user_id] = {"candies": 0, "points": 0}

                        outcome = random.choice(["treat", "trick"])
                        if outcome == "treat":
                            candies_found = random.randint(1, 10)
                            economy_data[user_id]["candies"] += candies_found
                            result = f"{interaction.user.mention} found {candies_found} candies!"
                        else:
                            points_lost = random.randint(1, 5)
                            economy_data[user_id]["points"] -= points_lost
                            result = f"{interaction.user.mention} got a trick and lost {points_lost} points!"

                        save_economy()

                        button.disabled = True
                        await interaction.response.edit_message(content=f"🎃 {result}", view=self)

                await channel.send("🎃 **Trick or Treat!** Press the button below to see what you get!", view=TrickOrTreatButton())

@bot.command(name="reset")
async def reset(ctx):
    user_id = str(ctx.author.id)

    if user_id in economy_data:
        economy_data[user_id] = {"candies": 0, "points": 0}
        save_economy()
        await ctx.send("Your candies and points have been reset to zero.")
    else:
        await ctx.send("You don't have any candies or points to reset.")

random_mins = random.randint(1, 10)
@tasks.loop(minutes=random_mins)
async def spawn_task():
    await spawn_trick_or_treat()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    spawn_task.start()

bot.run(TOKEN)