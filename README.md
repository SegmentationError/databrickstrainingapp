# Delta Update Portal — Scaffolding

This is the project skeleton, not the feature build. The goal of this milestone
is to prove three things work end to end before any bulk/row-edit/CSV logic
gets built on top:

1. **Identity** — Entra ID SSO, via Databricks Apps' own login, reaches this
   app as `X-Forwarded-Email` / `X-Forwarded-User` headers. No custom MSAL
   integration exists in this codebase (see `backend/auth.py`).
2. **SQL Warehouse connectivity** — this app's auto-provisioned service
   principal (not the logged-in user) can query Databricks (see
   `backend/databricks_client.py`).
3. **Metadata store connectivity** — Lakebase, Databricks' managed Postgres,
   attached as an app resource (see `backend/db.py`, `backend/models.py`).

`frontend/src/App.tsx` renders all three as a simple status page.

## What's deliberately NOT here yet

No bulk update, row editor, CSV upload, approval queue, or audit screen logic.
Those land on top of this skeleton, starting with bulk update (the simplest
end-to-end slice).

## Local development

```bash
# Backend
pip install -r requirements.txt
LOCAL_DEV=true uvicorn backend.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

`LOCAL_DEV=true` makes `auth.py` fall back to a fake identity, since the
`X-Forwarded-*` headers only exist behind the real Databricks Apps proxy.
The warehouse/metadata-store health checks still need real Databricks
credentials locally (e.g. `databricks auth login` + a `.env` with
`DATABRICKS_WAREHOUSE_HTTP_PATH`, `PGHOST`, etc.) — they won't pass with
`LOCAL_DEV` alone.

## Deploying

1. Create the app in the Databricks Apps UI (or via a `databricks.yml`
   bundle), pointing `source_code_path` at this directory.
2. In the app's **Resources** tab, attach:
   - A **SQL Warehouse** resource, keyed `sql-warehouse` (matches `app.yaml`).
   - A **Database** (Lakebase) resource, keyed `metadata-db` (matches
     `app.yaml`). This auto-creates a Postgres role for the app's service
     principal — no manual grants needed.
3. Grant the app's service principal `SELECT`/`MODIFY` on the actual Delta
   tables you register in `registered_tables` (Unity Catalog grants) —
   scoped only to what's on the allowlist, per the design doc.
4. Confirm Entra ID is configured as the SSO provider at the Databricks
   account level — this is the one external prerequisite that isn't part of
   this codebase at all.
5. `databricks apps deploy`.

## Why Lakebase for the metadata store

The design doc originally left this as "Postgres or a Delta control table,
your call." Lakebase resolves it cleanly: it's real Postgres (so the
`update_requests`/`audit_log` schema works as designed, including the
`approver_not_requester` check constraint), but it's a Databricks-native
resource — no separate database service to provision or operate, and the
app's service principal gets connected automatically.
