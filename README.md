# WebTestPilot

<p align="left">
  <a href="https://arxiv.org/abs/2602.11724">
    <img src="https://img.shields.io/badge/arXiv-Paper-red.svg" alt="arXiv">
  </a>
    <a href="https://sites.google.com/view/webtestpilot">
    <img src="https://img.shields.io/badge/Project-Page-green.svg" alt="Project Page">
  </a>
</p>

This is the official repository for the paper *"WebTestPilot: Agentic End-to-End Web Testing against Natural Language Specification by Inferring Oracles with Symbolized GUI Elements"*.

**TL;DR:** WebTestPilot turns what a multimodal agent sees on the web into symbolic representations that can be asserted in automated end-to-end testing.

<a href="http://www.youtube.com/watch?feature=player_embedded&v=hJhcSvN2KwU" target="_blank">
 <img src="http://img.youtube.com/vi/hJhcSvN2KwU/mqdefault.jpg" alt="Watch the video" width="360" border="10" />
</a>

## 📂 Structure

```graphql
/baselines    # Implementations of baselines (LaVague, NaviQAte, PinATA) and test runners (baselines + WebTestPilot)
/experiments  # Scripts for running experiments (RQ1–RQ4) in the paper
/benchmark    # Test cases and their injected bugs in the benchmark
/webapps      # Containerized deployment scripts for web applications in the benchmark
/webtestpilot # Implementation of WebTestPilot 
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

## 🖥 Running WebTestPilot

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

## 📝 Citation

If you find WebTestPilot useful for your research, please consider citing the following work:

```bibtex
@article{teoh2026webtestpilot,
  title   = {WebTestPilot: Agentic End-to-End Web Testing against Natural Language Specification by Inferring Oracles with Symbolized GUI Elements},
  author  = {Teoh, Xiwen and Lin, Yun and Nguyen, Duc-Minh and Ren, Ruofei and Zhang, Wenjie and Dong, Jin Song},
  journal = {Proceedings of the ACM on Software Engineering},
  volume  = {3},
  number  = {FSE},
  article = {FSE087},
  year    = {2026},
  month   = {7},
  doi     = {10.1145/3797115}
}
```
