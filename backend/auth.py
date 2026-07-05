"""
User identity for the Delta update portal.

Databricks Apps sit behind a reverse proxy that already completed the Entra ID
SSO login before a request ever reaches this app. The proxy forwards the
authenticated user's identity in `X-Forwarded-*` headers — there is no custom
MSAL/OIDC flow to write here.

We deliberately do NOT use `x-forwarded-access-token` (on-behalf-of-user
authorization). Per the design doc, this app uses its own service principal
(app/M2M authorization) to talk to the SQL Warehouse, scoped to the
registered-table allowlist — not the individual user's Unity Catalog grants.
The user's identity is only needed for audit trail / role checks.
"""

from dataclasses import dataclass
from fastapi import Request, HTTPException


@dataclass
class CurrentUser:
    email: str
    user_name: str


def get_current_user(request: Request) -> CurrentUser:
    email = request.headers.get("x-forwarded-email")
    user_name = request.headers.get("x-forwarded-user")

    if not email:
        # Local development fallback — Databricks Apps headers aren't present
        # outside the deployed runtime. Never let this fallback apply in prod;
        # the absence of the header there would mean something is misconfigured.
        import os

        if os.environ.get("LOCAL_DEV") == "true":
            return CurrentUser(email="local-dev@example.com", user_name="local-dev")
        raise HTTPException(status_code=401, detail="Missing identity headers — is this running behind Databricks Apps?")

    return CurrentUser(email=email, user_name=user_name or email)
