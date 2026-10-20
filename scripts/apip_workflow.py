"""Policy boundary and local executor for APIP income workflows.

Plans may be AI-generated, but action type and policy are assigned by this
module. Only a reversible local proposal-draft action has an executor today.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any
from uuid import UUID, uuid4


POLICIES = {
    "research_public_listing": {
        "approval": False,
        "handler": None,
        "blocked_status": "CAPABILITY_MISSING",
        "reason": "A permitted live public-source connector is not installed in this workflow runtime.",
    },
    "prepare_proposal_draft": {
        "approval": False,
        "handler": "prepare_proposal_draft",
        "blocked_status": None,
        "reason": "Creates a local draft from the supplied listing and owner-confirmed facts.",
    },
    "submit_proposal": {
        "approval": True,
        "handler": None,
        "blocked_status": "CAPABILITY_MISSING",
        "reason": "Submitting contacts a buyer and may consume marketplace credits; a verified account and submission adapter are unavailable.",
    },
    "spend_money": {
        "approval": True,
        "handler": None,
        "blocked_status": "CAPABILITY_MISSING",
        "reason": "Spending requires a reconciled opening balance, a specific amount, and a permitted payment integration.",
    },
    "accept_contract": {
        "approval": True,
        "handler": None,
        "blocked_status": "OWNER_HANDOFF",
        "reason": "Contract acceptance is a legally binding owner decision.",
    },
    "move_money": {
        "approval": True,
        "handler": None,
        "blocked_status": "OWNER_HANDOFF",
        "reason": "Financial transfers must be completed by the owner in the provider's secure flow.",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any, limit: int = 2000) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def _valid_uuid(value: Any) -> bool:
    try:
        return str(UUID(str(value))) == str(value)
    except (ValueError, TypeError, AttributeError):
        return False


def build_workflow(objective: str, actions: list[dict[str, Any]], authority: dict[str, Any] | None = None) -> dict[str, Any]:
    """Wrap proposed steps in protocol-assigned execution and approval states.

    `authority` is explicit owner scope; natural-language objective text alone
    never authorizes an external action or spending.
    """
    objective = _clean(objective, 3000)
    if not objective:
        raise ValueError("An objective is required.")
    authority = authority or {}
    normalized = []
    for proposed in actions:
        kind = _clean(proposed.get("type"), 80)
        policy = POLICIES.get(kind)
        action_id = str(uuid4())
        data = proposed.get("data") if isinstance(proposed.get("data"), dict) else {}
        if not policy:
            status = "UNSUPPORTED"
            reason = "This action type is not in APIP's allowlisted action catalog."
            approval_required = False
        else:
            approval_required = policy["approval"]
            approved = False
            if kind == "spend_money" and not authority.get("spending_balance_verified", False):
                status = "BLOCKED_BUDGET_LEDGER_UNVERIFIED"
                reason = "Reconcile the opening balance before asking for spending approval."
            elif kind == "spend_money" and (
                not isinstance(data.get("amount"), (int, float))
                or data.get("amount", 0) <= 0
                or not isinstance(authority.get("spending_limit", 0), (int, float))
                or data.get("amount", 0) > authority.get("spending_limit", 0)
            ):
                status = "BLOCKED_SPENDING_LIMIT"
                reason = "The specific amount must be positive and within the owner's explicit spending limit."
            elif policy["blocked_status"] == "OWNER_HANDOFF":
                status = "OWNER_HANDOFF"
                reason = policy["reason"]
            elif not policy["handler"]:
                # Do not ask the owner to approve an action the system cannot perform.
                status = policy["blocked_status"] or "CAPABILITY_MISSING"
                reason = policy["reason"]
            elif approval_required and not approved:
                status = "APPROVAL_REQUIRED"
                reason = policy["reason"]
            else:
                status = "READY"
                reason = policy["reason"]
        normalized.append({
            "action_id": action_id,
            "type": kind,
            "description": _clean(proposed.get("description"), 500),
            "data": data,
            "status": status,
            "approval_required": approval_required,
            "policy_reason": reason,
            "evidence": None,
        })
    return {
        "workflow_id": str(uuid4()),
        "created_at_utc": _now(),
        "objective": objective,
        "authority": {
            "spending_limit": authority.get("spending_limit", 0),
            "spending_balance_verified": bool(authority.get("spending_balance_verified", False)),
        },
        "actions": normalized,
        "verified_income": 0,
        "events": [],
        "status": "READY" if any(a["status"] == "READY" for a in normalized) else "BLOCKED",
    }


def _draft_text(data: dict[str, Any]) -> str:
    title = _clean(data.get("title"), 180) or "Proposal draft"
    buyer_request = _clean(data.get("buyer_request"), 1500) or "[Insert the verified buyer request]"
    scope = _clean(data.get("scope"), 1000) or "[Confirm a small, specific scope with the buyer]"
    owner_facts = _clean(data.get("owner_confirmed_facts"), 800)
    experience = owner_facts if owner_facts else "[Add only relevant experience you can truthfully confirm before sending.]"
    return (
        f"# {title}\n\n"
        "Hello,\n\n"
        f"I can help with: {buyer_request}\n\n"
        f"Relevant experience: {experience}\n\n"
        f"Proposed first scope: {scope}\n\n"
        "Before starting, I would confirm the input format, completion rules, deadline, and funded payment milestone through the marketplace. "
        "I will preserve the source data and flag ambiguous records instead of guessing.\n\n"
        "Regards,\n[Your name]\n\n"
        "---\nDRAFT ONLY. Not submitted. Replace bracketed fields and verify every claim before use.\n"
    )


def execute_local_action(workflow: dict[str, Any], action_id: str, data_dir: Path) -> dict[str, Any]:
    """Run only a READY, allowlisted local action and attach a hash evidence ref."""
    actions = workflow.get("actions", [])
    action = next((item for item in actions if item.get("action_id") == action_id), None)
    if action is None:
        raise ValueError("Action not found in this workflow.")
    if action.get("status") != "READY":
        raise PermissionError(f"Action is {action.get('status')}; only READY actions can run locally.")
    if action.get("type") != "prepare_proposal_draft":
        raise PermissionError("No local executor is registered for this action type.")

    workflow_id = str(workflow.get("workflow_id", ""))
    if not _valid_uuid(workflow_id) or not _valid_uuid(action_id):
        raise ValueError("Invalid workflow identifier.")
    out_dir = data_dir / "workflows" / workflow_id
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{action_id}.md"
    content = _draft_text(action.get("data", {}))
    with output_path.open("x", encoding="utf-8") as output:
        output.write(content)
    digest = sha256(content.encode("utf-8")).hexdigest()
    evidence = {"path": str(output_path), "sha256": digest}
    action["status"] = "COMPLETED"
    action["evidence"] = evidence
    action["completed_at_utc"] = _now()
    event = {
        "at_utc": action["completed_at_utc"],
        "event": "LOCAL_ACTION_COMPLETED",
        "workflow_id": workflow_id,
        "action_id": action_id,
        "action_type": action["type"],
        "evidence": evidence,
        "external_action": False,
        "payment_verified": False,
    }
    with (out_dir / "events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    if any(item["status"] == "READY" for item in actions):
        workflow["status"] = "READY"
    elif all(item["status"] == "COMPLETED" for item in actions):
        workflow["status"] = "COMPLETED"
    else:
        workflow["status"] = "BLOCKED"
    workflow.setdefault("events", []).append(event)
    return event


def approval_scope(action: dict[str, Any]) -> dict[str, Any]:
    """Return the exact non-secret scope an owner would approve at action time."""
    data = action.get("data", {})
    return {
        "action_id": action.get("action_id"),
        "type": action.get("type"),
        "target": _clean(data.get("url") or data.get("target"), 500),
        "amount": data.get("amount"),
        "currency": _clean(data.get("currency"), 8),
    }


def approve_action(workflow: dict[str, Any], action_id: str, confirmed_scope: dict[str, Any]) -> dict[str, Any]:
    """Apply one action-scoped approval only after an executor is available.

    This is deliberately fail-closed today because no external action handler
    is registered. It is the transition hook for a future connected adapter.
    """
    action = next((item for item in workflow.get("actions", []) if item.get("action_id") == action_id), None)
    if action is None:
        raise ValueError("Action not found in this workflow.")
    if action.get("status") != "APPROVAL_REQUIRED":
        raise PermissionError(f"Action is {action.get('status')}; no approval is being requested.")
    if confirmed_scope != approval_scope(action):
        raise ValueError("Approval scope does not exactly match the action details.")
    policy = POLICIES.get(action.get("type"), {})
    if not policy.get("handler"):
        raise PermissionError("Approval recorded nowhere: the required execution capability is unavailable.")
    action["approval_granted"] = True
    action["status"] = "READY"
    event = {
        "at_utc": _now(), "event": "ACTION_APPROVED", "workflow_id": workflow.get("workflow_id"),
        "action_id": action_id, "scope": approval_scope(action), "external_action": False,
    }
    workflow.setdefault("events", []).append(event)
    return event
