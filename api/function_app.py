"""
Azure Functions v2 — alexisalulema.com backend

Routes:
  POST /api/contact                  — contact form
  POST /api/demo/request             — request demo access
  GET  /api/demo/approve/{token}     — admin approves (via email link)
  GET  /api/demo/status/{id}         — frontend polls for demo status
"""
import json
import logging
import os
from datetime import datetime, timedelta, timezone

import azure.functions as func
import jwt
from pydantic import BaseModel, EmailStr, ValidationError

from shared.turnstile import verify_turnstile
from shared.email_sender import (
    send_contact_notification,
    send_admin_demo_request,
    send_demo_access_granted,
)
from shared.demo_store import create_ticket, activate_ticket, get_project_status

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "https://alexisalulema.com",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
}

PROJECT_NAMES = {
    "rag-demo": "RAG Chatbot",
    "bert-classifier": "BERT Text Classifier",
    "agent-ai-demo": "Multi-Agent AI",
    "fastapi-patterns": "FastAPI Production Patterns",
}

CONTAINER_APP_ENV_KEYS = {
    "rag-demo": "CONTAINER_APP_NAME_RAG",
    "bert-classifier": "CONTAINER_APP_NAME_BERT",
    "agent-ai-demo": "CONTAINER_APP_NAME_MULTIAGENT",
    "fastapi-patterns": "CONTAINER_APP_NAME_FASTAPI",
}


def _json_response(body: dict, status_code: int = 200) -> func.HttpResponse:
    return func.HttpResponse(
        body=json.dumps(body),
        status_code=status_code,
        headers=CORS_HEADERS,
    )


def _error(message: str, status_code: int = 400) -> func.HttpResponse:
    return _json_response({"error": message}, status_code)


def _jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET", "")
    if not secret or len(secret) < 32:
        raise RuntimeError("JWT_SECRET not configured or too short (min 32 chars)")
    return secret


def _site_base_url() -> str:
    return os.environ.get("SITE_BASE_URL", "https://alexisalulema.com").rstrip("/")


def _scale_container_app(project_id: str, min_replicas: int) -> None:
    """Scale a Container App to min_replicas (0 = scale to zero, 1 = bring up)."""
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.appcontainers import ContainerAppsAPIClient

    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    resource_group = os.environ["AZURE_RESOURCE_GROUP"]
    app_name_env = CONTAINER_APP_ENV_KEYS.get(project_id)
    if not app_name_env:
        raise ValueError(f"Unknown project_id: {project_id}")

    container_app_name = os.environ[app_name_env]
    credential = DefaultAzureCredential()
    client = ContainerAppsAPIClient(credential, subscription_id)

    existing = client.container_apps.get(resource_group, container_app_name)
    template = existing.template
    if template.scale is None:
        from azure.mgmt.appcontainers.models import Scale
        template.scale = Scale()
    template.scale.min_replicas = min_replicas

    client.container_apps.begin_update(
        resource_group,
        container_app_name,
        {"template": template},
    ).result()


# ---------------------------------------------------------------------------
# POST /api/contact
# ---------------------------------------------------------------------------

