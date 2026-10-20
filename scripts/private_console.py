"""APIP Private Console v1: local-first opportunity planning and evidence logging.

Binds to loopback only. GPT output is advisory text, never executable code.
No outreach, purchases, payments, or external commitments are performed.
"""
from __future__ import annotations

import html
import json
import os
import secrets
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "private-console"
EVENTS_FILE = DATA_DIR / "events.jsonl"
PLANS_FILE = DATA_DIR / "plans.jsonl"
HOST = "127.0.0.1"
PORT = int(os.environ.get("APIP_CONSOLE_PORT", "8765"))
MAX_BODY = 16_000
VALID_OUTCOMES = {"TESTED_DEMAND", "TESTED_NO_DEMAND", "IN_PROGRESS", "ABANDONED_WITH_REASON"}
LOCK = threading.Lock()
CSRF_TOKEN = secrets.token_urlsafe(32)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_jsonl(path: Path, record: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOCK, path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path: Path, limit: int = 12) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return list(reversed(rows[-limit:]))


def safe_text(value: str, max_len: int = 3000) -> str:
    return " ".join((value or "").strip().split())[:max_len]


def parse_form_body(raw: bytes) -> dict[str, list[str]]:
    """Decode a bounded URL-encoded form, rejecting excessive field counts."""
    return parse_qs(raw.decode("utf-8", errors="replace"), keep_blank_values=True, max_num_fields=12)


def local_plan(objective: str, skills: str, constraints: str, location: str) -> str:
    """Useful no-API demo plan; never represents live market research."""
    who = location or "your target market"
    skills_line = skills or "skills and resources not yet specified"
    constraints_line = constraints or "zero upfront spend; no external commitments"
    return (
        "DEMO MODE — this is a planning hypothesis, not live internet research.\n\n"
        f"OBJECTIVE\n{objective}\n\n"
        f"AVAILABLE SKILLS / RESOURCES\n{skills_line}\n\n"
        f"CONSTRAINTS\n{constraints_line}\n\n"
        "NEXT 3 ACTIONS\n"
        f"1. Define one customer group in {who} and identify a costly, observable problem they already have.\n"
        "2. Create one small sample deliverable using only information you are allowed to use; do not contact or publish anything yet.\n"
        "3. Test the sample with one consenting reviewer. Record their exact feedback and whether they indicate willingness to pay; do not treat interest as income.\n\n"
        "VALIDATION TEST\n"
        "A real target user can explain the value of the sample, and at least one qualified person explicitly confirms whether they would pay and why. This is demand evidence, not payment evidence.\n\n"
        "RISKS / CHECKS\n"
        "Check legitimacy, competition, delivery effort, privacy, and whether the customer has authority and budget. Reject requests involving deception, prohibited access, or sensitive data without authorization.\n\n"
        "COST / MONEY\n"
        "Spend ceiling: NGN 0. Expected revenue: unknown. Verified income: NGN 0 / not established.\n\n"
        "AUTONOMY BOUNDARY\n"
        "This plan does not browse the live web, contact anyone, publish offers, execute code, spend money, or move funds."
    )


def call_openai(objective: str, skills: str, constraints: str, location: str) -> tuple[str, dict]:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    model = os.environ.get("OPENAI_MODEL", "").strip()
    if os.environ.get("APIP_ALLOW_PAID_API", "0") != "1":
        raise RuntimeError("Live API is disabled. Set APIP_ALLOW_PAID_API=1 only after approving API spending.")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set. Demo mode is available without a key.")
    if not model:
        raise RuntimeError("OPENAI_MODEL is not set. Set it to a model available in your API account.")

    prompt = f"""You are APIP, an evidence-driven personal income opportunity planner.
Build a practical, low-cost plan from the user's objective. Be candid about uncertainty; do not guarantee earnings.
Return plain text with these headings: OBJECTIVE, OPPORTUNITY HYPOTHESES, NEXT 3 ACTIONS, VALIDATION TEST, RISKS / CHECKS, COST / MONEY, AUTONOMY BOUNDARY.
Prefer real, specific opportunity sources if web search is enabled, and distinguish sourced facts from hypotheses. Never claim you contacted anyone, delivered work, or verified payment. Do not generate executable code or instructions for evading law, platform rules, consent, or access controls. No external action is authorized by this request. Assume a NGN 0 spending ceiling. Suggest only actions the user can review before execution.

USER OBJECTIVE: {objective}
SKILLS / RESOURCES: {skills or 'Not specified'}
LOCATION / MARKET: {location or 'Not specified'}
CONSTRAINTS: {constraints or 'No upfront spend; owner approval before external actions'}
"""
    payload: dict = {"model": model, "input": prompt, "max_output_tokens": 1400}
    if os.environ.get("APIP_WEB_SEARCH", "0") == "1":
        payload["tools"] = [{"type": "web_search"}]
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Do not log or surface request headers, which contain the API key.
        detail = exc.read(1200).decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API returned HTTP {exc.code}: {detail}") from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"API connection failed: {exc}") from None

    pieces = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    pieces.append(content["text"])
    result = "\n\n".join(pieces).strip()
    if not result:
        raise RuntimeError("The API response contained no readable output text.")
    metadata = {
        "mode": "live_api",
        "model": model,
        "web_search_enabled": os.environ.get("APIP_WEB_SEARCH", "0") == "1",
        "api_cost_usd": "not calculated by this prototype",
    }
    return result, metadata


