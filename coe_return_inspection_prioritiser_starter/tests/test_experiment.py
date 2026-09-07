from app.experiment import (
    estimated_value_preserved,
    run_experiment,
)


def test_value_preserved_decreases_with_waiting_time():
    record = {
        "product_value": "100",
        "condition_hint": "damaged",
    }

    immediate = estimated_value_preserved(record, 0)
    delayed = estimated_value_preserved(record, 5)

    assert immediate == 100
    assert delayed < immediate


def test_experiment_returns_both_strategies():
    records = [
        {
            "return_id": "R001",
            "return_request_date": "2026-09-01",
            "transit_days": "10",
            "product_value": "500",
            "condition_hint": "damaged",
            "sensor_available": "yes",
            "location_available": "yes",
        },
        {
            "return_id": "R002",
            "return_request_date": "2026-09-02",
            "transit_days": "2",
            "product_value": "100",
            "condition_hint": "good",
            "sensor_available": "yes",
            "location_available": "yes",
        },
    ]

    result = run_experiment(records)

    assert "fifo" in result
    assert "priority" in result
    assert "improvement" in result
    assert "improvement_percent" in result


def test_fifo_uses_oldest_return_first():
    records = [
        {
            "return_id": "NEW",
            "return_request_date": "2026-09-05",
            "product_value": "100",
            "condition_hint": "good",
        },
        {
            "return_id": "OLD",
            "return_request_date": "2026-09-01",
            "product_value": "100",
            "condition_hint": "good",
        },
    ]

    result = run_experiment(records)

    assert result["fifo"]["inspection_order"] == ["OLD", "NEW"]
