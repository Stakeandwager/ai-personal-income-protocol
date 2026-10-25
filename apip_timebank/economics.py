"""Deterministic, test-only APIP TimeBank reward calculations.

No payment integrations or persistence are implemented here. Monetary values use
integer minor units, and inputs must be supplied as explicit records by a caller.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class FundingEntry:
    entry_id: str
    currency: str
    amount_minor: int
    status: str  # VERIFIED only means reconciled/received for this calculation
    allocated_to_rewards_minor: int
    restricted: bool = False
    reversed: bool = False

@dataclass(frozen=True)
class Deduction:
    deduction_id: str
    currency: str
    amount_minor: int
    approved: bool

@dataclass(frozen=True)
class RewardAllocation:
    subscriber_id: str
    currency: str
    eligible_points: int
    amount_minor: int


def distributable_pool(funding: Iterable[FundingEntry], deductions: Iterable[Deduction], currency: str) -> int:
    """Return available reward funds in minor units for one currency.

    Only unique, verified, unrestricted, unreversed funding records count.
    Only approved deductions for the same currency reduce the pool. Values must
    be non-negative. The result is floored at zero.
    """
    cur = currency.upper()
    seen: set[str] = set()
    total = 0
    for entry in funding:
        if not entry.entry_id or entry.entry_id in seen:
            raise ValueError(f"duplicate or empty funding ID: {entry.entry_id!r}")
        seen.add(entry.entry_id)
        if entry.currency.upper() != cur:
            continue
        if entry.amount_minor < 0 or entry.allocated_to_rewards_minor < 0:
            raise ValueError("funding amounts must be non-negative")
        if entry.allocated_to_rewards_minor > entry.amount_minor:
            raise ValueError("reward allocation cannot exceed funding entry amount")
        if entry.status.upper() == "VERIFIED" and not entry.restricted and not entry.reversed:
            total += entry.allocated_to_rewards_minor
    deduction_ids: set[str] = set()
    for deduction in deductions:
        if deduction.currency.upper() != cur or not deduction.approved:
            continue
        if not deduction.deduction_id or deduction.deduction_id in deduction_ids:
            raise ValueError(f"duplicate or empty deduction ID: {deduction.deduction_id!r}")
        deduction_ids.add(deduction.deduction_id)
        if deduction.amount_minor < 0:
            raise ValueError("deductions must be non-negative")
        total -= deduction.amount_minor
    return max(0, total)


def allocate_rewards(pool_minor: int, currency: str, points_by_subscriber: dict[str, int]) -> list[RewardAllocation]:
    """Allocate a pool proportionally using largest remainder in minor units.

    Ties are resolved by subscriber ID, making the result deterministic. Zero
    points or a zero pool produces zero allocations. Negative/invalid inputs fail.
    """
    if pool_minor < 0:
        raise ValueError("pool cannot be negative")
    if not currency or not currency.strip():
        raise ValueError("currency is required")
    if len(points_by_subscriber) != len(set(points_by_subscriber)):
        raise ValueError("subscriber IDs must be unique")
    for subscriber_id, points in points_by_subscriber.items():
        if not subscriber_id.strip() or not isinstance(points, int) or isinstance(points, bool) or points < 0:
            raise ValueError("subscriber IDs must be non-empty and points must be non-negative integers")
    total_points = sum(points_by_subscriber.values())
    if total_points == 0 or pool_minor == 0:
        return [RewardAllocation(s, currency.upper(), p, 0) for s, p in sorted(points_by_subscriber.items())]
    base: dict[str, int] = {}
    remainders: list[tuple[int, str]] = []
    for subscriber_id, points in points_by_subscriber.items():
        quotient, remainder = divmod(pool_minor * points, total_points)
        base[subscriber_id] = quotient
        remainders.append((remainder, subscriber_id))
    leftover = pool_minor - sum(base.values())
    for _, subscriber_id in sorted(remainders, key=lambda item: (-item[0], item[1]))[:leftover]:
        base[subscriber_id] += 1
    return [RewardAllocation(s, currency.upper(), points_by_subscriber[s], base[s]) for s in sorted(points_by_subscriber)]
