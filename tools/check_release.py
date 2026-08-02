#!/usr/bin/env python3
"""Run dependency-free repository and runtime release checks."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")
REQUIRED_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/needs-discovery-and-analysis-contract.md",
    "references/problem-type-playbooks.md",
    "references/evidence-claims-and-review.md",
    "references/synthesis-and-visualisation.md",
    "references/presentation-generator-brief.md",
    "references/worked-web-product-example.md",
    "assets/analysis-manifest.template.json",
    "assets/release.json",
    "scripts/analysis_guard.py",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "pyproject.toml",
    ".github/workflows/ci.yml",
    ".github/workflows/release.yml",
    "tools/build_skill_package.py",
    "tests/test_analysis_guard.py",
    "tests/test_forward_cases.py",
    "tests/test_reasoning_benchmarks.py",
    "tests/test_release.py",
    "tests/test_worked_example.py",
    "tests/fixtures/forward_cases.json",
    "tests/fixtures/forward_results_v2.json",
    "tests/fixtures/forward_results_v2_1_1.json",
    "tests/fixtures/reasoning_benchmarks.json",
    "tests/fixtures/worked_web_product_example.json",
)
STALE_FILES = ("references/dataviz-catalogue-selection.md",)
RELEASE_NOTE_HEADINGS = (
    "Why This Release Matters",
    "What Changed",
    "What Users Should Do",
    "Validation",
    "Known Limits",
)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8-sig")


def load_guard():
    path = ROOT / "scripts" / "analysis_guard.py"
    spec = importlib.util.spec_from_file_location("analysis_guard", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load analysis_guard.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_frontmatter() -> list[str]:
    errors: list[str] = []
    text = read("SKILL.md")
    if not text.startswith("---\n"):
        return ["SKILL.md frontmatter is missing"]
    _, raw, _ = text.split("---", 2)
    values: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            errors.append(f"invalid frontmatter line: {line}")
            continue
        values[key.strip()] = value.strip()
    if list(values) != ["name", "description"]:
        errors.append("frontmatter must contain only name and description")
    if values.get("name") != "governed-analytics-workflow":
        errors.append("frontmatter name is incorrect")
    description = values.get("description", "").lower()
    for term in ("infer", "question tree", "analysis blueprint", "problem type", "codex", "claude code", "gemini"):
        if term not in description:
            errors.append(f"frontmatter description missing: {term}")
    return errors


def check_files_and_links() -> list[str]:
    errors = [f"missing required file: {path}" for path in REQUIRED_FILES if not (ROOT / path).exists()]
    errors.extend(f"stale file remains: {path}" for path in STALE_FILES if (ROOT / path).exists())
    skill = read("SKILL.md")
    links = re.findall(r"\]\(([^)]+)\)", skill)
    for link in links:
        if link.startswith(("http://", "https://")):
            continue
        if not (ROOT / link).exists():
            errors.append(f"SKILL.md references missing resource: {link}")
    linked_references = {link for link in links if link.startswith("references/")}
    reference_files = {path.relative_to(ROOT).as_posix() for path in (ROOT / "references").rglob("*.md")}
    for path in sorted(reference_files - linked_references):
        errors.append(f"reference is not directly routed from SKILL.md: {path}")
    return errors


def check_content() -> list[str]:
    errors: list[str] = []
    skill = read("SKILL.md")
    if len(skill.splitlines()) >= 350:
        errors.append("SKILL.md must remain below 350 lines")
    for term in (
        "Interpret the request before selecting metrics",
        "Four Phases And Twelve Checkpoints",
        "always-on reasoning kernel",
        "make_predictions",
        "categorise_things",
        "spot_unusual",
        "identify_themes",
        "discover_connections",
        "find_patterns",
        "observation -> candidate -> validated -> approved",
        "Data Visualisation Catalogue",
        "measurement card",
        "Analysis Brief",
        "instrumentation_reliability",
        "experiment",
        "directly in the conversation",
    ):
        if term not in skill:
            errors.append(f"SKILL.md missing required contract text: {term}")
    openai = read("agents/openai.yaml")
    if "$governed-analytics-workflow" not in openai:
        errors.append("agents/openai.yaml default prompt does not name the skill")
    readme = read("README.md")
    for heading in (
        "## Why It Exists",
        "## Adaptive Workflow",
        "## Needs Discovery",
        "## Analysis Blueprint",
        "## Analytical Problem Types",
        "## Data Quality",
        "## Evidence Governance",
        "## Analysis Brief",
        "## Visualisation",
        "## Runtime Artifacts",
        "## Migration",
        "## Forward Benchmark",
        "## Release Checks",
    ):
        if heading not in readme:
            errors.append(f"README missing section: {heading}")
    try:
        template = json.loads(read("assets/analysis-manifest.template.json"))
    except json.JSONDecodeError as exc:
        errors.append(f"manifest template is invalid JSON: {exc}")
    else:
        guard = load_guard()
        if template.get("schema_version") != "2.0":
            errors.append("manifest template must use schema 2.0")
        errors.extend(f"manifest template: {error}" for error in guard.validate_manifest(template))
        errors.extend(f"runtime scan: {finding}" for finding in guard.scan_path(ROOT / "SKILL.md"))
        for folder in ("agents", "references", "assets", "scripts"):
            errors.extend(f"runtime scan: {finding}" for finding in guard.scan_path(ROOT / folder))
        try:
            release_metadata = json.loads(read("assets/release.json"))
        except json.JSONDecodeError as exc:
            errors.append(f"release metadata is invalid JSON: {exc}")
        else:
            if release_metadata.get("version") != project_version():
                errors.append("assets/release.json version does not match pyproject.toml")
            if release_metadata.get("schema_version") != "2.0":
                errors.append("assets/release.json must identify schema 2.0")
        try:
            forward_results = json.loads(read("tests/fixtures/forward_results_v2_1_1.json"))
        except json.JSONDecodeError as exc:
            errors.append(f"current forward results are invalid JSON: {exc}")
        else:
            if forward_results.get("skill_version") != project_version():
                errors.append("current forward-results version does not match pyproject.toml")
            if len(forward_results.get("cases", [])) != 14:
                errors.append("current forward results must cover all 14 benchmark cases")
            if forward_results.get("summary", {}).get("passed") is not True:
                errors.append("current forward results did not pass release acceptance")
    return errors


def project_version() -> str:
    match = re.search(r'^version\s*=\s*"([^"]+)"', read("pyproject.toml"), re.MULTILINE)
    if not match:
        raise RuntimeError("pyproject.toml does not declare a project version")
    return match.group(1)


def release_note_section(path: Path, version: str) -> tuple[str, list[str]]:
    if not path.exists():
        return "", [f"release notes file does not exist: {path}"]
    text = path.read_text(encoding="utf-8-sig")
    section_match = re.search(
        rf"^## {re.escape(version)}(?:\s+-[^\n]*)?\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not section_match:
        return "", [f"CHANGELOG is missing the {version} release section"]
    section = section_match.group("body")
    errors = [
        f"{version} release notes missing heading: {heading}"
        for heading in RELEASE_NOTE_HEADINGS
        if f"### {heading}" not in section
    ]
    return f"## {version}\n{section.strip()}\n", errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag")
    parser.add_argument("--release-notes", type=Path)
    parser.add_argument("--release-body-output", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    version = project_version()
    errors.extend(check_frontmatter())
    errors.extend(check_files_and_links())
    errors.extend(check_content())
    if args.tag:
        if not SEMVER.fullmatch(args.tag):
            errors.append(f"invalid semantic-version release tag: {args.tag}")
        elif args.tag.removeprefix("v") != version:
            errors.append(f"release tag {args.tag} does not match project version {version}")
    release_body = ""
    if args.release_notes:
        release_body, note_errors = release_note_section(args.release_notes, version)
        errors.extend(note_errors)
    elif args.release_body_output:
        errors.append("--release-body-output requires --release-notes")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Release check: FAIL ({len(errors)} error(s))")
        return 1
    if args.release_body_output:
        args.release_body_output.parent.mkdir(parents=True, exist_ok=True)
        args.release_body_output.write_text(release_body, encoding="utf-8", newline="\n")
    print(f"Release check: PASS ({len(REQUIRED_FILES)} required files, {len(read('SKILL.md').splitlines())} SKILL.md lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
