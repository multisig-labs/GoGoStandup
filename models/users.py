from typing import List, Optional

import arrow
from sqlmodel import JSON, Column, Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    username: str
    created_at: float = Field(default=arrow.utcnow().timestamp())
    updated_at: float = Field(default=arrow.utcnow().timestamp())
    next_at: float = Field(default=arrow.now().shift(days=1).timestamp())
    last_at: float = Field(default=0)
    days: Optional[List[str]] = Field(sa_column=Column(JSON, default=[]))
    message_time: int  # the time to send the message in seconds
    channel_id: int
    guild_id: int
    tz: Optional[str] = Field(default="utc")
