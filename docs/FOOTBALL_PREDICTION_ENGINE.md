# APIP Football Prediction Engine — v1

## Purpose
Record transparent football 1X2 predictions and later compare them with final scores. Version 1 has no real-money betting, bookmaker integration, paid API, automatic data feed, or claim of a proven betting edge.

## Model
The baseline calculates independent Poisson goal distributions from **user-supplied expected-goals assumptions**. It derives home-win, draw, and away-win probabilities. This model has not been trained or validated on historical match data. Output quality depends on the assumptions supplied.

## Create a prediction
From the repository root:

```cmd
python scripts\football_prediction.py predict --home "Arsenal" --away "Chelsea" --home-xg 1.6 --away-xg 1.0 --kickoff-utc "2026-10-25T16:30:00Z" --notes "Example assumptions; replace with documented estimates"
```

Copy the printed prediction ID. The example is only a software demonstration, not a real forecast.

Each prediction is appended to `data/football-predictions.csv` with a UTC creation time, model version, probabilities, and OPEN status. Preserve the original prediction so evaluation remains honest.

## Resolve a prediction
After the match is finished, use the ID printed when the prediction was created:

```cmd
python scripts\football_prediction.py resolve --id PASTE_ID_HERE --home-goals 2 --away-goals 1
```

Replace the ID and score with actual values from a source you trust. A resolved row cannot be resolved a second time.

## Test
```cmd
python -m unittest discover -s tests -v
```

## Honest evaluation
Do not judge the model by hit rate alone. A future evaluation should use a dated, untouched sample and report accuracy, multiclass Brier score or log loss, calibration, sample size, and a baseline comparison. Until that evaluation exists, do not describe the model as profitable or superior to bookmakers.

## Zero-cost and safety constraints
- Python standard library only; no external packages.
- No API keys, secrets, payment data, or personal banking information in this repository.
- No real-money betting or automated wagering.
- Any future data provider, paid model, or spending requires explicit owner approval.
