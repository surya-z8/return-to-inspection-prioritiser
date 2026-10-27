ipo# Return-to-Inspection Prioritiser

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
```
API Documentation

The application uses Flask to provide REST API endpoints for return prioritisation and experiment evaluation.

1. GET /api/returns

Purpose: Retrieves all return records and their calculated priority information.

Response: A JSON array containing return details, priority scores, priority labels, evidence, and manual-review indicators.

2. POST /api/returns

Purpose: Accepts a new return record, validates the presence of required fields, saves the record to the CSV dataset, and returns its calculated priority.

Required fields:

* return_id
* return_request_date
* transit_days
* product_value
* condition_hint
* inspection_outcome
* sensor_available
* location_available

Success response: HTTP 201 Created, with the scored return record.

Error response: HTTP 400 Bad Request if a required field is missing.

3. POST /api/score

Purpose: Calculates the priority of a single return record without saving it to the dataset.

Response: A JSON object containing the calculated priority and supporting evidence.

4. GET /api/experiment

Purpose: Runs the FIFO-versus-priority experiment and returns estimated value preservation and error-analysis metrics.

Response includes:

* FIFO value preserved
* Priority value preserved
* Absolute and percentage improvement
* True positives, false positives, false negatives, and true negatives
* Precision and recall

Data Storage and Schema

Return Dataset — data/returns.csv

The application stores return records in a CSV file.

Field	Description
return_id	Unique identifier for the return
return_request_date	Date the return was requested
transit_days	Transit or waiting duration in days
product_value	Estimated value of the returned container
condition_hint	Reported condition of the container
inspection_outcome	Inspection result or pending status
sensor_available	Indicates whether sensor data is available
location_available	Indicates whether location data is available

Offline Queue — data/store_forward.db

The SQLite database contains a return_queue table.

Column	Description
id	Auto-incrementing internal identifier
return_id	Unique return identifier
payload	JSON representation of the return record
status	Queue state: queued or processed

The queue supports local storage, retrieval, processing, and status checks through app/store_forward.py. These queue operations are currently implemented as Python functions, not Flask API endpoints.

Unit Testing and Error Boundaries

The project uses pytest for automated testing.

The current test suite covers:

* Priority scoring behaviour
* Experiment calculations and value-decay estimation
* FIFO and priority-based inspection comparisons
* SQLite store-and-forward queue operations

The most recent recorded test run completed with 8 passing tests.

Error Handling

* Missing required fields in POST /api/returns produce an HTTP 400 response.
* Invalid product-value or transit-time inputs are handled by the scoring logic with manual-review indicators.
* Unavailable sensor or location information triggers fallback evidence and manual review.
* Offline return records can be placed in the SQLite queue for later processing.

Current Limitations

The current prototype uses a synthetic dataset. Value-decay rates and prioritisation thresholds require validation using representative operational data. Additional tests should cover malformed JSON, duplicate return identifiers, CSV write failures, and database errors.
