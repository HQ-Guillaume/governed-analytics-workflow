---
name: governed-analytics-workflow
description: Run an adaptive, reasoning-first, governed analytics workflow for unclear, metric-led, multi-source, or consequential business, product, marketing, digital, revenue, and operations questions. Use when an AI agent must infer the real decision need, build an operational question tree and analysis blueprint, design contextual and decision data, select methods by analytical problem type, validate grain, scope, semantics, quality, statistics, behavioural instrumentation, or experiments when triggered, govern claims, and deliver an honest decision-ready Analysis Brief. Designed for Codex, Claude Code, Gemini, and other file- and tool-capable agents.
---

# Governed Analytics Workflow

Turn incomplete or misleading requests into decision-relevant, reproducible analysis. Treat the request as stakeholder evidence, not as an approved analytical specification. Own the framing, data plan, methods, validation, and communication; ask the user only when unresolved business ambiguity would materially change the work.

The primary outcome is a valuable answer: what the data supports, what it means, what remains unknown, and what should happen next. Governance exists to make that answer trustworthy, not to replace it.

## Non-Negotiable Rules

- Interpret the request before selecting metrics.
- Infer the underlying decision or learning need before selecting metrics or querying data.
- Apply the always-on reasoning kernel: request decomposition, need inference, construct validation, context necessity, evidence ceiling, scope/grain/denominator definition, and complete data-plan design.
- Activate additional reasoning methods only when their trigger is present.
- Build the question tree after initial reasoning and place it inside an analysis blueprint.
- Use only `context`, `decision`, `diagnostic`, `data_quality`, or `validation` for active question roles. Never use legacy `core` or `supporting` roles.
- Include context only when it defines, explains, validates, or changes interpretation or action.
- Give every active question a purpose, data requirement, population, grain, method, validation rule, and expected output.
- Give every important metric a definition fingerprint and every source an authority record.
- Validate technical calculations and business meaning separately.
- Block claim promotion when a critical quality check fails or remains unknown.
- Keep descriptive, diagnostic, associative, predictive, qualitative, and causal claims distinct.
- Do not generalize sample, browser, qualitative, or single-page evidence beyond its representativeness.
- Let presentation workers communicate approved claims; they may not create analytical results.
- Choose charts for communication fitness; use variety only as a tie-breaker.
- Use exact business language and plain sentences. Avoid generic, inflated, or formulaic wording.
- Version reviewed context and mark replaced claims or artifacts `superseded`; never silently overwrite them.
- If evidence is insufficient, narrow the claim, improve measurement, or report readiness instead of fabricating an answer.
- For behavioural telemetry, prove that event semantics, identifiers, duplicates, consent coverage, missing events, and release history do not manufacture the pattern.
- Deliver an honest Analysis Brief even when the answer is incomplete; name the known evidence, unknowns, limitations, and smallest useful next action.
- Put the executive answer, strongest supporting evidence, material limitations, and next action directly in the conversation; files supplement rather than replace the answer.

## Start Behaviour

Read the request and available context before asking questions. Apply only the reasoning and checks triggered by the decision, evidence, and consequence of error. Proceed on defensible assumptions; pause only for materially divergent framings, disputed outcomes, missing essential evidence, or consequential approval.

When the framing is not obvious, show a concise analyst recommendation:

```text
What I believe the business needs:
Decision or learning objective:
Necessary context:
Proposed decision and diagnostic questions:
What I am treating as hypotheses:
What I recommend parking or reframing:
Triggered route IDs:
Evidence ceiling:
Material decision needed, if any:
```

Do not ask the requester to design metrics, grain, methods, or the full data plan.

## Reference Router

- Read [needs-discovery-and-analysis-contract.md](references/needs-discovery-and-analysis-contract.md) whenever the request is unclear, metric-led, solution-led, contradictory, or missing context.
- Read [problem-type-playbooks.md](references/problem-type-playbooks.md) after selecting the framing and before approving methods or validation.
- Read [evidence-claims-and-review.md](references/evidence-claims-and-review.md) before source mapping, quality review, execution, claim promotion, recommendations, or durable-context updates.
- Read [synthesis-and-visualisation.md](references/synthesis-and-visualisation.md) before narrative design, chart selection, wording review, or stakeholder-output generation.
- Read [presentation-generator-brief.md](references/presentation-generator-brief.md) when a deck, PowerPoint, or external presentation handoff is requested.
- Read [worked-web-product-example.md](references/worked-web-product-example.md) when behavioural event sequences, missing predecessor events, reporting-window boundaries, identity changes, consent, duplicates, or instrumentation defects may explain the result.

## Four Phases And Twelve Checkpoints

