# AI Operations Agent

A production-style AI Operations Agent for a SaaS company.

## Business problem

When an application has an incident, an operations engineer normally has to:
1. Read the alert.
2. Inspect service health and recent logs.
3. Check deployment/version information.
4. Find the relevant runbook.
5. Decide whether a safe remediation is possible.
6. Ask for approval before changing production.
7. Execute the approved action.
8. Record an audit trail.
9. Produce an incident summary.

This project turns that workflow into an agent with tools, deterministic guardrails, human approval, audit logging, and an evaluation suite.

## Architecture

Alert -> FastAPI -> Agent -> Tools
                         |-> service health
                         |-> logs
                         |-> deployment metadata
                         |-> runbook retrieval
                         |-> remediation proposal
                         |-> human approval
                         |-> audit log

The remediation executor is deliberately simulated. Replace it with your real Kubernetes/cloud/ITSM adapter only after adding authentication, authorization, approval policies, and production safeguards.

## Stack

- Python
- FastAPI
- OpenAI Responses API
- Pydantic
- SQLite for the demo audit store
- Docker
- pytest
- Tool-calling agent loop

## Run

```bash
uv venv
uv pip install -r requirements.txt
copy .env.example .env
uv run uvicorn app.main:app --reload
```

Linux/macOS:

```bash
cp .env.example .env
uv run uvicorn app.main:app --reload
```

Open:
http://127.0.0.1:8000/docs

If OPENAI_API_KEY is missing, the service still runs in DEMO mode using deterministic decision logic. For the FDE portfolio version, configure a real model.

## Example

POST `/incidents`

```json
{
  "service": "payments-api",
  "severity": "SEV-1",
  "alert": "5xx rate is above 20% for 8 minutes",
  "environment": "production"
}
```

Then approve the proposed remediation:

POST `/approvals/{approval_id}`

```json
{
  "approved": true,
  "approved_by": "human-oncall@example.com"
}
```

## FDE skills demonstrated

- translating an operational problem into a workflow
- tool/API integration
- structured outputs
- retrieval over customer runbooks
- human-in-the-loop control
- production-style auditability
- failure handling
- evaluation
- Dockerized deployment
- API design
- observability-ready event logging

## Real customer extensions

1. Kubernetes adapter:
   - get pods
   - describe deployment
   - rollout status
   - restart a deployment only after approval

2. AWS adapter:
   - CloudWatch logs
   - ECS/EKS health
   - deployment metadata

3. Datadog/Grafana adapter:
   - metrics and traces

4. Jira/ServiceNow:
   - create and update incidents

5. Slack/Teams:
   - send approval requests

6. PostgreSQL/Snowflake:
   - inspect business KPIs

7. RAG:
   - replace the small local runbook store with pgvector, Pinecone, or another vector database

8. Evaluation:
   - add 50–200 historical incidents and measure tool-selection accuracy, groundedness, escalation rate, and unsafe-action rate
  
<img width="1366" height="768" alt="Image" src="https://github.com/user-attachments/assets/f9f4bf97-5adb-4ba0-bc74-3f95c6e91185" />
<img width="1366" height="768" alt="Image" src="https://github.com/user-attachments/assets/62592c21-8a4c-4b53-ad99-deb9f43f132a" />
<img width="1366" height="768" alt="Image" src="https://github.com/user-attachments/assets/8dc62322-0930-4de7-9467-d52981f9bf2e" />
<img width="1366" height="768" alt="Image" src="https://github.com/user-attachments/assets/e70e2935-0151-44ee-a2da-c20ca6ba16e4" />
