from app.agent import demo_decision
from app.tools import get_service_health, get_recent_logs, get_deployment, search_runbooks

def test_payment_timeout_gets_safe_proposal():
    service = "payments-api"
    health = get_service_health(service)
    logs = get_recent_logs(service)
    deployment = get_deployment(service)
    runbooks = search_runbooks("5xx timeout payment provider", service)

    result = demo_decision(
        service,
        "SEV-1",
        "5xx rate is above 20%",
        health,
        logs,
        deployment,
        runbooks,
    )

    assert result["needs_approval"] is True
    assert result["proposed_action"] == "rolling_restart"
    assert result["confidence"] > 0.8

def test_healthy_service_does_not_get_restart():
    service = "orders-api"
    result = demo_decision(
        service,
        "SEV-3",
        "normal traffic",
        get_service_health(service),
        get_recent_logs(service),
        get_deployment(service),
        search_runbooks("normal traffic", service),
    )

    assert result["needs_approval"] is False
    assert result["proposed_action"] is None