```text
1. Frame - infer the need, challenge the request, design the blueprint, and set the evidence ceiling
2. Evidence - map sources, validate readiness, execute bounded work, and review results
3. Synthesis - answer the blueprint with approved claims, appropriate visuals, and natural language
4. Delivery - validate the artifact, preserve lineage, and define follow-up
```

### Phase 1: Frame

#### 1. Interpret Before Structuring

Separate facts, objectives, constraints, hypotheses, suggested metrics, suggested methods, suggested solutions, output preferences, and uncertainties. Reconstruct the relevant process and identify the likely decision or learning objective. Test whether the requested measure represents the intended construct.

Use conditional reasoning only when triggered:

| Route ID | Trigger | Methods |
| --- | --- | --- |
| `ambiguity` | Ambiguity or metric-led request | Analytical laddering, alternative framing, assumption mapping |
| `multiple_stakeholders` | Materially different stakeholder decisions | Stakeholder and decision mapping |
| `multiple_sources` | Sources must be compared or combined | Source authority, semantic compatibility, join validation |
| `outcome_comparison` | Exposure or behaviour is compared with an outcome | Temporal eligibility, composition, confounding, sensitivity |
| `sample_browser_or_qualitative_evidence` | Sample, browser, or qualitative evidence | Representativeness gate |
| `prediction` | Future outcome, score, or forecast | Leakage, holdout, calibration, drift |
| `categorisation` | Cases assigned to labels | Label quality, class balance, stability |
| `anomaly_detection` | Observations judged against normal behaviour | Baseline, seasonality, false-positive review |
| `theme_identification` | Unstructured evidence coded into themes | Corpus coverage, codebook, negative cases, reviewer agreement |
| `consequential_work` | Error could cause material harm | Pre-mortem, falsification, independent review |
| `instrumentation_reliability` | Web or product telemetry underpins the result | Event semantics, duplicate and missing events, consent coverage, identity, release history |
| `experiment` | Randomized test or declared test winner | Eligibility, randomization unit, SRM, sample size, peeking, uncertainty, guardrails |

Record triggered routes with these exact IDs in `analysis_blueprint.conditional_routes`.

#### 2. Build The Analysis Blueprint

Create the question tree only after choosing a recommended framing. Use active roles `context`, `decision`, `diagnostic`, `data_quality`, and `validation`; use `optional`, `parked`, `rejected`, `unavailable`, or `superseded` for excluded branches.

Do not rename the roles for presentation. `decision` replaces the legacy `core` label; `context` replaces legacy `supporting` only when the branch is truly necessary context.

Require context only when it defines the population or baseline, explains the process, supports interpretation, tests composition or measurement effects, validates a denominator, or informs action. Record a stop rule so context does not expand without value.

Operationalize every active question with source, required data, population, grain, metric, method, validation, and expected output. Classify each analytical leaf as:

```text
make_predictions
categorise_things
spot_unusual
identify_themes
discover_connections
find_patterns
```

#### 3. Approve The Contract

Define population, exclusions, period, timezone, grain, sources, metric fingerprints, methods, comparisons, quality gates, claim limits, outputs, and definition of done. Ask for user approval only when an unresolved choice materially changes the decision, risk, or claim ceiling.

### Phase 2: Evidence

#### 4. Map Sources And Define Methods

Record source authority, freshness, coverage, natural grain, identifiers, joinability, permitted uses, and semantic limits. Define each metric and method contract, including estimand, eligible population, baseline, time logic, uncertainty, sensitivity, and permitted claim level.

#### 5. Validate Readiness

Validate source authority and freshness, population, period, timezone, filters, identifiers, grain, deduplication, denominators, missing-versus-zero semantics, expected domains, metric meaning, and source coverage. Add conditional checks for joins, availability, temporal ordering, sampling, outliers, sample size, uncertainty, multiple comparisons, confounding, selection bias, and sensitivity.

For web and product event data, explicitly reconcile event meaning with the visible or server-side outcome; test repeated emissions, missing transitions, consent-dependent coverage, identifier changes, and tracking or product releases. For experiments, validate eligibility, assignment and analysis units, sample-ratio mismatch, sample size and stopping logic, repeated peeking, uncertainty, and guardrails before calling a winner.

Record every check as `pass`, `warning`, `fail`, `unknown`, or `not_applicable`, with severity, evidence, impact, and required action. Critical `fail` or `unknown` results block validated or approved claims.

#### 6. Execute Bounded Work

Every operation must answer an active question or documented validation need. Preserve queries, code, source references, row counts, result tables, fingerprints, assumptions, and caveats. Workers may inspect and calculate; they may not approve claims, change definitions, publish, or update durable context.

#### 7. Validate Results And Claims

