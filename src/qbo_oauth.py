
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request
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

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Missing QuickBooks credentials in .env")

if ENVIRONMENT != "sandbox":
    raise RuntimeError("This demo permits sandbox mode only.")

app = Flask(__name__)

auth_client = AuthClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    environment=ENVIRONMENT,
)

@app.get("/")
def home():
    return (
        '<h2>RE Financial Analyzer</h2>'
        '<p>QuickBooks sandbox connection demo</p>'
        '<a href="/connect">Connect to QuickBooks</a>'
    )

@app.get("/connect")
def connect():
    url = auth_client.get_authorization_url(
        scopes=[Scopes.ACCOUNTING]
    )
    return redirect(url)

@app.get("/callback")
def callback():
    if request.args.get("error"):
        return jsonify({
            "connected": False,
            "error": "Authorization was denied or failed."
        }), 400

    code = request.args.get("code")
    realm_id = request.args.get("realmId")

    if not code or not realm_id:
        return jsonify({
            "connected": False,
            "error": "Missing authorization code or company ID."
        }), 400

    try:
        # Exchange the authorization code for OAuth tokens.
        auth_client.get_bearer_token(code, realm_id=realm_id)

        # Verify access by requesting company information from the sandbox.
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
        payload = response.json()
        company = payload.get("CompanyInfo", {})

        # Never return access tokens, refresh tokens, or secrets.
        return jsonify({
            "connected": True,
            "environment": "sandbox",
            "company_id": realm_id,
            "company_name": company.get("CompanyName", "Not provided"),
            "verification": "Company information retrieved successfully.",
        })

    except requests.RequestException:
        app.logger.exception("QuickBooks sandbox API request failed.")
        return jsonify({
            "connected": False,
            "error": "Sandbox API request failed. Check app permissions and authorization."
        }), 502
    except Exception:
        app.logger.exception("QuickBooks authorization failed.")
        return jsonify({
            "connected": False,
            "error": "Authorization failed. Check the redirect URI and app configuration."
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
