import os
import discord
from discord.enums import ActivityType
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timezone
import math
from pymongo import MongoClient

load_dotenv()

SECRET_KEY = os.getenv("BOT_TOKEN")
MONGO_DB_SCHEMA = os.getenv("MONGO_DB_SCHEMA")
MONGO_DB_USER = os.getenv("MONGO_DB_USER")
MONGO_DB_PASSWORD = os.getenv("MONGO_DB_PASSWORD")

dbclient = MongoClient(
    f"mongodb+srv://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@shortendb.mnjto.mongodb.net"
)

database = dbclient[MONGO_DB_SCHEMA]

collection = database.records

intents = discord.Intents(messages=True, guilds=True)
intents.reactions = True
intents.members = True
intents.presences = True

ignored = [297153970613387264, 234395307759108106, 735242803751288862]


def seconds_to_dict(seconds: int) -> dict:
    minutes = math.floor(seconds / 60)
    hours = math.floor(minutes / 60)
    days = math.floor(hours / 24)

    if (minutes > 0):
        seconds -= minutes * 60

    if (hours > 0):
        minutes -= hours * 60

    if (days > 0):
        hours -= days * 24

    return {
        "seconds": seconds,
        "minutes": minutes,
        "hours": hours,
        "days": days
    }


def get_msg_str(time_dict) -> str:
    msg_str = ""

    if time_dict["days"] > 1:
        msg_str += f"{time_dict['days']} dia{'s' if time_dict['days'] != 1 else ''}"

    if time_dict["hours"] > 1:
        if time_dict["days"] > 1:
            msg_str += ", "
        msg_str += f"{time_dict['hours']} hora{'s' if time_dict['horas'] != 1 else ''}"

    if time_dict["minutes"] > 1:
        if time_dict["hours"] > 1:
            msg_str += ", "
        msg_str += f"{time_dict['minutes']} minuto{'s' if time_dict['minutes'] != 1 else ''}"

    if time_dict["seconds"] > 1:
        if time_dict["minutes"] > 1:
            msg_str += " e "
        msg_str += f"{time_dict['seconds']} segundo{'s' if time_dict['seconds'] != 1 else ''}"

    return msg_str


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

        # if memberId != 307291335189331969:
        #     return None

        if before.activity and before.activity.type != ActivityType.playing:
            return None

        if after.activity and after.activity.type != ActivityType.playing:
            return None

        Guild = self.get_guild(guildId)
        channel = Guild.get_channel(830220208161030164)

        if not before.activity and after.activity:
            print(f"{before} iniciou {after.activity.name}")

            userDBInstance = collection.find_one({
                "discord_id": memberId,
                "game_name": after.activity.name
            })

            if not userDBInstance:
                collection.insert_one({
                    "discord_id": memberId,
                    "game_name": after.activity.name,
                    "last_time_played": 0,
                    "max_time_played": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                })

            return None

        if before.activity and not after.activity:
            start = before.activity.start.replace(
                microsecond=0, tzinfo=timezone.utc
            )
            end = datetime.now(timezone.utc).replace(
                microsecond=0, tzinfo=timezone.utc
            )

            print(end)

            time_delta = (end - start)

            time_secs = time_delta.total_seconds()

            time_minutes = math.floor(time_secs / 60)

            time_hours = math.floor(time_minutes / 60)

            time_days = math.floor(time_hours / 24)

            if (time_minutes > 0):
                time_secs -= time_minutes * 60

            if (time_hours > 0):
                time_minutes -= time_hours * 60

            if (time_days > 0):
                time_hours -= time_days * 24

            local_time_played = {
                "seconds": time_secs,
                "minutes": time_minutes,
                "hours": time_hours,
                "days": time_days
            }

            userDBInstance = collection.find_one({
                "discord_id": memberId,
                "game_name": before.activity.name
            })

            if userDBInstance:
                max_time_played = userDBInstance["max_time_played"]

                new_max_time_played = max_time_played

                if max_time_played < time_delta.total_seconds():
                    new_max_time_played = time_delta.total_seconds()

                collection.update_one({"_id": userDBInstance["_id"]}, {
                    '$set': {
                        "max_time_played": new_max_time_played,
                        "last_time_played": time_delta.total_seconds(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                })

                if max_time_played < time_delta.total_seconds():
                    async with channel.typing():
                        last_time_dict = seconds_to_dict(max_time_played)
                        last_msg_str = get_msg_str(last_time_dict)

                        new_time_dict = seconds_to_dict(
                            time_delta.total_seconds())
                        new_msg_str = get_msg_str(new_time_dict)

                        await channel.send(f"Ae {before.mention}, parabéns! Você bateu seu próprio recorde jogando {before.activity.name}!")

                        if last_msg_str:
                            await channel.send(f"{before.mention}, seu último recorde foi de {last_msg_str}!")

                        await channel.send(f"{before.mention}, seu novo recorde é de {new_msg_str}! Parabéns!")

            return None

        if before.activity.name != after.activity.name:
            bef_start = before.activity.start.replace(
                microsecond=0, tzinfo=timezone.utc
            )
            bef_end = datetime.now(timezone.utc).replace(
                microsecond=0, tzinfo=timezone.utc
            )

            aft_end = datetime.now(timezone.utc).replace(
                microsecond=0, tzinfo=timezone.utc
            )

            aft_start = after.activity.start.replace(
                microsecond=0, tzinfo=timezone.utc
            )

            bef_time_delta = (bef_end - bef_start)
            aft_time_delta = (aft_end - aft_start)

            bef_time_secs = bef_time_delta.total_seconds()
            aft_time_secs = aft_time_delta.total_seconds()

            bef_time_minutes = math.floor(bef_time_secs / 60)
            aft_time_minutes = math.floor(aft_time_secs / 60)

            bef_time_hours = math.floor(bef_time_minutes / 60)
            aft_time_hours = math.floor(aft_time_minutes / 60)

            bef_time_days = math.floor(bef_time_hours / 24)
            aft_time_days = math.floor(aft_time_hours / 24)

            if (bef_time_minutes > 0):
                bef_time_secs -= bef_time_minutes * 60

            if (aft_time_minutes > 0):
                aft_time_secs -= aft_time_minutes * 60

            if (bef_time_hours > 0):
                bef_time_minutes -= bef_time_hours * 60

            if (aft_time_hours > 0):
                aft_time_minutes -= aft_time_hours * 60

            if (bef_time_days > 0):
                bef_time_hours -= bef_time_days * 24

            if (aft_time_days > 0):
                aft_time_hours -= aft_time_days * 24

            bef_local_time_played = {
                "seconds": bef_time_secs,
                "minutes": bef_time_minutes,
                "hours": bef_time_hours,
                "days": bef_time_days
            }

            aft_local_time_played = {
                "seconds": aft_time_secs,
                "minutes": aft_time_minutes,
                "hours": aft_time_hours,
                "days": aft_time_days
            }

            '''
            ------------------
            DB PART
            ------------------
            '''

            beforeActivityRecord = collection.find_one({
                "discord_id": memberId,
                "game_name": before.activity.name
            })

            afterActivityRecord = collection.find_one({
                "discord_id": memberId,
                "game_name": after.activity.name
            })

            if not afterActivityRecord:
                collection.insert_one({
                    "discord_id": memberId,
                    "game_name": after.activity.name,
                    "last_time_played": 0,
                    "max_time_played": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                })

            if beforeActivityRecord:
                max_time_played = beforeActivityRecord["max_time_played"]

                new_max_time_played = max_time_played

                if max_time_played < bef_time_delta.total_seconds():
                    new_max_time_played = bef_time_delta.total_seconds()

                collection.update_one({"_id": beforeActivityRecord["_id"]}, {
                    '$set': {
                        "max_time_played": new_max_time_played,
                        "last_time_played": bef_time_delta.total_seconds(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                })

            if afterActivityRecord:
                max_time_played = afterActivityRecord["max_time_played"]

                new_max_time_played = max_time_played

                if max_time_played < aft_time_delta.total_seconds():
                    new_max_time_played = aft_time_delta.total_seconds()

                collection.update_one({"_id": afterActivityRecord["_id"]}, {
                    '$set': {
                        "max_time_played": new_max_time_played,
                        "last_time_played": aft_time_delta.total_seconds(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                })

            print(
                f"{before} fechou {before.activity.name} e abriu {after.activity.name}"
            )
            return None

        print("End")


client = Mauricio(command_prefix="...", self_bot=False, intents=intents)
client.run(SECRET_KEY)
