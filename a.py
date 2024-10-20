import discord
from discord import app_commands
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

bot.remove_command('help')

CATEGORY_ID = 1245417060989927424

if not os.path.exists("economy.json"):
    with open("economy.json", "w") as f:
        json.dump({}, f)

with open("economy.json", "r") as f:
    economy_data = json.load(f)

def load_economy():
    with open("economy.json", "r") as f:
        return json.load(f)

def save_economy(data):
    with open("economy.json", "w") as f:
        json.dump(data, f)

@bot.hybrid_command(name="balance", description="Display your balance")
async def balance(ctx):
    user_id = str(ctx.author.id)
    candies = economy_data.get(user_id, {}).get("candies", 0)

    embed = discord.Embed(title=f"{ctx.author.name}'s Balance", color=discord.Color.purple())
    embed.add_field(name="Candies", value=candies, inline=True)
    if isinstance(ctx.channel, discord.TextChannel):
        await ctx.send(embed=embed)
        await ctx.message.delete()
    else:
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
            discord.SelectOption(label="Pumpkin Smash", description="Rock-Paper-Scissors with a spooky twist"),  
            discord.SelectOption(label="Ghost Guess", description="Guess where the ghost is hiding"),  
            discord.SelectOption(label="Witch's Coin Flip", description="Flip a cursed coin"),  
            discord.SelectOption(label="Skeleton Dice Roll", description="Roll a dice against a skeleton"),  
            discord.SelectOption(label="Vampire Card Draw", description="Draw from Dracula's deck of cards"),  
            discord.SelectOption(label="Monster Battle", description="Higher or Lower battle against a monster"),    
            discord.SelectOption(label="Cauldron Math", description="Solve spooky math problems") 
        ]  
    )  
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user and self.invoker.id != interaction.user.id:
            await interaction.response.send_message("You can't play this game. Only the person who invoked can play.", ephemeral=True)
            return

        selected_game = select.values[0]

        await interaction.message.delete()

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
        elif selected_game == "Cauldron Math":
            await self.cauldron_math(interaction)

    # Game: Pumpkin Smash (Rock-Paper-Scissors variant)
    async def pumpkin_smash(self, interaction):
        class PumpkinSmashView(discord.ui.View):
            @discord.ui.button(label="🎃", style=discord.ButtonStyle.secondary)
            async def pumpkin_button(self, interaction, button):
                await self.play_game(interaction, "🎃")
            @discord.ui.button(label="🧙", style=discord.ButtonStyle.secondary)
            async def witch_button(self, interaction, button):
                await self.play_game(interaction, "🧙")
            @discord.ui.button(label="👻", style=discord.ButtonStyle.secondary)
            async def ghost_button(self, interaction, button):
                await self.play_game(interaction, "👻")

            async def play_game(self, interaction, user_choice):
                bot_choice = random.choice(["🎃", "🧙", "👻"])
                result = self.check_winner(user_choice, bot_choice)
                smash_yes_reward = 0
                smash_no_reward = 0
                if result == "You win!":
                    smash_yes_reward = random.randint(1, 5)
                elif result == "It's a tie!":
                    smash_yes_reward = random.randint(1, 5)
                else:
                    smash_no_reward = random.randint(1,5)
                user_id = str(interaction.user.id)
                if user_id not in economy_data:
                    economy_data[user_id] = {"candies": 0}  # Initialize user data if not present
                user_id = str(interaction.user.id)
                economy_data[user_id]["candies"] += smash_yes_reward
                economy_data[user_id]["candies"] -= smash_no_reward
                save_economy(economy_data)
                user_display_name = interaction.user.display_name
                user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
                embed = discord.Embed(title="Pumpkin Smash", color=discord.Color.orange())
                embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
                embed.add_field(name="You:", value=user_choice, inline=True)
                embed.add_field(name="Bot:", value=bot_choice, inline=True)
                embed.add_field(name="Result:", value=result, inline=False)
                if result == "You win!":
                    embed.add_field(name="Reward", value=f"+{smash_yes_reward} candies", inline=False)
                elif result == "It's a tie!":
                    embed.add_field(name="Reward", value=f"+{smash_yes_reward} candies", inline=False)
                else:
                    embed.add_field(name="Reward", value=f"-{smash_no_reward} candies", inline=False)
                await interaction.channel.send(embed=embed)
                await interaction.message.delete()

            def check_winner(self, user_choice, bot_choice):
                if user_choice == bot_choice:
                    return "It's a tie!"
                elif (user_choice == "🎃" and bot_choice == "👻") or \
                     (user_choice == "🧙" and bot_choice == "🎃") or \
                     (user_choice == "👻" and bot_choice == "🧙"):
                    return "You win!"
                else:
                    return "You lose!"

        buttonchoiceembedtest = discord.Embed(title="Choose: 🎃, 🧙, or 👻", color=discord.Color.orange())
        user_display_name = interaction.user.display_name
        user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        buttonchoiceembedtest.set_footer(text=user_display_name, icon_url=user_avatar_url)
        buttonchoiceembedtest.set_author(name=f"Pumpkin Smash", icon_url="https://media.discordapp.net/attachments/1198631394046386205/1297232346302386227/pumpkin.jpeg?ex=67152d44&is=6713dbc4&hm=339658cdb7190789f72980b94a2d06b4cba0beb6fe827145d56d8202442db687&=&format=webp&width=671&height=671")
        await interaction.response.send_message(embed=buttonchoiceembedtest, view=PumpkinSmashView())

    # Game: Ghost Guess
    async def ghost_guess(self, interaction):
        ghost_house = random.randint(1, 5)

        class GhostGuessView(discord.ui.View):
            @discord.ui.button(label="1️⃣", style=discord.ButtonStyle.secondary)
            async def button_1(self, interaction, button):
                await self.check_house(interaction, 1)
            @discord.ui.button(label="2️⃣", style=discord.ButtonStyle.secondary)
            async def button_2(self, interaction, button):
                await self.check_house(interaction, 2)
            @discord.ui.button(label="3️⃣", style=discord.ButtonStyle.secondary)
            async def button_3(self, interaction, button):
                await self.check_house(interaction, 3)  
            @discord.ui.button(label="4️⃣", style=discord.ButtonStyle.secondary)
            async def button_4(self, interaction, button):
                await self.check_house(interaction, 4)
            @discord.ui.button(label="5️⃣", style=discord.ButtonStyle.secondary)
            async def button_5(self, interaction, button):
                await self.check_house(interaction, 5)
            async def check_house(self, interaction, user_guess):
                result = "You found the ghost!" if user_guess == ghost_house else "Wrong guess! The ghost wasn't there."
                ghost_yes_reward = 0
                ghost_no_reward = 0
                if result == "You found the ghost!":
                    ghost_yes_reward = random.randint(1, 5)
                else:
                    ghost_no_reward = random.randint(1,5)
                user_id = str(interaction.user.id)
                if user_id not in economy_data:
                    economy_data[user_id] = {"candies": 0}  # Initialize user data if not present
                user_id = str(interaction.user.id)
                economy_data[user_id]["candies"] += ghost_yes_reward
                economy_data[user_id]["candies"] -= ghost_no_reward
                save_economy(economy_data)
                embed = discord.Embed(title="Ghost Guess", color=discord.Color.dark_blue())
                user_display_name = interaction.user.display_name
                user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
                embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
                embed.add_field(name="You:", value=user_guess, inline=True)
                embed.add_field(name="Ghost:", value=ghost_house, inline=True)
                embed.add_field(name="Result:", value=result, inline=False)
                if result == "You found the ghost!":
                    embed.add_field(name="Reward:", value=f"+{ghost_yes_reward} candies", inline=False)
                else:
                    embed.add_field(name="Reward:", value=f"-{ghost_no_reward} candies", inline=False)
                await interaction.channel.send(embed=embed)
                await interaction.message.delete()

        embed = discord.Embed(title=f"Guess which haunted house the ghost is hiding in (1️⃣ -> 5️⃣)", color=discord.Color.dark_blue())
        embed.set_author(name="Ghost Guess", icon_url=f"https://media.discordapp.net/attachments/1198631394046386205/1297232345887146025/ghost.jpeg?ex=67152d44&is=6713dbc4&hm=479964cd1dfa53bb55be065675ab33bdc55b712e704a75bac6d6491616a05e76&=&format=webp&width=671&height=671")
        user_display_name = interaction.user.display_name
        user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
        await interaction.response.send_message(embed=embed, view=GhostGuessView())

    # Game: Witch's Coin Flip
    async def coin_flip(self, interaction):
        class CoinFlipView(discord.ui.View):
            @discord.ui.button(label="Heads", style=discord.ButtonStyle.secondary)
            async def heads_button(self, interaction, button):
                await self.flip_coin(interaction, "Heads")
            @discord.ui.button(label="Tails", style=discord.ButtonStyle.secondary)
            async def tails_button(self, interaction, button):
                await self.flip_coin(interaction, "Tails")
            async def flip_coin(self, interaction, user_choice):
                outcome = random.choice(["Heads", "Tails"])
                result = "You guessed correctly!" if user_choice == outcome else "You guessed wrong!"
                coin_yes_reward = 0
                coin_no_reward = 0
                if result == "You guessed correctly!":
                    coin_yes_reward = random.randint(1, 5)
                else:
                    coin_no_reward = random.randint(1,5)
                user_id = str(interaction.user.id)
                if user_id not in economy_data:
                    economy_data[user_id] = {"candies": 0}  # Initialize user data if not present
                user_id = str(interaction.user.id)
                economy_data[user_id]["candies"] += coin_yes_reward
                economy_data[user_id]["candies"] -= coin_no_reward
                save_economy(economy_data)

                embed = discord.Embed(title="Witch's Coin Flip", color=discord.Color.dark_green())
                user_display_name = interaction.user.display_name
                user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
                embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
                embed.add_field(name="You:", value=user_choice, inline=True)
                embed.add_field(name="Coin:", value=outcome, inline=True)
                embed.add_field(name="Result:", value=result, inline=False)
                if result == "You guessed correctly!":
                    embed.add_field(name="Reward:", value=f"+{coin_yes_reward} candies", inline=False)
                else:
                    embed.add_field(name="Reward:", value=f"-{coin_no_reward} candies", inline=False)
                await interaction.channel.send(embed=embed)
                await interaction.message.delete()

        embed = discord.Embed(title="Heads or Tails? Flip the Witch's coin", color=discord.Color.dark_green())
        user_display_name = interaction.user.display_name
        user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
        embed.set_author(name=f"Witch's Coin Flip", icon_url="https://media.discordapp.net/attachments/1198631394046386205/1297243944265977987/witchs_coin_flip.jpeg?ex=67153811&is=6713e691&hm=d8cf26e8f607226c4db757ef752fceeba93bb616103512738d1379c426885e2c&=&format=webp&width=671&height=671")
        await interaction.response.send_message(embed=embed, view=CoinFlipView())

    # Game: Skeleton Dice Roll
    async def dice_roll(self, interaction):
        skeleton_roll = random.randint(1, 6)

        class DiceRollView(discord.ui.View):

            @discord.ui.button(label="🎲", style=discord.ButtonStyle.secondary)
            async def roll_dice(self, interaction, button):
                player_roll = random.randint(1, 6)
                if player_roll == skeleton_roll:
                    result = "You draw!"
                else:
                    result = "You win!" if player_roll > skeleton_roll else "You lose!"
                    
                reward = 0
                lose_penalty = 0
                draw_penalty = 0

                # Determine reward or penalty
                if result == "You win!":
                    reward = random.randint(1, 5)  # Reward for winning
                    lose_penalty = 0  # No penalty when winning
                elif result == "You lose!":
                    reward = 0  # No reward when losing
                    lose_penalty = random.randint(1, 5)
                elif result == "You draw!":
                    reward = 0  # No reward when losing
                    draw_penalty = random.randint(1, 5)
                else:
                    return

                user_id = str(interaction.user.id)
                if user_id not in economy_data:
                    economy_data[user_id] = {"candies": 0}  # Initialize user data if not present

                economy_data[user_id]["candies"] += reward  # Add reward
                economy_data[user_id]["candies"] -= lose_penalty
                economy_data[user_id]["candies"] += draw_penalty # Deduct lose penalty
                save_economy(economy_data)  # Save updated economy data

                embed = discord.Embed(title="Skeleton Dice Roll", color=discord.Color.greyple())
                user_display_name = interaction.user.display_name
                user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
                embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
                embed.add_field(name="You:", value=player_roll, inline=True)
                embed.add_field(name="Skeleton:", value=skeleton_roll, inline=True)
                embed.add_field(name="Result:", value=result, inline=False)
                if result == "You win!":
                    embed.add_field(name="Reward:", value=f"+{reward} candies", inline=True)
                elif result == "You lose!":
                    embed.add_field(name="Reward:", value=f"-{lose_penalty} candies", inline=True)
                else:
                    embed.add_field(name="Reward:", value=f"+{draw_penalty} candies", inline=True)
                
                await interaction.response.send_message(embed=embed)
                await interaction.message.delete()

        view = DiceRollView()
        embed=discord.Embed(title="Roll the dice", color=discord.Color.greyple())
        user_display_name = interaction.user.display_name
        user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
        embed.set_author(name="Skeleton Dice Roll", icon_url="https://media.discordapp.net/attachments/1198631394046386205/1297244785966452807/sksleton_dice_roll.jpeg?ex=671538da&is=6713e75a&hm=eaa814abbe8df03fc39f94762e820cbbfe9b1526fc1ef3f1e0c8e43565b3d724&=&format=webp&width=671&height=671")
        await interaction.response.send_message(embed=embed, view=view)

    # Game: Vampire Card Draw
    async def card_draw(self, interaction):
        card_deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King", "Ace"]
        dracula_card = random.choice(card_deck)

        class CardDrawView(discord.ui.View):
            @discord.ui.button(label="🃏", style=discord.ButtonStyle.secondary)
            async def draw_card(self, interaction, button):
                player_card = random.choice(card_deck)
                result = "You win!" if card_deck.index(player_card) > card_deck.index(dracula_card) else "You lose!"
                user_id = str(interaction.user.id)
                if user_id not in economy_data:
                    economy_data[user_id] = {"candies": 0}  # Initialize user data if not present
                card_win_reward = 0
                card_lose_reward = 0
                if result == "You win!":
                    card_win_reward = random.randint(1, 5)  
                else:
                    card_lose_reward = random.randint(1, 5)
                user_id = str(interaction.user.id)
                economy_data[user_id]["candies"] += card_win_reward
                economy_data[user_id]["candies"] -= card_lose_reward
                save_economy(economy_data)

                embed = discord.Embed(title="Vampire Card Draw", color=discord.Color.red())
                user_display_name = interaction.user.display_name
                user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
                embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
                embed.add_field(name="You:", value=player_card, inline=True)
                embed.add_field(name="Dracula:", value=dracula_card, inline=True)
                embed.add_field(name="Result:", value=result, inline=False)
                if result == "You win!":
                    embed.add_field(name="Reward:", value=f"+{card_win_reward} candies", inline=False)
                else:
                    embed.add_field(name="Reward:", value=f"-{card_lose_reward} candies", inline=False)
                
                await interaction.channel.send(embed=embed)
                await interaction.message.delete()
        embed = discord.Embed(title="Draw a card from Dracula's deck", color=discord.Color.red())
        user_display_name = interaction.user.display_name
        user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
        embed.set_author(name="Vampire Card Draw", icon_url="https://media.discordapp.net/attachments/1198631394046386205/1297246760221282394/vampire_card_draw.jpeg?ex=67153ab1&is=6713e931&hm=5f953b0cff5e9a84184f9708c3349e02ab043f11e85f2ca6e5c961efbb65a31a&=&format=webp&width=671&height=671")
        await interaction.response.send_message(embed=embed, view=CardDrawView())

    # Game: Monster Battle (Higher or Lower)
    async def monster_battle(self, interaction):
        class MonsterBattleView(discord.ui.View):
            @discord.ui.button(label="⬆️", style=discord.ButtonStyle.secondary)
            async def higher_button(self, interaction, button):
                await self.play_game(interaction, "higher")

            @discord.ui.button(label="⬇️", style=discord.ButtonStyle.secondary)
            async def lower_button(self, interaction, button):
                await self.play_game(interaction, "lower")

            async def play_game(self, interaction, user_choice):
                player_number = random.randint(1, 20)
                monster_number = random.randint(1, 20)

                result = "You win!" if (user_choice == "higher" and player_number > monster_number) or \
                                      (user_choice == "lower" and player_number < monster_number) else "You lose!"
                user_id = str(interaction.user.id)
                if user_id not in economy_data:
                    economy_data[user_id] = {"candies": 0}  # Initialize user data if not present
                win_reward = 0
                lose_reward = 0
                if result == "You win!":
                    win_reward = random.randint(1,5)
                elif result == "You lose!":
                    lose_reward = random.randint(1, 5)
                else:
                    return
                user_id = str(interaction.user.id)
                economy_data[user_id]["candies"] += win_reward
                economy_data[user_id]["candies"] -= lose_reward
                save_economy(economy_data)

                embed = discord.Embed(title="Monster Battle", color=discord.Color(value=0x427d68))
                user_display_name = interaction.user.display_name
                user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
                embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
                embed.add_field(name="You:", value=player_number, inline=True)
                embed.add_field(name="Monster:", value=monster_number, inline=True)
                embed.add_field(name="Result:", value=result, inline=False)
                if result == "You win!":
                    embed.add_field(name="Reward:", value=f"+{win_reward} candies", inline=False)
                else:
                    embed.add_field(name="Reward:", value=f"-{lose_reward} candies", inline=False)
                await interaction.channel.send(embed=embed)
                await interaction.message.delete()

        embed = discord.Embed(title="Higher or Lower? Choose your fate", color=discord.Color(value=0x427d68))
        user_display_name = interaction.user.display_name
        user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
        embed.set_author(name="Monster Battle", icon_url="https://media.discordapp.net/attachments/1198631394046386205/1297248622215299304/monster_battle.jpeg?ex=67153c6d&is=6713eaed&hm=483e1a2afc0c3bcabebfddb6718100685434e91535cab724c4ab69f9a0de687a&=&format=webp&width=671&height=671")
        await interaction.response.send_message(embed=embed, view=MonsterBattleView())

    # Game: Cauldron Math
    async def cauldron_math(self, interaction):
        # Generate a random math problem
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operation = random.choice(["+", "-", "*"])
        
        if operation == "+":
            answer = num1 + num2
        elif operation == "-":
            answer = num1 - num2
        else:  # operation == "*"
            answer = num1 * num2

        # List of answers including the correct one and two incorrect options
        buttons = [
            (str(answer - 5), False),  # Incorrect option
            (str(answer), True),       # Correct option
            (str(answer / 6), False)   # Incorrect option
        ]

        # Shuffle the buttons to randomize their position
        random.shuffle(buttons)

        # Define the CauldronMathView class
        class CauldronMathView(discord.ui.View):
            def __init__(self):
                super().__init__()

            # Button 1
            @discord.ui.button(label=buttons[0][0], style=discord.ButtonStyle.secondary if buttons[0][1] else discord.ButtonStyle.secondary)
            async def button_1(self, interaction, button):
                await self.check_answer(interaction, buttons[0][1])

            # Button 2
            @discord.ui.button(label=buttons[1][0], style=discord.ButtonStyle.secondary if buttons[1][1] else discord.ButtonStyle.secondary)
            async def button_2(self, interaction, button):
                await self.check_answer(interaction, buttons[1][1])

            # Button 3
            @discord.ui.button(label=buttons[2][0], style=discord.ButtonStyle.secondary if buttons[2][1] else discord.ButtonStyle.secondary)
            async def button_3(self, interaction, button):
                await self.check_answer(interaction, buttons[2][1])

            # Function to handle answer validation
            async def check_answer(self, interaction, is_correct):
                user_id = str(interaction.user.id)
                if user_id not in economy_data:
                    economy_data[user_id] = {"candies": 0}  # Initialize user data if not present

                if is_correct:
                    yes_reward = random.randint(1, 5)
                    economy_data[user_id]["candies"] += yes_reward
                    result_message = "Correct!"
                else:
                    no_reward = random.randint(1, 5)
                    economy_data[user_id]["candies"] -= no_reward
                    result_message = "Incorrect!"

                save_economy(economy_data)
                embed = discord.Embed(title="Cauldron Math", color=discord.Color(value=0x18FF00))
                user_display_name = interaction.user.display_name
                user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
                embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
                embed.add_field(name="Result:", value=result_message, inline=False)
                if is_correct:
                    embed.add_field(name="Reward:", value=f"+{yes_reward} candies", inline=False)
                else:
                    embed.add_field(name="Reward:", value=f"-{no_reward} candies", inline=False)
                await interaction.channel.send(embed=embed)
                await interaction.message.delete()

        embed = discord.Embed(title=f"Calculate: {num1} {operation} {num2}", color=discord.Color(value=0x18FF00))
        user_display_name = interaction.user.display_name
        user_avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        embed.set_footer(text=user_display_name, icon_url=user_avatar_url)
        embed.set_author(name="Cauldron Math", icon_url="https://media.discordapp.net/attachments/1198631394046386205/1297249828908302427/cauldron_math.jpeg?ex=67153d8c&is=6713ec0c&hm=fc729b0b2b27161fa1d334ead8ab7924200150c3c82ad1fdabaa450f76bf43fa&=&format=webp&width=671&height=671")
        await interaction.response.send_message(embed=embed, view=CauldronMathView())

