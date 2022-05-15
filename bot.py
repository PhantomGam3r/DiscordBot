# bot.py
import os

import discord
from dotenv import load_dotenv
import fact_sphere, asyncio
import animalapi as animal_facts
import random, requests
from chuck_facts_list import chuck_facts
from sun_tzu import sun_tzu_quotes
import randfacts

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

# define fact_channels list global
fact_channels = []
types = ["fact_sphere", "animal_fact", "random_fact", "chuck_norris", "sun_tzu", "cat_fact"]

word_blacklist = [" die ", " killed ", " dying ", " kill ", " killing "]

every_x_seconds = 25*60
delete_after_x_seconds = every_x_seconds * 12 - 5

class Fact:
    def __init__(self, text, file, type, truth_type, has_file):
        self.text = text
        self.file = file
        self.type = type
        self.truth_type = truth_type
        self.has_file = has_file

        # print all the attributes
        print("Fact: ", self.text)
        print("Data: ", self.file)
        print("Type: ", self.type)
        print("True: ", self.truth_type)
        print("File: ", self.has_file)
        print("\n")


def get_cat_fact():
    url = "https://some-random-api.ml/facts/cat"
    response = requests.get(url)
    fact = response.json()["fact"]

    url = "https://some-random-api.ml/img/cat"
    response = requests.get(url)
    image = response.json()["link"]

    return fact, image

# define get_random_fact function
def get_random_fact():
    data = "none"
    truth_type = "unspecified"
    # get random type
    type = random.choices(types, weights=(5, 40, 35, 1, 10, 25), k=1)[0]
    # get random fact
    if type == "fact_sphere":
        fact_data = fact_sphere.fact()
        fact = fact_data.text
        data = fact_data.audio.filepath
        truth_type = fact_data.type
        # if any of the blacklisted words are in the fact as a whole word, and not as part of a word, get another fact
        for word in word_blacklist:
            if word in fact:
                return get_random_fact()
    elif type == "animal_fact":
        fact_data = animal_facts.rand_animals()
        fact = fact_data["fact"]
        data = fact_data["image"]
    elif type == "random_fact":
        fact = randfacts.get_fact()
    elif type == "chuck_norris":
        fact = random.choice(chuck_facts)
    elif type == "sun_tzu":
        fact = random.choice(sun_tzu_quotes)
    elif type == "cat_fact":
        fact, data = get_cat_fact()
    
    if data == "none":
        has_file = False
    else:
        has_file = True
    
    return Fact(fact, data, type, truth_type, has_file)


class FactData:
    def __init__(self, title, color):
        self.title = title
        self.color = color

def get_data_from_fact(fact):
    data = FactData("", 0)
    if fact.type == "fact_sphere":
        data.title = "Fact Sphere says:"
        # depending on truth level, set color, uses the fact_sphere.FactType enum
        if fact.truth_type == fact_sphere.FactType.FALSE:
            data.color = 0xe02a1d
        if fact.truth_type == fact_sphere.FactType.NEARLY_TRUE:
            data.color = 0xa2b535
        if fact.truth_type == fact_sphere.FactType.NOT_FACTS:
            data.color = 0xf2d46f
        if fact.truth_type == fact_sphere.FactType.PARTIALLY_TRUE:
            data.color = 0x84ad51
        if fact.truth_type == fact_sphere.FactType.PROBABLY_FALSE:
            data.color = 0xc97d42
        if fact.truth_type == fact_sphere.FactType.SUBJECTIVE_UNVERIFIABLE:
            data.color = 0x42c9c3
        if fact.truth_type == fact_sphere.FactType.TRUE:
            data.color = 0x1fed41
    elif fact.type == "animal_fact":
        data.title = "Fact about this Animal!"
        data.color = 0xd94867
    elif fact.type == "random_fact":
        data.title = "Fact for you!"
        data.color = 0xe844eb
    elif fact.type == "chuck_norris":
        data.title = "True Fact about Chuck Norris"
        data.color = 0x6dedc9
    elif fact.type == "sun_tzu":
        data.title = "Sun Tzu says..."
        data.color = 0xffd700
    elif fact.type == "cat_fact":
        data.title = "Fact about Cats!"
        data.color = 0x1f052f
    return data

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for server in client.guilds:
        for channel in server.channels:
            if "fact" in channel.name.lower():
                fact_channels.append(channel)
                print(f"Found channel {channel.name} in {server.name}")
    
    # Send a fact_sphere fact every x seconds in fact_channel
    while True:
        try:
            for fact_channel in fact_channels:
                fact = get_random_fact()
                # send embed with fact and image if there is one and delete after x seconds
                fact_data = get_data_from_fact(fact)
                embed = discord.Embed(title = fact_data.title, description = fact.text, color = fact_data.color)
                if fact.type != "fact_sphere":
                    if fact.has_file:
                        embed.set_image(url = fact.file)
                    await fact_channel.send(embed = embed, delete_after = delete_after_x_seconds)
                elif fact.has_file:
                    await fact_channel.send(embed = embed, delete_after = delete_after_x_seconds, file=discord.File(fact.file, filename="fact_sphere.mp3"))
            await asyncio.sleep(every_x_seconds)
        except AttributeError:
            print("AttributeError")

# upon bot joining a new server, add the fact channels of it to the list of fact channels
@client.event
async def on_guild_join(guild):
    for channel in guild.channels:
        if "fact" in channel.name.lower():
            fact_channels.append(channel)

client.run(TOKEN)