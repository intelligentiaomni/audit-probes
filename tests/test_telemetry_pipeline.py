import json
import tempfile
import unittest
from pathlib import Path

from audit_probes import telemetry_pipeline


@unittest.skipIf(telemetry_pipeline.pd is None, "pandas is not installed")
class TelemetryPipelineTests(unittest.TestCase):
    def test_dashboard_frame_cleans_and_flags_anomalies(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            sample = Path(temp_dir, "telemetry.json")
            sample.write_text(
                json.dumps(
                    [
                        {"time": 0, "altitude": 100.0},
                        {"time": 1, "altitude": None},
                        {"time": 2, "altitude": 200.0},
                        {"time": 3, "altitude": 2500.0},
                    ]
                ),
                encoding="utf-8",
            )

            frame = telemetry_pipeline.build_dashboard_frame(sample)

        self.assertEqual(frame.loc[1, "altitude"], 150.0)
        self.assertTrue(frame.loc[3, "anomaly_flag"])
        self.assertIn("linearly interpolated", frame.attrs["interpolation_assumption"])


if __name__ == "__main__":
    unittest.main()
