from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class SyncStatusResponse(BaseModel):
    job_id: int
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str
    produtos_count: Optional[int] = None
    codigos_count: Optional[int] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class SyncTriggerResponse(BaseModel):
    job_id: int
    status: str
    message: str


class SyncListResponse(BaseModel):
    jobs: list[SyncStatusResponse]
    total: int