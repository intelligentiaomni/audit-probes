import json
import unittest
from pathlib import Path

from audit_probes.cloud_probe import probe_consistency
from audit_probes.cyber_audit import audit_repository


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"


class FakeResponse:
    def __init__(self, status_code=200, content=b"ok"):
        self.status_code = status_code
        self.content = content


class FakeSession:
    def __init__(self, responses):
        self._responses = responses

    def get(self, url, timeout):
        return self._responses.pop(0)


class SchemaTests(unittest.TestCase):
    def test_schema_files_are_valid_json(self):
        for schema_path in SCHEMA_DIR.glob("*.json"):
            with self.subTest(schema=schema_path.name):
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft-07/schema#")
                self.assertIn("title", schema)
                self.assertIn("type", schema)

    def test_cyber_audit_schema_matches_report_shape(self):
        schema = json.loads((SCHEMA_DIR / "cyber_audit.schema.json").read_text(encoding="utf-8"))
        report = audit_repository(ROOT / "data" / "targets" / "ghasum")

        self.assertEqual(schema["required"], ["target", "summary", "findings", "errors"])
        self.assertEqual(set(report), set(schema["required"]))
        self.assertEqual(
            set(report["summary"]),
            set(schema["properties"]["summary"]["required"]),
        )

    def test_cloud_probe_schema_matches_summary_shape(self):
        schema = json.loads((SCHEMA_DIR / "cloud_probe.schema.json").read_text(encoding="utf-8"))
        summary = probe_consistency(
            "https://example.com",
            attempts=2,
            session=FakeSession([FakeResponse(content=b"a"), FakeResponse(content=b"a")]),
        )

        self.assertEqual(set(summary), set(schema["required"]))
        self.assertEqual(len(summary["results"]), summary["attempts"])
        self.assertEqual(set(summary["results"][0]), {"ok", "status", "latency", "size", "fingerprint"})

    def test_telemetry_schema_matches_sample_dataset(self):
        schema = json.loads((SCHEMA_DIR / "telemetry_pipeline.json").read_text(encoding="utf-8"))
        sample = json.loads((ROOT / "data" / "samples" / "esa_sample.json").read_text(encoding="utf-8"))

        self.assertEqual(schema["type"], "array")
        self.assertGreaterEqual(len(sample), schema["minItems"])
        for record in sample:
            self.assertIn("time", record)
            self.assertIn("altitude", record)


if __name__ == "__main__":
    unittest.main()