@bot.command(name="game")
async def game(ctx):
    view = HalloweenGames(ctx.author)
    await ctx.message.delete()
    gameselectembed = discord.Embed(title="Select a game to play", color=discord.Color.gold())
    gameselectembed.set_footer(text=f"{ctx.author.display_name}", icon_url=ctx.author.avatar.url)
    await ctx.send(embed=gameselectembed, view=view)

class TrickOrTreatButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # No timeout for the button

    @discord.ui.button(label="Trick or Treat!", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)

        # Ensure that user data is initialized
        if user_id not in economy_data:
            economy_data[user_id] = {"candies": 0}

        outcome = random.choice(["treat", "trick"])
        
        if outcome == "treat":
            candies_found = random.randint(1, 10)
            economy_data[user_id]["candies"] += candies_found  # This should accumulate candies
            result = f"{interaction.user.mention} found {candies_found} candies!"
        else:
            # Points are no longer being tracked or affected
            candies_lost = random.randint(1, 5)
            economy_data[user_id]["candies"] -= candies_lost
            result = f"{interaction.user.mention} got a trick and lost {candies_lost} candies!"

        save_economy(economy_data)  # Ensure the economy is saved after changes

        button.disabled = True
        await interaction.response.edit_message(content=f"🎃 {result}", view=self)

