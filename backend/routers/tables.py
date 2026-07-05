"""
Registered-table allowlist endpoints (Section 6 of the design doc).
Stubbed for the scaffolding milestone — real list/create logic comes with
the bulk-update feature build.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_registered_tables():
    # TODO: query registered_tables via SessionLocal, return active rows only.
    return {"tables": []}
