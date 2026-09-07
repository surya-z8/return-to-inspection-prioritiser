from app.scoring import prioritise

CONDITION_LOSS_RATE = {
    "excellent": 0.01,
    "good": 0.02,
    "unknown": 0.04,
    "minor_damage": 0.05,
    "damaged": 0.07,
    "wet": 0.08,
    "contaminated": 0.10,
}


def loss_rate(record):
    condition = str(record.get("condition_hint", "unknown")).strip().lower()
    return CONDITION_LOSS_RATE.get(condition, 0.04)


def estimated_value_preserved(record, inspection_wait_days):
    try:
        value = float(record.get("product_value", 0))
    except (TypeError, ValueError):
        value = 0

    rate = loss_rate(record)

    estimated_loss = value * rate * inspection_wait_days
    preserved = max(0, value - estimated_loss)

    return round(preserved, 2)


def simulate_inspection(records):
    results = []

    for wait_days, record in enumerate(records):
        item = dict(record)
        item["inspection_wait_days"] = wait_days
        item["estimated_value_preserved"] = estimated_value_preserved(
            item, wait_days
        )
        results.append(item)

    return results


def run_experiment(records):
    # Baseline: inspect oldest returns first (FIFO)
    fifo_order = sorted(
        records,
        key=lambda r: r.get("return_request_date", "")
    )

    # Proposed approach: inspect highest-priority returns first
    priority_order = prioritise(records)

    fifo_results = simulate_inspection(fifo_order)
    priority_results = simulate_inspection(priority_order)

    fifo_preserved = round(
        sum(item["estimated_value_preserved"] for item in fifo_results),
        2
    )

    priority_preserved = round(
        sum(item["estimated_value_preserved"] for item in priority_results),
        2
    )

    improvement = round(
        priority_preserved - fifo_preserved,
        2
    )

    if fifo_preserved > 0:
        improvement_percent = round(
            (improvement / fifo_preserved) * 100,
            2
        )
    else:
        improvement_percent = 0

    return {
        "fifo": {
            "total_value_preserved": fifo_preserved,
            "inspection_order": [
                item["return_id"] for item in fifo_results
            ],
        },
        "priority": {
            "total_value_preserved": priority_preserved,
            "inspection_order": [
                item["return_id"] for item in priority_results
            ],
        },
        "improvement": improvement,
        "improvement_percent": improvement_percent,
    }
