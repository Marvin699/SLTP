from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ScoreSessionCreate(BaseModel):
    section_id: str
    title: str
    groups: Optional[list] = None
    dimensions: Optional[list] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ScoreSessionResponse(BaseModel):
    id: int
    token: str
    section_id: str
    title: str
    groups: list
    dimensions: list
    weights: Optional[dict] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScoreSubmitItem(BaseModel):
    group_id: str
    dimension: str
    score: float


class ScoreSubmitRequest(BaseModel):
    session_token: str
    scorer_role: str
    scorer_name: Optional[str] = None
    scores: List[ScoreSubmitItem]


class GroupSummary(BaseModel):
    group_id: str
    dimension_scores: dict
    total_avg: float
    weighted_avg: Optional[float] = None
    score_count: int
