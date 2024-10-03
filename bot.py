import datetime
import json
import traceback
import accounts
import discord
import requests
from discord import app_commands
from discord.ext import commands
import ocr
import songs

TOKEN = "token"
CHANNEL_ID = 123


def save_users(data, filename='users.json'):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2)


def load_users(filename='users.json'):
    def keystoint(x):
        return {int(k): v for k, v in x.items()}

    with open(filename, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file, object_hook=keystoint)

    return data


def create_score_embed(user: accounts.Account, score: accounts.Score, diff: int):
    maxperformance = accounts.Score(score.song, diff, score.difficulty.maxcombo).performance
    for i in range(len(user.scores)):
        if score == user.scores[i]:
            topplay = i
    embed = discord.Embed(title=f"{score.song.group.name} - {score.song.title} [{score.difficulty.difficulty.name}, Lv. {score.difficulty.level}]",
                          description=f"__**Top play #{topplay + 1}**__",
                          colour=0xe4007f,
                          timestamp=datetime.datetime.now())
    embed.set_author(name="%s: %.2fp" % (user.name, user.performance))
    embed.add_field(name="Score",
                    value="(unsupported)",
                    inline=True)
    embed.add_field(name="Accuracy",
                    value="%2.2f%%" % score.accuracy,
                    inline=True)
    embed.add_field(name="Performance",
                    value="**%.2f**/%.2fp" % (score.performance, maxperformance),
                    inline=True)
    embed.add_field(name="Combo",
                    value=f"**{score.combo}x**/{score.difficulty.maxcombo}x",
                    inline=True)
    embed.add_field(name="Hit judgements",
                    value="{%d/%d/%d/%d/%d}" % (score.perfect, score.great, score.good, score.bad, score.miss),
                    inline=True)
    embed.set_footer(text="School Idol Festival 2 Leaderboards",
                     icon_url="https://cdn.discordapp.com/avatars/1203549902341414972"
                              "/9d8cb72447bbf9a012931024438e3b2f.png")

    return embed


def create_profile_embed(user: accounts.Account):
    description = "Overall Performance: `%.2f`\n" % user.performance
    description += "Accuracy: `%2.2f%%`\n" % user.accuracy
    description += "Score count: `%d`\n" % len(user.scores)
    if user.friendcode != 0:
        description += "Friend code: `%d`\n" % user.friendcode

    topplays = ""
    for i, score in zip(range(10), user.scores):
        topplays += "**#%d** __**%s - %s**__ [%s, Lv.%d]\n" % (
            i + 1, score.song.group.name, score.song.title, score.difficulty.difficulty.name, score.difficulty.level)
        topplays += "**%.2fp** (%2.2f%%) [**%dx**/%dx]\n" % (
            score.performance, score.accuracy, score.combo, score.difficulty.maxcombo)

    embed = discord.Embed(title=f"Profile stats for {user.name}",
                          description=description,
                          colour=0xe4007f,
                          timestamp=datetime.datetime.now())

    embed.add_field(name="Top Plays",
                    value=topplays,
                    inline=False)

    embed.set_footer(text="School Idol Festival 2 Leaderboards",
                     icon_url="https://cdn.discordapp.com/avatars/1203549902341414972/9d8cb72447bbf9a012931024438e3b2f.png")

    return embed


songbook = songs.Songbook()
songbook.songs = songs.load_songs('songs.json')
users = load_users()
accountlist = accounts.load_accounts(songbook)

songs.save_songs(songbook.songs)
accounts.save_accounts(accountlist)

bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print("Leaderboard bot is running.")
    # channel = bot.get_channel(CHANNEL_ID)
    # await channel.send(main.accountlist[0])
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)


class Edit(discord.ui.Modal, title='Edit Score Values'):
    perfect = discord.ui.TextInput(label='Perfects')
    great = discord.ui.TextInput(label='Greats')
    good = discord.ui.TextInput(label='Goods')
    bad = discord.ui.TextInput(label='Bads')
    miss = discord.ui.TextInput(label='Misses')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Score edited.", ephemeral=False)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=False)
        traceback.print_exception(type(error), error, error.__traceback__)


