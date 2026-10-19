"""Zero-dependency football 1X2 prediction recorder.

Probabilities are generated from user-supplied expected goals using independent
Poisson goal models. This is a transparent baseline, not a trained model or a
claim of predictive edge. Version 1 has no real-money betting.
"""
import argparse
import csv
import math
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "data" / "football-predictions.csv"
FIELDS = [
    "prediction_id", "created_at_utc", "kickoff_utc", "home_team", "away_team",
    "home_expected_goals", "away_expected_goals", "p_home", "p_draw", "p_away",
    "predicted_outcome", "actual_home_goals", "actual_away_goals",
    "actual_outcome", "status", "model_version", "notes",
]
MODEL_VERSION = "poisson-baseline-1"


def poisson_distribution(expected_goals, max_goals=10):
    """Return normalized P(goals=k), for k in 0..max_goals."""
    try:
        lam = float(expected_goals)
    except (TypeError, ValueError) as exc:
        raise ValueError("Expected goals must be a number.") from exc
    if not math.isfinite(lam) or lam < 0 or lam > 8:
        raise ValueError("Expected goals must be between 0 and 8 inclusive.")
    values = [math.exp(-lam)]
    for k in range(1, max_goals + 1):
        values.append(values[-1] * lam / k)
    total = sum(values)
    if total <= 0:
        raise ValueError("Could not calculate a valid goal distribution.")
    return [value / total for value in values]


def calculate_probabilities(home_xg, away_xg, max_goals=10):
    home = poisson_distribution(home_xg, max_goals)
    away = poisson_distribution(away_xg, max_goals)
    p_home = p_draw = p_away = 0.0
    for h, hp in enumerate(home):
        for a, ap in enumerate(away):
            joint = hp * ap
            if h > a:
                p_home += joint
            elif h == a:
                p_draw += joint
            else:
                p_away += joint
    total = p_home + p_draw + p_away
    return p_home / total, p_draw / total, p_away / total


def outcome_for_score(home_goals, away_goals):
    if home_goals < 0 or away_goals < 0:
        raise ValueError("Goals cannot be negative.")
    if home_goals > away_goals:
        return "HOME"
    if home_goals == away_goals:
        return "DRAW"
    return "AWAY"


def choose_outcome(probabilities):
    labels = ("HOME", "DRAW", "AWAY")
    return labels[max(range(3), key=lambda index: probabilities[index])]


def _read_rows(path):
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"Prediction ledger header mismatch: {path}")
        return list(reader)


def _write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def create_prediction(path, home_team, away_team, home_xg, away_xg,
                      kickoff_utc="", notes=""):
    home_team = home_team.strip()
    away_team = away_team.strip()
    if not home_team or not away_team:
        raise ValueError("Both team names are required.")
    if home_team.casefold() == away_team.casefold():
        raise ValueError("Home and away teams must be different.")
    probs = calculate_probabilities(home_xg, away_xg)
    rows = _read_rows(path)
    row = {
        "prediction_id": uuid.uuid4().hex[:12],
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kickoff_utc": kickoff_utc.strip(),
        "home_team": home_team,
        "away_team": away_team,
        "home_expected_goals": f"{float(home_xg):.4f}",
        "away_expected_goals": f"{float(away_xg):.4f}",
        "p_home": f"{probs[0]:.6f}",
        "p_draw": f"{probs[1]:.6f}",
        "p_away": f"{probs[2]:.6f}",
        "predicted_outcome": choose_outcome(probs),
        "actual_home_goals": "",
        "actual_away_goals": "",
        "actual_outcome": "",
        "status": "OPEN",
        "model_version": MODEL_VERSION,
        "notes": notes.strip(),
    }
    rows.append(row)
    _write_rows(path, rows)
    return row


def resolve_prediction(path, prediction_id, home_goals, away_goals):
    if not isinstance(home_goals, int) or not isinstance(away_goals, int):
        raise ValueError("Final scores must be whole numbers.")
    actual = outcome_for_score(home_goals, away_goals)
    rows = _read_rows(path)
    matches = [row for row in rows if row["prediction_id"] == prediction_id]
    if not matches:
        raise ValueError(f"No prediction found with ID {prediction_id}.")
    row = matches[0]
    if row["status"] != "OPEN":
        raise ValueError("This prediction is already resolved; it cannot be overwritten.")
    row["actual_home_goals"] = str(home_goals)
    row["actual_away_goals"] = str(away_goals)
    row["actual_outcome"] = actual
    row["status"] = "RESOLVED"
    _write_rows(path, rows)
    return row


def build_parser():
    parser = argparse.ArgumentParser(
        description="Record football 1X2 probabilities. No betting or money movement."
    )
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER,
                        help="CSV ledger path (default: data/football-predictions.csv)")
    sub = parser.add_subparsers(dest="command", required=True)
    predict = sub.add_parser("predict", help="Record a pre-match prediction")
    predict.add_argument("--home", required=True, help="Home team name")
    predict.add_argument("--away", required=True, help="Away team name")
    predict.add_argument("--home-xg", required=True, type=float, help="Assumed home expected goals (0-8)")
    predict.add_argument("--away-xg", required=True, type=float, help="Assumed away expected goals (0-8)")
    predict.add_argument("--kickoff-utc", default="", help="Optional kickoff timestamp in UTC")
    predict.add_argument("--notes", default="", help="Optional source/assumption notes")
    resolve = sub.add_parser("resolve", help="Record final score for an OPEN prediction")
    resolve.add_argument("--id", required=True, help="Prediction ID printed by predict")
    resolve.add_argument("--home-goals", required=True, type=int)
    resolve.add_argument("--away-goals", required=True, type=int)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "predict":
            row = create_prediction(args.ledger, args.home, args.away,
                                    args.home_xg, args.away_xg,
                                    args.kickoff_utc, args.notes)
            print(f"Prediction ID: {row['prediction_id']}")
            print(f"{row['home_team']} vs {row['away_team']}")
            print(f"Home win: {float(row['p_home']):.1%} | Draw: {float(row['p_draw']):.1%} | Away win: {float(row['p_away']):.1%}")
            print(f"Most likely 1X2 outcome: {row['predicted_outcome']}")
            print(f"Recorded in: {args.ledger}")
            print("Model note: probabilities depend on your supplied expected-goal assumptions.")
        else:
            row = resolve_prediction(args.ledger, args.id, args.home_goals, args.away_goals)
            print(f"Resolved {row['prediction_id']}: {row['actual_outcome']} ({row['actual_home_goals']}-{row['actual_away_goals']})")
    except (ValueError, OSError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
