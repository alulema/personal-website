"""Azure Table Storage operations for demo request tickets."""
import os
import uuid
from datetime import datetime, timezone
from azure.data.tables import TableServiceClient, TableClient
from azure.core.exceptions import ResourceNotFoundError

TABLE_NAME_ENV = "DEMO_TABLE_NAME"
DEFAULT_TABLE = "demotickets"


def _get_table_client() -> TableClient:
    conn_str = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    table_name = os.environ.get(TABLE_NAME_ENV, DEFAULT_TABLE)
    service = TableServiceClient.from_connection_string(conn_str)
    service.create_table_if_not_exists(table_name)
    return service.get_table_client(table_name)


def create_ticket(
    project_id: str,
    requester_name: str,
    requester_email: str,
    reason: str,
) -> str:
    ticket_id = str(uuid.uuid4())
    table = _get_table_client()
    table.create_entity({
        "PartitionKey": project_id,
        "RowKey": ticket_id,
        "requesterName": requester_name,
        "requesterEmail": requester_email,
        "reason": reason,
        "status": "pending",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "expiresAt": "",
        "accessUrl": "",
    })
    return ticket_id


def activate_ticket(
    project_id: str,
    ticket_id: str,
    access_url: str,
    expires_at: datetime,
) -> None:
    table = _get_table_client()
    table.update_entity({
        "PartitionKey": project_id,
        "RowKey": ticket_id,
        "status": "active",
        "accessUrl": access_url,
        "expiresAt": expires_at.isoformat(),
    }, mode="merge")


def get_project_status(project_id: str) -> dict:
    """Returns { status: active|pending|offline, expiresAt: ISO string | None }"""
    table = _get_table_client()
    try:
        entities = list(table.query_entities(
            f"PartitionKey eq '{project_id}' and status eq 'active'"
        ))
    except ResourceNotFoundError:
        return {"status": "offline", "expiresAt": None}

    now = datetime.now(timezone.utc)
    for entity in entities:
        expires_raw = entity.get("expiresAt", "")
        if expires_raw:
            expires_at = datetime.fromisoformat(expires_raw)
            if expires_at > now:
                return {"status": "active", "expiresAt": expires_raw}

    # Check if any pending tickets exist
    try:
        pending = list(table.query_entities(
            f"PartitionKey eq '{project_id}' and status eq 'pending'"
        ))
        if pending:
            return {"status": "pending", "expiresAt": None}
    except ResourceNotFoundError:
        pass

    return {"status": "offline", "expiresAt": None}
