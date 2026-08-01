# Evidence, Quality, Claims, And Review

Use this reference to govern source roles, data readiness, metric compatibility, bounded execution, claim promotion, recommendations, independent review, and artifact freshness.

## Contents

- Source authority and semantic validation
- Metric and method contracts
- Quality checks and readiness gates
- Bounded execution
- Claims and recommendations
- Independent review
- Staleness, context, privacy, and access

## Source Authority

Create one record per source:

```json
{
  "source_id": "S1",
  "name": "",
  "owner": "",
  "authority": "canonical | supporting | illustrative | experimental",
  "source_grain": "",
  "coverage": "",
  "freshness": {"valid_as_of": "", "revalidate_after": ""},
  "join_keys": [],
  "joinability": "direct | aggregate_only | none | unknown",
  "allowed_uses": [],
  "forbidden_uses": [],
  "access_and_pii": "",
  "caveats": []
}
```

Multiple sources do not become compatible because they describe the same topic. Do not divide, join, or compare across sources until grain, population, period, identifiers, semantics, and authority permit it.

## Semantic Validation

Technical availability is not business validity. For every important event, field, status, category, or interface action:

1. Inspect documentation and observed values.
2. Verify the operational or visible outcome when relevant.
3. Identify technical aliases that represent one business outcome.
4. Identify one technical value that represents several outcomes.
5. Record direct measures, proxies, and invalid interpretations.
6. Define deduplication and precedence rules before calculation.

Browser evidence can validate wording, visible outcomes, geometry, and instrumentation behaviour. It does not establish aggregate prevalence or impact by itself.

## Metric Definition And Method Contract

Every important metric needs a definition fingerprint:

```text
population
calculation grain
time window and timezone
scope and filters
numerator and denominator
deduplication
source/query reference
run date
```

Also record:

```text
intended construct
direct measure or proxy
coverage and missingness
measurement limit
target quantity or estimand
baseline or comparison
time logic
uncertainty method
sensitivity checks
permitted claim types
```

Do not compare metrics with incompatible fingerprints unless the difference is intentional, visible, and justified.

The guard hashes the fingerprint as SHA-256 over canonical JSON: keys sorted, compact separators, ASCII escapes, then UTF-8 bytes. The hash detects definition changes; it is not a claim that the query ran correctly. Store `fingerprint_hash` on validated, approved, or active metrics and snapshot it on dependent claims and artifacts.

## Quality Checks

Record checks as structured evidence:

```json
{
  "check_id": "DQ1",
  "category": "grain_identifiers",
  "condition": "always | conditional",
  "question_ids": ["Q1"],
  "source_ids": ["S1"],
  "metric_ids": ["M1"],
  "status": "pass | warning | fail | unknown | not_applicable",
  "severity": "critical | major | minor | info",
  "evidence_ref": "",
  "impact": "",
  "required_action": "",
  "checked_at": ""
}
```

### Always-On Categories

For evidence or claim readiness, cover:

```text
source_authority
source_freshness
population_scope
period_timezone
grain_identifiers
deduplication
denominator
missing_zero
domain_completeness
metric_semantics
source_coverage
```

Use `not_applicable` only with a reason. A template row is not evidence of a completed check.

### Conditional Categories

Add when triggered:

```text
join_cardinality
availability
temporal_ordering
representativeness
outliers_skew
minimum_sample
uncertainty
multiple_comparisons
composition_confounding
selection_bias
sensitivity
prediction_leakage
prediction_calibration
label_quality
anomaly_baseline
theme_validation
instrumentation_semantics
instrumentation_duplicates
instrumentation_missing_events
instrumentation_consent_coverage
instrumentation_change_history
instrumentation_identity
experiment_eligibility
experiment_randomization_unit
experiment_srm
experiment_sample_size
experiment_peeking
experiment_guardrails
```

