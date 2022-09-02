from typing import List, Optional

import arrow
from sqlmodel import JSON, Column, Field, SQLModel, BigInteger


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    created_at: float = Field(default=arrow.utcnow().timestamp())
    updated_at: float = Field(default=arrow.utcnow().timestamp())
    next_at: float = Field(default=arrow.now().shift(days=1).timestamp())
    last_at: float = Field(default=0)
    days: Optional[List[str]] = Field(sa_column=Column(JSON, default=[]))
    message_time: int  # the time to send the message in seconds
    channel_id: int = Field(sa_column=Column(BigInteger))
    guild_id: int = Field(sa_column=Column(BigInteger))
    user_id: int = Field(sa_column=Column(BigInteger))
    tz: Optional[str] = Field(default="utc")
