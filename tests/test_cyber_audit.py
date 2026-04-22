import json
import tempfile
import unittest
from pathlib import Path

from audit_probes.cyber_audit import audit_repository, scan_for_secrets


class CyberAuditTests(unittest.TestCase):
    def test_scan_for_secrets_finds_keyword(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir, "config.py")
            path.write_text('API_KEY = "topsecret123"\n', encoding="utf-8")

            findings = scan_for_secrets(temp_dir)

        self.assertEqual(findings, [("config.py", 'API_KEY = "topsecret123"')])

    def test_audit_repository_writes_json_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "app.py").write_text(
                'import os\nTOKEN = "abcd1234"\nvalue = os.environ["SERVICE_TOKEN"]\n',
                encoding="utf-8",
            )
            (root / "requirements.txt").write_text("requests==2.28\n", encoding="utf-8")
            output = root / "audit.json"

            report = audit_repository(root, output_path=output)

            self.assertGreaterEqual(report["summary"]["findings"], 3)
            self.assertTrue(output.exists())
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["target"], str(root.resolve()))

    def test_documented_github_tokens_are_not_reported_as_secrets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text(
                "GH_TOKEN: ${{ github.token }}\nuses: actions/create-github-app-token@v1\n",
                encoding="utf-8",
            )

            report = audit_repository(root)

        self.assertEqual(report["summary"]["findings"], 0)

    def test_go_mod_dependencies_are_checked(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "go.mod").write_text(
                "module example.com/probe\n\n"
                "go 1.23.0\n\n"
                "require (\n"
                "\tgolang.org/x/tools v0.40.0\n"
                ")\n",
                encoding="utf-8",
            )

            report = audit_repository(root)

        self.assertEqual(report["summary"]["findings"], 1)
        self.assertEqual(report["findings"][0]["category"], "outdated_dependency")


if __name__ == "__main__":
    unittest.main()
