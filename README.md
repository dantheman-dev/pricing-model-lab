# pricing-model-lab

Python pricing analysis lab for comparing model-derived values, observed values, and deviation thresholds for decision support workflows.

## Features

- Load a CSV with columns: `item_id`, `observed_value`, `model_value`
- Validate inputs (numeric checks, missing-value detection)
- Calculate relative deviation: `(observed_value - model_value) / model_value`
- Add a `review_flag` column based on a configurable threshold (default **3%**)
- Output a clean CSV sorted by absolute deviation (largest first)
- CLI interface via `argparse`

## Project Structure

```
pricing-model-lab/
├── data/
│   └── sample_data.csv        # Synthetic sample dataset
├── pricing_model_lab/
│   ├── __init__.py
│   ├── processor.py           # Core pipeline logic
│   └── cli.py                 # Command-line interface
├── tests/
│   └── test_processor.py      # pytest tests
├── pyproject.toml
└── requirements.txt
```

## Installation

```bash
pip install -e .
```

## Usage

### Command Line

```bash
pricing-model-lab INPUT_CSV OUTPUT_CSV [--threshold THRESHOLD]
```

| Argument | Description |
|---|---|
| `INPUT_CSV` | Path to input CSV (columns: `item_id`, `observed_value`, `model_value`) |
| `OUTPUT_CSV` | Path for the processed output CSV |
| `--threshold` | Absolute deviation threshold for the review flag (default: `0.03` → 3%) |

**Example:**

```bash
pricing-model-lab data/sample_data.csv output.csv --threshold 0.05
```

### Python API

```python
from pricing_model_lab.processor import process

result = process("data/sample_data.csv", "output.csv", threshold=0.03)
print(result.head())
```

## Running Tests

```bash
pytest
```

