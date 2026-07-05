"""
Connection to the Databricks SQL Warehouse, authenticated as this app's own
auto-provisioned service principal (M2M / app authorization) — not the
logged-in user's identity. The service principal is granted access only to
the tables on the registered-table allowlist (see metadata_schema.sql).

`Config()` auto-discovers the service principal's credentials from the
environment Databricks injects at runtime (DATABRICKS_CLIENT_ID,
DATABRICKS_CLIENT_SECRET, DATABRICKS_HOST) — nothing to configure manually.
"""

import os
from contextlib import contextmanager

from databricks import sql
from databricks.sdk.core import Config

_cfg = Config()


@contextmanager
def warehouse_connection():
    conn = sql.connect(
        server_hostname=_cfg.host,
        http_path=os.environ["DATABRICKS_WAREHOUSE_HTTP_PATH"],
        credentials_provider=lambda: _cfg.authenticate,
    )
    try:
        yield conn
    finally:
        conn.close()


def run_query(query: str, params: tuple | None = None) -> list[dict]:
    """Runs a parameterized query and returns rows as dicts. Never f-string
    user input into `query` — always pass values via `params`."""
    with warehouse_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            columns = [c[0] for c in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
