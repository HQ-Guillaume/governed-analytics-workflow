# Changelog

## 2.1.0 - 2026-08-01

### Why This Release Matters

Version 2.1 makes the useful analytical answer the primary human outcome. It adds concrete validity checks for behavioural telemetry and experiments, produces an honest decision-ready brief even when evidence is incomplete, and removes user-selectable analysis modes without breaking schema 2.0 manifests.

### What Changed

- Added the stakeholder-facing Analysis Brief with explicit answer, evidence, interpretation, alternatives, limitations, unknowns, next action, and traceability.
- Made text-only Analysis Briefs valid deliveries; visuals are required only when they add communication value.
- Added `brief` generation and one cumulative `gate` command, plus structured `--format json` output for automation.
- Added the `instrumentation_reliability` route for event semantics, duplicates, missing events, consent coverage, identity when relevant, and release history.
- Added the `experiment` route for eligibility, assignment and analysis units, sample-ratio mismatch, sample size, stopping and peeking, uncertainty, and guardrails.
- Added a complete synthetic web/product worked example that reconciles form sends apparently missing a preceding open.
- Removed analysis modes from the active workflow and new manifest template; old `light`, `standard`, and `deep` values remain accepted only for schema 2.0 compatibility and are ignored.
- Hardened validation against null or malformed collections, string reference lists, circular question trees, invalid metric statuses, absent fingerprint hashes, UTF-8 BOM files, and chart-name substring false positives.
- Centralized collection and fingerprint helpers, documented SHA-256 canonicalization, fixed atomic-write cleanup and migration path comparison, and expanded portability scanning.
- Added runtime release identity, multi-OS/multi-Python CI, version-scoped release notes, and published SHA-256 checksum artifacts.

### What Users Should Do

- Use `analysis_guard.py brief` as the default human output and add a deck only when the audience needs one.
- Apply instrumentation and experiment routes only when their triggers are present.
- Run `analysis_guard.py gate <manifest> --format json` for the final repeatable check.
- Existing schema 2.0 manifests remain valid; remove the deprecated `needs_discovery.mode` field when next editing them.
- Fresh installations should use the `v2.1.0` release archive or tag.

### Validation

- Full dependency-free unit, malformed-input, route, brief, gate, migration, benchmark-contract, worked-example, portability, and deterministic-package suite.
- Release check verifies project, runtime, changelog, and packaged release-version identity.
- CI covers Python 3.10 and 3.13 on Ubuntu and Windows.

### Known Limits

- The guard validates declared structure and selected invariants; it cannot prove that an external query, experiment implementation, or business interpretation is correct.
- The worked example is synthetic and demonstrates the diagnostic method, not a production prevalence estimate.
- Historical v2.0 blind benchmark scores are retained as a clearly labelled baseline and are not represented as a v2.1 rerun.

## 2.0.2 - 2026-07-15

### Why This Release Matters

Version 2.0.2 completes the cross-platform deterministic packaging work by fixing the ZIP creator-system metadata explicitly instead of inheriting it from the build host.

### What Changed

- Set every ZIP entry's creator system to a fixed Unix-compatible value on all platforms.
- Added a regression assertion for the creator-system field alongside stored compression and canonical text bytes.
- Preserved the v2.0 analytical runtime without behavioural changes.

### What Users Should Do

- Use the `v2.0.2` archive for new installations and automated distribution.
- No manifest or installed-runtime migration is required from `v2.0.0` or `v2.0.1`.

### Validation

- Full 54-test suite and release checks.
- ZIP entry comparison confirmed that creator-system metadata was the only remaining difference between Windows and GitHub Actions builds.
- Release acceptance requires the local and published SHA-256 digests to match.

### Known Limits

- The runtime ZIP uses stored mode and is therefore larger than a compressed archive; this is intentional to remove compression-library variability.

## 2.0.1 - 2026-07-15

### Why This Release Matters

Version 2.0.1 normalized runtime content across Windows and Linux checkouts. Verification then found one remaining host-specific ZIP creator-system header, corrected in `v2.0.2`.

### What Changed

- Canonicalized runtime text files to LF while building the ZIP.
- Switched the small runtime archive to ZIP stored mode so output does not depend on the platform's deflate implementation.
- Added a regression test that supplies mixed CRLF, CR, and LF input to the package builder.
- Kept the v2.0 analytical runtime and behavioural benchmark unchanged.

### What Users Should Do

- Prefer the superseding `v2.0.2` archive for clean installations and automated distribution.
- Existing installed v2.0 runtime files do not require a behavioural migration.

### Validation

- Full unit, regression, migration, benchmark, portability, and release suite.
- Local and GitHub-built archive digest comparison after publication.

### Known Limits

- The archive still inherited a platform-specific creator-system header; runtime behaviour and installation contents were unaffected.

## 2.0.0 - 2026-07-15

### Why This Release Matters

Version 2.0 makes analytical judgment the workflow's primary behaviour. The agent now treats a request as stakeholder input, independently infers the real decision need, designs the complete analysis, and limits conclusions to evidence that has passed explicit quality gates.

### What Changed

