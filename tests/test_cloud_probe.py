import unittest

from audit_probes.cloud_probe import probe, probe_consistency


class FakeResponse:
    def __init__(self, status_code=200, content=b"ok"):
        self.status_code = status_code
        self.content = content


class FakeSession:
    def __init__(self, responses):
        self._responses = responses

    def get(self, url, timeout):
        return self._responses.pop(0)


class CloudProbeTests(unittest.TestCase):
    def test_probe_collects_basic_metrics(self):
        result = probe("https://example.com", session=FakeSession([FakeResponse(content=b"payload")]))

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["size"], 7)
        self.assertEqual(len(result["fingerprint"]), 16)

    def test_probe_consistency_detects_multiple_payloads(self):
        session = FakeSession(
            [
                FakeResponse(content=b"a"),
                FakeResponse(content=b"b"),
                FakeResponse(content=b"a"),
            ]
        )

        summary = probe_consistency("https://example.com", attempts=3, session=session)

        self.assertFalse(summary["consistent_payload"])
        self.assertEqual(summary["success_rate"], 1.0)
        self.assertEqual(len(summary["unique_fingerprints"]), 2)


if __name__ == "__main__":
    unittest.main()
