# Analytical Problem-Type Playbooks

Use problem types after selecting the recommended framing and drafting the analysis blueprint. They route methods and validation; they do not replace the business decision, determine required context by themselves, or dictate a chart.

## Routing Rules

- Assign one primary type to the analysis and secondary types only to distinct subquestions.
- Decompose mixed requests rather than forcing one method to answer incompatible questions.
- A type may be revised when readiness changes, but record the contract change and stale dependencies.
- Apply universal profiling internally: population, time coverage, grain, missingness, label/outcome prevalence where relevant, and source freshness.
- Require a stakeholder-facing descriptive chapter only when it helps answer the confirmed tree. It is central to `find_patterns`, but supporting for many other types.
- Select the method from the question, target quantity, design, and evidence readiness rather than from a requested metric or preferred conclusion.
- Keep the type-specific branch separate from descriptive context and quality validation.

## Method Contract

For every active analytical method, record:

```text
question and decision use
target quantity or estimand
eligible population and grain
baseline or comparison
time logic
method and assumptions
effect-size and uncertainty treatment
minimum sample or evidence requirement
validation and sensitivity checks
permitted claim level
follow-up when the evidence ceiling is reached
```

Statistical significance alone is never sufficient. Review practical magnitude, stability, uncertainty, and business relevance.

## Make Predictions

**Purpose:** Estimate a future or currently unknown outcome for an entity or period.

**Frame:** What is predicted, for whom, at what prediction time, over what horizon, and for what decision?

**Required inputs:** A defensible target, observation window, prediction horizon, features available at prediction time, sufficient historical outcomes, and a deployment/use context.

**Method families:** Regression, classification, survival analysis, forecasting, ranking, and appropriate established domain libraries.

**Baseline:** Historical outcome prevalence, naive rule, persistence/seasonal forecast, or current decision process.

**Validation:** Time-aware or representative holdout, backtesting, leakage checks, calibration, error by important segment, uncertainty, class imbalance, threshold trade-offs, fairness where relevant, and robustness to drift.

**Claim limits:** Predictive importance is not a causal driver. Performance on training data is not deployment performance.

**Common outputs:** Error and uncertainty summaries, calibration or lift, threshold scenarios, forecast intervals, and operational implications.

**Follow-up:** Drift monitoring, recalibration, retraining criteria, outcome capture, and decision-impact review.

**Conditional route:** Activate only when the task requires an unknown or future value for a defined decision time. Reject features unavailable at prediction time and evaluation that reuses training observations.

## Categorise Things

**Purpose:** Assign observations to known classes or create useful, stable groupings.

**Frame:** Are categories predefined or discovered, mutually exclusive or overlapping, and what action follows assignment?

**Required inputs:** Category definitions or segmentation objective, representative examples, label provenance, and handling for unknown/multiple categories.

**Method families:** Rules, supervised classification, clustering, taxonomy mapping, entity resolution, and human coding.

**Baseline:** Existing taxonomy, majority class, current business rule, or simple segmentation.

**Validation:** Label quality, inter-rater agreement when human-labelled, class balance, confusion matrix or per-class error, cluster stability, separation and usefulness, unknown handling, and temporal stability.

**Claim limits:** Discovered clusters are analytical constructs, not natural truths. A class label does not explain why the observation belongs there.

**Common outputs:** Category definitions, assignment quality, segment profiles, uncertain/unclassified share, and actionability by class.

**Follow-up:** Label review, taxonomy governance, drift/stability checks, and manual escalation rules.

**Conditional route:** Activate label provenance, class balance, unknown handling, and stability checks. Use clustering only when discovered groups have a decision purpose and a stability review.

## Spot Something Unusual

**Purpose:** Detect departures from an expected baseline.

**Frame:** Unusual relative to which population, period, seasonality, peer group, or control limits, and what response should follow?

**Required inputs:** Stable comparison baseline, sufficient history or peers, known calendar/context effects, and an investigation workflow.

**Method families:** Statistical process control, residual analysis, robust thresholds, change-point detection, anomaly models, and rule-based alerts.

**Baseline:** Normal range with seasonality, trend, known events, and data-quality behaviour separated from business behaviour.

**Validation:** Backtesting on known incidents, false-positive/false-negative trade-offs, sensitivity to window and threshold, peer/context review, duplicate alerts, and data-pipeline anomaly checks.

**Claim limits:** Unusual does not mean harmful, fraudulent, or causal. Detection requires investigation.

**Common outputs:** Ranked anomalies, expected range, magnitude, context, confidence, and investigation priority.

**Follow-up:** Alert precision review, threshold tuning, incident outcomes, and baseline refresh.

**Conditional route:** Activate only after defining the normal baseline and the cost of false positives and false negatives. Separate data-pipeline anomalies from business anomalies.

## Identify Themes

**Purpose:** Extract recurring concepts, needs, concerns, or narratives from unstructured evidence.

**Frame:** Which corpus, voices, period, language, sampling process, and decision should the themes represent?

**Required inputs:** Corpus definition, sampling/coverage, privacy rules, text quality, language handling, and traceable source excerpts where allowed.

