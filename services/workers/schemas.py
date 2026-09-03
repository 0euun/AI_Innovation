"""Platform Connector가 생성하는 공통 이벤트 계약."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Platform = Literal["demo_forum", "demo_social", "demo_video", "x", "instagram", "youtube", "threads"]


class Engagement(BaseModel):
    likes: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)


class NormalizedEvent(BaseModel):
    event_id: str
    occurred_at: datetime
    platform: Platform
    author_ref: str  # 원본 계정 ID가 아닌 pseudonymous reference
    target_ref: str
    text: str
    hashtags: list[str] = Field(default_factory=list)
    engagement: Engagement = Field(default_factory=Engagement)