- Added a small always-on reasoning kernel for request decomposition, need inference, construct validation, context necessity, evidence ceilings, population logic, and complete data planning.
- Added trigger-based routes for ambiguity, multiple stakeholders, multiple sources, outcome comparisons, sampled or browser evidence, prediction, categorisation, anomalies, themes, and consequential work.
- Added an operational analysis blueprint around the question tree, with active and excluded question roles, bidirectional data-plan lineage, adaptive context, and stop rules.
- Added manifest schema `2.0` with concise needs discovery, analysis blueprint, quality checks, richer claim context, measurement cards, wording review, and rendered-output QA.
- Added stage-specific `validate --stage contract|evidence|claims|delivery`, standalone `quality`, and safe `migrate` commands; legacy claim posture remains explicitly unresolved instead of being inferred.
- Added always-on and route-specific quality checks covering source authority, freshness, scope, grain, identifiers, deduplication, denominators, missing versus zero, domains, semantics, coverage, joins, temporal order, representativeness, uncertainty, confounding, selection, and sensitivity.
- Added explicit method contracts, structured evidence ceilings, warning propagation, causal-design requirements, and critical quality blockers for claim promotion.
- Added function-first chart selection, variety as a tie-breaker, mandatory measurement context, natural-language review, and rendered-slide QA.
- Added a blind twelve-case forward benchmark with two confusing requests for each analytical problem type and a 20-point acceptance rubric.
- Retained the four-phase, twelve-checkpoint workflow, cross-agent portability, stale-dependency controls, and deterministic runtime packaging.

### What Users Should Do

- Start new work from the schema `2.0` manifest or `analysis_guard.py init`.
- Let the agent recommend the framing and data plan; supply business clarification only when a material decision fork remains.
- Run validation at the contract, evidence, claims, and delivery stages rather than relying only on final strict validation.
- Run `quality` before claim promotion and carry warnings into affected claims and visuals.
- Migrate reopened v1 analyses with `migrate`; review every unresolved v2 requirement before restoring approvals.
- Use measurement cards and rendered QA for every stakeholder analytical visual.

### Validation

- Python compilation for the runtime guard and repository utilities.
- 53 passing unit and regression tests for schema migration, staged validation, conditional routes, quality gates, evidence ceilings, warning propagation, metric fingerprints, stale dependencies, chart rules, wording review, and measurement cards.
- Blind forward-test coverage across prediction, categorisation, anomaly detection, theme identification, connection discovery, and pattern finding; all six release cases passed at 19-20 out of 20 with no critical failure.
- Portability and secret scanning across the runtime package.
- Deterministic package and clean-install activation checks.
- Repository release checks for version, documentation, reference routing, runtime scope, and release-note completeness.

### Known Limits

- The guard can enforce declared definitions and selected semantic invariants, but it cannot prove that an external query, model, statistical design, or business interpretation is correct.
- Blind benchmark scoring still requires reviewer judgment; structural tests only validate the benchmark contract.
- Live chart-catalogue consultation, source access, browser inspection, and rendered PowerPoint QA depend on the tools available to the executing agent.
- Migration deliberately leaves v2 definitions and approvals unresolved rather than guessing them.

## 1.0.0 - 2026-07-15

### Why This Release Matters

The workflow now treats needs discovery and analytical reasoning as first-class work. It no longer assumes that a stakeholder's questions, indicators, methods, or preferred explanations form a valid analysis specification.

### What Changed

- Replaced the visible twelve-step launch with four adaptive phases while preserving twelve operational checkpoints.
- Added `Light`, `Standard`, and `Deep` needs-discovery modes.
- Added request decomposition, decision-backward framing, analytical laddering, assumption mapping, alternative framing, stakeholder mapping, evidence-ceiling analysis, minimum-useful scope, and pre-mortems.
- Added draft, confirmed, and operational question trees with request coverage and decision lineage.
- Added playbooks for prediction, categorisation, anomaly detection, theme identification, connection discovery, and pattern finding.
- Added source-authority records, metric definition fingerprints, semantic validation, availability rules, temporal eligibility, and representativeness gates.
- Added observation-to-approved claim promotion, independent review lenses, versioned durable context, and stale dependency handling.
- Added a function-first live Data Visualisation Catalogue gate, hard chart rejection rules, specialist-chart exceptions, and rendered output QA.
- Restricted presentation generation to approved claims and canonical results.
- Replaced the large default artifact list with a canonical JSON manifest and conditional review views.
- Added the zero-dependency `analysis_guard.py` utility for scaffolding, validation, fingerprinting, stale checks, and portability scans.
- Added deterministic runtime packaging, CI, release automation, and behavioral regression tests.
- Updated repository documentation and agent metadata for the v1 workflow.

### What Users Should Do

- Start new analyses from `assets/analysis-manifest.template.json` or `analysis_guard.py init`.
- Confirm the inferred need and question tree before material execution for ambiguous or consequential work.
- Run strict manifest, stale dependency, and portability checks before stakeholder delivery.
- Treat existing pre-1.0 analysis folders as legacy artifacts; migrate only when they need to be reopened or republished.

### Validation

- System skill validation.
- Python compilation for runtime and release utilities.
- Unit tests for strict manifests, all six problem types, question-tree routing, approved-claim enforcement, expected-domain completeness, exclusive-distribution chart rejection, stale fingerprints, portability scanning, and deterministic packaging.
- Runtime scan for client-specific terms, secrets, and machine-specific absolute paths.
- Clean repository and release-package checks.

### Known Limits

- The guard validates governance structure and selected semantic invariants; it cannot prove that an external query, statistical model, or business interpretation is correct.
- Live chart-catalogue consultation, source access, browser inspection, and rendered PowerPoint QA still depend on available tools.
- Existing analyses are not automatically migrated to the v1 manifest.

## 0.3.4 - 2026-06-14

- Removed residual analysis-specific examples and kept the reusable skill generic.

## 0.3.3 - 2026-06-14

- Hardened analyst orientation, grain checks, and delivery handoff.

## 0.3.2 - 2026-06-14

- Added Data Visualisation Catalogue guidance.

## Earlier Releases

- `0.1.0` through `0.3.1` established the original twelve-step governed workflow, presentation handoff, documentation, and readiness checks.
