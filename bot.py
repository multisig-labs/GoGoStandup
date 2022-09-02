from email import message
import os

import nextcord
from dotenv import load_dotenv
from nextcord.ext import commands, tasks
from sqlmodel import create_engine, Session, SQLModel, select
from pytimeparse import parse
import arrow

from models import User, Channel
from util import next_time

load_dotenv()

DB_URI = os.getenv("DB_URI", "sqlite:///db.sqlite3")
TESTING_GUILD_ID = int(os.getenv("TESTING_GUILD_ID") or 0)

TESTING_GUILD_IDS = [TESTING_GUILD_ID]

if TESTING_GUILD_ID == 0:
    TESTING_GUILD_IDS = []

# WEEK_TABLE = {
#     "su": 0,
#     "m": 1,
#     "t": 2,
#     "w": 3,
#     "th": 4,
#     "f": 5,
#     "s": 6,
# }

WEEK = ["su", "m", "t", "w", "th", "f", "s"]

engine = create_engine(DB_URI)

SQLModel.metadata.create_all(engine)

bot = commands.Bot()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.slash_command(description="A test command", guild_ids=TESTING_GUILD_IDS)
async def ping(interaction: nextcord.Interaction):
    print("Pong!")
    await interaction.response.send_message("Pong!")


@bot.slash_command(description="Register and/or edit a standup!", guild_ids=TESTING_GUILD_IDS)
async def standup(interaction: nextcord.Interaction, days: str, message_time: str):
    print("Registering...")
    session = Session(engine)

    # check to see if the channel_id is already in the database
    statement = select([Channel]).where(
        Channel.channel_id == str(interaction.channel_id))
    results = session.execute(statement)
    chan = results.first()
    if not chan:
        chan = Channel(channel_id=str(interaction.channel_id),
                       guild_id=str(interaction.guild_id))
        session.add(chan)

    statement = select([User]).where(
        User.channel_id == str(interaction.channel_id)
    ).where(User.user_id == str(interaction.user.id))
    results = session.execute(statement)
    user = results.first()
    if not user:
        user = User(user_id=str(interaction.user.id), username=str(
            interaction.user.name), days=days.split(','), message_time=parse(message_time),
            channel_id=str(interaction.channel_id), next_at=next_time(parse(message_time)))
        session.add(user)
        session.commit()
        await interaction.response.send_message(f"Registered {user.username} with id {user.id}, days {user.days}, time {user.message_time}")
    else:
        # update isn't working for some reason
        # this will work fine.
        session.delete(user)
        user = User(user_id=str(interaction.user.id), username=str(
            interaction.user.name), days=days.split(','), message_time=parse(message_time),
            channel_id=str(interaction.channel_id), next_at=next_time(parse(message_time)))
        session.add(user)
        session.commit()
        await interaction.response.send_message(f"Updated {user.username} with id {user.id}, days {user.days}, time {user.message_time}")
    session.close()


@tasks.loop(seconds=10)
async def send_loop():
    end = arrow.utcnow()
    start = end.shift(seconds=-10)
    weekday = end.weekday()
    session = Session(engine)
    statement = select([User]).where(User.next_at <= end.timestamp()).where(
        User.next_at >= start.timestamp())
    results = session.execute(statement)
    users = results.fetchall()
    users = [weekday]
    for user in users:
        print(user.user_id)
        channel = bot.get_channel(int(user.user_id))
        await channel.send_message(f"Hey {user.username}! Its time for your daily standup! Please respond to this DM to complete your standup.")
        user.next_at = next_time(user.message_time)
    session.close()


@send_loop.before_loop
async def before_send_loop():
    await bot.wait_until_ready()


if __name__ == "__main__":
    send_loop.start()
    bot.run(os.getenv("TOKEN"))
