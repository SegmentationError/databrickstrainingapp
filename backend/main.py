"""
Entry point for the Delta update portal backend.

This is intentionally a skeleton: the goal of this milestone is proving the
three connectivity paths work end to end (identity, SQL Warehouse, metadata
store) before any real feature logic (bulk/row-edit/CSV) gets built on top.
"""

from fastapi import FastAPI, Depends
from sqlalchemy import text

from backend.auth import get_current_user, CurrentUser
from backend.db import SessionLocal
from backend.databricks_client import run_query
from backend.routers import tables, requests as requests_router

app = FastAPI(title="Delta Update Portal")

app.include_router(tables.router, prefix="/api/tables", tags=["tables"])
app.include_router(requests_router.router, prefix="/api/requests", tags=["requests"])


@app.get("/api/whoami")
def whoami(user: CurrentUser = Depends(get_current_user)):
    """Proves the identity-forwarding path: Entra ID SSO -> Databricks ->
    X-Forwarded-* headers -> this app, with no custom login code."""
    return {"email": user.email, "user_name": user.user_name}


@app.get("/api/health/warehouse")
def health_warehouse():
    """Proves the app's service principal can reach the SQL Warehouse."""
    rows = run_query("SELECT 1 AS ok")
    return {"warehouse": "reachable", "result": rows}


@app.get("/api/health/metadata-store")
def health_metadata_store():
    """Proves the app can reach the Lakebase metadata store."""
    with SessionLocal() as session:
        session.execute(text("SELECT 1"))
    return {"metadata_store": "reachable"}
