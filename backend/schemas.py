from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from .models import ApprovalMode, TaskStatus, DecisionSource

class ChildProfileCreate(BaseModel):
    name: str
    phone_number: str
    age: int
    backup_contact_phone: Optional[str] = None

class ChildProfileResponse(ChildProfileCreate):
    id: int
    parent_id: int
    approval_mode: ApprovalMode
    auto_approve_max_amount: Optional[float]
    auto_approve_timeout_minutes: Optional[int]

    class Config:
        from_attributes = True

class TaskDetails(BaseModel):
    category: str
    summary_text: str
    details: Dict[str, Any]
    confidence: float

class EmergencyEventResponse(BaseModel):
    trigger_reason: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ProcessCallResponse(BaseModel):
    call_id: str
    transcript: str
    is_emergency: bool
    task: Optional[TaskDetails] = None
    emergency_event: Optional[EmergencyEventResponse] = None

class TaskDecision(BaseModel):
    decision: str # "approved" or "declined"

class TaskDecisionResponse(BaseModel):
    status: str

class TaskRecordResponse(BaseModel):
    id: int
    child_id: int
    call_id: str
    transcript: str
    summary_text: str
    category: str
    details_json: str
    status: TaskStatus
    decision_source: Optional[DecisionSource]
    created_at: datetime
    decided_at: Optional[datetime]

    class Config:
        from_attributes = True
