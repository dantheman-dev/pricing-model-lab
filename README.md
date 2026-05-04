# Pricing Model Lab

Pricing Model Lab is a synthetic Python project for comparing observed values against model-derived values and flagging deviations for review.

The goal is to demonstrate a simple decision-support workflow:
- load structured data
- validate inputs
- calculate deviations
- apply review thresholds
- output a clean, ranked result

## Example Output

| item_id | observed_value | model_value | deviation | review_flag |
|--------|----------------|-------------|------------|-------------|
| A-104  | 102.50         | 98.20       | 4.38%      | Review      |
| A-219  | 75.00          | 74.10       | 1.21%      | OK          |

## What This Demonstrates

- Python data pipelines
- Data validation
- Pricing / comparative analysis
- Decision-support workflows
- Clean, reproducible outputs

## Disclaimer

All data in this project is synthetic and for demonstration purposes only.