**Method families:** Human coding, thematic analysis, topic modelling, embedding-assisted clustering, summarisation with evidence anchors, and mixed-method quantification.

**Baseline:** Corpus composition, source/segment coverage, document length, missing voices, and a codebook or initial coding frame.

**Validation:** Codebook clarity, negative cases, reviewer agreement or adjudication, theme stability across samples/segments, traceable examples, saturation limitations, and privacy review.

**Claim limits:** Theme frequency is not automatically prevalence in the population. Model-generated labels require human semantic review.

**Common outputs:** Ranked or structured themes, supporting evidence, segment differences, exceptions, and unanswered questions. Avoid word clouds as the sole decision surface.

**Follow-up:** Codebook refinement, new-sample validation, qualitative interviews, and recurring corpus refresh.

**Conditional route:** Activate corpus coverage, language, privacy, codebook, negative-case, and reviewer-agreement checks. Do not infer population prevalence from unrepresentative text.

## Discover Connections

**Purpose:** Identify associations, dependencies, sequences, or network relationships among variables, behaviours, or entities.

**Frame:** Which variables or events, at what aligned grain and time order, for what explanatory or decision purpose?

**Required inputs:** Compatible grains, temporal definitions, sufficient overlap, meaningful comparison groups, and known confounders or selection mechanisms.

**Method families:** Correlation, stratified comparison, regression, cohort analysis, sequence/path analysis, association rules, and network analysis.

**Baseline:** Marginal distributions, missingness, outcome prevalence, overlap, and simple unadjusted relationship.

**Validation:** Grain and time alignment, denominator compatibility, confounding and composition checks, multiple-comparison caution, uncertainty, sensitivity to specifications, reverse causality, and temporal ordering.

**Claim limits:** Association does not establish contribution or causality. Post-outcome behaviour cannot support a pre-outcome explanation.

**Common outputs:** Effect/association size with uncertainty, stratified comparisons, sequences, robustness notes, and alternative explanations.

**Follow-up:** Better measurement, replication, causal design, controlled experiment, or no causal follow-up when unnecessary.

**Conditional route:** Activate temporal eligibility, grain compatibility, composition, confounding, reverse-causality, uncertainty, multiple-comparison, and sensitivity checks. Keep full-period description separate from pre-outcome analysis.

## Find Patterns

**Purpose:** Describe recurring distributions, trends, sequences, cohorts, funnels, or usage structures.

**Frame:** Pattern in what population, measure, period, grain, and segmentation, and why does it matter?

**Required inputs:** Complete domain definitions, stable denominators, sufficient coverage, interpretable ordering/time, and relevant breakdowns.

**Method families:** Descriptive distributions, trends, cohorts, funnels, paths, segmentation, seasonality, and top/bottom comparisons with denominator thresholds.

**Baseline:** Complete population and domain, including zero/start states, missing categories, central tendency and spread where appropriate.

**Validation:** Exclusive versus cumulative metric shape, monotonicity where required, denominator and domain completeness, outliers, segment composition, stability across time, minimum sample sizes, and sensitivity to bucketing.

**Claim limits:** A pattern does not explain motive or establish cause. Low interaction may reflect low availability or poor measurement rather than low value.

**Common outputs:** Distributions, trends, small multiples, cohorts, stage progression, and decision-relevant contrasts.

**Follow-up:** Monitoring, deeper diagnostic questions, measurement improvement, or experiments derived from robust patterns.

**Conditional route:** Activate complete-domain, zero/start-state, missingness, exclusive-versus-cumulative, denominator, outlier, segment-composition, and bucketing-sensitivity checks.

## Mixed-Type Analysis

Use a question-to-type map:

```text
Q1: What is happening?                    -> find_patterns
Q2: Which behaviours move together?       -> discover_connections
Q3: Which cases are likely next month?    -> make_predictions
Q4: Which cases require investigation?    -> spot_unusual
```

Keep separate evidence and claim limits for each branch. A predictive branch cannot answer why; an association branch cannot prove cause; a thematic branch cannot establish population prevalence without an appropriate sampling design.

## Experiment Decision Route

An experiment is a design route, not a seventh problem type. The outcome comparison will usually use `discover_connections`, while allocation, exposure, and segment patterns may use `find_patterns`.

Before a winner or rollout claim, require eligibility, assignment and analysis units, sample-ratio-mismatch review, planned sample size, stopping and peeking treatment, effect size with uncertainty, implementation integrity, and guardrails. If randomization or stopping validity fails, lower the claim ceiling to a directional observed comparison.

## Problem-Type Review Checklist

- Does the type match the answer the question seeks?
- Are required inputs available before method selection?
- Is the baseline appropriate to the type?
- Are validation checks type-specific rather than generic only?
- Does claim language stay within the type's evidence ceiling?
- Does stakeholder output include the information needed to use the result responsibly?
- Is follow-up appropriate to the type rather than defaulting to an experiment?
- Is required context included because it changes interpretation, rather than because a standard chapter expects it?
- Is the method contract complete enough for another analyst to reproduce and challenge the result?
