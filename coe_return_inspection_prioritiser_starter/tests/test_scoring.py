import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from scoring import score_return, prioritise

def test_high_value_delayed_damaged_return_is_high():
    score,label,evidence,manual=score_return({
        "product_value":600,"transit_days":15,"condition_hint":"damaged",
        "sensor_available":"yes","location_available":"yes"})
    assert label=="HIGH"
    assert score>=70
    assert len(evidence)>=2
    assert manual is False

def test_missing_sensor_triggers_manual_fallback():
    score,label,evidence,manual=score_return({
        "product_value":100,"transit_days":3,"condition_hint":"good",
        "sensor_available":"no","location_available":"yes"})
    assert manual is True
    assert any("fallback" in e.lower() for e in evidence)

def test_invalid_value_is_safe():
    score,label,evidence,manual=score_return({
        "product_value":"not-a-number","transit_days":3,"condition_hint":"good",
        "sensor_available":"yes","location_available":"yes"})
    assert score>=0
    assert manual is True

def test_prioritise_orders_highest_first():
    result=prioritise([
        {"return_id":"A","product_value":20,"transit_days":1,"condition_hint":"excellent"},
        {"return_id":"B","product_value":500,"transit_days":12,"condition_hint":"damaged"}])
    assert result[0]["return_id"]=="B"
