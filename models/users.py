from typing import List, Optional

import arrow
from sqlmodel import JSON, Column, Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    username: str
    created_at: float = Field(default=arrow.utcnow().timestamp())
    updated_at: float = Field(default=arrow.utcnow().timestamp())
    next_at: float = Field(default=arrow.now().shift(days=1).timestamp())
    days: List[str] = Field(sa_column=Column(JSON, default=[]))
    message_time: int  # the time to send the message in seconds
    channel_id: Optional[str] = Field(
        default=None, foreign_key="channel.channel_id")