The instrumentation categories apply only when web or product telemetry underpins a result. Identity is additionally required when user- or journey-level matching depends on stitching. The experiment categories apply only to randomized tests or winner/rollout decisions.

### Quality Gates

- A critical `fail` or `unknown` blocks `validated` and `approved` claims.
- A major warning requires a visible impact and required action.
- A warning affecting interpretation must appear on dependent claims and visuals.
- `not_applicable` requires a rationale in `impact` or `required_action`.
- Structural validation cannot prove that an external query, model, or business interpretation is correct; retain source evidence and independent review.

## Availability And Temporal Eligibility

- Use eligible denominators for optional content, products, features, or journeys.
- If availability cannot be measured, report raw use and the denominator limitation.
- Prove event order before describing behaviour as pre-outcome.
- Exclude or separately describe outcomes that precede required exposure.
- Keep full-period descriptive behaviour separate from contribution-oriented comparisons.
- Treat missing timestamps, ambiguous ordering, and censoring as quality conditions, not silent assumptions.

## Web And Product Instrumentation Reliability

Before treating an event sequence as user behaviour:

1. Define the event against the interface or server outcome.
2. Preserve raw event time, collection time, timezone, visit, person, component, campaign, and attempt identifiers.
3. Reproduce the pairing rule and include the required lookback before filtering the report window.
4. Test retry, double-fire, batch, replay, and server/client duplicate signatures.
5. Reconcile expected journey transitions with missing events.
6. Quantify consent and blocker coverage by platform and event source.
7. Test anonymous-to-known, device, session, and login identity changes when relevant.
8. Align discontinuities with tag, schema, CMP, app, and product releases.

Report mutually exclusive cause categories that reconcile to the original anomaly count. Use `unobservable` or `unknown` when collection cannot establish whether the behaviour occurred.

## Practical Experiment Validity

For an A/B test or rollout decision, record and validate:

- eligible population and exclusion timing;
- assignment mechanism, randomization unit, analysis unit, and exposure rule;
- sample-ratio mismatch and allocation changes;
- repeated users, devices, contamination, and attrition;
- primary outcome, sample-size plan, stopping rule, and repeated peeking;
- effect size, uncertainty, practical threshold, and segment stability;
- guardrail outcomes and implementation integrity.

If these cannot be recovered, report the observed comparison as incomplete or directional rather than retroactively inventing a clean experiment.

## Representativeness Gate

Before generalizing sampled evidence, record target population, sampling frame, selection method, sample size, coverage, important variants, devices or contexts represented, known exclusions, and supported claim scope.

Use `illustrative` when evidence demonstrates a possible behaviour but cannot estimate prevalence. Use `directional` only when coverage supports a cautious pattern. Never multiply a sample geometry observation by an aggregate rate to manufacture precision.

## Statistical Review

Apply problem-type methods, then review:

- distribution, skew, outliers, and missingness;
- effect size and uncertainty;
- practical importance, not significance alone;
- minimum sample and small cells;
- segment composition and Simpson's-paradox risk;
- multiple comparisons and selective reporting;
- confounding, selection, and reverse causality;
- sensitivity to definitions, filters, time windows, and buckets;
- temporal eligibility and leakage.

Record inconclusive results. Absence of statistical evidence is not proof of no effect, and statistical detection is not proof of business value.

## Bounded Work Packets

Task packet:

```json
{
  "task_id": "T1",
  "question_ids": ["Q1"],
  "objective": "",
  "allowed_source_ids": ["S1"],
  "allowed_operations": [],
  "required_output_schema": {},
  "validation_rules": [],
  "prohibited_actions": ["publish", "approve_claim", "update_durable_context"]
}
```

Result packet:

```json
{
  "task_id": "T1",
  "question_ids": ["Q1"],
  "source_refs": [],
  "operations": [],
  "result_refs": [],
  "row_counts": {},
  "metric_ids": [],
  "candidate_claims": [],
  "assumptions": [],
  "caveats": [],
  "validation_results": [],
  "status": "draft"
}
```

