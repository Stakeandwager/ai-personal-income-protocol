import importlib.util
import http.client
import json
import os
import socket
import tempfile
import threading
import unittest
from urllib.parse import urlencode
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "private_console.py"
spec = importlib.util.spec_from_file_location("private_console", MODULE_PATH)
app = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(app)


class PrivateConsoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join(timeout=2)

    def post_raw(self, headers, body):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        connection.request("POST", "/plan", body=body, headers=headers)
        response = connection.getresponse()
        result = response.status, response.read()
        connection.close()
        return result

    def post_form(self, path, values):
        body = urlencode(values)
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        connection.request("POST", path, body=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
        response = connection.getresponse()
        result = response.status, response.read()
        connection.close()
        return result

    def test_csrf_token_is_present_in_form(self):
        page = app.make_page().decode("utf-8")
        token_field = f'name="csrf_token" value="{app.CSRF_TOKEN}"'
        self.assertGreaterEqual(page.count(token_field), 1)

    def test_post_routes_reject_missing_invalid_and_tampered_csrf_tokens(self):
        invalid_tokens = [
            ("missing", None),
            ("invalid", "not-the-token"),
            ("tampered", app.CSRF_TOKEN[:-1] + ("a" if app.CSRF_TOKEN[-1] != "a" else "b")),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            plans_path = Path(tmp) / "plans.jsonl"
            events_path = Path(tmp) / "events.jsonl"
            original_plan = '{"plan_id":"p1","workflow":{}}\n'
            plans_path.write_text(original_plan, encoding="utf-8")
            routes = (
                ("/plan", {"objective": "Test"}),
                ("/action", {"plan_id": "p1", "action_id": "a1"}),
                ("/outcome", {"plan_id": "p1", "outcome": "IN_PROGRESS"}),
            )
            for route, fields in routes:
                for label, token in invalid_tokens:
                    with self.subTest(route=route, token=label), \
                            patch.object(app, "PLANS_FILE", plans_path), \
                            patch.object(app, "EVENTS_FILE", events_path):
                        form = dict(fields)
                        if token is not None:
                            form["csrf_token"] = token
                        status, response = self.post_form(route, form)
                        self.assertEqual(status, 403)
                        self.assertIn(b"missing or invalid security token", response)
                        self.assertEqual(plans_path.read_text(encoding="utf-8"), original_plan)
                        self.assertFalse(events_path.exists())

    def test_binds_only_loopback(self):
        self.assertEqual(app.HOST, "127.0.0.1")

    def test_demo_plan_is_explicitly_not_live_research(self):
        plan = app.local_plan("Find paid work", "Writing", "Zero spend", "Lagos")
        self.assertIn("DEMO MODE", plan)
        self.assertIn("does not browse the live web", plan)
        self.assertIn("Verified income: NGN 0", plan)

    def test_ai_plan_parser_requires_typed_action_list(self):
        summary, actions = app.parse_ai_execution_plan(json.dumps({
            "plan": "Find a listing and prepare a draft.",
            "actions": [{"type": "prepare_proposal_draft", "description": "Draft locally", "data": {"title": "Test"}}],
        }))
        self.assertEqual(summary, "Find a listing and prepare a draft.")
        self.assertEqual(actions[0]["type"], "prepare_proposal_draft")
        with self.assertRaisesRegex(RuntimeError, "valid structured JSON"):
            app.parse_ai_execution_plan("plain text without actions")

    def test_response_sources_keep_url_citation_evidence(self):
        payload = {
            "output": [{"type": "message", "content": [{
                "type": "output_text",
                "text": '{"plan":"Use current public source.","actions":[]}citeturn0search0',
                "annotations": [{"type": "url_citation", "url": "https://example.com/listing", "title": "Public listing"}],
            }]}],
        }
        text, sources = app.extract_response_text_and_sources(payload)
        summary, actions = app.parse_ai_execution_plan(text)
        self.assertEqual(summary, "Use current public source.")
        self.assertEqual(actions, [])
        self.assertEqual(sources, [{"title": "Public listing", "url": "https://example.com/listing"}])

    def test_saved_plan_snapshots_project_to_latest_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plans.jsonl"
            path.write_text('\n'.join([
                json.dumps({"plan_id": "p1", "version": 1}),
                json.dumps({"plan_id": "p2", "version": 1}),
                json.dumps({"plan_id": "p1", "version": 2}),
            ]), encoding="utf-8")
            with patch.object(app, "PLANS_FILE", path):
                plans = app.read_plans()
        self.assertEqual([(p["plan_id"], p["version"]) for p in plans], [("p1", 2), ("p2", 1)])

    def test_console_shows_external_capability_blocker_without_submit_control(self):
        workflow = app.build_workflow(
            "Apply to a listing",
            [{"type": "submit_proposal", "description": "Submit application", "data": {"url": "https://example.com/job"}}],
        )
        plan = {
            "plan_id": "p2", "plan": "Review the opportunity", "mode": "live_api",
            "created_at_utc": "now", "workflow": workflow,
            "metadata": {"sources": [{"title": "Listing", "url": "https://example.com/job"}]},
        }
        with patch.object(app, "read_plans", return_value=[plan]), patch.object(app, "read_jsonl", return_value=[]):
            page = app.make_page().decode("utf-8")
        self.assertIn("CAPABILITY_MISSING", page)
        self.assertIn("Source evidence", page)
        self.assertNotIn('action="/action"', page)

    def test_action_endpoint_executes_only_local_draft_and_records_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            plans_path = base / "plans.jsonl"
            events_path = base / "events.jsonl"
            data_dir = base / "private"
            workflow = app.build_workflow(
                "Prepare an application", [{"type": "prepare_proposal_draft", "data": {"title": "Local proposal"}}]
            )
            action = workflow["actions"][0]
            plan = {"plan_id": "p1", "plan": "Test plan", "workflow": workflow, "mode": "test"}
            plans_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
            with patch.object(app, "PLANS_FILE", plans_path), patch.object(app, "EVENTS_FILE", events_path), patch.object(app, "DATA_DIR", data_dir):
                status, response = self.post_form("/action", {
                    "csrf_token": app.CSRF_TOKEN, "plan_id": "p1", "action_id": action["action_id"],
                })
                updated = app.read_plans()[0]
                events = app.read_jsonl(events_path)
            self.assertEqual(status, 200)
            self.assertIn(b"Nothing was submitted", response)
            self.assertEqual(updated["workflow"]["actions"][0]["status"], "COMPLETED")
            self.assertTrue(Path(updated["workflow"]["actions"][0]["evidence"]["path"]).exists())
            self.assertEqual(events[-1]["event"], "LOCAL_ACTION_COMPLETED")
            self.assertFalse(events[-1].get("payment_verified", False))

    def test_live_api_disabled_by_default(self):
        old = os.environ.pop("APIP_ALLOW_PAID_API", None)
        try:
            with self.assertRaisesRegex(RuntimeError, "Live API is disabled"):
                app.call_openai("x", "", "", "")
        finally:
            if old is not None:
                os.environ["APIP_ALLOW_PAID_API"] = old

    def test_private_records_are_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "events.jsonl"
            app.append_jsonl(target, {"event": "TEST", "ok": True})
            rows = app.read_jsonl(target)
            self.assertEqual(rows, [{"event": "TEST", "ok": True}])

    def test_valid_outcomes_are_bounded(self):
        self.assertEqual(app.VALID_OUTCOMES, {"TESTED_DEMAND", "TESTED_NO_DEMAND", "IN_PROGRESS", "ABANDONED_WITH_REASON"})

    def test_plan_outcome_transitions_stop_at_terminal_state(self):
        events = []
        self.assertEqual(app.plan_status("p1", events), "DRAFT")
        self.assertTrue(app.can_record_outcome("DRAFT", "IN_PROGRESS"))
        events.insert(0, {"event": "OUTCOME_RECORDED", "plan_id": "p1", "outcome": "IN_PROGRESS"})
        status = app.plan_status("p1", events)
        self.assertEqual(status, "IN_PROGRESS")
        self.assertTrue(app.can_record_outcome(status, "TESTED_DEMAND"))
        events.insert(0, {"event": "OUTCOME_RECORDED", "plan_id": "p1", "outcome": "TESTED_DEMAND"})
        status = app.plan_status("p1", events)
        self.assertEqual(status, "TESTED_DEMAND")
        self.assertFalse(app.can_record_outcome(status, "IN_PROGRESS"))
        self.assertFalse(app.can_record_outcome(status, "TESTED_NO_DEMAND"))
        self.assertFalse(app.can_record_outcome("DRAFT", "PAYMENT_VERIFIED"))

    def test_plan_status_uses_latest_matching_event(self):
        events = [
            {"event": "OUTCOME_RECORDED", "plan_id": "p1", "outcome": "IN_PROGRESS"},
            {"event": "OUTCOME_RECORDED", "plan_id": "p2", "outcome": "IN_PROGRESS"},
            {"event": "OUTCOME_RECORDED", "plan_id": "p1", "outcome": "TESTED_DEMAND"},
        ]
        self.assertEqual(app.plan_status("p1", events), "IN_PROGRESS")
        self.assertEqual(app.plan_status("unknown", events), "DRAFT")

    def test_record_outcome_appends_once_and_refuses_terminal_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "events.jsonl"
            recorded, state = app.record_outcome("p1", "TESTED_NO_DEMAND", "sample reviewed", target)
            self.assertTrue(recorded)
            self.assertEqual(state, "DRAFT")
            recorded, state = app.record_outcome("p1", "TESTED_DEMAND", "later", target)
            self.assertFalse(recorded)
            self.assertEqual(state, "TESTED_NO_DEMAND")
            events = app.read_jsonl(target)
            self.assertEqual(len(events), 1)
            self.assertFalse(events[0]["payment_verified"])

    def test_non_numeric_content_length_is_rejected_without_server_error(self):
        status, _ = self.post_raw({"Content-Length": "invalid"}, b"x")
        self.assertEqual(status, 400)
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        connection.request("GET", "/health")
        self.assertEqual(connection.getresponse().status, 200)
        connection.close()

    def test_too_many_form_fields_are_rejected_without_server_error(self):
        body = "&".join(f"field{i}=x" for i in range(13))
        status, response = self.post_raw({"Content-Length": str(len(body))}, body.encode())
        self.assertEqual(status, 400)
        self.assertIn(b"too many fields", response)

    def test_incomplete_request_body_is_rejected(self):
        with socket.create_connection(("127.0.0.1", self.port), timeout=2) as client:
            client.sendall(b"POST /plan HTTP/1.1\r\nHost: localhost\r\nContent-Length: 10\r\n\r\nx")
            client.shutdown(socket.SHUT_WR)
            chunks = []
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
            response = b"".join(chunks)
        self.assertIn(b"400 Bad Request", response)
        self.assertIn(b"Incomplete request body", response)


if __name__ == "__main__":
    unittest.main()
