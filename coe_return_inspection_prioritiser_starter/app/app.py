from flask import Flask, jsonify, render_template, request
import csv
from pathlib import Path

from app.scoring import prioritise
from app.experiment import run_experiment, calculate_error_analysis


# Initialise the Flask application.
app = Flask(__name__)

# Build absolute paths so the application can locate the dataset
# regardless of the directory from which the program is started.
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "returns.csv"


def load_records():
    """Load all return records from the CSV dataset."""
    # DictReader converts each CSV row into a dictionary using column names.
    with open(DATA, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_record(record):
    """Append a new return record to the CSV dataset."""

    # Keep the field names consistent with the existing dataset schema.
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

    # Append the record without overwriting existing return records.
    with open(DATA, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(record)


@app.get("/")
def index():
    """Display the main application dashboard."""
    return render_template("index.html")


@app.get("/api/returns")
def returns():
    """Return all records with their calculated priority information."""
    # Load the dataset, calculate priorities, and return the results as JSON.
    return jsonify(prioritise(load_records()))


@app.post("/api/returns")
def add_return():
    """Validate and save a return record, then return its priority score."""
    # Read the incoming JSON request body as a Python object.
    record = request.get_json(force=True)

    # These fields must be present before the record can be saved.
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

    # Return HTTP 400 if any required field is missing.
    for field in required_fields:
        if field not in record:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Persist the submitted record in the CSV dataset.
    save_record(record)

    # Calculate the priority score for the newly submitted record.
    scored = prioritise([record])[0]

    # HTTP 201 indicates that the record was created successfully.
    return jsonify(scored), 201


@app.post("/api/score")
def score_one():
    """Calculate the priority of one record without saving it."""
    # Score the submitted JSON record and return the result as JSON.
    return jsonify(
        prioritise(
            [request.get_json(force=True)]
        )[0]
    )


@app.get("/api/experiment")
def experiment():
    """Run the inspection-priority experiment and return its metrics."""
    # Load records used to compare FIFO and priority-based inspection.
    records = load_records()

    # Calculate the experiment results, including estimated value preserved.
    result = run_experiment(records)

    # Add error-analysis metrics to help evaluate prioritisation performance.
    result["error_analysis"] = calculate_error_analysis(
        records
    )

    # Return the combined experiment results as JSON.
    return jsonify(result)


if __name__ == "__main__":
    # Start the Flask development server when this file runs directly.
    app.run(debug=True)