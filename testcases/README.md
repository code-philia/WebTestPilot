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
