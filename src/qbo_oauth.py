
import json
import os
import secrets
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request, session
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

CLIENT_ID = os.getenv("QBO_CLIENT_ID")
CLIENT_SECRET = os.getenv("QBO_CLIENT_SECRET")
REDIRECT_URI = os.getenv(
    "QBO_REDIRECT_URI", "http://localhost:8000/callback"
)
ENVIRONMENT = os.getenv("QBO_ENVIRONMENT", "sandbox")
TOKEN_FILE = ROOT / "token.json"

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Missing QuickBooks credentials in .env")

if ENVIRONMENT != "sandbox":
    raise RuntimeError("This demo permits sandbox mode only.")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=REDIRECT_URI.startswith("https://"),
)

auth_client = AuthClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    environment=ENVIRONMENT,
)


def save_tokens():
    """Persist OAuth credentials locally; never expose them to the browser."""
    token_data = {
        "access_token": auth_client.access_token,
        "refresh_token": auth_client.refresh_token,
        "realm_id": auth_client.realm_id,
        "expires_in": auth_client.expires_in,
        "x_refresh_token_expires_in": (
            auth_client.x_refresh_token_expires_in
        ),
        "x_refresh_token_hard_expires_in": (
            auth_client.x_refresh_token_hard_expires_in
        ),
    }

    if not token_data["access_token"] or not token_data["refresh_token"]:
        raise RuntimeError("OAuth response did not contain both required tokens.")
    temporary_file = TOKEN_FILE.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(token_data, indent=2),
        encoding="utf-8",
    )

    # Restrict permissions where supported; keep token.json Git-ignored.
    try:
        os.chmod(temporary_file, 0o600)
    except OSError:
        pass

    temporary_file.replace(TOKEN_FILE)

    try:
        os.chmod(TOKEN_FILE, 0o600)
    except OSError:
        pass


@app.get("/")
def home():
    return (
        "<h2>RE Financial Analyzer</h2>"
        "<p>QuickBooks sandbox connection demo</p>"
        '<a href="/connect">Connect to QuickBooks</a>'
    )


@app.get("/connect")
def connect():
    state = secrets.token_urlsafe(32)
    session["qbo_oauth_state"] = state

    url = auth_client.get_authorization_url(
        scopes=[Scopes.ACCOUNTING],
        state_token=state,
    )
    return redirect(url)


@app.get("/callback")
def callback():
    if request.args.get("error"):
        session.pop("qbo_oauth_state", None)
        return jsonify({
            "connected": False,
            "error": "Authorization was denied or failed.",
        }), 400

    returned_state = request.args.get("state")
    expected_state = session.pop("qbo_oauth_state", None)

    if (
        not returned_state
        or not expected_state
        or not secrets.compare_digest(returned_state, expected_state)
    ):
        return jsonify({
            "connected": False,
            "error": "Invalid OAuth state. Start the connection again.",
        }), 400

    code = request.args.get("code")
    realm_id = request.args.get("realmId")

    if not code or not realm_id:
        return jsonify({
            "connected": False,
            "error": "Missing authorization code or company ID.",
        }), 400

    try:
        auth_client.get_bearer_token(code, realm_id=realm_id)

        if not auth_client.access_token or not auth_client.refresh_token:
            raise RuntimeError("OAuth token exchange returned incomplete credentials.")

        response = requests.get(
            f"https://sandbox-quickbooks.api.intuit.com/v3/company/"
            f"{realm_id}/companyinfo/{realm_id}",
            headers={
                "Authorization": f"Bearer {auth_client.access_token}",
                "Accept": "application/json",
            },
            timeout=20,
        )
        response.raise_for_status()

        company = response.json().get("CompanyInfo", {})

        # Save credentials only after the sandbox API request succeeds.
        save_tokens()

        return jsonify({
            "connected": True,
            "environment": "sandbox",
            "company_id": realm_id,
            "company_name": company.get("CompanyName", "Not provided"),
            "verification": "Company information retrieved successfully.",
            "tokens_saved": True,
        })

    except requests.RequestException:
        app.logger.warning("QuickBooks sandbox API request failed.")
        return jsonify({
            "connected": False,
            "error": "Sandbox API request failed. Check authorization and app configuration.",
        }), 502
    except Exception:
        app.logger.exception("QuickBooks OAuth callback failed.")
        return jsonify({
            "connected": False,
            "error": "Authorization failed. Check the sandbox connection and local configuration.",
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
