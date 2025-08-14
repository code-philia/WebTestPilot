Guidelines
- Each test case already assumes user is logged in and on home page of web application
- Each test case must be isolated (i.e., is not dependent of data from earlier test cases)
- Each test case must be atomic (i.e., one of create, read, update, delete)

Setup scripts
```
uv sync
source .venv/bin/activate
playwright install
```

Reference: https://playwright.dev/python/docs/codegen-intro
Start running codegen
```
playwright codegen https://demo.bookstackapp.com
```

Running tests
```
pytest --headed bookstack/book.py
pytest --headed bookstack/*

<!-- Speed up with tests in parallel -->
pytest -n 4 bookstack/*.py -v --tb=short
```

To run baselines:
uv venv .venv-pinata
source .venv-pinata/bin/activate
uv pip install -e ".[pinata]"
python baselines/evaluate.py pinata bookstack

uv venv .venv-webtestpilot
source .venv-webtestpilot/bin/activate
uv pip install -e ".[webtestpilot]"
python baselines/evaluate.py webtestpilot bookstack

uv venv .venv-naviqate
source .venv-naviqate/bin/activate
uv pip install -e ".[naviqate]"
python baselines/evaluate.py naviqate bookstack

uv venv .venv-pinata
source .venv-pinata/bin/activate
uv pip install -e ".[pinata]"
python baselines/evaluate.py lavague bookstack