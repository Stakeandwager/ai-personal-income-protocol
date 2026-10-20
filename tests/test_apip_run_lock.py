import json
import concurrent.futures
import threading
import tempfile
import unittest
from pathlib import Path

from scripts.apip_run_lock import LockError, acquire, release, status


class APIPRunLockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "run.lock"

    def tearDown(self):
        self.temp.cleanup()

    def test_exclusive_lock_prevents_second_run(self):
        barrier = threading.Barrier(2)

        def try_acquire(run_id):
            barrier.wait()
            try:
                return ("acquired", acquire(self.path, run_id))
            except LockError:
                return ("blocked", run_id)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(try_acquire, ("run-one", "run-two")))
        self.assertCountEqual([result[0] for result in results], ["acquired", "blocked"])
        self.assertEqual(status(self.path)["run_id"], next(value for state, value in results if state == "acquired"))

    def test_only_owner_can_release_and_stale_locks_fail_closed(self):
        token = acquire(self.path, "run-one")
        with self.assertRaises(LockError):
            release(self.path, "other-run")
        self.assertTrue(self.path.exists())
        release(self.path, token)
        self.assertIsNone(status(self.path))

    def test_corrupt_lock_requires_manual_inspection(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("{bad json", encoding="utf-8")
        with self.assertRaises(LockError):
            status(self.path)
        with self.assertRaises(LockError):
            acquire(self.path)


if __name__ == "__main__":
    unittest.main()
