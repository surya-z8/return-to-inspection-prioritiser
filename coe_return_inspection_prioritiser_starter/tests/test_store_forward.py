from app.store_forward import (
    enqueue_return,
    get_queued_returns,
    process_queue,
    queue_status,
)


def test_store_and_forward_queue():
    record = {
        "return_id": "TEST_QUEUE_001",
        "product_value": "500",
        "condition_hint": "wet",
    }

    enqueue_return(record)

    queued = get_queued_returns()

    assert any(
        item["return_id"] == "TEST_QUEUE_001"
        for item in queued
    )

    result = process_queue()

    assert "TEST_QUEUE_001" in result["processed_return_ids"]

    status = queue_status()

    assert status["queued"] == 0
    assert status["processed"] >= 1
    