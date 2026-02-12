# WebTestPilot

This is the official repository for the paper *"WebTestPilot: Agentic End-to-End Web Testing against Natural Language Specification by Inferring Oracles with Symbolized GUI Elements"*.

WebTestPilot is an agentic framework for automated web testing that leverages natural language specifications, GUI element grounding, and inference of oracles.

## 📂 Structure

```graphql
/baselines        # Implementations of baselines (LaVague, NaviQAte, PinATA) and their test runners
/experiments      # Scripts for running experiments (RQ1–RQ4) from the paper
/benchmark        # Benchmark test cases and injected bugs used in experiments
/webapps          # Containerized deployment and seeding scripts for target web applications
/webtestpilot     # WebTestPilot implementation
```

## ⚙️ Setup

1. **Clone and initialize** 

    Clone the repository and run the setup script. It will check for required tools (`uv`, `docker`, `docker-compose`) and guide you through module setup step-by-step. You will need to confirm each step interactively.
   
    ```bash
    ./setup.sh
    ```

2. **Deploy the GUI grounding model** 
    
    WebTestPilot uses `inclusionAI/UI-Venus-Ground-7B` for locating GUI elements. To deploy the model, you need to install and configure [vLLM](https://docs.vllm.ai/en/latest/getting_started/quickstart/) and run the following command:

    ```bash
    HF_HOME=$(HF_HOME) \
    vllm serve inclusionAI/UI-Venus-Ground-7B \
    --max_model_len 4K \
    --max_num_seqs 8 \
    --trust-remote-code \
    --limit-mm-per-prompt '{"image": 1, "video": 0}'
    ```

    This will start a local server exposing the GUI grounding model.

3. **Configure environment variables** 

    Copy the `.env.example` file and update variables as needed:

    ```bash
    cp .env.example .env
    ```

    Required variables:
    - `OPENAI_API_KEY`: used by baselines and WebTestPilot
    - `GUI_GROUNDING_MODEL_BASE_URL`: used by WebTestPilot
    - `LOCAL_MODEL_BASE_URL`: used in experiments RQ3 and RQ4

## 🚀 Running Experiments

Go to `./experiments` folder and follow the `README.md` instructions provided in each section.

## 🖥 Running WebTestPilot Standalone

You can run WebTestPilot outside of experiments by installing it as an editable package:

```bash
pip install -e ./webtestpilot
uv pip install -e ./webtestpilot
```

Minimal example:

```python
from webtestpilot import WebTestPilot, Config, BugReport, Session, Step
from playwright.sync_api import sync_playwright

# Hook to handle bug reports
def hook(report: BugReport):
    print("A bug was reported:", report)

# Define the steps to test
steps = [
    Step(condition="", action="From the dashboard click 'Page Template' link", expectation="Page contains title 'Page Template'"),
    Step(condition="", action="Click 'Add Comment'", expectation="A WYSIWYG comment editor is open"),
    # ...
]

# Launch browser
playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=True)
page = browser.new_page()

# Load configuration
config = Config.load("path/to/config.yaml")

# Create a session
session = Session(page, config)

# Run WebTestPilot
WebTestPilot.run(session, steps, assertion=True, hooks=[hook])
```