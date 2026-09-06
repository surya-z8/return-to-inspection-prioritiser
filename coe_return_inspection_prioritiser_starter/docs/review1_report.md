# Review 1 Report — 35% Project Completion

## 1. Project title
**Return-To-Inspection Prioritiser Based Value Loss for Reusable-Packaging Network Collecting Containers Businesses**

## 2. Problem analysis
Returned reusable containers can wait before inspection. During waiting, high-value items and items with condition risk may lose resale value or become harder to recover. The prototype therefore prioritises inspection using product value, transit/wait time, condition hints and data availability.

## 3. Stakeholders
- Collection/returns operations team
- Inspection team
- Warehouse staff
- Reusable-packaging network manager
- Businesses returning containers

## 4. User/workflow map
Business creates return -> container travels -> return/transit/value/condition data captured -> prioritiser calculates score -> HIGH items move forward -> operator sees evidence -> missing sensor/location data triggers manual fallback and later reconciliation.

## 5. Labels and thresholds
- HIGH: score >= 70
- MEDIUM: 40–69
- LOW: < 40

These are initial prototype thresholds and should be validated with operations staff.

## 6. Scoring model
- Value-loss component: up to 35 points
- Delay component: up to 30 points
- Condition-risk component: up to 40 points
- Total capped at 100

## 7. Dataset
A synthetic dataset of 10 return records is included in `data/returns.csv`.

## 8. Edge/failure cases
1. Missing sensor data -> manual review/store-and-forward flag.
2. Missing location data -> manual review/store-and-forward flag.
3. Invalid product value -> safe fallback for scoring + manual review.
4. High-value delayed damaged return -> HIGH priority with evidence.

## 9. Baseline and experiment
Baseline: FIFO/oldest-return-first inspection.

Proposed: descending priority-score inspection.

Primary metric: estimated resale value preserved by inspecting risky/high-value returns earlier.

Secondary metrics: HIGH-priority waiting time, percentage inspected within target, false-positive rate, false-negative rate.

## 10. Prototype completed
- Problem definition
- Stakeholder/workflow map
- Synthetic dataset
- Explainable prioritisation logic
- API endpoint
- Browser dashboard
- Evidence for HIGH results
- Automated tests
- README
- Experiment plan

## 11. Next steps
- Validate thresholds with stakeholders.
- Expand the dataset.
- Add actual store-and-forward queue behaviour.
- Compare FIFO vs prioritised ordering quantitatively.
- Calibrate value-loss estimates using historical resale/inspection data.
- Maintain plan-change history.
