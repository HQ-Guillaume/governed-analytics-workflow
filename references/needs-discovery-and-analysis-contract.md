# Needs Discovery And Analysis Contract

Use this reference to infer the real analytical need from incomplete, excessive, metric-led, solution-led, or contradictory input. The request is evidence about the stakeholder's context, not the analysis specification. The question tree is produced after reasoning; it does not replace reasoning.

## Contents

- Always-on reasoning kernel
- Adaptive discovery router
- Request decomposition and construct validity
- Decision and context reasoning
- Conditional methods
- Analysis blueprint and question tree
- User interaction and stop conditions
- Analysis contract

## Always-On Reasoning Kernel

Apply these seven moves to every analysis:

1. **Decompose the request.** Separate facts, objectives, constraints, hypotheses, suggested metrics, suggested methods, suggested solutions, output preferences, and uncertainties.
2. **Infer the underlying need.** Establish the likely decision or learning objective and what different findings would change.
3. **Validate constructs.** Test whether each requested measure represents the concept the requester wants to understand.
4. **Assess context necessity.** Identify only the contextual evidence needed to define, explain, validate, or act on the result.
5. **Set the evidence ceiling.** State the strongest claim the design and available sources can support.
6. **Define population logic.** Recommend population, scope, period, timezone, grain, filters, exclusions, and denominator.
7. **Design the complete data plan.** Include decision, context, diagnostic, quality, and validation data even when the requester did not name them.

Keep this reasoning concise. Record its decisions and assumptions, not hidden chain-of-thought.

## Adaptive Discovery Router

Apply the always-on kernel once, then add only the methods whose trigger is present. A clear low-risk question can proceed after a concise internal frame. Ambiguity, incompatible sources, causal wording, behavioural telemetry, experiments, or consequential decisions activate their specific checks. The workflow has no user-selectable analysis modes.

Show the recommended frame when it helps the requester correct a material assumption. Pause only when a plausible alternative would change the population, decision, evidence ceiling, method, or consequence of error.

## Request Decomposition

Treat material statements as follows:

| Class | Treatment |
| --- | --- |
| Observed fact | Preserve with provenance and freshness status |
| Business objective | Use to infer the decision or learning objective |
| Constraint | Treat as binding when explicit and feasible |
| Hypothesis | Test or retain as unverified |
| Suggested metric | Evaluate construct, grain, denominator, actionability, and availability |
| Suggested method | Treat as a candidate unless methodologically required |
| Suggested solution | Separate from the problem and test the need first |
| Output preference | Preserve unless it conflicts with evidence integrity |
| Uncertainty | Convert to an assumption, question, readiness gap, or user decision |

Prior analyses, dashboards, stakeholder statements, and browser observations are context. Classify them as `authoritative`, `current`, `illustrative`, `stale`, or `superseded` before reuse.

## Construct-To-Measure Validation

For every important requested concept, record:

```text
intended construct
proposed observable measure
measurement grain
direct measure or proxy
coverage and missingness
known semantic limits
valid uses
invalid interpretations
```

Examples of required reframing include:

- visit duration is not section reading time;
- threshold reach is not direct content visibility;
- interaction is not satisfaction or value;
- outcome association is not causal contribution;
- raw use across all entities is not an availability-adjusted interaction rate.

If the measure cannot support the intended construct, recommend the strongest defensible proxy and the measurement improvement needed for a direct answer.

## Decision-Backward Framing And Reasoning

Infer or establish:

```text
decision owner
decision or learning objective
available actions or options
deadline or revisit condition
cost of being wrong
what different answers would change
```

Use the answer-to-action test. If plausible answers would not change an action or meaningful learning outcome, treat the item as context, diagnostic support, or optional work rather than a core decision question.

Exploratory analysis may use a learning objective. Do not invent a false immediate decision.

## Context Necessity Test

Include a contextual data item only when it does at least one of the following:

- defines the population, baseline, denominator, or normal range;
- explains the relevant business process or user journey;
- makes a decision comparison interpretable;
- tests a composition, measurement, or selection explanation;
- supports a realistic action or follow-up.

Record why context is included and define a stop rule. Do not create a generic descriptive chapter by default.

## Conditional Reasoning Methods

Activate methods from observed triggers, not because they exist.

Use these stable route identifiers in `analysis_blueprint.conditional_routes`:

| Route identifier | Trigger |
| --- | --- |
| `ambiguity` | The literal request is unclear, metric-led, solution-led, or internally inconsistent. |
| `multiple_stakeholders` | Stakeholders have materially different decisions, definitions, or consequences. |
| `multiple_sources` | More than one source must be compared, reconciled, or combined. |
| `outcome_comparison` | Behaviour, exposure, or attributes are compared against a later outcome. |
| `sample_browser_or_qualitative_evidence` | Evidence is sampled, browser-observed, or qualitative. |
| `prediction` | A future outcome, score, or forecast is required. |
| `categorisation` | Cases must be assigned to labels or operational groups. |
| `anomaly_detection` | Observations must be judged against an expected baseline. |
| `theme_identification` | Unstructured evidence must be coded into recurring themes. |
| `consequential_work` | Error could create material harm, irreversible action, or external exposure. |
| `instrumentation_reliability` | Web or product telemetry may be affected by event semantics, implementation, identity, consent, or releases. |
| `experiment` | A randomized test is being designed, analysed, stopped, or used for a rollout decision. |

