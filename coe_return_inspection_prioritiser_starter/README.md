# Return-to-Inspection Prioritiser

A working prototype for prioritising returned reusable-packaging containers for inspection based on expected resale value loss, transit delay, product-condition risk, and data availability.

## Problem

Returned reusable containers can lose resale value when inspection is delayed. The system prioritises returns that have higher potential value loss and condition risk so that inspection teams can act earlier.

## Key Features

- Explainable HIGH / MEDIUM / LOW priority scoring
- Product value and transit-delay based prioritisation
- Condition-risk scoring using condition hints
- Non-linear exponential value-decay model
- FIFO vs Priority inspection experiment
- Resale value preservation measurement
- False Positive / False Negative error analysis
- Precision and Recall measurement
- Evidence for every high-priority output
- Sensor/location availability handling
- Manual review fallback for missing data
- SQLite store-and-forward queue for offline network scenarios
- Flask REST API
- Browser dashboard
- Automated unit and edge-case tests
- Synthetic return dataset
- Auditable project plan history

## Value Decay Model

The prototype models resale-value loss using an exponential decay function instead of a simple linear penalty.

The estimated preserved value is calculated from:

`preserved_value = product_value × e^(-k × inspection_wait_days)`

The decay constant `k` is derived from the condition-specific daily loss rate.

This allows value loss to compound over longer inspection delays.

## Experiment

The prototype compares two inspection strategies:

### Baseline
FIFO (First-In-First-Out) inspection based on return request date.

### Proposed Approach
Priority-based inspection using the calculated priority score.

The experiment measures:

- Total value preserved by FIFO
- Total value preserved by priority inspection
- Absolute value improvement
- Percentage improvement

Current experiment result on the synthetic dataset:

- FIFO value preserved: **$2454.98**
- Priority value preserved: **$2475.68**
- Value improvement: **$20.70**
- Improvement: **0.84%**

## Error Analysis

Completed inspection outcomes are compared against predicted HIGH-priority returns.

Current evaluation:

- True Positive: **5**
- False Positive: **0**
- False Negative: **1**
- True Negative: **3**
- Pending outcomes excluded: **1**
- Precision: **100%**
- Recall: **83.33%**

Pending inspection outcomes are excluded because they do not provide final ground-truth labels.

## Store-and-Forward

When network or location/sensor data is unavailable, the system supports manual fallback and local storage.

A SQLite queue stores return records locally while they are waiting to be forwarded.

Queue operations include:

- Enqueue a return
- Read queued returns
- Process queued returns after connectivity is restored
- Check queued and processed record counts

This provides a simulation of offline/store-and-forward behaviour.

## Edge Cases Tested

The prototype was tested for:

1. Sensor and location data unavailable
   - Manual review is enabled.
   - Store-and-forward/manual fallback evidence is generated.

2. Invalid product value and transit time
   - Invalid fields are detected.
   - Manual review is required instead of crashing.

3. Offline/store-and-forward scenario
   - Return data is stored in the local SQLite queue.
   - Queued records can be processed after recovery.

## Testing

Automated tests cover scoring, experiment calculations, value decay, and store-and-forward behaviour.

Current test result:

`8 passed`

Run tests with:

```bash
pytest -q