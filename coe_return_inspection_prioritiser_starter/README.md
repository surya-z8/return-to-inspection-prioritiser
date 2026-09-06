# Return-to-Inspection Prioritiser

A working prototype for prioritising returned reusable-packaging containers for inspection based on expected resale value loss and product-condition risk.

## Run
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app/app.py

Open http://127.0.0.1:5000

## Test
pytest -q

## Included
- Explainable priority scoring
- HIGH/MEDIUM/LOW thresholds
- Evidence for high-priority outputs
- Store-and-forward/manual fallback flag
- Synthetic dataset
- Flask API and browser dashboard
- Automated edge-case tests
- Phase 1 report draft
