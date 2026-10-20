"""APIP v1 opportunity discovery starter.

Deterministic, zero-cost hypothesis generator. It is not an AI model,
customer-acquisition bot, or proof of income.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "opportunities-latest.json"

OPPORTUNITIES = [
    {
        "id": "LOCAL_MENU_REFRESH",
        "customer": "Small restaurants and food vendors",
        "problem": "Menus may be unclear, outdated, or difficult to share digitally",
        "deliverable": "A cleaned-up menu and shareable price-list mock-up",
        "revenue_path": "Offer a fixed-price menu cleanup after the owner approves outreach",
        "validation_test": "Prepare one sample from public information and ask an owner for feedback before offering paid work",
        "estimated_cost_ngn": 0,
    },
    {
        "id": "INVENTORY_TRACKER",
        "customer": "Small retailers and market traders",
        "problem": "Stock and reorder decisions may be tracked inconsistently",
        "deliverable": "A reusable stock and reorder spreadsheet template",
        "revenue_path": "Demonstrate a sample and offer setup or customization",
        "validation_test": "Build a generic sample and test whether a target user can use it without help",
        "estimated_cost_ngn": 0,
    },
    {
        "id": "WEBSITE_CLARITY_AUDIT",
        "customer": "Small businesses with public websites",
        "problem": "Visitors may not quickly understand the offer or next step",
        "deliverable": "A concise audit with specific copy and navigation improvements",
        "revenue_path": "Offer a paid audit or implementation after a prospect confirms the problem",
        "validation_test": "Audit one public site as a sample; seek permission before using it in a public portfolio",
        "estimated_cost_ngn": 0,
    },
    {
        "id": "PRODUCT_DESCRIPTION_PACK",
        "customer": "Small online sellers",
        "problem": "Product listings may not explain benefits and specifications clearly",
        "deliverable": "A pack of improved product descriptions based on supplied facts",
        "revenue_path": "Sell a small fixed-scope listing-improvement service",
        "validation_test": "Create a before-and-after sample using public product facts and test it with a seller",
        "estimated_cost_ngn": 0,
    },
    {
        "id": "APIP_PROTOCOL_SETUP",
        "customer": "Solo builders and small teams",
        "problem": "Income experiments may lack clear evidence, cost, and outcome tracking",
        "deliverable": "A configured experiment ledger and validation report",
        "revenue_path": "Offer a setup service using the APIP approach",
        "validation_test": "Prepare a demo ledger and ask target users whether it solves a real tracking problem",
        "estimated_cost_ngn": 0,
    },
]


def readiness_score(item: dict) -> int:
    """Operational completeness only; never a probability of sale."""
    fields = ("customer", "problem", "deliverable", "revenue_path", "validation_test")
    return sum(bool(item.get(field)) for field in fields) + int(item.get("estimated_cost_ngn") == 0)


def generate() -> dict:
    ideas = sorted(OPPORTUNITIES, key=lambda item: (-readiness_score(item), item["id"]))
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "HYPOTHESES_ONLY",
        "notice": "These are unvalidated hypotheses, not confirmed demand or income.",
        "ai_model_used": False,
        "paid_services_used": False,
        "external_outreach_performed": False,
        "money_movement_performed": False,
        "income_generated_or_verified": False,
        "opportunities": [
            {**item, "status": "UNVALIDATED_HYPOTHESIS", "readiness_score": readiness_score(item)}
            for item in ideas
        ],
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    data = generate()
    OUTPUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated {len(data['opportunities'])} unvalidated hypotheses.")
    print(f"Report: {OUTPUT.relative_to(ROOT)}")
    print("No AI model, paid service, external outreach, or money movement was used.")


if __name__ == "__main__":
    main()
