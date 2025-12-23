# Experiments Directory

This directory contains experiment intent definitions for TFC-0003 standardized runs.

Experiments are defined as Python modules that can be executed with:
```bash
python tools/run.py --experiment experiments/<experiment-name>.py
```

Each experiment should specify datasets, models, and training configurations.