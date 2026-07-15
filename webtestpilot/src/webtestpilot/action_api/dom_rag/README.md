# DOM-RAG Mode

This README records the current DOM-RAG implementation progress, setup steps, and known issues from the latest PrestaShop run.

## Current Status

DOM-RAG is implemented as an action execution mode for WebTestPilot. The latest PrestaShop run completed 14/23 test cases, or 60.9%.

Recent changes moved semantic grounding away from local hand-written heuristics:

- Removed direct action fallbacks for app-specific cases.
- Removed local action intent parsing.
- Removed lexical action scoring and lexical candidate blending.
- Added a structured LLM decision step over ranked DOM candidates.
- Kept deterministic DOM collection, model-based candidate ranking, and deterministic execution by label.

## Setup

Install the WebTestPilot environment from the project root:

```bash
cd /Users/zap/Documents/SJTU/WebTestPilot/webtestpilot
uv sync
uv run playwright install
```

If BAML files are changed, regenerate the client:

```bash
uv run baml-cli generate
```

Make sure `sentencepiece` is installed. It is currently listed in `webtestpilot/pyproject.toml` and is needed by some Hugging Face tokenizers used by the DOM-RAG rankers.

## Enable DOM-RAG

Set the executor mode in `webtestpilot/src/webtestpilot/config.yaml`:

```yaml
executor:
  mode: "dom_rag"
```

Both `"dom_rag"` and `"dom-rag"` are accepted by the action API.

Current DOM-RAG settings live under:

```yaml
executor:
  dom_rag:
    dom_rag_top_k: 100
    dom_rag_max_candidates: 500
    dom_rag_dual_top_k: 80
    dom_rag_cross_top_k: 500
    enable_dual_encoder: false
    enable_cross_encoder: true
    dom_rag_dual_encoder_model: "McGill-NLP/MiniLM-L6-dmr"
    dom_rag_cross_encoder_model: "osunlp/MindAct_CandidateGeneration_deberta-v3-base"
    dom_rag_ranker_device: mps
```

Notes:

- Use `dom_rag_ranker_device: null` for CPU.
- Use `cuda` on a CUDA GPU.
- Use `mps` on Apple Silicon only if the local PyTorch/transformers stack is stable.
- `enable_dual_encoder: false` means the current run primarily relies on cross-encoder reranking over collected candidates.

## Run RQ1 With DOM-RAG

From the project root:

```bash
cd /Users/zap/Documents/SJTU/WebTestPilot
bash experiments/rq1/run.sh webtestpilot prestashop
```

Outputs are written to:

```text
experiments/rq1/results/webtestpilot_prestashop/
```

Each run has:

- a top-level `run_*.log`
- a `run_*` result directory
- per-test `history.json`, `trace.json`, and `result.json`

## Method

DOM-RAG follows this pipeline:

1. Collect visible/actionable DOM elements from the current page.
2. Convert each element into a `DOMCandidate` containing label, XPath, role, tag, text, aria label, title, placeholder, value, context, selector hint, bounding box, disabled state, and score.
3. Rank candidates with model-based retrieval:
   - dual encoder retrieval when enabled,
   - cross encoder reranking when enabled.
4. Send the ranked candidate list and screenshot to the LLM through `DecideDomRagCandidate`.
5. The LLM returns a structured `CandidateDecision`:
   - `action_type`
   - `selected_label`
   - `input_text`
   - `key`
   - `confidence`
   - `reason`
   - `rejected_labels`
   - `fallback_needed`
6. Python converts the structured decision into one of the existing executable actions:
   - `click_by_label`
   - `type`
   - `press`
   - `scroll_up`
   - `scroll_down`
   - `wait`
   - `finished`
   - `no_answer`
7. If the LLM reports low confidence or fallback is needed, DOM-RAG emits `no_answer`. If all DOM-RAG rounds fail, the mode raises an error. DOM-RAG itself does not fall back to SoM.

## Why DOM-RAG Instead of SoM-Only Grounding

Some failed test cases that look like oracle failures are not purely oracle problems. In the SoM pipeline, the UI-grounding model first predicts a coordinate from the screenshot, then `mark.js` exposes nearby active elements for the reasoning model to choose from. When `maxNearby` was set to `1`, only the nearest active element to the predicted coordinate was exposed. If the coordinate was slightly off, the correct target was excluded from the candidate set.

That creates a brittle failure chain:

1. The UI-grounding coordinate is close but not exact.
2. `mark.js` exposes only one nearby candidate.
3. The correct target is missing from the SoM candidate set.
4. The reasoning model either returns `no_answer()` or treats a nearby label as the intended target.
5. The oracle may incorrectly pass an intermediate step.
6. The pipeline continues from an unchanged or corrupted UI state.
7. A later step fails, making the final error look like an oracle or business-flow failure even though the root cause was earlier candidate-recall loss.

DOM-RAG is motivated by a different assumption: for web apps, the target is often represented more clearly in the DOM or accessibility tree than in pixels alone. Instead of asking a visual grounding model to predict where a target is, DOM-RAG asks:

> Given the instruction, retrieve semantically plausible live DOM elements, then ask the reasoning model to rank and validate which element should receive the action.

This is useful because many targets have explicit text, accessible names, roles, form metadata, table context, or ancestor context. For example, a target like `My wishlist` can be retrieved from DOM text/accessibility data and evaluated in context under `My wishlists`. That is easier to validate than predicting a pixel coordinate and hoping the correct element is inside a small nearby candidate set.