# Function to spawn the Trick or Treat event
async def spawn_trick_or_treat():
 #   guilds = bot.guilds
   # for guild in guilds:
       # category = discord.utils.get(guild.channels, id=1296899979473850368)
       # if category:
          #  channels = [channel for channel in category.text_channels if channel.permissions_for(guild.me).send_messages]
          #  if channels:
               # channel = random.choice(channels)
                await bot.get_channel(1296899979473850368).send("🎃 **Trick or Treat!** Press the button below to see what you get!", view=TrickOrTreatButton())

@commands.has_permissions(administrator=True)
@bot.tree.command(name="treat", description="Spawn a Trick or Treat button")
async def treat(interaction: discord.Interaction, channel: discord.TextChannel = None):
    target_channel = channel or interaction.channel
    await target_channel.send("🎃 **Trick or Treat!** Press the button below to see what you get!", view=TrickOrTreatButton())
    await interaction.response.send_message("I spawned a Trick or Treat!", ephemeral=True)

@commands.is_owner()
@bot.tree.command(name="reset", description="Reset your or a user's balance")
@app_commands.describe(user="User to reset (leave blank to reset yourself)")
async def reset(interaction: discord.Interaction, user: discord.User = None):
    if user is None:
        # Reset the calling user's data
        user_id = str(interaction.user.id)
        if user_id in economy_data:
            del economy_data[user_id]  # Remove the calling user's data completely
            save_economy(economy_data)
            await interaction.response.send_message("Your economy data has been completely removed.", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have any economy data to reset.", ephemeral=True)
    else:
        # Check if the user has permission to reset all users
        if interaction.user.guild_permissions.administrator:  # Check for admin privileges
            user_id = str(user.id)
            if user_id in economy_data:
                del economy_data[user_id]  # Remove that user's data completely
                save_economy(economy_data)
                await interaction.response.send_message(f"{user.mention}'s economy data has been completely removed.", ephemeral=True)
            else:
                await interaction.response.send_message(f"{user.mention} doesn't have any economy data to reset.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to reset other users' data.", ephemeral=True)
            
class ConfirmResetView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.yes_count = 0  # Counter for "Yes" clicks

    @discord.ui.button(emoji="<a:yes:1296526664918110260>", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("You can't interact with this button.", ephemeral=True)
            return
        
        self.yes_count += 1

        if self.yes_count >= 2:
            # Delete all economy data and confirm
            economy_data.clear()  # Clears the entire dictionary
            save_economy(economy_data)  # Ensure data is saved after clearing
            await interaction.response.edit_message(content="The economy has been reset. No more inflation!", embed=None, view=None)
        else:
            # Send the same embed and buttons again for the second confirmation
            await interaction.response.edit_message(embed=create_confirm_embed(), view=self)

    @discord.ui.button(emoji="<a:no:1296526639555149866>", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("You can't interact with this button.", ephemeral=True)
            return
        
        # Delete the message and cancel the process
        await interaction.response.edit_message(content="The reset process has been canceled.", embed=None, view=None)


# Function to create the confirmation embed
def create_confirm_embed():
    embed = discord.Embed(
        title="Reset Economy",
        description="Are you sure you want to reset the economy? This action cannot be undone.",
        color=discord.Color.orange()
    )
    return embed

@commands.is_owner()
@bot.tree.command(name="clear_economy", description="Reset all user's balances")
async def clear_economy(interaction: discord.Interaction):
    embed = create_confirm_embed()
    view = ConfirmResetView(interaction)
    await interaction.response.send_message(embed=embed, view=view)

@bot.hybrid_command(name="leaderboard", description="Show top 10 user's balances")
async def leaderboard(ctx):
    sorted_economy = sorted(economy_data.items(), key=lambda x: x[1].get("candies", 0), reverse=True)
    top_10 = sorted_economy[:10]
    embed = discord.Embed(title="🎃 Leaderboard 🎃", color=discord.Color.gold())
    for i, (user_id, data) in enumerate(top_10, start=1):
        user = await bot.fetch_user(int(user_id))  # Fetch the user by ID
        candies = data.get("candies", 0)
        embed.add_field(name=f"#{i} - {user.name}", value=f"Candies: {candies}", inline=False)

    if not top_10:
        embed.description = "No data available yet."

    if isinstance(ctx.channel, discord.TextChannel):
        await ctx.send(embed=embed)
        await ctx.message.delete()
    else:
        await ctx.send(embed=embed)
    
@commands.is_owner()
@bot.tree.command(name="add", description="Add candies to a user")
async def add(interaction: discord.Interaction, user: discord.User, amount: int):
    user_id = str(user.id)
    economy_data = load_economy()
    if user_id not in economy_data:
        economy_data[user_id] = {"candies": 0}
    economy_data[user_id]["candies"] += amount
    await interaction.response.send_message(f"Added {amount} candies to {user.mention}.", ephemeral=True)
    save_economy(economy_data)
   
@commands.is_owner()    
@bot.tree.command(name="remove", description="Remove candies from a user")
async def remove(interaction: discord.Interaction, user: discord.User, amount: int):
    user_id = str(user.id)
    economy_data = load_economy()
    if user_id not in economy_data:
        economy_data[user_id] = {"candies": 0}
    if economy_data[user_id]["candies"] < amount:
        await interaction.response.send_message(f"{user.mention} does not have enough candies to remove.", ephemeral=True)
        return
    economy_data[user_id]["candies"] -= amount
    await interaction.response.send_message(f"Removed {amount} candies from {user.mention}.", ephemeral=True)
    save_economy(economy_data)


@bot.hybrid_command(description="View event commands")
async def help(ctx):
    helpembed = discord.Embed(title="🎃 Halloween Event Commands 🎃", color=discord.Color.orange())
    helpembed.add_field(name="balance", value=f"Used to view how many candies you have.", inline=False)
    helpembed.add_field(name="leaderboard", value=f"Used to view the top 10 users with the highest balances.", inline=False)
    helpembed.add_field(name="game", value=f"Used to play various spooky games.", inline=False)
    helpembed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar.url)
    if isinstance(ctx.channel, discord.TextChannel):
        await ctx.send(embed=helpembed, delete_after=30)
        await ctx.message.delete()
    else:
        await ctx.send(embed=helpembed)

#################################################################################################################################################################################################

random_mins = random.randint(5, 10)
@tasks.loop(minutes=random_mins)
async def spawn_task():
    await spawn_trick_or_treat()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    spawn_task.start()
    await bot.tree.sync()

bot.run(TOKEN)
