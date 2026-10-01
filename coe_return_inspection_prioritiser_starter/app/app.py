from flask import Flask, jsonify, render_template, request
import csv
from pathlib import Path

from app.scoring import prioritise
from app.experiment import run_experiment, calculate_error_analysis


app = Flask(__name__)

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "returns.csv"


def load_records():
    with open(DATA, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

<<<<<<< HEAD
def save_record(record):
    fieldnames = [
        "return_id",
        "return_request_date",
        "transit_days",
        "product_value",
        "condition_hint",
        "inspection_outcome",
        "sensor_available",
        "location_available",
    ]

    with open(DATA, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(record)
        
=======
>>>>>>> 03099ff (Improve value decay and add error analysis)

@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/returns")
def returns():
    return jsonify(prioritise(load_records()))

@app.post("/api/returns")
def add_return():
    record = request.get_json(force=True)

    required_fields = [
        "return_id",
        "return_request_date",
        "transit_days",
        "product_value",
        "condition_hint",
        "inspection_outcome",
        "sensor_available",
        "location_available",
    ]

    for field in required_fields:
        if field not in record:
            return jsonify({"error": f"Missing field: {field}"}), 400

    save_record(record)

    scored = prioritise([record])[0]

    return jsonify(scored), 201

@app.post("/api/score")
def score_one():
    return jsonify(
        prioritise(
            [request.get_json(force=True)]
        )[0]
    )


@app.get("/api/experiment")
def experiment():
    records = load_records()

    result = run_experiment(records)

    result["error_analysis"] = calculate_error_analysis(
        records
    )

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)