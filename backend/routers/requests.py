"""
Update-request lifecycle endpoints (Section 7 of the design doc):
build/preview -> submit -> review -> apply -> audit.
Stubbed for the scaffolding milestone — real logic comes with the
bulk-update feature build (the first mode implemented end to end).
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/pending")
def list_pending_requests():
    # TODO: query update_requests WHERE status = 'pending', scoped to the
    # current user's approver assignments.
    return {"requests": []}


@router.post("/")
def submit_request():
    # TODO: validate filter/diff against the registered table's allowlisted
    # columns, run the COUNT(*) preview, insert a pending update_requests row.
    return {"status": "not_implemented"}
