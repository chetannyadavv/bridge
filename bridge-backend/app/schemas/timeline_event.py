from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TimelineEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dispute_id: str
    timestamp: datetime
    title: str
    description: str
