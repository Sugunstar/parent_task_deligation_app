from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from models import ApprovalMode, TaskStatus, DecisionSource


# ─── Child Profile ───────────────────────────────────────────────

class ChildProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone_number: str = Field(min_length=1, max_length=20)
    age: int = Field(ge=1, le=18)
    backup_contact_phone: Optional[str] = None


class ChildProfileUpdate(BaseModel):
    """Partial update — all fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=1, max_length=20)
    age: Optional[int] = Field(None, ge=1, le=18)
    backup_contact_phone: Optional[str] = None


class ChildProfileResponse(BaseModel):
    id: int
    parent_id: int
    name: str
    phone_number: str
    age: int
    approval_mode: ApprovalMode
    auto_approve_max_amount: Optional[float] = None
    auto_approve_timeout_minutes: Optional[int] = None
    backup_contact_phone: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Task / Call Processing ──────────────────────────────────────

class TaskDetails(BaseModel):
    category: str
    summary_text: str
    details: Dict[str, Any]
    confidence: float


class TaskDecision(BaseModel):
    decision: str = Field(pattern="^(approved|declined)$")


class TaskRecordResponse(BaseModel):
    id: int
    child_id: int
    call_id: str
    transcript: str
    summary_text: str
    category: str
    details_json: str
    status: TaskStatus
    decision_source: Optional[DecisionSource] = None
    created_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Emergency ───────────────────────────────────────────────────

class EmergencyEventResponse(BaseModel):
    id: int
    child_id: int
    trigger_reason: str
    transcript_snippet: str
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    backup_contact_notified: bool
    acknowledged: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Call Processing Response ────────────────────────────────────

class ProcessCallResponse(BaseModel):
    call_id: str
    task_id: int
    transcript: str
    is_emergency: bool
    task: Optional[TaskDetails] = None
    emergency_event: Optional[EmergencyEventResponse] = None
