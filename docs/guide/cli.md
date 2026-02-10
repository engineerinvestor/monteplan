# CLI Reference

monteplan includes a command-line interface built with Click.

## Installation

The CLI is installed automatically with the package:

```bash
pip install monteplan
```

## Commands

### `monteplan run`

Run a Monte Carlo simulation.

```bash
monteplan run [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|---|---|---|---|
| `--config PATH` | File path | None | Path to JSON config file. Uses defaults if not provided. |
| `--output PATH` | File path | None | Path to write results JSON. |
| `--paths INT` | Integer | 5000 | Number of simulation paths. |
| `--seed INT` | Integer | 42 | Random seed. |

### Examples

```bash
# Run with defaults
monteplan run

# Custom path count and seed
monteplan run --paths 10000 --seed 123

# Load from config file
monteplan run --config my_plan.json

# Save results
monteplan run --config my_plan.json --output results.json --paths 10000 --seed 42
```

### Version

```bash
monteplan --version
```

## Config File Format

The `--config` file is a JSON document containing all four configuration objects:

```json
{
  "plan": { ... },
  "market": { ... },
  "policies": { ... },
  "sim_config": { ... }
}
```

Generate a config file programmatically:

```python
from monteplan.config.defaults import default_plan, default_market, default_policies, default_sim_config
from monteplan.io.serialize import dump_config

json_str = dump_config(default_plan(), default_market(), default_policies(), default_sim_config())
with open("my_plan.json", "w") as f:
    f.write(json_str)
```

Then use it:

```bash
monteplan run --config my_plan.json --output results.json
```

## Output Format

Console output shows the success probability and terminal wealth percentiles:

```
Running simulation: 5000 paths, seed=42
Plan: age 30 → 65 → 95

Success probability: 47.9%
Terminal wealth percentiles:
  p5: $0
  p25: $0
  p50: $234,567
  p75: $1,234,567
  p95: $4,567,890
```

When `--output` is specified, a JSON file is written with summary metrics.
