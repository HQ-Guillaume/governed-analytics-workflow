# Synthesis, Visualisation, And Language

Use this reference after evidence and claim review. Synthesis answers the analysis blueprint with approved claims; it does not rescue weak evidence through polished language or decorative charts.

## Contents

- Narrative contract
- Decision-ready Analysis Brief
- Problem-type narrative routing
- Chart selection and variety
- Measurement cards
- Wording review
- Presentation boundary
- Rendered output QA

## Narrative Contract

Build from:

```text
decision or learning objective
-> necessary context
-> decision question
-> approved claims
-> interpretation within the evidence ceiling
-> recommendation, next action, or remaining uncertainty
```

Do not reproduce the request's metric order. Do not force every analysis into one deck structure. Include context only when it defines, explains, validates, or changes the decision interpretation.

For medium- or high-risk work, freeze approved claims, narrative order, result tables, required caveats, template, language, and terminology before generating a deck. Material changes mark affected slides stale.

## Decision-Ready Analysis Brief

The Analysis Brief is the default human deliverable. A deck, dashboard, or detailed appendix is optional and should derive from it.

A text-only brief is a valid delivery. Add a chart only when it makes an important pattern, comparison, distribution, sequence, or uncertainty materially easier to understand.

```text
Business question
Executive answer
Evidence supporting the answer
Interpretation
Alternative explanations
Limitations
What remains unknown
Recommended next action
Methods and traceability
```

Use `complete` when the decision question is answered within the evidence ceiling. Use `incomplete` when useful findings exist but a material part remains unresolved. Use `blocked` when no decision-ready conclusion is supportable until a named dependency changes.

An incomplete answer is still useful when it states:

- what was established and for which population and period;
- what could not be established and why;
- whether the gap is behavioural, statistical, semantic, or instrumentation-related;
- the smallest data or measurement action that would resolve it;
- what decision is safe now and what decision should wait.

Do not replace the answer with a validation log. Put technical check details in methods and traceability unless they materially change the executive interpretation.

## Problem-Type Narrative Biases

| Type | Stakeholder narrative should normally establish |
| --- | --- |
| Make predictions | Decision context, baseline, performance, calibration, uncertainty, threshold trade-offs, use limits |
| Categorise things | Category purpose, definitions, coverage, quality, stability, action by class |
| Spot unusual | Expected baseline, departures, magnitude, context, false-positive risk, investigation priority |
| Identify themes | Corpus and coverage, themes, evidence, exceptions, implications without false prevalence |
| Discover connections | Compatible population, temporal scope, relationship magnitude, robustness, alternatives, no unsupported cause |
| Find patterns | Complete relevant baseline, distributions or trends, important contrasts, interpretation, next questions or actions |

Mixed analyses must preserve branch boundaries. One branch's evidence posture cannot strengthen another.

## Chart-Selection Gate

Use The Data Visualisation Catalogue as the default external guide:

- `https://datavizcatalogue.com/index.html`
- `https://datavizcatalogue.com/search.html`

For each distinct communication function:

1. State the slide question and approved claim.
2. Identify variable types, ordering, exclusivity, cumulative or stage logic, time, geography, categories, series, sample size, and uncertainty.
3. Select the communication function.
4. Consult the live catalogue once when internet access is available; open unfamiliar chart pages when needed.
5. Shortlist valid candidates and reject misleading ones.
6. Choose the clearest valid chart for the audience.
7. Use variety only when equally valid choices exist or the communication function changes.
8. Record required labels and render the result.

If the live catalogue is unavailable, use the function map below and record the fallback. A user-provided visual system can override styling, not evidence or chart integrity.

## Offline Function Map

| Need | Function | Common choices |
| --- | --- | --- |
| Compare categories or groups | Comparison | Sorted bar, grouped bar, dot plot, small multiples |
| Show a distribution | Distribution | Histogram, box plot, density, ordered exclusive bars |
| Show change over time | Data over time | Line, small multiples, indexed line, area when magnitude matters |
| Show association | Relationship | Scatterplot, heatmap, grouped estimates with intervals |
| Show part of a whole | Proportion | 100% stacked bar, stacked bar; pie only for very few parts |
| Show cumulative stage reach | Ordered progression | Stepped bars, stage bars, line; funnel only for genuinely nested stages |
| Show movement or flow | Movement or flow | Sankey or flow only when path transfer is the message |
| Show range or uncertainty | Range | Interval plot, error bars, box plot, forecast band |
| Show hierarchy | Hierarchy | Tree or treemap when nesting is essential |
| Show location | Location | Choropleth, dot or bubble map with appropriate normalization |
| Show text themes | Analysing text | Ranked bars, theme matrix, evidence excerpts |
| Explain an interface or spatial context | Reference | Annotated screenshot, page map, table, process diagram |

