# Governed Analytics Workflow

[![CI](https://github.com/haiqigeng/governed-analytics-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/haiqigeng/governed-analytics-workflow/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/haiqigeng/governed-analytics-workflow?sort=semver)](https://github.com/haiqigeng/governed-analytics-workflow/releases/latest)
[![License](https://img.shields.io/github/license/haiqigeng/governed-analytics-workflow)](LICENSE)

A reasoning-first, evidence-governed analytics skill for Codex, Claude Code, Gemini, and other file- and tool-capable AI agents.

## Why It Exists

Analytics requests are often incomplete, overloaded, or already framed around a preferred metric, chart, explanation, or solution. The requester may understand the business problem without knowing the population, grain, denominator, method, or evidence needed to answer it.

This skill makes the agent responsible for analytical framing. It treats the request as stakeholder input, infers the real decision or learning need, designs the complete analysis, validates the evidence, governs claims, and communicates the result in language the audience can understand.

```text
stakeholder input
-> inferred business need
-> analysis blueprint
-> complete data plan
-> validated evidence
-> governed claims
-> stakeholder output or action
```

It does not store hidden chain-of-thought or make the requester design the analysis.

## What v2.1 Changes

Version 2.1 keeps the v2 schema and focuses the workflow more sharply on useful analytical answers:

- an always-on reasoning kernel challenges the literal request;
- conditional methods activate only when their trigger is present;
- the question tree sits inside an operational analysis blueprint;
- context is included only when it improves interpretation or action;
- stage-specific quality gates protect evidence, claims, and delivery;
- claim posture and evidence ceilings are explicit;
- every stakeholder visual carries measurement context and rendered QA;
- wording review favours direct, natural, domain-correct language;
- v1 manifests migrate without inheriting unreviewed approvals.
- a decision-ready Analysis Brief is the default human output, including structured incomplete answers;
- behavioural telemetry activates concrete instrumentation-reliability checks;
- A/B tests activate practical assignment, SRM, stopping, uncertainty, and guardrail checks;
- the guard is robust to malformed collections and BOM-encoded JSON;
- `brief`, `gate`, and machine-readable `--format json` outputs reduce manual handoffs.

The runtime remains compact and platform-neutral.

## Adaptive Workflow

The skill retains four phases and twelve operational checkpoints:

1. **Frame:** decompose the request, infer the need, build the blueprint, and approve the contract.
2. **Evidence:** map sources and methods, validate readiness, execute bounded work, and review results and claims.
3. **Synthesis:** answer the blueprint, design visuals and wording, and build the stakeholder narrative.
4. **Delivery:** inspect and version the output, then define follow-up.

The agent applies a small reasoning kernel to every request and activates extra methods only when their trigger is present. There are no user-selectable analysis modes. It proposes a defensible frame and asks the user only when unresolved business ambiguity or approval would materially change the analysis.

## Needs Discovery

Every analysis applies a small reasoning kernel:

1. Decompose facts, objectives, constraints, hypotheses, suggested metrics, methods, solutions, output preferences, and uncertainties.
2. Infer the underlying decision or learning objective.
3. Test whether proposed measures represent the intended constructs.
4. Identify only the context needed to define, explain, validate, or act.
5. Set the strongest claim the evidence could support.
6. Define population, scope, period, timezone, grain, filters, exclusions, and denominator.
7. Design the complete decision, context, diagnostic, quality, and validation data plan.

Conditional routes add analytical laddering, stakeholder mapping, source compatibility, temporal eligibility, representativeness, model validation, anomaly baselines, theme review, instrumentation reliability, experiment validity, pre-mortems, falsification, or independent review only when relevant.

## Analysis Blueprint

The question tree is generated after initial reasoning:

```text
business need
-> context questions
-> decision questions
-> diagnostic questions
-> data-quality and validation questions
-> required data
-> methods and evidence
-> claims
-> presentation and action
```

Active question roles are `context`, `decision`, `diagnostic`, `data_quality`, and `validation`. Excluded branches use `optional`, `parked`, `rejected`, `unavailable`, or `superseded`.

Every active question must define its purpose, data requirements, population, grain, metric, method, validation, and expected output. Every material request item is mapped to the tree or receives a documented reason for exclusion.

## Analytical Problem Types

One primary type guides the analysis; secondary types belong to distinct subquestions.

| Type | Core validation |
| --- | --- |
| Make predictions | Leakage, temporal holdout, calibration, threshold trade-offs, drift |
| Categorise things | Label quality, class balance, per-class errors, stability |
| Spot something unusual | Baseline, seasonality, sensitivity, false positives |
| Identify themes | Corpus coverage, codebook quality, negative cases, reviewer agreement |
| Discover connections | Compatible grain, temporal order, confounding, selection, sensitivity |
| Find patterns | Complete domains, zero states, denominators, stable segments |

Each method records the quantity estimated, eligible population, baseline, time logic, uncertainty, validation, sensitivity, and permitted claim level.

## Data Quality

Every evidence-stage analysis checks:

- source authority and freshness;
- population, period, timezone, and filters;
- natural grain and identifiers;
- deduplication and denominator logic;
- missing values versus zero values;
- expected domain completeness;
- metric semantics and source coverage.

Conditional checks cover joins, availability, temporal ordering, representativeness, outliers, sample size, uncertainty, multiple comparisons, confounding, selection, and sensitivity. Prediction, categorisation, anomaly, and theme routes add their own quality requirements.

When web or product events underpin the answer, the instrumentation route checks event semantics, duplicate and missing events, consent coverage, identity stitching when relevant, and tracking or product release history. When an experiment underpins a winner or rollout decision, the experiment route checks eligibility, assignment and analysis units, sample-ratio mismatch, sample size, stopping and peeking, uncertainty, and guardrails.

Each check returns `pass`, `warning`, `fail`, `unknown`, or `not_applicable`. A critical failure or unresolved critical check blocks claim promotion. Warnings must follow the affected claims and visuals.

## Evidence Governance

Important metrics receive a definition fingerprint containing population, grain, period, scope, filters, numerator, denominator, deduplication, query reference, and run date. Sources record authority, coverage, freshness, joinability, allowed uses, forbidden uses, and caveats.

Findings move through a controlled lifecycle:

```text
observation -> candidate -> validated -> approved
                         \-> rejected
validated or approved -> superseded when replaced
```

Claims record posture, population, denominator, temporal scope, coverage, missingness, uncertainty, alternatives, decision use, evidence, metrics, and quality warnings. Observational evidence produces hypotheses or tests, not unsupported prescriptions. Changed metric fingerprints mark dependent claims and outputs stale.

Fingerprint hashes use SHA-256 over canonical JSON with sorted keys, compact separators, ASCII escapes, and UTF-8 bytes. They detect definition changes; they do not prove that an external query executed correctly.

## Analysis Brief

The default human deliverable is `analysis-brief.md`, containing:

```text
business question -> executive answer -> supporting evidence
-> interpretation and alternatives -> limitations and unknowns
-> recommended next action -> methods and traceability
```

The answer status is `complete`, `incomplete`, or `blocked`. An incomplete brief still states what is known, what cannot be established, why the gap exists, and the smallest useful next action. A deck is optional and derives from the approved brief and claims. The agent also puts the executive answer, strongest evidence, material limitations, and next action directly in the conversation; a generated file never replaces the explanation.

In JSON output, `brief` reports `generated`, `answer_status`, `analysis_ready`, and `delivery_ready` separately. Successful generation does not imply that the claims or final delivery gate passed.

See the [worked web/product example](references/worked-web-product-example.md) for a full raw-event reproduction of apparent form sends without a preceding form open.

## Visualisation

Chart choice is function-first. The skill consults [The Data Visualisation Catalogue](https://datavizcatalogue.com/search.html) once per distinct communication function when internet access is available and uses a documented offline map otherwise.

Appropriateness and readability come first. Variety is only a tie-breaker between equally valid choices. Hard rules reject exclusive classes shown as funnels, percentages without denominators, missing zero states, lines across unordered categories, part-to-whole charts for overlapping groups, incompatible comparisons, and causal-looking visuals without causal evidence.

Every stakeholder visual includes or clearly references:

```text
population | grain | period | denominator | coverage
unit | temporal scope | missing/zero treatment | claim posture | source
```

Rendered output is inspected for chart accuracy, labels, text fit, readability, caveats, terminology, and natural wording.

## Runtime Artifacts

The canonical run file is `analysis-manifest.json` using schema `2.0`:

```text
analyses/<analysis-id>/
|-- analysis-manifest.json
|-- evidence/
|-- analysis-brief.md
`-- requested delivery, when needed
```

Create and validate a run:

```powershell
python scripts/analysis_guard.py init analyses/example-analysis --analysis-id example-analysis
python scripts/analysis_guard.py validate analyses/example-analysis/analysis-manifest.json --stage contract
python scripts/analysis_guard.py validate analyses/example-analysis/analysis-manifest.json --stage evidence
python scripts/analysis_guard.py quality analyses/example-analysis/analysis-manifest.json
python scripts/analysis_guard.py validate analyses/example-analysis/analysis-manifest.json --stage claims
python scripts/analysis_guard.py validate analyses/example-analysis/analysis-manifest.json --stage delivery
python scripts/analysis_guard.py stale analyses/example-analysis/analysis-manifest.json --fail-on-stale
python scripts/analysis_guard.py scan analyses/example-analysis
python scripts/analysis_guard.py brief analyses/example-analysis/analysis-manifest.json --output analyses/example-analysis/analysis-brief.md
python scripts/analysis_guard.py gate analyses/example-analysis/analysis-manifest.json --format json
```

The guard is deterministic and dependency-free. It validates contracts and selected semantic invariants; it cannot prove that an external query, model, or business interpretation is correct.

## Migration

Migrate a v1 manifest into a separate file:

```powershell
python scripts/analysis_guard.py migrate path/to/analysis-manifest.json --output path/to/analysis-manifest-v2.json
```

Migration preserves legacy content, marks new v2 requirements unresolved, and demotes approved contracts, validated metrics, approved claims, stakeholder visuals, and active artifacts until review. It never invents definitions or silently overwrites the source. Use `--write` only when explicit in-place replacement is intended.

Schema `2.0` identifies the manifest's structural family, not a promise that every older manifest passes every newer validator unchanged. Validation became stricter in v2.1. Older schema-2.0 manifests may need `fingerprint --write` and explicit review before they pass evidence, claims, or delivery validation.

## Forward Benchmark

The repository contains a blind benchmark of raw, confusing requests across all six problem types, including telemetry-reliability and experiment cases. Executing agents receive only the raw request. The hidden rubric scores:

- real-need identification and alternative framing;
- necessary context and exclusion discipline;
- complete operational data planning;
- population, scope, grain, denominator, and method correctness;
- evidence limitations and claim discipline;
- presentation clarity.

Release acceptance requires no critical failure and a score of at least 16 out of 20. The v2.1.1 release stores the raw blind responses and reviewed scores for all fourteen cases; all passed, including the telemetry-reliability and experiment cases. The historical six-case v2.0.0 baseline remains separately labelled, and score changes are not treated as a controlled model-quality uplift because different executing agents were used. Static tests also enforce schema migration, conditional routes, quality gates, claim ceilings, measurement cards, chart rules, wording review, staleness, portability, and deterministic packaging.

## Installation

Clone into the skills directory used by your agent:

```powershell
git clone https://github.com/haiqigeng/governed-analytics-workflow.git "$env:USERPROFILE\.codex\skills\governed-analytics-workflow"
```

Alternatively, extract the `governed-analytics-workflow` folder from the latest runtime zip into the agent's skills directory, then restart or reload the agent.

## Agent Compatibility

The skill describes analytical operations rather than vendor-specific commands. Codex, Claude Code, Gemini, and other agents can use local equivalents for files, queries, notebooks, APIs, browsers, statistics, charts, and presentations.

The reusable package contains no client data, credentials, source integrations, prior analysis results, or machine-specific paths.

## Release Checks

```powershell
python tools/check_release.py --tag v2.1.1 --release-notes CHANGELOG.md
python -m unittest discover -s tests -v
python tools/build_skill_package.py --output dist/governed-analytics-workflow-v2.1.1.zip
```

Tagged releases build the same deterministic runtime package tested locally.

## Privacy And Security

Keep generated analysis and private data outside this repository. Do not commit credentials, client information, private links, raw exports, personal data, or machine-specific paths. See [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
