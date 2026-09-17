import uuid
from fastapi import FastAPI, HTTPException

from .models import IncidentRequest, ApprovalRequest
from . import store
from .agent import investigate
from .tools import execute_approved_action

app = FastAPI(
    title="AI Operations Agent",
    version="1.0.0",
    description="FDE portfolio project: incident investigation + human-approved remediation."
)

store.init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/incidents")
def create_incident(req: IncidentRequest):
    incident_id = f"INC-{uuid.uuid4().hex[:10].upper()}"

    store.save_incident({
        "incident_id": incident_id,
        "service": req.service,
        "severity": req.severity,
        "alert": req.alert,
        "environment": req.environment,
        "status": "investigating",
    })

    store.audit(incident_id, "incident_created", req.model_dump())

    result = investigate(
        incident_id=incident_id,
        service=req.service,
        severity=req.severity,
        alert=req.alert,
        environment=req.environment,
    )
    return result

@app.post("/approvals/{approval_id}")
def approve(approval_id: str, req: ApprovalRequest):
    approval = store.get_approval(approval_id)
    if not approval:
        raise HTTPException(404, "Approval not found")

    store.update_approval(approval_id, req.approved, req.approved_by)

    store.audit(
        approval["incident_id"],
        "approval_decision",
        {
            "approval_id": approval_id,
            "approved": req.approved,
            "approved_by": req.approved_by,
        },
    )

    if not req.approved:
        return {
            "status": "rejected",
            "approval_id": approval_id,
            "message": "No production action was executed."
        }

    # In a real system, store the service on the approval record and authorize
    # the adapter against the approved incident scope. This demo keeps the
    # executor simulated and limited to the known portfolio scenario.
    result = execute_approved_action(
        service="payments-api",
        action=approval["action"],
    )

    store.audit(approval["incident_id"], "action_executed", result)

    return {
        "status": "executed",
        "approval_id": approval_id,
        "result": result,
    }
