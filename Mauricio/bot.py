import os
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv
from datetime import datetime, tzinfo, timezone
from dateutil import tz

load_dotenv()

SECRET_KEY = os.getenv("BOT_TOKEN")

intents = discord.Intents(messages=True, guilds=True)
intents.reactions = True
intents.members = True
intents.presences = True

ignored = [297153970613387264, 234395307759108106, 735242803751288862]


class Mauricio(commands.Bot):
    async def on_ready(self):
        print(self.user)

        activity = discord.Activity(
            name=f"você!", type=discord.ActivityType.watching)
        await self.change_presence(status=discord.Status.online, activity=activity)

    async def on_member_update(self, before, after):
        guildId = after.guild.id
        memberId = before.id

        if guildId != 493941258516168704:
            return None

        if memberId in ignored:
            return None

        if memberId != 307291335189331969:
            return None

        Guild = self.get_guild(guildId)
        channel = Guild.get_channel(675469062515458078)

        if not before.activity:
            print(f"{before} iniciou {after.activity.name}")
            return None

        if before.activity and not after.activity:
            start = before.activity.start.replace(
                microsecond=0, tzinfo=tz.tzlocal()
            )
            end = datetime.now(timezone.utc).replace(
                microsecond=0, tzinfo=tz.tzlocal()
            )

            time_delta = (end - start)

            time_secs = time_delta.total_seconds()

            time_minutes = (time_secs / 60) if time_secs % 60 == 0 else 0

            time_hours = (time_minutes / 60) if time_minutes % 60 == 0 else 0

            time_days = (time_hours / 24) if time_hours % 24 == 0 else 0

            time_played = {
                "seconds": time_secs,
                "minutes": time_minutes,
                "hours": time_hours,
                "days": time_days
            }

            print(
                f"{before} fechou {before.activity.name}! {time_played}"
            )

            return None

        if before.activity.name != after.activity.name:
            print(
                f"{before} fechou {before.activity.name} e abriu {after.activity.name}"
            )
            return None

        print("Edge case here!")


client = Mauricio(command_prefix="...", self_bot=False, intents=intents)
client.run(SECRET_KEY)
