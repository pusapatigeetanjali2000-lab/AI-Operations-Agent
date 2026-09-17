from typing import Literal, Optional
from pydantic import BaseModel, Field

Severity = Literal["SEV-1", "SEV-2", "SEV-3"]

class IncidentRequest(BaseModel):
    service: str
    severity: Severity
    alert: str
    environment: str = "production"

class ApprovalRequest(BaseModel):
    approved: bool
    approved_by: str = Field(min_length=2)

class ToolCall(BaseModel):
    tool: str
    arguments: dict
    result: dict

class IncidentResult(BaseModel):
    incident_id: str
    status: str
    diagnosis: str
    confidence: float
    evidence: list[str]
    proposed_action: Optional[str] = None
    approval_id: Optional[str] = None
    tool_calls: list[ToolCall] = []
