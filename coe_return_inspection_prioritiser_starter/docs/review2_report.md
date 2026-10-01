# Review 2 Report — 70% Project Completion

## 1. Project Title

**Return-To-Inspection Prioritiser Based Value Loss for Reusable-Packaging Network Collecting Containers Businesses**

## 2. Review 2 Objective

The second development phase focused on improving the reliability, measurable evaluation, offline handling, and explainability of the return-to-inspection prioritisation prototype.

The main improvements were:

- Non-linear resale-value decay modelling
- Quantitative FIFO vs Priority evaluation
- False Positive and False Negative analysis
- Precision and Recall measurement
- SQLite store-and-forward queue
- Manual fallback for unavailable sensor/location data
- Edge-case validation
- Automated store-and-forward testing
- Improved experiment dashboard
- Updated project documentation

## 3. Improved Value-Loss Model

The initial prototype used a simple heuristic approach for value-loss estimation.

For Review 2, the value-loss model was improved using exponential decay.

The preserved value is estimated using:

`preserved_value = product_value × e^(-k × inspection_wait_days)`

The decay constant is derived from a condition-specific daily loss rate.

Different condition hints use different loss rates, including:

- excellent
- good
- unknown
- minor_damage
- damaged
- wet
- contaminated

This provides a non-linear model where value loss compounds as inspection is delayed.

## 4. Baseline vs Proposed Approach

### Baseline

FIFO (First-In-First-Out) inspection is used as the baseline.

Returns are inspected according to return request date.

### Proposed Approach

The proposed system calculates a priority score using:

- Product value
- Transit/wait time
- Condition risk
- Sensor/location availability

Returns are then ordered from highest to lowest priority.

## 5. Quantitative Experiment

The experiment compares the estimated resale value preserved under FIFO and priority-based inspection.

### Measured result

- FIFO value preserved: **$2454.98**
- Priority value preserved: **$2475.68**
- Absolute improvement: **$20.70**
- Percentage improvement: **0.84%**

The result demonstrates the measurable difference between the baseline FIFO strategy and the proposed prioritisation strategy on the current synthetic dataset.

The dataset is synthetic, so this result should be treated as a prototype measurement rather than a production performance claim.

## 6. Error Analysis

The prototype now compares predicted HIGH-priority returns against completed inspection outcomes.

The ground-truth positive outcomes are:

- repair
- clean
- discard

The negative outcome is:

- pass

Pending outcomes are excluded because they do not represent completed ground truth.

### Current results

- True Positive: **5**
- False Positive: **0**
- False Negative: **1**
- True Negative: **3**
- Pending excluded: **1**
- Precision: **100%**
- Recall: **83.33%**

This analysis explicitly identifies both false positives and false negatives.

## 7. Store-and-Forward Implementation

The prototype now includes a local SQLite store-and-forward queue.

When connectivity is unavailable, return records can be stored locally instead of being lost.

The queue supports:

1. Initialising the local SQLite queue
2. Enqueuing return records
3. Reading queued returns
4. Processing queued returns after recovery
5. Reporting queued and processed record counts

The SQLite database is treated as a local temporary queue and is excluded from the Git repository.

## 8. Manual Fallback

The prioritisation system handles unavailable operational data.

When both sensor and location information are unavailable, the system:

- Continues generating a priority score
- Produces an evidence message
- Enables `manual_review`
- Indicates store-and-forward/manual fallback

Example edge-case result:

- Return ID: `EDGE001`
- Sensor available: `no`
- Location available: `no`
- Priority: `HIGH`
- Priority score: `91.4`
- Manual review: `True`

Evidence explicitly indicates that store-and-forward/manual fallback is enabled.

## 9. Invalid Input Handling

The system was tested with invalid product-value and transit-time inputs.

Example:

- Product value: `xyz`
- Transit days: `abc`

The system did not crash.

Instead, it:

- Detected the invalid product value
- Detected the invalid transit time
- Added manual-review evidence
- Set `manual_review` to `True`
- Returned a safe priority result

This provides a failure-safe behaviour for malformed input data.

## 10. Automated Testing

Automated tests cover:

- Value-decay behaviour
- FIFO ordering
- Priority experiment output
- Scoring behaviour
- Store-and-forward queue behaviour

Current test result:

**8 passed in 0.11 seconds**

The store-and-forward test verifies that:

- A return can be queued
- The queued return can be retrieved
- The queued return can be processed
- Queue status changes after processing

## 11. Dashboard Improvements

The browser dashboard was enhanced to display:

- FIFO value preserved
- Priority value preserved
- Value improvement
- Improvement percentage
- FIFO inspection order
- Priority inspection order
- True Positive
- False Positive
- False Negative
- True Negative
- Precision
- Recall
- Pending outcomes excluded

This makes the evaluation results visible to the intended operational stakeholder.

## 12. Edge and Failure Cases

The following cases have been tested:

### Case 1 — Sensor and Location Unavailable

The system enables manual review and provides fallback evidence.

### Case 2 — Invalid Input

Invalid product value and transit time are detected without crashing the application.

### Case 3 — Offline Store-and-Forward

Return data is stored in the local SQLite queue and can be processed after recovery.

These cases demonstrate that the prototype has defined behaviour beyond the normal successful input path.

## 13. Evidence and Explainability

High-priority results include evidence explaining why the return received a high score.

Evidence can reference:

- High product value
- Long transit/wait duration
- Condition risk
- Missing sensor/location information

This allows an operator to understand the reason behind prioritisation rather than receiving only a numeric score.

## 14. Current Prototype Architecture

```text
Return Request
      |
      v
Input Data
      |
      +---- Product Value
      +---- Transit Days
      +---- Condition Hint
      +---- Sensor Availability
      +---- Location Availability
      |
      v
Priority Scoring
      |
      +---- Priority Score
      +---- HIGH / MEDIUM / LOW
      +---- Evidence
      +---- Manual Review Flag
      |
      v
Inspection Priority Queue
      |
      +---- Normal Network
      |
      +---- Offline -> SQLite Store-and-Forward