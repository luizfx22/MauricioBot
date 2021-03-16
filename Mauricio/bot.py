import os
import discord
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("BOT_TOKEN")

print(SECRET_KEY)


class MyClient(discord.Client):
    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    async def on_message(self, message):
        print("Message from {0.author}: {0.content}".format(message))


client = MyClient()
client.run("")
