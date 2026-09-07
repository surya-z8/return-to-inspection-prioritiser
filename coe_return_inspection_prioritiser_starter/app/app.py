from flask import Flask, jsonify, render_template, request
import csv
from pathlib import Path
from app.scoring import prioritise
from app.experiment import run_experiment
app = Flask(__name__)
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "returns.csv"

def load_records():
    with open(DATA, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/returns")
def returns():
    return jsonify(prioritise(load_records()))

@app.post("/api/score")
def score_one():
    return jsonify(prioritise([request.get_json(force=True)])[0])

@app.get("/api/experiment")
def experiment():
    return jsonify(run_experiment(load_records()))

if __name__ == "__main__":
    app.run(debug=True)