The full DOM is usually too large to send directly to an LLM, so DOM-RAG uses retrieval and reranking. This follows the same high-level direction as recent web-agent work: Mind2Web observes that raw real-world HTML is often too large for direct LLM input and uses filtering to improve effectiveness and efficiency; Prune4Web similarly treats real pages as too large, often 10,000-100,000 DOM tokens, and reports large reductions in candidate elements with improved low-level grounding accuracy.

The practical distinction is:

- SoM-only grounding: "Given an image, predict where the target is."
- DOM/accessibility RAG: "Given an instruction, retrieve plausible live elements, then ask the LLM to decide whether a candidate is operationally correct."

DOM-RAG is not meant to remove visual reasoning entirely. It is meant to reduce dependence on a black-box coordinate prediction as the single source of truth, especially in dense real-world web apps where small coordinate errors or training-data bias can exclude the correct candidate.

### UI Grounding Failure Modes DOM-RAG Targets

The SoM pipeline can fail even when the instruction is clear and the target is visible. The inaccuracies fall into three broad types.

#### 1. Stochastic Coordinate Instability

The same screenshot, instruction, and UI-grounding model can produce different bounding boxes or points across runs. Even if one run lands near the target, another run may drift enough that `mark.js` exposes a different nearby widget. DOM-RAG reduces this by retrieving from the live DOM/accessibility structure instead of relying on one sampled coordinate.

#### 2. Systematic Grounding Inaccuracy

The model may be consistent but consistently localized to the wrong coordinate. The following issues are common consequences of that systematic localization error:

- **Visual target confusion:** text buttons are often easy to identify visually, but icon-only buttons can be ambiguous. DOM-RAG can use attributes such as accessible labels, titles, roles, form metadata, and ancestor context that are not always visible in the screenshot.
- **Semantic target-binding confusion:** when there are multiple similar objects, such as three comments, the instruction may require deleting the first comment but the UI-grounding model may click the second. This can happen when the crop does not contain the full repeated structure. DOM-RAG can represent repeated elements with DOM order, parent containers, table/list rows, and sibling context, making "first", "second", or row-bound actions easier to validate.
- **Localization precision error:** a wrong center point can exclude the intended widget from the nearby marked set, especially with small crop sizes, `maxNearby=1`, or many active widgets in the same region. DOM-RAG retrieves candidate elements globally or from a larger candidate pool, so the target is less likely to disappear because of a small coordinate miss.
- **Element overload in one region:** dense toolbars, tables, grids, and action columns often contain many controls close together. A coordinate-based crop may expose only the nearest wrong widget. DOM-RAG can preserve multiple plausible controls and let the LLM compare their text, roles, and context.
- **Invalid label hallucination:** when the correct target is visible but absent from the SoM active-element set, the reasoning model may invent or assume a nearby/sequential label instead of refusing, asking for another crop, scrolling, or using a DOM/accessibility fallback. DOM-RAG makes missing-target cases explicit through `fallback_needed` and `no_answer`, and gives the model a ranked candidate list with labels that actually exist.
- **Large element under-selection:** the target may be a large interactive surface, such as an editor area, whose center is far from the predicted point. Even when the predicted point visually falls inside the editor, `mark.js` with `maxNearby=1` may return a smaller nearby active element, such as a toolbar `Paragraph` button, because that smaller element's center is closer. DOM-RAG can retrieve the editor surface itself by role, contenteditable state, ARIA metadata, or DOM scope instead of depending on center-point distance.

#### 3. Out-of-Distribution Websites

A visual UI-grounding model can be biased toward layouts and widgets seen during training. New websites that satisfy WebTestPilot's criteria may still present unfamiliar visual styling. DOM/accessibility retrieval relies more on live web structure and standard browser semantics, so it can generalize across visual themes when the DOM is meaningful.

These issues do not prove DOM-RAG is always better. They define where DOM-RAG is expected to help: when the target is semantically represented in the DOM/accessibility tree and coordinate-only grounding loses candidate recall or binds to the wrong repeated visual object.

## Latest PrestaShop Failure Patterns

The latest run showed these common pitfalls:

- Candidate collection can miss the operational target, especially product-page buttons and table cells.
- Table row/cell grounding remains weak. Examples include clicking a column header instead of the first product name, or selecting a nearby order control instead of the row matching an order ID/reference pair.
- Dropdown/select workflows are under-modeled. Some seller order tests clicked the `<select>` or a nearby control but did not actually select the intended status option.
- Searchable dropdowns were confused with global search. In refund/ship flows, the LLM typed into the back-office global search field instead of the dropdown's local search input.
- Same-label or same-region controls are confused. Examples include page-level `Go to Catalog` versus sidebar `Catalog`, and `Update status` versus nearby buttons.
- Modal confirmations need stronger state-change verification. Wishlist removal clicked a confirmation-looking target but the item remained in the list.
- Assertion generation still creates false positives and false bugs, including bad generated code and brittle list-order comparisons.

## Next Work

Highest-impact improvements:

- Enrich `DOMCandidate` with table metadata: row text, column name, row index, cell coordinates, and sibling cell values.
- Enrich candidates with form/select metadata: current value, available options, opened/closed state, and option ownership.
- Add modal/dialog scope metadata so confirmation buttons can be distinguished from page-level buttons.
- Improve post-action validation so wrong intermediate navigation is caught before later steps fail.
- Keep semantic target selection in the structured LLM decision; avoid reintroducing local action-intent heuristics.
