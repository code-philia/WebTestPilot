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

### 2. Configure environment variables

```bash
cp .env.example .env
```

Required for the default **browser-use** mode:

* `ANTHROPIC_API_KEY` + `ANTHROPIC_MODEL_NAME` — or the equivalent for your chosen provider (`OPENAI_API_KEY`, `GOOGLEAI_API_KEY`, etc.)

Required for **SoM** mode (and `/experiments`):

* `GUI_GROUNDING_MODEL_BASE_URL` — endpoint of the local GUI grounding model (see [SoM mode](#%EF%B8%8F-som-mode-optional) below)
* `OPENAI_API_KEY`

### 3. Configure runtime settings

Set the provider and execution mode in:

```
/webtestpilot/src/webtestpilot/config.yaml
```

Supported providers:

* `Claude` (Anthropic) — default
* `GPT` (OpenAI)
* `Gemini` (Google)
* `Local` (self-hosted via OpenAI-compatible API)

> **Notes**
>
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

The **SoM** (Set-of-Mark) mode uses a two-stage pipeline: a local GUI grounding model proposes element coordinates, then a multimodal LLM selects the exact element from annotated candidates. This is the mode used in the paper's experiments.

To switch to SoM mode, set in `config.yaml`:

```yaml
executor:
  mode: "som"
```

SoM mode requires deploying `inclusionAI/UI-Venus-Ground-7B` as a local model server. Install and configure [vLLM](https://docs.vllm.ai/en/latest/getting_started/quickstart/) with:

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

SoM mode does **not** require `--remote-debugging-port`.

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
