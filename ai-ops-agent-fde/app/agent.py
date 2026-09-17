import json
import uuid
from typing import Any

from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL
from .tools import (
    get_service_health,
    get_recent_logs,
    get_deployment,
    search_runbooks,
    propose_rolling_restart,
)
from .models import IncidentResult, ToolCall
from . import store

SYSTEM = """You are an AI Operations Agent embedded with a SaaS operations team.

Your job is to investigate incidents using evidence, not guesswork.

Rules:
- Never claim an action was executed unless the execution tool returned success.
- Never directly execute production remediation from the investigation endpoint.
- Production changes require explicit human approval.
- Cite concrete evidence from tool results.
- If evidence is insufficient, say so and escalate.
- Prefer the smallest safe remediation.
- Do not invent logs, metrics, versions, or runbook instructions.
- Return JSON with:
  diagnosis, confidence, evidence, proposed_action, needs_approval.
"""

def demo_decision(service, severity, alert, health, logs, deployment, runbooks):
    evidence = []
    if health["error_rate"] is not None:
        evidence.append(f"error_rate={health['error_rate']}")
    evidence.extend(logs[:4])
    if deployment["version"]:
        evidence.append(f"version={deployment['version']}")

    joined = " ".join(logs).lower()
    if service == "payments-api" and "timeout" in joined and health["error_rate"] and health["error_rate"] > 0.20:
        return {
            "diagnosis": "Elevated payment failures are consistent with upstream payment-provider timeouts and connection-pool exhaustion.",
            "confidence": 0.91,
            "evidence": evidence,
            "proposed_action": "rolling_restart",
            "needs_approval": True,
        }

    return {
        "diagnosis": "No safe remediation was established from the available evidence.",
        "confidence": 0.55,
        "evidence": evidence,
        "proposed_action": None,
        "needs_approval": False,
    }

def llm_decision(payload):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": json.dumps(payload, indent=2)},
        ],
    )
    text = response.output_text
    return json.loads(text)

def investigate(incident_id: str, service: str, severity: str, alert: str, environment: str):
    calls = []

    health = get_service_health(service)
    calls.append(ToolCall(tool="get_service_health", arguments={"service": service}, result=health))

    logs = get_recent_logs(service)
    calls.append(ToolCall(tool="get_recent_logs", arguments={"service": service}, result={"logs": logs}))

    deployment = get_deployment(service)
    calls.append(ToolCall(tool="get_deployment", arguments={"service": service}, result=deployment))

    runbooks = search_runbooks(alert, service)
    calls.append(ToolCall(tool="search_runbooks", arguments={"query": alert, "service": service}, result={"matches": runbooks}))

    payload = {
        "incident": {
            "incident_id": incident_id,
            "service": service,
            "severity": severity,
            "alert": alert,
            "environment": environment,
        },
        "health": health,
        "logs": logs,
        "deployment": deployment,
        "runbooks": runbooks,
    }

    if OPENAI_API_KEY:
        try:
            decision = llm_decision(payload)
        except Exception:
            decision = demo_decision(service, severity, alert, health, logs, deployment, runbooks)
    else:
        decision = demo_decision(service, severity, alert, health, logs, deployment, runbooks)

    approval_id = None
    if decision.get("needs_approval") and decision.get("proposed_action"):
        approval_id = str(uuid.uuid4())
        store.save_approval(
            approval_id,
            incident_id,
            decision["proposed_action"]
        )
        store.audit(incident_id, "approval_requested", {
            "approval_id": approval_id,
            "action": decision["proposed_action"]
        })

    store.audit(incident_id, "investigation_completed", {
        "diagnosis": decision["diagnosis"],
        "confidence": decision["confidence"],
        "evidence": decision["evidence"],
    })

    return IncidentResult(
        incident_id=incident_id,
        status="awaiting_human_approval" if approval_id else "investigated",
        diagnosis=decision["diagnosis"],
        confidence=float(decision["confidence"]),
        evidence=decision["evidence"],
        proposed_action=decision.get("proposed_action"),
        approval_id=approval_id,
        tool_calls=calls,
    )