Check filters, joins, grain, domains, zero states, denominators, deduplication, time ordering, availability, missingness, uncertainty, segment composition, representativeness, and claim language. Use effect size, stability, and business importance rather than statistical significance alone.

Promote findings through:

```text
observation -> candidate -> validated -> approved
                         \-> rejected
validated or approved -> superseded when replaced
```

Keep observation, interpretation, claim, and recommendation separate. Observational evidence should normally produce a hypothesis or test, not an unsupported prescription.

### Phase 3: Synthesis

#### 8. Answer The Analysis Blueprint

Answer each active context, decision, diagnostic, data-quality, and validation question with an approved claim, a documented limitation, or an explicit unavailable result. Keep branches separate when their populations, methods, or evidence postures differ.

Create the stakeholder-facing Analysis Brief with: business question, executive answer, supporting evidence, interpretation, alternative explanations, limitations, unknowns, recommended next action, and methods references. Use `complete`, `incomplete`, or `blocked` honestly; do not suppress useful partial conclusions.

#### 9. Design Visuals And Language

For each analytical visual, record the communication function, data structure, chart candidates, selected chart, measurement card, catalogue decision, wording review, and rendered QA. The measurement card must state population, grain, period, denominator, coverage, unit, temporal scope, missing/zero treatment, and claim posture.

Use the Data Visualisation Catalogue once per distinct communication function when internet access is available. Use the offline function map otherwise and record the fallback. Prefer repeated clear charts over decorative variety; use a different form when the question or data structure warrants it.

#### 10. Build The Stakeholder Narrative

Use the Analysis Brief as the primary human output. Build it from the analysis blueprint and approved claims, not from the request's order. Separate verified facts, interpretation, recommendation, and limitations. Add a deck only when the audience or request needs one, and freeze the claim set and narrative before generating medium- or high-risk decks.

Return the useful conclusion in the conversation even when a file is generated. Do not end with only a file path or validation log.

Do not require a chart when concise prose or a small table communicates the answer more clearly.

### Phase 4: Delivery

#### 11. Review And Version

Inspect rendered output for chart accuracy, labels, zero states, denominators, uncertainty, caveats, text fit, terminology, and natural wording. Use technical, target-audience, and domain-aware but analysis-naive review lenses.

Keep one active deliverable per purpose. Mark dependencies stale when definitions or claims change. Update durable context only with reviewed knowledge.

#### 12. Define Follow-Up

Choose monitoring, validation, experiment, measurement improvement, refresh, or no follow-up based on the problem type. Record the owner, success metric, guardrails, and revisit condition for every recommendation.

## Canonical Run Artifacts

Use `analyses/<analysis_id>/` unless the user provides another location. Create a v2 run with:

```text
python scripts/analysis_guard.py init analyses/<analysis_id> --analysis-id <analysis_id>
```

Keep `analysis-manifest.json` as the canonical contract, evidence under `evidence/`, and only the review views or deliverables the work needs. Validate by stage:

```text
python scripts/analysis_guard.py validate analyses/<analysis_id>/analysis-manifest.json --stage contract
python scripts/analysis_guard.py validate analyses/<analysis_id>/analysis-manifest.json --stage evidence
python scripts/analysis_guard.py quality analyses/<analysis_id>/analysis-manifest.json
python scripts/analysis_guard.py validate analyses/<analysis_id>/analysis-manifest.json --stage claims
python scripts/analysis_guard.py validate analyses/<analysis_id>/analysis-manifest.json --stage delivery
python scripts/analysis_guard.py stale analyses/<analysis_id>/analysis-manifest.json --fail-on-stale
python scripts/analysis_guard.py scan analyses/<analysis_id>
python scripts/analysis_guard.py brief analyses/<analysis_id>/analysis-manifest.json --output analyses/<analysis_id>/analysis-brief.md
```

For a final repeatable check, run the cumulative gate once; use JSON for automation:

```text
python scripts/analysis_guard.py gate analyses/<analysis_id>/analysis-manifest.json --format json
```

Migrate a v1 manifest into a separate v2 file with:

```text
python scripts/analysis_guard.py migrate path/to/analysis-manifest.json --output path/to/analysis-manifest-v2.json
```

Migration preserves history, marks new requirements unresolved, and demotes legacy validated or approved claims until v2 review. It never silently rewrites the source manifest.

## Agent And Tool Portability

Use local equivalents for files, queries, notebooks, APIs, browsers, statistics, charts, and presentations. Do not require one vendor, agent, MCP server, operating system, or analytics platform. Record missing capabilities and use the strongest feasible fallback.

Never copy credentials, client data, prior analysis results, or machine-specific paths into the reusable skill. Keep generated analysis work in the user's chosen workspace and access-controlled where needed.
