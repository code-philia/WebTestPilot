# WebTestPilot

<p align="left">
  <a href="https://arxiv.org/abs/2602.11724">
    <img src="https://img.shields.io/badge/arXiv-Paper-red.svg" alt="arXiv">
  </a>
  <a href="https://sites.google.com/view/webtestpilot">
    <img src="https://img.shields.io/badge/Project-Page-green.svg" alt="Project Page">
  </a>
  <a href="./examples">
    <img src="https://img.shields.io/badge/Examples-Step%20by%20Step-blue.svg" alt="Examples">
  </a>
</p>

This is the official repository for the paper *"WebTestPilot: Agentic End-to-End Web Testing against Natural Language Specification by Inferring Oracles with Symbolized GUI Elements"*.

**TL;DR:** WebTestPilot converts what a multimodal agent sees on the web into symbolic representations that can be asserted in automated end-to-end tests.

**New here?** Start with [`examples/`](./examples) for step-by-step executions with screenshots, traces, and bug demonstrations.

<a href="http://www.youtube.com/watch?feature=player_embedded&v=hJhcSvN2KwU" target="_blank">
 <img src="http://img.youtube.com/vi/hJhcSvN2KwU/mqdefault.jpg" alt="Watch the video" width="360" border="10" />
</a>


## 📂 Structure

```graphql
/baselines    # Baseline implementations + test runners
/benchmark    # Test cases and injected bugs
/examples     # Visual walkthroughs with screenshots, traces, and logs
/experiments  # Scripts for RQ1–RQ4 experiments
/webapps      # Containerized benchmark applications
/webtestpilot # Core implementation
```

## ⚙️ Setup

1. **Clone and initialize**

    Run the setup script:

    ```bash
    ./setup.sh
    ```

    This checks required tools (`uv`, `docker`, `docker-compose`) and guides you interactively.

2. **Configure environment variables**

    ```bash
    cp .env.example .env
    ```

3. **Configure runtime settings**

    Set the provider and execution mode in:

    ```
    /webtestpilot/src/webtestpilot/config.yaml
    ```

    Supported providers:

    * `Claude` (Anthropic)
    * `GPT` (OpenAI)
    * `Gemini` (Google)
    * `OpenRouter` (self-hosted via OpenAI-compatible API)

    > [!NOTE]
    > 1. Ensure corresponding API keys/endpoints for your provider are set in `.env` (Step 2).  
    > 2. `/experiments` uses this config by default (see `/baselines/config.py` to override).  
    > 3. For standalone usage, you can provide a custom config path (see example below).

## 🚀 Running Experiments

Navigate to:

```bash
cd experiments
```

Follow the `README.md` in each submodule.

## 🖥 Running WebTestPilot (Standalone)

Install as editable package:

```bash
pip install -e ./webtestpilot
# or
uv pip install -e ./webtestpilot
```

### Minimal example

The default mode is **browser-use**: a one-shot LLM agent navigates the browser directly with no GUI grounding model required. The browser must expose a CDP endpoint so browser-use can connect to the existing session.

```python
from webtestpilot import WebTestPilot, Config, BugReport, Session, Step
from playwright.sync_api import sync_playwright

def hook(report: BugReport):
    print("A bug was reported:", report)

steps = [
    Step(condition="", action="From the dashboard click 'Page Template' link", expectation="Page contains title 'Page Template'"),
    Step(condition="", action="Click 'Add Comment'", expectation="A WYSIWYG comment editor is open"),
]

playwright = sync_playwright().start()
# Expose the CDP endpoint so browser-use can connect to the same browser session
browser = playwright.chromium.launch(headless=True, args=["--remote-debugging-port=9222"])
page = browser.new_page()

config = Config.load("path/to/config.yaml")
session = Session(page, config)

WebTestPilot.run(session, steps, assertion=True, hooks=[hook])
```

## ⚙️ SoM Mode (Optional)

SoM (Set-of-Mark) mode uses a two-stage grounding pipeline with a local vision model for element localization. This is the configuration used in the paper’s experiments.

<details>
<summary><b>Show SoM setup and configuration</b></summary>

To switch to SoM mode, set in `config.yaml`:

```yaml
executor:
  mode: "som"
````

SoM mode requires deploying `inclusionAI/UI-Venus-Ground-7B` as a local model server. Install and configure vLLM with:

* `vllm==0.19.0`
* `torch==2.10.0` (pinned for ABI compatibility)
* `transformers` (custom revision `21fac7ab`)
* `accelerate>=1.10.0`, `openai>=1.99.9`, `pillow>=11.3.0`

Then run:

```bash
vllm serve inclusionAI/UI-Venus-Ground-7B \
  --max_model_len 4K \
  --max_num_seqs 8 \
  --trust-remote-code \
  --limit-mm-per-prompt '{"image": 1, "video": 0}'
```

SoM mode does **not** require `--remote-debugging-port`.

</details>

## 📝 Citation

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
