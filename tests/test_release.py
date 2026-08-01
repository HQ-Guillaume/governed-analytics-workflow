from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import re
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_skill_package", ROOT / "tools" / "build_skill_package.py")
assert SPEC and SPEC.loader
build_skill_package = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_skill_package)


class ReleaseTest(unittest.TestCase):
    def test_release_check_passes(self) -> None:
        project_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        version_match = re.search(r'^version\s*=\s*"([^"]+)"', project_text, re.MULTILINE)
        self.assertIsNotNone(version_match)
        tag = f"v{version_match.group(1)}"
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "tools" / "check_release.py"), "--tag", tag, "--release-notes", str(ROOT / "CHANGELOG.md")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_release_check_rejects_tag_version_mismatch(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(ROOT / "tools" / "check_release.py"),
                "--tag",
                "v3.0.0",
                "--release-notes",
                str(ROOT / "CHANGELOG.md"),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("does not match project version", result.stderr)

    def test_release_body_contains_only_current_version_section(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "release-notes.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(ROOT / "tools" / "check_release.py"),
                    "--tag",
                    "v2.1.0",
                    "--release-notes",
                    str(ROOT / "CHANGELOG.md"),
                    "--release-body-output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            body = output.read_text(encoding="utf-8")
            self.assertIn("## 2.1.0", body)
            self.assertNotIn("## 2.0.2", body)

    def test_runtime_package_is_deterministic_and_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.zip"
            second = Path(temp) / "second.zip"
            for output in (first, second):
                result = subprocess.run(
                    [sys.executable, "-B", str(ROOT / "tools" / "build_skill_package.py"), "--output", str(output)],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with ZipFile(first) as archive:
                names = set(archive.namelist())
                compression_types = {entry.compress_type for entry in archive.infolist()}
                creator_systems = {entry.create_system for entry in archive.infolist()}
            self.assertIn("governed-analytics-workflow/SKILL.md", names)
            self.assertIn("governed-analytics-workflow/scripts/analysis_guard.py", names)
            self.assertIn("governed-analytics-workflow/assets/analysis-manifest.template.json", names)
            self.assertNotIn("governed-analytics-workflow/README.md", names)
            self.assertFalse(any(name.startswith("governed-analytics-workflow/tests/") for name in names))
            self.assertEqual({ZIP_STORED}, compression_types)
            self.assertEqual({3}, creator_systems)

    def test_runtime_text_is_normalized_for_cross_platform_determinism(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            sample = Path(temp) / "sample.yaml"
            sample.write_bytes(b"first: value\r\nsecond: value\rthird: value\n")
            self.assertEqual(
                b"first: value\nsecond: value\nthird: value\n",
                build_skill_package.canonical_runtime_bytes(sample),
            )

    def test_packaged_guard_validates_packaged_template(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_path = Path(temp) / "skill.zip"
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(ROOT / "tools" / "build_skill_package.py"),
                    "--output",
                    str(archive_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

            extracted = Path(temp) / "extracted"
            with ZipFile(archive_path) as archive:
                archive.extractall(extracted)

            skill_root = extracted / "governed-analytics-workflow"
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(skill_root / "scripts" / "analysis_guard.py"),
                    "validate",
                    str(skill_root / "assets" / "analysis-manifest.template.json"),
                ],
                cwd=skill_root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_packaged_guard_exposes_v2_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_path = Path(temp) / "skill.zip"
            result = subprocess.run(
                [sys.executable, "-B", str(ROOT / "tools" / "build_skill_package.py"), "--output", str(archive_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            extracted = Path(temp) / "extracted"
            with ZipFile(archive_path) as archive:
                archive.extractall(extracted)
            guard = extracted / "governed-analytics-workflow" / "scripts" / "analysis_guard.py"
            result = subprocess.run(
                [sys.executable, "-B", str(guard), "--help"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            for command in ("migrate", "validate", "quality", "brief", "gate"):
                self.assertIn(command, result.stdout)

    def test_runtime_package_contains_release_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_path = Path(temp) / "skill.zip"
            build_skill_package.build(archive_path)
            with ZipFile(archive_path) as archive:
                metadata = archive.read("governed-analytics-workflow/assets/release.json")
            release = json.loads(metadata)
            self.assertEqual("2.1.0", release["version"])
            self.assertEqual("2.0", release["schema_version"])


if __name__ == "__main__":
    unittest.main()
