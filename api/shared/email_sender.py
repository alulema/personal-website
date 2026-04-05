"""Email sending via Azure Communication Services."""
import os
from azure.communication.email import EmailClient


def _get_client() -> EmailClient:
    conn_str = os.environ["AZURE_COMMUNICATION_CONNECTION_STRING"]
    return EmailClient.from_connection_string(conn_str)


def _sender() -> str:
    return os.environ.get(
        "AZURE_COMMUNICATION_SENDER_ADDRESS",
        "DoNotReply@alexisalulema.com",
    )


def send_contact_notification(name: str, email: str, subject: str, message: str) -> None:
    destination = os.environ["CONTACT_DESTINATION_EMAIL"]
    client = _get_client()
    client.begin_send({
        "senderAddress": _sender(),
        "recipients": {"to": [{"address": destination}]},
        "content": {
            "subject": f"[alexisalulema.com] {subject}",
            "plainText": f"From: {name} <{email}>\n\n{message}",
            "html": (
                f"<p><strong>From:</strong> {name} &lt;{email}&gt;</p>"
                f"<p><strong>Subject:</strong> {subject}</p>"
                f"<hr/><p>{message.replace(chr(10), '<br/>')}</p>"
            ),
        },
    }).result()


def send_admin_demo_request(
    requester_name: str,
    requester_email: str,
    project_id: str,
    project_name: str,
    reason: str,
    approve_30_url: str,
    approve_60_url: str,
    approve_120_url: str,
) -> None:
    admin_email = os.environ["ADMIN_EMAIL"]
    client = _get_client()
    btn = "display:inline-block;padding:10px 20px;margin:4px;border-radius:6px;background:#38bdf8;color:#0a0f1e;font-weight:600;text-decoration:none;"
    client.begin_send({
        "senderAddress": _sender(),
        "recipients": {"to": [{"address": admin_email}]},
        "content": {
            "subject": f"[Demo Request] {project_name} — {requester_name}",
            "html": f"""
            <h2>New demo access request</h2>
            <p><strong>Project:</strong> {project_name} ({project_id})</p>
            <p><strong>Requester:</strong> {requester_name} &lt;{requester_email}&gt;</p>
            <p><strong>Reason:</strong> {reason or '(not provided)'}</p>
            <h3>Approve access for:</h3>
            <a href="{approve_30_url}" style="{btn}">30 minutes</a>
            <a href="{approve_60_url}" style="{btn}">1 hour</a>
            <a href="{approve_120_url}" style="{btn}">2 hours</a>
            <p style="color:#666;font-size:12px;">These links expire in 24 hours.</p>
            """,
        },
    }).result()


def send_demo_access_granted(
    requester_name: str,
    requester_email: str,
    project_name: str,
    access_url: str,
    duration_minutes: int,
) -> None:
    client = _get_client()
    client.begin_send({
        "senderAddress": _sender(),
        "recipients": {"to": [{"address": requester_email}]},
        "content": {
            "subject": f"[alexisalulema.com] Access granted — {project_name}",
            "html": f"""
            <h2>Your demo access is ready</h2>
            <p>Hi {requester_name},</p>
            <p>Your access to <strong>{project_name}</strong> has been approved for <strong>{duration_minutes} minutes</strong>.</p>
            <p><a href="{access_url}" style="display:inline-block;padding:12px 24px;border-radius:6px;background:#38bdf8;color:#0a0f1e;font-weight:600;text-decoration:none;">Open Demo</a></p>
            <p style="color:#666;font-size:12px;">This link will stop working after {duration_minutes} minutes.</p>
            """,
        },
    }).result()
