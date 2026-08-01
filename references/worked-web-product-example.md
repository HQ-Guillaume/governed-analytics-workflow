# Worked Web/Product Analytics Example

This synthetic example shows the expected end-to-end behaviour of the skill. It is deliberately close to a common production question, but contains no client data.

## Request

"Why does the July report contain form sends without a preceding form open? Give the product team the real causes, not only a count."

## Decision framing

- **Decision:** decide whether to fix the interface, the tracking, or the reporting logic.
- **Population:** all server-confirmed form sends from 1 July through 31 July, Europe/Paris time.
- **Event grain:** one raw event row; the decision metric is one deduplicated send attempt.
- **Pairing rule:** pair each send to the nearest earlier, unused `form_open` with the same visit and widget, within 30 minutes.
- **Evidence ceiling:** the event stream can establish observed event sequences and measurement defects. It cannot prove that a person did not open the form when the open event was unobservable.
- **Triggered routes:** `ambiguity`, `multiple_sources`, and `instrumentation_reliability`.

The 30-minute lookback is applied before filtering the output to July. An open may support only one send unless the product contract explicitly says that one open permits several distinct submissions.

## Minimal raw evidence

| Person | Visit | Time (Europe/Paris) | Event | Widget | Attempt | Important detail |
| --- | --- | --- | --- | --- | --- | --- |
| P-101 | V-A | 30 Jun 23:58:00 | `form_open` | W1 |  | Outside the report window |
| P-101 | V-A | 1 Jul 00:02:00 | `form_send` | W1 | S1 | Valid server-confirmed send |
| P-202 | V-B | 12 Jul 10:05:00 | `form_open` | W2 |  | One observed open |
| P-202 | V-B | 12 Jul 10:08:00.000 | `form_send` | W2 | S2 | Valid server-confirmed send |
| P-202 | V-B | 12 Jul 10:08:00.120 | `form_send` | W2 | S3 | Same payload and response as S2 |
| anon-7 | V-C | 16 Jul 14:00:00 | `form_open` | W1 |  | Anonymous browser identifier |
| customer-92 | V-C | 16 Jul 14:03:00 | `form_send` | W1 | S4 | Login changed the person identifier |
| P-404 | V-D | 21 Jul 09:15:00 | `form_send` | W1 | S5 | Server event exists; client analytics consent was denied |
| P-505 | V-E | 28 Jul 11:00:00 | `form_open` | W3 |  | Component emitted the displayed widget ID |
| P-505 | V-E | 28 Jul 11:04:00 | `form_send` | W4 | S6 | Submit handler emitted a stale widget ID |

## Reproduction

The naive query first filters events to July, then searches for an earlier open with exact person, visit, and widget IDs. It sees six send rows, finds one match, and labels five rows "send without open."

The governed reproduction changes one thing at a time and records the row impact:

| Diagnostic step | Newly explained rows | Remaining unexplained | Interpretation |
| --- | ---: | ---: | --- |
| Naive July-only exact match | 1 matched | 5 | Starting point, not a conclusion |
| Add the 30-minute pre-window lookback | 1 | 4 | S1 had an open just before July |
| Deduplicate identical server responses within one second | 1 | 3 | S3 is a duplicate emission, not a second user submission |
| Bridge anonymous and logged-in IDs within the same visit | 1 | 2 | S4 lost its match at login |
| Reconcile consent coverage with the server log | 1 classified as unobservable | 1 | S5 cannot prove "no open" because the browser event was not collectable |
| Validate widget semantics against the component release | 1 | 0 | S6 used inconsistent widget IDs across open and send handlers |

The categories are mutually exclusive in the final reconciliation. Their counts sum to the five initially unmatched rows.

## Required instrumentation evidence

The analysis must record these conditional checks:

- `instrumentation_semantics`: confirm what `form_open` and `form_send` mean in the interface and server.
- `instrumentation_duplicates`: test retry, double-fire, and repeated-response signatures.
- `instrumentation_missing_events`: compare expected journey transitions with observed sequences.
- `instrumentation_consent_coverage`: show which client events were collectable under each consent state.
- `instrumentation_change_history`: align anomalies with releases, tag changes, and schema changes.
- `instrumentation_identity` when person- or journey-level matching depends on identity stitching.

## Decision-ready Analysis Brief

**Answer status:** Complete for the six synthetic rows; production prevalence still requires the same reconciliation over the full dataset.

**Executive answer:** Five sends appeared to lack an earlier open, but the event-level reproduction found five measurement or matching causes: a report-boundary omission, a duplicate send event, an identity change, asymmetric consent coverage, and inconsistent widget IDs. The data does not show five people submitting a form they never opened.

**What the evidence means:** The current KPI mixes product behaviour with collection and query behaviour. It should not be used as a UX problem rate until those categories are separated.

**Limitations and unknowns:** For consent-blocked client events, the data can establish that the open was unobservable, not whether it happened. The synthetic counts demonstrate the method, not a real production rate.

**Recommended next action:** implement a pre-window lookback, deduplicate server attempts, use a documented visit-level identity bridge, expose consent coverage, and fix the widget ID contract. Then rerun the metric and report each cause separately.

## Regression expectation

An agent using this skill should not stop at "the open is missing." It should reproduce the pairing logic, inspect raw rows on both sides of the reporting boundary, reconcile source and identity semantics, quantify each mutually exclusive cause, and state what the telemetry cannot know.
