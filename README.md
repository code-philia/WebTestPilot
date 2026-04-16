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

**TL;DR:** WebTestPilot converts what a multimodal agent sees on the web into symbolic representations that can be asserted in automated end-to-end tests.

<a href="http://www.youtube.com/watch?feature=player_embedded&v=hJhcSvN2KwU" target="_blank">
 <img src="http://img.youtube.com/vi/hJhcSvN2KwU/mqdefault.jpg" alt="Watch the video" width="360" border="10" />
</a>

## 📂 Structure

```graphql
/baselines    # Baseline implementations + test runners
/experiments  # Scripts for RQ1–RQ4 experiments
/benchmark    # Test cases and injected bugs
/webapps      # Containerized benchmark applications
/webtestpilot # Core implementation
```
## ⚙️ Setup

### 1. Clone and initialize

Run the setup script:

```bash
./setup.sh
```

This checks required tools (`uv`, `docker`, `docker-compose`) and guides you interactively.

### 2. Deploy the GUI grounding model

WebTestPilot uses `inclusionAI/UI-Venus-Ground-7B` to locate GUI elements in a screenshot.

Install and configure [vLLM](https://docs.vllm.ai/en/latest/getting_started/quickstart/), ensuring the following dependencies:
* `vllm==0.19.0`
* `torch==2.10.0` *(pinned for vLLM ABI compatibility)*
* `transformers` *(custom git revision `21fac7ab` from Hugging Face)*
* `accelerate>=1.10.0`, `openai>=1.99.9`, `pillow>=11.3.0`

Then run:

```bash
HF_HOME=$(HF_HOME) \
vllm serve inclusionAI/UI-Venus-Ground-7B \
--max_model_len 4K \
--max_num_seqs 8 \
--trust-remote-code \
--limit-mm-per-prompt '{"image": 1, "video": 0}'
```

This starts a local model server.

### 3. Configure environment variables

```bash
cp .env.example .env
```

Required:

* `OPENAI_API_KEY`
* `GUI_GROUNDING_MODEL_BASE_URL`
* `LOCAL_MODEL_BASE_URL` (for RQ3, RQ4)

### 4. Configure runtime settings

Set the base model in:

```
/webtestpilot/src/webtestpilot/config.yaml
```

Supported providers:

* `GPT` (OpenAI)
* `Gemini` (Google)
* `Claude` (Anthropic)
* `Local` (self-hosted via API)

> **Notes**
>
> 1. Ensure corresponding API keys/endpoints are set in `.env` (Step 3).
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
uv pip install -e ./webtestpilot
```

### Minimal example

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
browser = playwright.chromium.launch(headless=True)
page = browser.new_page()

config = Config.load("path/to/config.yaml")
session = Session(page, config)

WebTestPilot.run(session, steps, assertion=True, hooks=[hook])
```

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