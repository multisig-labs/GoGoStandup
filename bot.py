import os
from typing import Optional

import arrow
import nextcord
from dotenv import load_dotenv
from nextcord.ext import commands, tasks
from pytimeparse import parse
from sqlmodel import Session, SQLModel, create_engine, select

from models import User
from util import next_time

load_dotenv()

DB_URI = os.getenv("DB_URI", "sqlite:///db.sqlite3")
TESTING_GUILD_ID = int(os.getenv("TESTING_GUILD_ID", "0"))

TESTING_GUILD_IDS = [TESTING_GUILD_ID]

if TESTING_GUILD_ID == 0:
    TESTING_GUILD_IDS = []

engine = create_engine(DB_URI)

SQLModel.metadata.create_all(engine)

intents = nextcord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: nextcord.Message):
    if message.author.bot or message.guild:
        return

    session = Session(engine)
    statement = select([User]).where(User.user_id == message.author.id)
    results = session.execute(statement)
    user = results.first()
    user: User = user[0] if user else None
    if not user:
        print(f"User {message.author.id} not found, ignoring.")
        await message.channel.send(f"Hey! Sorry, I don't recognize you. If you would like to register standup bot, see here: https://github.com/multisig-labs/GoGoStandup")
        session.close()
        return
    if int(user.last_at) == int(user.updated_at):
        await message.channel.send("You have already sent your standup today. Check back later!")
    else:
        now = arrow.utcnow()
        user.updated_at = now.timestamp()
        user.last_at = user.updated_at
        channel = bot.get_channel(user.channel_id)
        await channel.send(f"Hey! Here is {message.author.mention}'s standup!\n\n{message.content}")
        await message.channel.send("Standup sent!")
        session.add(user)
        session.commit()
        print(f"{message.author.id} sent standup.")

    session.close()


@bot.slash_command(description="A test command", guild_ids=TESTING_GUILD_IDS)
async def ping(interaction: nextcord.Interaction):
    print("Pong!")
    await interaction.response.send_message("Pong!")


@bot.slash_command(description="Register and/or edit a standup!", guild_ids=TESTING_GUILD_IDS)
async def standup(interaction: nextcord.Interaction, message_time: str, days: Optional[str] = '', time_zone: Optional[str] = 'utc'):
    if days == '':
        days = []
    else:
        days = days.split(',')

    session = Session(engine)

    statement = select([User]).where(
        User.channel_id == interaction.channel_id
    ).where(User.user_id == interaction.user.id)
    results = session.execute(statement)
    user = results.first()
    user = user[0] if user else None
    if not user:
        user = User(user_id=interaction.user.id, username=interaction.user.name, days=days, message_time=parse(message_time),
                    channel_id=interaction.channel_id, guild_id=interaction.guild_id, next_at=next_time(parse(message_time), time_zone), tz=time_zone)
        session.add(user)
        session.commit()
        await interaction.response.send_message(f"{interaction.user.mention} registered their standup for {days or 'weekdays'}")
        print(
            f"Registered {user.username} with id {user.id}, days {user.days}, time {user.message_time}")
    else:
        # update isn't working for some reason
        # this will work fine.
        session.delete(user)
        user = User(user_id=interaction.user.id, username=interaction.user.name, days=days, message_time=parse(message_time),
                    channel_id=interaction.channel_id, guild_id=interaction.guild_id, next_at=next_time(parse(message_time), time_zone), tz=time_zone)
        session.add(user)
        session.commit()
        await interaction.response.send_message(f"{interaction.user.mention} updated their standup for {days or 'weekdays'}")
        print(
            f"Updated {user.username} with id {user.id}, days {user.days}, time {user.message_time}")

    session.close()


@bot.slash_command(description="Remove the user's standup.", guild_ids=TESTING_GUILD_IDS)
async def sitdown(interaction: nextcord.Interaction):
    session = Session(engine)

    statement = select([User]).where(
        User.channel_id == interaction.channel_id
    ).where(User.user_id == interaction.user.id)
    results = session.execute(statement)
    user = results.first()
    user = user[0] if user else None
    if not user:
        await interaction.response.send_message(f"{interaction.user.mention} you are not registered.")
    else:
        session.delete(user)
        session.commit()
        await interaction.response.send_message(f"{interaction.user.mention} removed their standup.")
        print(f"{interaction.user.name} removed their standup.")

    session.close()


@bot.slash_command(description="Get the next standup time", guild_ids=TESTING_GUILD_IDS)
async def next(interaction: nextcord.Interaction):
    session = Session(engine)

    statement = select([User]).where(
        User.channel_id == interaction.channel_id
    ).where(User.user_id == interaction.user.id)
    results = session.execute(statement)
    user = results.first()
    user: User = user[0] if user else None
    if not user:
        await interaction.response.send_message(f"{interaction.user.mention} you haven't registered your standup yet. See here: https://github.com/multisig-labs/GoGoStandup")
        session.close()
        return
    else:
        await interaction.response.send_message(f"{interaction.user.mention} your next standup is {arrow.get(user.next_at).to(user.tz).humanize()} at {arrow.get(user.next_at).to(user.tz).format('HH:mm on MMMM Do')}")
        session.close()


@bot.slash_command(description="Get the last standup time", guild_ids=TESTING_GUILD_IDS)
async def last(interaction: nextcord.Interaction):
    session = Session(engine)

    statement = select([User]).where(
        User.channel_id == interaction.channel_id
    ).where(User.user_id == interaction.user.id)
    results = session.execute(statement)
    user = results.first()
    user: User = user[0] if user else None
    if not user:
        await interaction.response.send_message(f"{interaction.user.mention} you haven't registered your standup yet. See here: https://github.com/multisig-labs/GoGoStandup")
        session.close()
        return
    else:
        await interaction.response.send_message(f"{interaction.user.mention} your last standup was {arrow.get(user.last_at).to(user.tz).humanize()} at {arrow.get(user.last_at).to(user.tz).format('HH:mm on MMMM Do')}")
        session.close()


@ tasks.loop(seconds=10)
async def send_loop():
    now = arrow.utcnow()
    session = Session(engine)
    statement = select([User]).where(User.next_at <= now.timestamp())
    results = session.execute(statement)
    users = results.fetchall()
    # the users are returned as tuples
    # so we need to remove them from the tuple
    users = [user[0] for user in users]
    for user in users:
        channel = bot.get_channel(user.channel_id)
        member = channel.guild.get_member(user.user_id)
        if not member:
            print(f"Member {user.user_id} not found! Deleting user.")
            session.delete(user)
            continue
        dm_chan = await member.create_dm()
        print(f"Sending standup message to {user.user_id}")
        await dm_chan.send(f"Hey {user.username}! Its time for your daily standup! Please respond to this DM to complete your standup.")
        user.next_at = next_time(user.message_time, user.tz, user.days)
        user.updated_at = arrow.utcnow().timestamp()
        session.add(user)
    session.commit()
    session.close()


@ send_loop.before_loop
async def before_send_loop():
    await bot.wait_until_ready()


if __name__ == "__main__":
    send_loop.start()
    bot.run(os.getenv("TOKEN"))
