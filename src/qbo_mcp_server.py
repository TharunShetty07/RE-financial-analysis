
import json
import os
import threading
from pathlib import Path

import requests
from dotenv import load_dotenv
from intuitlib.client import AuthClient
from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

CLIENT_ID = os.getenv("QBO_CLIENT_ID")
CLIENT_SECRET = os.getenv("QBO_CLIENT_SECRET")
REDIRECT_URI = os.getenv(
    "QBO_REDIRECT_URI", "http://localhost:8000/callback"
)
ENVIRONMENT = os.getenv("QBO_ENVIRONMENT", "sandbox")
TOKEN_FILE = ROOT / "token.json"
TOKEN_LOCK = threading.Lock()

if ENVIRONMENT != "sandbox":
    raise RuntimeError("This MCP server only permits QuickBooks sandbox mode.")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Missing QuickBooks credentials in .env")

mcp = FastMCP("RE Financial QuickBooks Sandbox")


def load_tokens():
    if not TOKEN_FILE.exists():
        raise RuntimeError(
            "QuickBooks sandbox is not authenticated. Complete OAuth setup first."
        )

    data = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    if not data.get("access_token") or not data.get("refresh_token"):
        raise RuntimeError("The local token file is missing required OAuth tokens.")
    if not data.get("realm_id"):
        raise RuntimeError("The local token file is missing the company realm ID.")
    return data


def save_tokens(data):
    """Atomically save tokens without printing or returning secrets."""
    temp_file = TOKEN_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        os.chmod(temp_file, 0o600)
    except OSError:
        pass
    temp_file.replace(TOKEN_FILE)


def refresh_access_token():
    """Refresh the access token and persist Intuit's rotated refresh token."""
    with TOKEN_LOCK:
        data = load_tokens()

        client = AuthClient(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            environment=ENVIRONMENT,
        )
        client.refresh(data["refresh_token"])

        if not client.access_token or not client.refresh_token:
            raise RuntimeError(
                "QuickBooks token refresh returned incomplete credentials. "
                "Reauthorize the sandbox connection."
            )

        data["access_token"] = client.access_token
        data["refresh_token"] = client.refresh_token
        if client.expires_in is not None:
            data["expires_in"] = client.expires_in
        if client.x_refresh_token_expires_in is not None:
            data["x_refresh_token_expires_in"] = (
                client.x_refresh_token_expires_in
            )
        if client.x_refresh_token_hard_expires_in is not None:
            data["x_refresh_token_hard_expires_in"] = (
                client.x_refresh_token_hard_expires_in
            )

        save_tokens(data)
        return data


def qbo_get(path):
    """Make a read-only QuickBooks sandbox API request."""
    data = load_tokens()
    url = (
        "https://sandbox-quickbooks.api.intuit.com/v3/company/"
        f"{data['realm_id']}/{path.lstrip('/')}"
    )

    def send(access_token):
        return requests.get(
            url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            params={"minorversion": "75"},
            timeout=20,
        )

    response = send(data["access_token"])

    if response.status_code == 401:
        response.close()
        data = refresh_access_token()
        response = send(data["access_token"])

    if response.status_code == 401:
        response.close()
        raise RuntimeError(
            "QuickBooks rejected the refreshed access token. "
            "Reauthorize the sandbox connection."
        )

    response.raise_for_status()
    return response.json()


@mcp.tool()
def qbo_sandbox_status() -> dict:
    """Verify the connected QuickBooks sandbox company."""
    data = load_tokens()
    payload = qbo_get(f"companyinfo/{data['realm_id']}")
    company = payload.get("CompanyInfo", {})
    return {
        "connected": True,
        "environment": "sandbox",
        "company_name": company.get("CompanyName", "Not provided"),
        "verification": "Company information retrieved successfully.",
    }


@mcp.tool()
def qbo_list_accounts() -> dict:
    """Read the chart of accounts from the QuickBooks sandbox."""
    return qbo_get("query?query=select * from Account")


if __name__ == "__main__":
    mcp.run(transport="stdio")
