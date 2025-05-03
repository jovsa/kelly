# Kelly Betting

> This is for learning/experimentation purposes.

## Setup Instructions

To create a virtual environment using [uv](https://github.com/astral-sh/uv) and install the requirements, run the following commands:

```bash
# Install uv if you don't have it
pip install uv

# Create a virtual environment with Python 3.11
uv venv --python 3.11 .venv

# Activate the virtual environment (macOS/Linux)
source .venv/bin/activate

# Install requirements
uv pip install -r requirements.txt
```

## Running Tests

To run all unittests with verbose output, use:

```bash
python -m pytest -v
```