Specialist diagnostics such as calibration, lift, precision-recall, residual, control, or survival plots may override catalogue choices. Explain them in plain language.

## Visual Decision Record

```json
{
  "visual_id": "V1",
  "claim_ids": ["C1"],
  "question_id": "Q1",
  "result_ref": "",
  "message": "",
  "communication_function": "comparison",
  "data_structure": {
    "metric_shape": "rate",
    "ordered": true,
    "categories_overlap": false,
    "series_count": 2
  },
  "candidate_charts": ["grouped_bar", "dot_plot"],
  "selected_chart": "dot_plot",
  "selection_rationale": "",
  "variety_role": "tie_breaker | structure_required | not_applicable",
  "required_labels": [],
  "live_catalogue_checked": true,
  "qa_status": "pending"
}
```

Do not require a different chart merely because a previous slide used the same form. Repetition is preferable when it makes comparison easier.

## Hard Rejection Rules

Reject a visual when it:

- presents mutually exclusive classes as sequential funnel stages;
- uses a line across unordered categories;
- uses part-to-whole encoding for overlapping groups;
- omits an expected zero/start state or source-domain value;
- displays a percentage without population and denominator meaning;
- compares incompatible periods, grains, fingerprints, or axes;
- ranks raw volume when normalized performance is required;
- hides sample size or uncertainty that changes interpretation;
- implies causality without a causal design;
- uses an unnecessarily complex radial, network, flow, treemap, or dual-axis chart;
- turns illustrative evidence into a population percentage;
- cannot be read by the target audience at rendered size.

## Measurement Card

Every analytical stakeholder visual must carry or clearly reference:

```json
{
  "population": "",
  "grain": "",
  "period": "",
  "denominator": "",
  "coverage": "",
  "unit": "",
  "temporal_scope": "",
  "missing_zero_treatment": "",
  "claim_posture": "",
  "source_ref": ""
}
```

Place the information where the audience can understand the chart. It may be split between subtitle, labels, note, and speaker notes, but it must not be absent.

## Wording Review

Use exact user-visible, operational, or approved business vocabulary in main outputs. Keep technical field and event names in methods or appendices unless the audience needs them.

Review each slide for:

- direct, concrete sentences;
- one supported message;
- defined population, rate, and period;
- technical terms explained in plain language;
- facts separated from interpretation and recommendation;
- no unsupported intent, attention, value, contribution, improvement, or causality;
- no generic filler, inflated confidence, repetitive conclusion patterns, or abstract AI-style phrasing;
- natural wording in the requested language;
- exact interface wording where similar actions could be confused.

Do not rely on a static banned-word list. Judge whether a domain-aware but analytics-naive reader can explain the message accurately after one reading.

Wording review record:

```json
{
  "audience": "",
  "language": "",
  "terminology_source": "",
  "plain_language_passed": false,
  "fact_interpretation_recommendation_separated": false,
  "notes": ""
}
```

## Presentation Generator Boundary

The presentation worker may select and order approved claims, simplify language without changing meaning, render approved visual designs, apply a template, and surface caveats and implications.

It may not calculate or merge results, change population or denominator, promote a claim, turn association into causality, omit required caveats, or invent an explanation or recommendation.

## Rendered Output QA

Inspect rendered slides or pages, not only source code or XML. Check:

- slide order and one-message discipline;
- text fit, font size, contrast, and overlap;
- title accuracy and claim posture;
- axes, units, baselines, sorting, periods, samples, denominators, and coverage;
- expected domains and zero states;
- legend and label clarity;
- uncertainty and caveats beside the claims they constrain;
- template and brand application;
- source screenshots readable and correctly framed;
- terminology and translation consistency;
- no stale claim, result, or fingerprint dependency.

Set `qa_status` to `passed`, `failed`, or `not_possible` with notes. If rendering or inspection is impossible, state the limitation and do not claim visual QA passed.
