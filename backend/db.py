"""
Metadata store connection — Lakebase (Databricks' managed Postgres), attached
to this app as a "Database" resource. Databricks injects PGHOST/PGPORT/
PGDATABASE/PGUSER as environment variables and grants this app's service
principal a matching Postgres role automatically.

Authentication uses a short-lived OAuth token rather than a static password —
generated fresh on each new connection via a SQLAlchemy `do_connect` event
hook, since Lakebase tokens expire (enforced at connect time, not mid-session).
"""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from databricks.sdk.core import Config

_cfg = Config()

_engine = create_engine(
    "postgresql+psycopg://"
    f"{os.environ.get('PGUSER', _cfg.client_id)}@"
    f"{os.environ['PGHOST']}:{os.environ.get('PGPORT', '5432')}/"
    f"{os.environ.get('PGDATABASE', 'databricks_postgres')}"
    "?sslmode=require"
)


@event.listens_for(_engine, "do_connect")
def _inject_oauth_token(dialect, conn_rec, cargs, cparams):
    # Fetch a fresh token on every new physical connection rather than
    # caching one — avoids using an expired token on a long-lived app.
    cparams["password"] = _cfg.authenticate()["Authorization"].split(" ")[1]


SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
