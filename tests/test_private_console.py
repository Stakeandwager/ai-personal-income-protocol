import importlib.util
import http.client
import json
import os
import socket
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

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

    def test_csrf_token_is_present_in_both_forms(self):
        page = app.make_page().decode("utf-8")
        token_field = f'name="csrf_token" value="{app.CSRF_TOKEN}"'
        self.assertEqual(page.count(token_field), 2)

    def test_binds_only_loopback(self):
        self.assertEqual(app.HOST, "127.0.0.1")

    def test_demo_plan_is_explicitly_not_live_research(self):
        plan = app.local_plan("Find paid work", "Writing", "Zero spend", "Lagos")
        self.assertIn("DEMO MODE", plan)
        self.assertIn("does not browse the live web", plan)
        self.assertIn("Verified income: NGN 0", plan)

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
