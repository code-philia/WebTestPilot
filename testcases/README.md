## Setup
```
uv sync
source .venv/bin/activate
playwright install
```

## Creating tests
Reference: https://playwright.dev/python/docs/codegen-intro
Start running codegen
```
playwright codegen https://demo.bookstackapp.com
```

## Running tests
```
pytest --headed bookstack/book.py
pytest --headed bookstack/*

<!-- Speed up with tests in parallel -->
pytest -n 4 bookstack/*.py -v --tb=short
```