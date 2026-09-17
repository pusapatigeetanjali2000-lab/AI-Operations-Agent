from dataclasses import dataclass
from typing import Any

# In production these are adapters around Kubernetes, AWS, Datadog,
# ServiceNow, Jira, Slack, Postgres, etc.

SERVICES = {
    "payments-api": {
        "status": "degraded",
        "error_rate": 0.27,
        "latency_ms": 1840,
        "version": "2026.09.17.3",
        "healthy_replicas": 3,
        "desired_replicas": 6,
    },
    "orders-api": {
        "status": "healthy",
        "error_rate": 0.01,
        "latency_ms": 180,
        "version": "2026.09.17.2",
        "healthy_replicas": 6,
        "desired_replicas": 6,
    },
}

LOGS = {
    "payments-api": [
        "15:41 ERROR upstream timeout to payment-provider",
        "15:42 ERROR connection pool exhausted",
        "15:42 WARN retry queue depth=1840",
        "15:43 ERROR 502 returned by /charge",
        "15:43 ERROR payment-provider timeout rate=31%",
    ],
    "orders-api": [
        "15:40 INFO request latency p95=180ms",
        "15:41 INFO database connections normal",
    ],
}

RUNBOOKS = [
    {
        "id": "RB-001",
        "title": "Payment provider timeout",
        "service": "payments-api",
        "text": (
            "If payment-provider timeouts cause elevated 5xx errors, first confirm "
            "provider timeout logs and connection pool exhaustion. Check deployment "
            "health. Do not restart production automatically. If more than 20% 5xx "
            "persists for 5 minutes, escalate to the on-call engineer and propose "
            "rolling restart after approval."
        )
    },
    {
        "id": "RB-002",
        "title": "Healthy orders API",
        "service": "orders-api",
        "text": "No remediation is required when error rate is below 5% and replicas are healthy."
    },
]

def get_service_health(service: str) -> dict[str, Any]:
    return SERVICES.get(service, {
        "status": "unknown",
        "error_rate": None,
        "latency_ms": None,
        "version": None,
        "healthy_replicas": 0,
        "desired_replicas": 0,
    })

def get_recent_logs(service: str, limit: int = 20) -> list[str]:
    return LOGS.get(service, [])[-limit:]

def get_deployment(service: str) -> dict[str, Any]:
    health = get_service_health(service)
    return {
        "service": service,
        "version": health["version"],
        "healthy_replicas": health["healthy_replicas"],
        "desired_replicas": health["desired_replicas"],
    }

def search_runbooks(query: str, service: str) -> list[dict[str, str]]:
    words = set(query.lower().split())
    matches = []
    for rb in RUNBOOKS:
        if rb["service"] != service:
            continue
        haystack = f'{rb["title"]} {rb["text"]}'.lower()
        score = sum(1 for w in words if len(w) > 3 and w in haystack)
        if score:
            matches.append({**rb, "score": score})
    return sorted(matches, key=lambda x: x["score"], reverse=True)

def propose_rolling_restart(service: str) -> dict[str, Any]:
    # Proposal only. This tool NEVER changes production.
    return {
        "action": "rolling_restart",
        "service": service,
        "safety": "requires_human_approval",
        "reason": "Runbook allows a rolling restart after approval when persistent 5xx is confirmed."
    }

def execute_approved_action(service: str, action: str) -> dict[str, Any]:
    # Deliberately simulated for the portfolio project.
    if action != "rolling_restart":
        raise ValueError("Unsupported action")
    return {
        "executed": True,
        "service": service,
        "action": action,
        "mode": "SIMULATED",
        "message": "Production action simulated. Replace this adapter with a controlled Kubernetes/API implementation."
    }
