"""Cloudflare Turnstile server-side token verification."""
import os
import httpx

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


async def verify_turnstile(token: str, remote_ip: str | None = None) -> bool:
    secret = os.environ.get("TURNSTILE_SECRET_KEY", "")
    if not secret:
        raise RuntimeError("TURNSTILE_SECRET_KEY not configured")

    payload = {"secret": secret, "response": token}
    if remote_ip:
        payload["remoteip"] = remote_ip

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(TURNSTILE_VERIFY_URL, data=payload)
        resp.raise_for_status()
        result = resp.json()

    return bool(result.get("success", False))