### Ambiguity Or Metric-Led Requests

- **Analytical laddering:** ask internally why each requested metric matters until reaching a decision or learning need.
- **Alternative framing:** compare literal, inferred, and minimum-useful frames; recommend one.
- **Assumption mapping:** record statement, owner, importance, evidence required, alternatives, claim ceiling, and status.

### Multiple Stakeholders

Map requester, decision owner, affected teams, source owners, technical reviewers, and final audience. Pause only when competing expectations would create materially different analyses or decisions.

### Multiple Sources

Determine source authority, semantic compatibility, grain, time, identifiers, coverage, joinability, and permitted uses before comparison or combination.

### Outcome Comparison

Prove exposure and outcome order. Separate pre-outcome behaviour from full-period description. Check composition, confounding, selection, reverse causality, and sensitivity before explanatory wording.

### Sample, Browser, Or Qualitative Evidence

Apply a representativeness gate. Use `illustrative` when evidence shows a possible behaviour but cannot estimate prevalence; use `directional` only when coverage supports a cautious pattern.

### Consequential Work

- **Pre-mortem:** imagine the analysis caused a poor decision; convert plausible causes into requirements.
- **Falsification:** state what evidence would weaken or overturn the preferred interpretation.
- **Independent review:** use a clean-context reviewer with the contract and evidence, not the intended verdict.

### Instrumentation Reliability

Reproduce the result from raw events before interpreting behaviour. Define each event against the visible or server-side outcome, then test duplicate emissions, missing expected transitions, reporting-window lookback, timestamp and timezone handling, identifier changes, consent-dependent collection, and tracking or product release history. Distinguish `observed no event` from `the behaviour did not happen`.

### Experiments

Confirm the eligible population, assignment mechanism, randomization unit, analysis unit, primary outcome, planned sample size, stopping rule, and guardrails. Check sample-ratio mismatch, cross-device or repeated-user contamination, peeking, attrition, uncertainty, and practical importance. Do not declare a winner from a favourable point estimate alone.

Problem-type-specific routes are defined in `problem-type-playbooks.md`.

## Analysis Blueprint

Build the blueprint after selecting the recommended framing:

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

### Question Roles

Use active roles:

```text
context
decision
diagnostic
data_quality
validation
```

Use excluded roles:

```text
optional
parked
rejected
unavailable
superseded
```

The user-facing tree should normally contain two to four decision or context questions. The operational tree may contain more diagnostic and quality leaves.

### Operational Question Contract

Every active question must contain:

```json
{
  "question_id": "Q1",
  "parent_id": null,
  "text": "",
  "role": "decision",
  "purpose": "",
  "problem_type": "find_patterns",
  "decision_relevance": "",
  "source_ids": [],
  "data_requirement_ids": [],
  "metric_ids": [],
  "population": "",
  "grain": "",
  "method": "",
  "validation_rules": [],
  "expected_output": "",
  "status": "operational"
}
```

### Data-Plan Contract

Every data requirement must state:

```text
requirement ID and linked question IDs
purpose
source IDs
population and grain
scope and denominator
measure or fields needed
method
validation rules
status
```

Classify the requirement as context, decision, diagnostic, quality, or validation data. The agent proposes these requirements; the requester does not need to enumerate them.

### Request Coverage

Map every material request item to:

```text
answered_by_question
supporting_context
parked
rejected
unavailable
superseded
```

Record a reason for every item not answered directly. Request coverage prevents silent omission without making the request authoritative.

## User Interaction

Show the recommended frame rather than asking the requester to construct it. Ask a targeted question only when:

- two defensible framings support materially different decisions;
- the outcome or business definition is disputed;
- a consequential claim requires human approval;
- essential evidence or access cannot be inferred or obtained;
- a binding constraint conflicts with a defensible analysis.

Otherwise state the assumption, choose the most defensible path, and continue.

When new information changes population, outcome, grain, source authority, metric meaning, method, or claim ceiling, revise the blueprint and mark dependent claims and artifacts stale.

## Analysis Contract

The approved contract must identify:

| Area | Required content |
| --- | --- |
| Purpose | Inferred need, decision or learning objective, owner, audience, deadline |
| Reasoning | Decomposition, selected frame, confidence, assumptions, construct checks, evidence ceiling |
| Blueprint | Active questions, problem types, context rationale, data plan, stop rule |
| Scope | Population, exclusions, period, timezone, grain, segments |
| Evidence | Source authority, semantics, representativeness, freshness, joinability |
| Metrics | Definitions, fingerprints, coverage, measurement limits |
| Methods | Estimands, baselines, comparisons, uncertainty, validation, sensitivity, claim limits |
| Delivery | Expected artifacts, presentation inputs, review and approval gates |

Do not approve the contract merely because every field is populated. Review whether it represents the real need and whether the proposed evidence can answer it.
