"""Mock API payloads for the Encrata SDK test suite.

These mirror the REAL wire format the API returns: every endpoint uses full
field names (name, company, socials, ...).
"""

from __future__ import annotations

# ── Email intelligence ────────────────────────────────────────────────

PERSON = {
    "name": "Elon Musk",
    "email": "elon@tesla.com",
    "company": "Tesla",
    "role": "CEO",
    "industry": "Automotive",
    "location": "Austin, Texas",
    "birthplace": "Pretoria, South Africa",
    "current_location": "Austin, Texas",
    "bio": "Founder, CEO and product architect.",
    "age": "53",
    "gender": "male",
    "education": "University of Pennsylvania",
    "phone": "+1-555-0100",
    "photo": "https://cdn.encrata.com/p/elon.jpg",
    "validity": "valid",
    "socials": {
        "linkedin": "https://linkedin.com/in/elonmusk",
        "twitter": "https://x.com/elonmusk",
        "instagram": None,
        "facebook": None,
        "github": "https://github.com/elonmusk",
    },
    "breach": {
        "count": 2,
        "services": ["Adobe", "LinkedIn"],
        "exposed_data": ["email", "password"],
    },
    "registered_services": {"count": 3, "services": ["GitHub", "Stripe", "Slack"]},
    "news": [
        {"title": "Tesla hits record", "url": "https://news/1", "date": "2025-01-02", "source": "Reuters"},
    ],
    "publications": [
        {"title": "Rockets 101", "url": "https://doi/1", "year": 2020, "cited_by": 42},
    ],
}

VALIDATION = {"email": "elon@tesla.com", "validity": "valid", "message": "Deliverable mailbox."}

BREACH_REPORT = {
    "email": "elon@tesla.com",
    "count": 2,
    "services": ["Adobe", "LinkedIn"],
    "exposed_data": ["email", "password"],
    "message": "Found in 2 breaches.",
}

# ── Monitors ───────────────────────────────────────────────────────────

MONITOR = {
    "id": "mon_123",
    "name": "Sales VIPs",
    "status": "active",
    "frequency": "monthly",
    "change_detection": "diff_only",
    "data_source_type": "list",
    "data_source_ref": "list_456",
    "email_count": 12,
    "tracked_fields": ["name", "company", "role"],
    "last_run_at": None,
    "next_run_at": "2026-07-01T00:00:00Z",
    "created_at": "2026-06-01T00:00:00Z",
}

MONITORS_RESPONSE = {"monitors": [MONITOR]}

MONITOR_RUN = {
    "id": "run_789",
    "monitor_id": "mon_123",
    "monitor_name": "Sales VIPs",
    "status": "completed",
    "total_records": 12,
    "changes_detected": 3,
    "credits_used": 12,
    "started_at": "2026-06-10T00:00:00Z",
    "completed_at": "2026-06-10T00:05:00Z",
}

RUNS_RESPONSE = {"runs": [MONITOR_RUN], "total": 1}

SNAPSHOT = {
    "id": "snap_1",
    "email": "elon@tesla.com",
    "has_changes": True,
    "changes": {"company": ["SpaceX", "Tesla"]},
    "data": {"name": "Elon Musk", "company": "Tesla"},
}

RESULTS_RESPONSE = {"results": [SNAPSHOT], "total": 1}

TRIGGER_RUN_RESPONSE = {"run_id": "run_789", "status": "queued", "message": "Run queued."}

# ── Contact lists ───────────────────────────────────────────────────

CONTACT_LIST = {
    "id": "list_456",
    "name": "Sales VIPs",
    "email_count": 3,
    "created_at": "2026-06-01T00:00:00Z",
}
