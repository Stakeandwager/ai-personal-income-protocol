import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "browser-extension" / "timebank"

class ExtensionPackageTests(unittest.TestCase):
    def test_manifest_is_valid_mv3_and_minimal_permission(self):
        manifest = json.loads((EXT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["manifest_version"], 3)
        self.assertEqual(manifest["permissions"], ["storage"])
        self.assertNotIn("host_permissions", manifest)
        self.assertEqual(manifest["action"]["default_popup"], "popup.html")

    def test_referenced_files_exist(self):
        manifest = json.loads((EXT / "manifest.json").read_text(encoding="utf-8"))
        for path in [manifest["background"]["service_worker"], manifest["action"]["default_popup"], "popup.css", "popup.js"]:
            self.assertTrue((EXT / path).is_file(), path)

    def test_extension_has_no_network_api_calls(self):
        for path in [EXT / "popup.js", EXT / "service-worker.js"]:
            source = path.read_text(encoding="utf-8")
            for forbidden in ["fetch(", "XMLHttpRequest", "WebSocket("]:
                self.assertNotIn(forbidden, source, f"{forbidden} found in {path.name}")

    def test_payment_processing_is_not_enabled(self):
        source = (EXT / "popup.js").read_text(encoding="utf-8").lower()
        self.assertIn("eligibleforrewards: false", source)
        self.assertNotIn("paymentprocessor", source)

if __name__ == "__main__": unittest.main()