Workers cannot publish, approve their own claims, change source-of-truth definitions, or update durable context.

## Claim Lifecycle

```text
observation: captured result not yet interpreted or validated
candidate: decision-relevant statement awaiting validation
validated: evidence, quality gates, fingerprints, and posture passed review
approved: authorized for the intended stakeholder use
rejected: checked and unsupported or misleading
superseded: replaced by a newer definition, result, or decision
```

Keep observation, interpretation, claim, and recommendation separate.

Claim record:

```json
{
  "claim_id": "C1",
  "question_ids": ["Q1"],
  "statement": "",
  "status": "candidate",
  "claim_type": "descriptive | diagnostic | associative | predictive | qualitative | causal | unknown (unpromoted migration only)",
  "evidence_posture": "verified | directional | assumed | needs_validation",
  "temporal_scope": "full_period | pre_outcome | post_outcome | cross_sectional | not_applicable | unknown",
  "population": "",
  "denominator": "",
  "coverage": "",
  "missingness": "",
  "uncertainty": "",
  "evidence_refs": [],
  "metric_ids": [],
  "alternative_explanations": [],
  "decision_use": "",
  "valid_as_of": "",
  "approved_by": "",
  "approved_at": ""
}
```

Validated or approved claims require compatible metric fingerprints, validated evidence, complete measurement context, no blocking quality result, a permitted claim type, and a current validity date. Causal claims require a causal-design reference.

Migration may set `claim_type` to `unknown` when v1 evidence did not declare a posture. Resolve it before validation or approval; the migration must not infer a descriptive posture merely because the legacy record lacks one.

## Recommendations

Recommendation record:

```text
recommendation ID and decision ID
supporting approved claim IDs
hypothesis
expected mechanism
target population
proposed action
success metrics
guardrails
experiment or implementation requirement
owner
revisit condition
```

Observational findings should normally support a test, validation study, measurement improvement, or bounded operational action. Do not turn association into a redesign prescription without an adequate causal design.

## Independent Review

### Technical Lens

- source authority, freshness, code, and query reproducibility;
- filters, joins, grain, time, deduplication, domains, denominators, missingness;
- uncertainty, sensitivity, sample size, and problem-type validation;
- semantic, temporal, and claim-to-evidence validity.

### Audience Lens

- understandable population, measure, unit, period, denominator, and coverage;
- no technical labels without explanation;
- caveats visible where interpretation occurs;
- no title or chart implying a stronger claim;
- decision implication clear without hiding uncertainty.

### Domain-Aware, Analysis-Naive Lens

- assumptions a close analyst may have stopped noticing;
- mismatch with business process or interface behaviour;
- plausible alternative explanations;
- missing context a knowledgeable new reader needs.

Prefer a clean-context reviewer supplied with the contract, evidence packet, proposed claims, and draft output rather than the intended verdict.

## Artifact Dependencies And Staleness

Artifacts declare question, metric, evidence, claim, visual, and recommendation dependencies plus current metric fingerprint hashes. When an upstream definition or status changes:

1. demote dependent claims to `candidate` or mark them `superseded`;
2. mark dependent artifacts `stale`;
3. regenerate only affected outputs;
4. review before restoring `active` status.

Keep one active artifact per purpose.

## Versioned Durable Context

Store only reviewed knowledge. Record old and new values or definitions, validity window, run date, source analysis and claim IDs, owner, reviewer, reason, and status. Prefer pointers to the canonical manifest over copied facts.

## Privacy And Access

- Keep raw sources access-controlled.
- Use anonymized examples unless identifiers are necessary and authorized.
- Never place credentials or secrets in manifests, evidence, logs, decks, repositories, or durable context.
- Record access limitations and evidence not inspected.
- Run the portability and secret scan before sharing or publishing artifacts.
