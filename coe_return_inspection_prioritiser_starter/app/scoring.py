from flask import request

HIGH = 70
MEDIUM = 40

def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, float(x)))

def score_return(r):
    evidence = []
    manual_review = False

    try:
        value = float(r.get("product_value", 0))
    except (TypeError, ValueError):
        value = 0
        manual_review = True
        evidence.append("Invalid product value; manual review required.")

    try:
        transit = float(r.get("transit_days", 0))
    except (TypeError, ValueError):
        transit = 0
        manual_review = True
        evidence.append("Invalid transit time; manual review required.")

    condition = str(r.get("condition_hint", "unknown")).lower()
    sensor_ok = str(r.get("sensor_available", "yes")).lower() in {"yes", "true", "1"}
    location_ok = str(r.get("location_available", "yes")).lower() in {"yes", "true", "1"}

    value_component = clamp((value / 500.0) * 35.0)
    time_component = clamp((transit / 14.0) * 30.0)

    condition_weights = {
        "excellent": 5,
        "good": 10,
        "unknown": 20,
        "minor_damage": 25,
        "damaged": 35,
        "wet": 38,
        "contaminated": 40,
    }
    condition_component = condition_weights.get(condition, 20)

    if value >= 350:
        evidence.append(f"High product value (${value:.0f}) increases potential resale-value loss.")
    if transit >= 7:
        evidence.append(f"{transit:.0f} transit/wait days indicates inspection delay risk.")
    if condition in {"damaged", "wet", "contaminated", "minor_damage"}:
        evidence.append(f"Condition hint '{condition}' indicates elevated condition risk.")
    elif condition == "unknown":
        evidence.append("Condition is unknown, so conservative risk is applied.")

    if not sensor_ok or not location_ok:
        manual_review = True
        evidence.append("Sensor/location data unavailable: store-and-forward/manual fallback enabled.")

    score = clamp(value_component + time_component + condition_component)

    if score >= HIGH:
        label = "HIGH"
    elif score >= MEDIUM:
        label = "MEDIUM"
    else:
        label = "LOW"

    return round(score, 1), label, evidence, manual_review

def prioritise(records):
    output = []
    for r in records:
        score, label, evidence, manual_review = score_return(r)
        item = dict(r)
        item.update({
            "priority_score": score,
            "priority": label,
            "evidence": evidence,
            "manual_review": manual_review,
        })
        output.append(item)
    return sorted(output, key=lambda x: x["priority_score"], reverse=True)
