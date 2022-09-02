from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Channel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: str
    guild_id: str
    created_at: datetime = Field(default=datetime.utcnow())