class ContactPayload(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    turnstileToken: str


@app.route(route="contact", methods=["POST", "OPTIONS"])
async def contact(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS_HEADERS)

    try:
        payload = ContactPayload(**req.get_json())
    except (ValidationError, ValueError) as exc:
        return _error(f"Invalid request: {exc}")

    remote_ip = req.headers.get("CF-Connecting-IP") or req.headers.get("X-Forwarded-For")

    try:
        valid = await verify_turnstile(payload.turnstileToken, remote_ip)
    except Exception as exc:
        logger.error("Turnstile verification error: %s", exc)
        return _error("Security check failed", 500)

    if not valid:
        return _error("Security challenge failed. Please try again.", 403)

    try:
        send_contact_notification(
            name=payload.name,
            email=payload.email,
            subject=payload.subject,
            message=payload.message,
        )
    except Exception as exc:
        logger.error("Email send error: %s", exc)
        return _error("Could not send message. Please try again later.", 500)

    return _json_response({"ok": True})


# ---------------------------------------------------------------------------
# POST /api/demo/request
# ---------------------------------------------------------------------------

class DemoRequestPayload(BaseModel):
    name: str
    email: EmailStr
    projectId: str
    reason: str = ""


@app.route(route="demo/request", methods=["POST", "OPTIONS"])
async def demo_request(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS_HEADERS)

    try:
        payload = DemoRequestPayload(**req.get_json())
    except (ValidationError, ValueError) as exc:
        return _error(f"Invalid request: {exc}")

    project_name = PROJECT_NAMES.get(payload.projectId)
    if not project_name:
        return _error("Unknown project", 404)

    try:
        ticket_id = create_ticket(
            project_id=payload.projectId,
            requester_name=payload.name,
            requester_email=payload.email,
            reason=payload.reason,
        )
    except Exception as exc:
        logger.error("Could not create ticket: %s", exc)
        return _error("Could not process request. Please try again.", 500)

    secret = _jwt_secret()
    base_url = _site_base_url()

    def _make_approve_token(duration_minutes: int) -> str:
        return jwt.encode(
            {
                "sub": "demo-approve",
                "ticketId": ticket_id,
                "projectId": payload.projectId,
                "requesterEmail": payload.email,
                "requesterName": payload.name,
                "durationMinutes": duration_minutes,
                "exp": datetime.now(timezone.utc) + timedelta(hours=24),
            },
            secret,
            algorithm="HS256",
        )

    try:
        send_admin_demo_request(
            requester_name=payload.name,
            requester_email=payload.email,
            project_id=payload.projectId,
            project_name=project_name,
            reason=payload.reason,
            approve_30_url=f"{base_url}/api/demo/approve/{_make_approve_token(30)}",
            approve_60_url=f"{base_url}/api/demo/approve/{_make_approve_token(60)}",
            approve_120_url=f"{base_url}/api/demo/approve/{_make_approve_token(120)}",
        )
    except Exception as exc:
        logger.error("Could not send admin email: %s", exc)
        return _error("Could not process request. Please try again.", 500)

    return _json_response({"ok": True, "ticketId": ticket_id}, 202)


# ---------------------------------------------------------------------------
# GET /api/demo/approve/{token}
# ---------------------------------------------------------------------------

_APPROVE_HTML_SUCCESS = """<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><title>Demo Approved</title>
<style>body{{font-family:system-ui,sans-serif;background:#0a0f1e;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}}
.card{{background:#111827;border:1px solid #1e2a3a;border-radius:12px;padding:2rem 3rem;text-align:center;max-width:480px}}
h1{{color:#38bdf8;margin-bottom:0.5rem}}p{{color:#64748b}}</style></head>
<body><div class="card"><h1>✓ Access Granted</h1>
<p>{name} will receive an email with the demo link in a moment.</p>
<p>Duration: <strong>{duration} minutes</strong></p></div></body></html>"""

_APPROVE_HTML_ERROR = """<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><title>Error</title>
<style>body{{font-family:system-ui,sans-serif;background:#0a0f1e;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}}
.card{{background:#111827;border:1px solid #1e2a3a;border-radius:12px;padding:2rem 3rem;text-align:center;max-width:480px}}
h1{{color:#f87171;margin-bottom:0.5rem}}p{{color:#64748b}}</style></head>
<body><div class="card"><h1>Error</h1><p>{message}</p></div></body></html>"""


@app.route(route="demo/approve/{token}", methods=["GET"])
def demo_approve(req: func.HttpRequest) -> func.HttpResponse:
    token = req.route_params.get("token", "")
    html_headers = {"Content-Type": "text/html; charset=utf-8"}

    try:
        claims = jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return func.HttpResponse(
            _APPROVE_HTML_ERROR.format(message="This approval link has expired."),
            status_code=410,
            headers=html_headers,
        )
    except jwt.InvalidTokenError:
        return func.HttpResponse(
            _APPROVE_HTML_ERROR.format(message="Invalid approval link."),
            status_code=400,
            headers=html_headers,
        )

    if claims.get("sub") != "demo-approve":
        return func.HttpResponse(
            _APPROVE_HTML_ERROR.format(message="Invalid token type."),
            status_code=400,
            headers=html_headers,
        )

    ticket_id: str = claims["ticketId"]
    project_id: str = claims["projectId"]
    requester_email: str = claims["requesterEmail"]
    requester_name: str = claims["requesterName"]
    duration_minutes: int = claims["durationMinutes"]
    project_name = PROJECT_NAMES.get(project_id, project_id)
    base_url = _site_base_url()

    # Scale Container App up
    try:
        _scale_container_app(project_id, min_replicas=1)
    except Exception as exc:
        logger.error("Container App scale error: %s", exc)
        return func.HttpResponse(
            _APPROVE_HTML_ERROR.format(message="Could not start demo environment. Check Azure logs."),
            status_code=500,
            headers=html_headers,
        )

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
    access_url = f"{base_url}/demos/{project_id}/"

    try:
        activate_ticket(project_id, ticket_id, access_url, expires_at)
    except Exception as exc:
        logger.error("Could not activate ticket: %s", exc)

    try:
        send_demo_access_granted(
            requester_name=requester_name,
            requester_email=requester_email,
            project_name=project_name,
            access_url=access_url,
            duration_minutes=duration_minutes,
        )
    except Exception as exc:
        logger.error("Could not send access email: %s", exc)

    return func.HttpResponse(
        _APPROVE_HTML_SUCCESS.format(name=requester_name, duration=duration_minutes),
        status_code=200,
        headers=html_headers,
    )


# ---------------------------------------------------------------------------
# GET /api/demo/status/{id}
# ---------------------------------------------------------------------------

@app.route(route="demo/status/{id}", methods=["GET", "OPTIONS"])
def demo_status(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS_HEADERS)

    project_id = req.route_params.get("id", "")
    if project_id not in PROJECT_NAMES:
        return _error("Unknown project", 404)

    try:
        status = get_project_status(project_id)
    except Exception as exc:
        logger.error("Status check error: %s", exc)
        return _json_response({"status": "offline", "expiresAt": None})

    return _json_response(status)


# ---------------------------------------------------------------------------
# Timer: expire sessions + scale Container Apps to zero (every 5 minutes)
# ---------------------------------------------------------------------------

def _expire_and_scale_down(project_id: str) -> None:
    from azure.data.tables import TableServiceClient

    conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        return

    table_name = os.environ.get("DEMO_TABLE_NAME", "demotickets")
    service = TableServiceClient.from_connection_string(conn_str)
    table = service.get_table_client(table_name)

    now = datetime.now(timezone.utc)
    entities = list(table.query_entities(
        f"PartitionKey eq '{project_id}' and status eq 'active'"
    ))

    expired_any = False
    for entity in entities:
        expires_raw = entity.get("expiresAt", "")
        if expires_raw:
            expires_at = datetime.fromisoformat(expires_raw)
            if expires_at <= now:
                table.update_entity({
                    "PartitionKey": entity["PartitionKey"],
                    "RowKey": entity["RowKey"],
                    "status": "expired",
                }, mode="merge")
                expired_any = True
                logger.info("Expired ticket %s for %s", entity["RowKey"], project_id)

    if expired_any:
        status = get_project_status(project_id)
        if status["status"] != "active":
            _scale_container_app(project_id, min_replicas=0)
            logger.info("Scaled down Container App for %s", project_id)


@app.timer_trigger(schedule="0 */5 * * * *", arg_name="timer", run_on_startup=False)
def cleanup_expired_demos(timer: func.TimerRequest) -> None:
    logger.info("Cleanup timer triggered")
    for project_id in PROJECT_NAMES:
        try:
            _expire_and_scale_down(project_id)
        except Exception as exc:
            logger.error("Cleanup error for %s: %s", project_id, exc)
