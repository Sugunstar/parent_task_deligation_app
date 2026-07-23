import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from .database import Base
import enum

class ApprovalMode(str, enum.Enum):
    always_approve = "always_approve"
    auto_approve_under_threshold = "auto_approve_under_threshold"

class TaskStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    declined = "declined"
    executed = "executed"
    failed = "failed"

class DecisionSource(str, enum.Enum):
    manual = "manual"
    auto_timeout = "auto_timeout"

class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    auth_id = Column(String, unique=True, index=True) # Firebase Auth ID
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    children = relationship("ChildProfile", back_populates="parent")

class ChildProfile(Base):
    __tablename__ = "child_profiles"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id"))
    name = Column(String)
    phone_number = Column(String, index=True)
    age = Column(Integer)
    approval_mode = Column(Enum(ApprovalMode), default=ApprovalMode.always_approve)
    auto_approve_max_amount = Column(Float, nullable=True)
    auto_approve_timeout_minutes = Column(Integer, default=5, nullable=True)
    backup_contact_phone = Column(String, nullable=True)
    voice_embedding = Column(Text, nullable=True) # Assuming JSON or base64 string for simplicity

    parent = relationship("Parent", back_populates="children")
    tasks = relationship("TaskRecord", back_populates="child")
    emergency_events = relationship("EmergencyEvent", back_populates="child")

class TaskRecord(Base):
    __tablename__ = "task_records"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id"))
    call_id = Column(String, index=True)
    transcript = Column(Text)
    summary_text = Column(String)
    category = Column(String) # "food" | "cab" | "none"
    details_json = Column(Text) # JSON string
    status = Column(Enum(TaskStatus), default=TaskStatus.pending)
    decision_source = Column(Enum(DecisionSource), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)

    child = relationship("ChildProfile", back_populates="tasks")

class EmergencyEvent(Base):
    __tablename__ = "emergency_events"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id"))
    trigger_reason = Column(String)
    transcript_snippet = Column(Text)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    backup_contact_notified = Column(Boolean, default=False)
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    child = relationship("ChildProfile", back_populates="emergency_events")