def make_page(message: str = "") -> bytes:
    plans = read_jsonl(PLANS_FILE)
    events = read_jsonl(EVENTS_FILE)
    plan_cards = []
    for p in plans:
        body = html.escape(p.get("plan", ""))
        meta = html.escape(f"{p.get('created_at_utc','')} · {p.get('mode','')} · {p.get('status','DRAFT')}")
        plan_cards.append(f'<article><p class="meta">{meta}</p><pre>{body}</pre><form method="post" action="/outcome"><input type="hidden" name="csrf_token" value="{CSRF_TOKEN}"><input type="hidden" name="plan_id" value="{html.escape(p.get("plan_id", ""))}"><label>Record actual outcome<select name="outcome"><option value="IN_PROGRESS">Still working</option><option value="TESTED_DEMAND">Tested: demand evidence</option><option value="TESTED_NO_DEMAND">Tested: no demand</option><option value="ABANDONED_WITH_REASON">Abandoned with reason</option></select></label><input name="evidence" maxlength="500" placeholder="Evidence reference / short note (no secrets)"><button>Record outcome</button></form></article>')
    event_lines = "".join(f'<li><span class="meta">{html.escape(e.get("at_utc", ""))}</span> — {html.escape(e.get("event", ""))}: {html.escape(e.get("summary", ""))}</li>' for e in events)
    notice = f'<p class="notice">{html.escape(message)}</p>' if message else ""
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>APIP Private Console</title><style>
:root{{color-scheme:light dark;font:16px system-ui,sans-serif}}body{{max-width:960px;margin:0 auto;padding:24px;line-height:1.5}}h1{{margin-bottom:4px}}.sub,.meta{{opacity:.72;font-size:.9rem}}form,.panel,article{{border:1px solid #8886;border-radius:12px;padding:16px;margin:16px 0}}label{{display:block;margin:12px 0 5px}}input,textarea,select{{box-sizing:border-box;width:100%;padding:10px;border:1px solid #8888;border-radius:8px;font:inherit}}button{{padding:10px 14px;border:0;border-radius:8px;margin-top:12px;cursor:pointer;font-weight:650}}textarea{{min-height:86px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}}.notice{{padding:12px;border-left:4px solid #888;background:#8881}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}@media(max-width:640px){{.grid{{grid-template-columns:1fr}}}}li{{margin:8px 0}}.pill{{display:inline-block;border:1px solid #8888;border-radius:99px;padding:3px 9px;font-size:.8rem}}
</style></head><body><h1>APIP Private Console</h1><p class="sub">Local-only prototype · binds to 127.0.0.1 · no money custody · no external actions</p>{notice}<div class="panel"><span class="pill">DRAFT-ONLY EXECUTION</span><p>Describe what you want to achieve. APIP will create an opportunity plan. It will not send messages, publish offers, run generated code, spend money, or transfer funds.</p><form method="post" action="/plan"><input type="hidden" name="csrf_token" value="{CSRF_TOKEN}"><label for="objective">Your objective *</label><textarea id="objective" name="objective" required maxlength="3000" placeholder="I need to earn income. I can do ... and have ...">{''}</textarea><div class="grid"><div><label for="skills">Skills and resources</label><textarea id="skills" name="skills" maxlength="2000" placeholder="Skills, device, time available, portfolio"></textarea></div><div><label for="location">Target market / location</label><textarea id="location" name="location" maxlength="500" placeholder="For example: Lagos, Nigeria; remote work"></textarea></div></div><label for="constraints">Constraints</label><textarea id="constraints" name="constraints" maxlength="1500" placeholder="Default: no upfront spend; no external actions without approval"></textarea><button type="submit">Build opportunity plan</button></form><p class="meta">Live API calls are off by default. Demo mode works without an API key or API cost.</p></div><h2>Saved plans</h2>{''.join(plan_cards) if plan_cards else '<p class="sub">No plans saved yet. Create your first plan above.</p>'}<h2>Recent audit events</h2><ul>{event_lines if event_lines else '<li class="sub">No events recorded yet.</li>'}</ul><p class="sub">Local records live under data/private-console/ and are excluded from Git. Do not enter passwords, API keys, banking details, medical records, or unnecessary personal data.</p></body></html>'''
    return page.encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "APIPPrivateConsole/1.0"

    def log_message(self, fmt: str, *args) -> None:
        # Avoid console logs containing submitted form content.
        print(f"{self.log_date_time_string()} {self.address_string()} {fmt % args}")

    def _send(self, code: int, body: bytes, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send(200, b'{"status":"ok","external_actions":false}', "application/json; charset=utf-8")
            return
        if parsed.path != "/":
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        self._send(200, make_page())

    def do_POST(self) -> None:
        if self.client_address[0] not in ("127.0.0.1", "::1"):
            self._send(403, b"Local access only", "text/plain; charset=utf-8")
            return
        origin = self.headers.get("Origin")
        if origin and origin != "null" and origin not in (f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"):
            self._send(403, b"Origin rejected", "text/plain; charset=utf-8")
            return
        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length) if raw_length is not None else 0
        except (TypeError, ValueError):
            self._send(400, b"Invalid Content-Length", "text/plain; charset=utf-8")
            return
        if length < 1:
            self._send(400, b"Invalid request size", "text/plain; charset=utf-8")
            return
        if length > MAX_BODY:
            self._send(413, b"Invalid request size", "text/plain; charset=utf-8")
            return
        raw = self.rfile.read(length)
        if len(raw) != length:
            self._send(400, b"Incomplete request body", "text/plain; charset=utf-8")
            return
        try:
            form = parse_form_body(raw)
        except ValueError:
            self._send(400, b"Invalid form: too many fields", "text/plain; charset=utf-8")
            return
        value = lambda key: safe_text(form.get(key, [""])[0])
        if not secrets.compare_digest(value("csrf_token"), CSRF_TOKEN):
            self._send(403, make_page("Request rejected: missing or invalid security token."))
            return
        route = urlparse(self.path).path

        if route == "/plan":
            objective = value("objective")
            if not objective:
                self._send(400, make_page("Please enter an objective."))
                return
            skills, constraints, location = value("skills"), value("constraints"), value("location")
            try:
                plan, metadata = call_openai(objective, skills, constraints, location)
                mode = metadata["mode"]
            except RuntimeError as exc:
                # When live API is explicitly disabled or not configured, use a safe offline plan.
                if os.environ.get("APIP_ALLOW_PAID_API", "0") != "1":
                    plan = local_plan(objective, skills, constraints, location)
                    mode = "demo_offline"
                    metadata = {"mode": mode, "reason": "Live API disabled; no network call made."}
                elif "OPENAI_API_KEY is not set" in str(exc) or "OPENAI_MODEL is not set" in str(exc):
                    plan = local_plan(objective, skills, constraints, location)
                    mode = "demo_offline"
                    metadata = {"mode": mode, "reason": str(exc)}
                else:
                    append_jsonl(EVENTS_FILE, {"at_utc": now_utc(), "event": "API_ERROR", "summary": str(exc)[:500]})
                    self._send(200, make_page(f"Live request did not complete: {exc}. No external action was taken."))
                    return
            plan_id = secrets.token_hex(8)
            record = {"plan_id": plan_id, "created_at_utc": now_utc(), "objective": objective, "skills": skills, "location": location, "constraints": constraints, "plan": plan, "mode": mode, "metadata": metadata, "status": "DRAFT", "external_actions_performed": False, "income_verified": False}
            append_jsonl(PLANS_FILE, record)
            append_jsonl(EVENTS_FILE, {"at_utc": now_utc(), "event": "PLAN_CREATED", "summary": f"{plan_id} ({mode}); external actions none; income not verified"})
            self._send(200, make_page(f"Plan saved as {plan_id} ({mode}). No external action was taken."))
            return

        if route == "/outcome":
            plan_id, outcome, evidence = value("plan_id"), value("outcome"), value("evidence")
            if not plan_id or outcome not in VALID_OUTCOMES:
                self._send(400, make_page("Outcome not recorded: invalid plan or outcome."))
                return
            known = any(p.get("plan_id") == plan_id for p in read_jsonl(PLANS_FILE, limit=10000))
            if not known:
                self._send(404, make_page("Outcome not recorded: plan ID not found."))
                return
            append_jsonl(EVENTS_FILE, {"at_utc": now_utc(), "event": "OUTCOME_RECORDED", "plan_id": plan_id, "outcome": outcome, "evidence_reference_or_note": evidence, "payment_verified": False, "summary": f"{plan_id}: {outcome}; not independently verified"})
            self._send(200, make_page(f"Outcome recorded for {plan_id}. This is a user-reported outcome, not independent verification."))
            return

        self._send(404, b"Not found", "text/plain; charset=utf-8")


def main() -> None:
    if HOST != "127.0.0.1":
        raise RuntimeError("Refusing to start: console must bind to loopback only.")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"APIP Private Console: http://{HOST}:{PORT}")
    print("Local-only mode. No outreach, purchases, money movement, or arbitrary code execution.")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping APIP Private Console...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