class Buttons(discord.ui.View):
    def __init__(self, scoreattribs):
        super().__init__()
        self.score = scoreattribs

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancelbutton(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.edit_message(content="Score submission cancelled.", embed=None, view=None)

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.grey, disabled=True)
    async def editbutton(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.send_modal(Edit())
        # await interaction.response.send_message("Score edited.", ephemeral=False)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green)
    async def submitbutton(self, interaction: discord.Interaction, Button: discord.ui.Button):
        id = interaction.user.id
        user = accountlist[users.get(id)]
        diff = songs.Difficulties[self.score[1]].value - 1
        try:
            newscore = accounts.Score(self.score[0],
                                      diff,
                                      self.score[2],
                                      self.score[3],
                                      self.score[4],
                                      self.score[5],
                                      self.score[6],
                                      self.score[7])
        except ZeroDivisionError:
            await interaction.response.edit_message(
                content="Max combo for this song has not been added.\nThis has been reported and your score has not "
                        "been submitted.",
                embed=None, view=None)
            return
        except Exception as e:
            await interaction.response.edit_message(
                content=f"**An error occured while submtting your score.**\n{e}", embed=None,
                view=None)
            return
        status = user.add_score(newscore)
        accounts.save_accounts(accountlist)
        if status == 1:
            embed = create_score_embed(accountlist[users.get(interaction.user.id)], newscore, diff)
            await interaction.response.edit_message(content="Score submitted to your profile!", embed=None, view=None)
            await interaction.followup.send(content="", ephemeral=False, embed=embed)
        else:
            await interaction.response.edit_message(content="Your score was not submitted because you have another "
                                                            "play on the same difficulty worth more performance.",
                                                    embed=None, view=None)


@bot.tree.command(name="addscore", description="Add score to your profile.")
@app_commands.describe(score="Enter score screenshot")
async def addscore(interaction: discord.Interaction, score: discord.Attachment):
    if interaction.user.id not in users.keys():
        await interaction.response.send_message("You are not in the database. Consider creating an account using "
                                                "`/createaccount`!")
    await interaction.response.defer(ephemeral=True)

    image = requests.get(score).content
    with open('score', 'wb') as handler:
        handler.write(image)

    attribs = ocr.get_score_attributes('score')

    song = songs.search_songs(attribs[0], songbook)
    if song is None:
        await interaction.followup.send(
            content="**Could not detect song from image.**\nMake sure your screenshot is high resolution and doesn't "
                    "have any notifications or volume bars in the way.\nThe Japanese version of the game is not "
                    "currently supported.", embed=None)
        with open("unknownsongs.txt", "a") as file:
            file.write(attribs[0])
            file.write("\n")
        return
    attribs[0] = song

    embed = discord.Embed(title="Are you sure you want to add this score?",
                          description="**Double-check that all fields are correct!**\n"
                                      "The bot is not perfect at detecting numbers.",
                          colour=0xe4007f,
                          timestamp=datetime.datetime.now())

    embed.add_field(name="Song",
                    value=attribs[0].title,
                    inline=True)
    embed.add_field(name="Difficulty",
                    value=attribs[1],
                    inline=True)
    embed.add_field(name="",
                    value="",
                    inline=False)
    embed.add_field(name="Perfects",
                    value=attribs[2],
                    inline=True)
    embed.add_field(name="Greats",
                    value=attribs[3],
                    inline=True)
    embed.add_field(name="Goods",
                    value=attribs[4],
                    inline=True)
    embed.add_field(name="Bads",
                    value=attribs[5],
                    inline=True)
    embed.add_field(name="Misses",
                    value=attribs[6],
                    inline=True)

    embed.set_footer(text="School Idol Festival 2 Leaderboards",
                     icon_url="https://cdn.discordapp.com/avatars/1203549902341414972"
                              "/9d8cb72447bbf9a012931024438e3b2f.png")

    await interaction.followup.send(embed=embed, ephemeral=True, view=Buttons(attribs))


@bot.tree.command(name="profile", description="Show your full profile stats.")
# @app_commands.describe(score="Show your full profile stats.")
async def showprofile(interaction: discord.Interaction):
    if interaction.user.id in users.keys():
        id = interaction.user.id
        user = accountlist[users.get(id)]
        await interaction.response.send_message(embed=create_profile_embed(user))
    else:
        await interaction.response.send_message("You are not in the database. Consider creating an account using "
                                                "`/createaccount`!")


@bot.tree.command(name="createaccount", description="Create a new account.")
@app_commands.describe(name="Name", friendcode="Friend Code")
async def createaccount(interaction: discord.Interaction, name: str, friendcode: int = 0):
    if interaction.user.id in users.keys():
        await interaction.response.send_message("You already have an account in the system.")
    else:
        newaccount = accounts.Account(name, len(accountlist), friendcode)
        print(newaccount)
        accountlist.append(newaccount)
        users[interaction.user.id] = newaccount.id
        save_users(users)
        accounts.save_accounts(accountlist)
        await interaction.response.send_message(f"Account `{newaccount.name}` created successfully!")


@bot.tree.command(name="leaderboard", description="Show leaderboard.")
# @app_commands.describe(score="Enter score screenshot")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()

    accountlist.sort(key=lambda x: x.performance, reverse=True)
    description = "```\n"
    for i in range(min(len(accountlist), 10)):
        description += "%12s:   %2.2f\n" % (accountlist[i].name, accountlist[i].performance)
    description += "```"
    embed = discord.Embed(title="SIF2 Leaderboard",
                          description=description,
                          timestamp=datetime.datetime.now())
    embed.set_footer(text="School Idol Festival 2 Leaderboards",
                     icon_url="https://cdn.discordapp.com/avatars/1203549902341414972/9d8cb72447bbf9a012931024438e3b2f.png")

    await interaction.followup.send(embed=embed, ephemeral=False)


bot.run(TOKEN)
