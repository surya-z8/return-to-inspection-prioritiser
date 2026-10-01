import math
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
    condition = str(
        record.get("condition_hint", "unknown")
    ).strip().lower()

    return CONDITION_LOSS_RATE.get(condition, 0.04)


def decay_constant(record):
    """
    Convert the one-day loss rate into an exponential
    decay constant.

    This keeps the original one-day assumption while
    modelling compounding value loss over longer waits.
    """
    rate = loss_rate(record)

    return -math.log(1 - rate)


def estimated_value_preserved(record, inspection_wait_days):
    try:
        value = float(record.get("product_value", 0))
    except (TypeError, ValueError):
        value = 0

    k = decay_constant(record)

    preserved = value * math.exp(
        -k * inspection_wait_days
    )

    return round(max(0, preserved), 2)


def simulate_inspection(records):
    results = []

    for wait_days, record in enumerate(records):
        item = dict(record)

        item["inspection_wait_days"] = wait_days

        item["estimated_value_preserved"] = (
            estimated_value_preserved(
                item,
                wait_days
            )
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
        sum(
            item["estimated_value_preserved"]
            for item in fifo_results
        ),
        2
    )

    priority_preserved = round(
        sum(
            item["estimated_value_preserved"]
            for item in priority_results
        ),
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
                item["return_id"]
                for item in fifo_results
            ],
        },
        "priority": {
            "total_value_preserved": priority_preserved,
            "inspection_order": [
                item["return_id"]
                for item in priority_results
            ],
        },
        "improvement": improvement,
        "improvement_percent": improvement_percent,
    }
def calculate_error_analysis(records):
    """
    Compare predicted HIGH priority against the
    ground-truth inspection outcome.

    Positive outcome = repair, clean, or discard.
    Pass = negative outcome.
    Pending outcomes are excluded because they are
    not final ground truth.
    """

    positive_outcomes = {"repair", "clean", "discard"}

    predicted = prioritise(records)

    tp = 0
    fp = 0
    fn = 0
    tn = 0
    excluded = 0

    for item in predicted:
        outcome = str(
            item.get("inspection_outcome", "")
        ).strip().lower()

        predicted_positive = (
            item.get("priority") == "HIGH"
        )

        if outcome == "pending":
            excluded += 1
            continue

        actual_positive = outcome in positive_outcomes

        if predicted_positive and actual_positive:
            tp += 1

        elif predicted_positive and not actual_positive:
            fp += 1

        elif not predicted_positive and actual_positive:
            fn += 1

        else:
            tn += 1

    total_predicted_positive = tp + fp
    total_actual_positive = tp + fn

    precision = (
        round(tp / total_predicted_positive * 100, 2)
        if total_predicted_positive > 0
        else 0
    )

    recall = (
        round(tp / total_actual_positive * 100, 2)
        if total_actual_positive > 0
        else 0
    )

    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "excluded_pending": excluded,
        "precision_percent": precision,
        "recall_percent": recall,
    }