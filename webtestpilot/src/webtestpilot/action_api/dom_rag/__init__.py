import json
import logging
import re
from functools import lru_cache
from typing import Any

from playwright.sync_api import Page

from webtestpilot.action_api.dom_rag.ranker import (
    DomRagRanker,
)
from webtestpilot.action_api.dom_rag.types import DOMCandidate
from webtestpilot.action_api.som.automator import execute
from webtestpilot.baml_client.sync_client import b
from webtestpilot.data_models import Session
from webtestpilot.utils import get_screenshot, pil_to_baml, wait_for_dom_stability

logger = logging.getLogger(__name__)


def execute_action_dom_rag(session: Session, action: str) -> None:
    """
    Execute a natural-language action with DOM-RAG.

    Pipeline:
    1. collect visible/actionable DOM candidates,
    2. DMR-style dual encoder retrieval,
    3. MindAct-style cross encoder reranking,
    4. ask the LLM to make the structured grounding decision,
    5. execute through existing label -> XPath API.
    """
    options = {
        "client_registry": session.config.action_proposer,
        "collector": session.collector,
    }

    top_k = max(1, int(session.config.dom_rag_top_k))
    max_candidates = max(1, int(session.config.dom_rag_max_candidates))
    dual_top_k = max(1, int(session.config.dom_rag_dual_top_k))
    cross_top_k = max(1, int(session.config.dom_rag_cross_top_k))

    max_rounds = 2
    page = session.page
    previous_failure: dict[str, Any] | None = None

    ranker = get_dom_rag_ranker(session.config)

    all_candidates = collect_dom_candidates(page, max_candidates=max_candidates)
    logger.info("DOM-RAG collected %d visible/actionable candidates", len(all_candidates))

    for round_idx in range(max_rounds):
        # Second round broadens retrieval if the model said no_answer.
        round_multiplier = round_idx + 1
        round_top_k = min(max_candidates, top_k * round_multiplier)

        candidates = retrieve_dom_candidates_hybrid(
            action=action,
            candidates=all_candidates,
            llm_top_k=round_top_k,
            dual_top_k=min(dual_top_k * round_multiplier, max_candidates),
            cross_top_k=max(cross_top_k, round_top_k),
            ranker=ranker,
        )

        decision = decide_dom_rag_candidate(
            page=page,
            action=action,
            candidates=candidates,
            baml_options=options,
            previous_failure=previous_failure,
        )
        code = dom_rag_decision_to_action_code(decision, candidates)

        session.trace.append(
            {
                "action": action,
                "action_code": code,
                "decision": dom_rag_decision_to_trace(decision),
                "mode": "dom-rag",
                "round": round_idx,
                "candidate_count": len(all_candidates),
                "retrieved_labels": [candidate.label for candidate in candidates],
                "retrieved_candidates": [
                    {
                        "label": candidate.label,
                        "score": candidate.score,
                        "xpath": candidate.xpath,
                        "role": candidate.role,
                        "tag": candidate.tag,
                        "type": candidate.type,
                        "text": candidate.text,
                        "aria_label": candidate.aria_label,
                        "title": candidate.title,
                        "placeholder": candidate.placeholder,
                        "context": candidate.context,
                        "selector_hint": candidate.selector_hint,
                        "rect": candidate.rect,
                    }
                    for candidate in candidates
                ],
            }
        )

        som_mapping = {candidate.label: candidate.xpath for candidate in candidates}
        trace, no_answer = execute(code, page, som_mapping)
        session.trace.extend(trace)

        if no_answer:
            previous_failure = {
                "kind": "model_no_answer_or_low_confidence",
                "round": round_idx,
                "decision": dom_rag_decision_to_trace(decision),
                "retrieved_candidates": [
                    {
                        "label": candidate.label,
                        "score": candidate.score,
                        "text": candidate.text,
                        "role": candidate.role,
                        "tag": candidate.tag,
                        "context": candidate.context,
                    }
                    for candidate in candidates
                ],
            }
            logger.info("DOM-RAG returned no_answer in round %d; broadening retrieval.", round_idx)
            continue

        wait_for_dom_stability(page)
        session.capture_state(prev_action=action)
        return

    raise RuntimeError(
        "DOM-RAG could not identify an executable target: "
        + json.dumps(previous_failure or {}, ensure_ascii=False)
    )


@lru_cache(maxsize=4)
def _cached_dom_rag_ranker(
    dual_model_name: str,
    cross_model_name: str,
    enable_dual: bool,
    enable_cross: bool,
    device: str | None,
) -> DomRagRanker:
    return DomRagRanker(
        dual_model_name=dual_model_name,
        cross_model_name=cross_model_name,
        enable_dual=enable_dual,
        enable_cross=enable_cross,
        device=device,
    )


def get_dom_rag_ranker(config) -> DomRagRanker:
    return _cached_dom_rag_ranker(
        config.dom_rag_dual_encoder_model,
        config.dom_rag_cross_encoder_model,
        bool(config.dom_rag_enable_dual_encoder),
        bool(config.dom_rag_enable_cross_encoder),
        config.dom_rag_ranker_device,
    )


def decide_dom_rag_candidate(
    *,
    page: Page,
    action: str,
    candidates: list[DOMCandidate],
    baml_options: dict,
    previous_failure: dict[str, Any] | None = None,
):
    screenshot_baml = pil_to_baml(get_screenshot(page))
    active_elements = format_dom_candidates(candidates)
    previous_failure_text = json.dumps(previous_failure or {}, ensure_ascii=False, indent=2)

    decision = b.DecideDomRagCandidate(
        screenshot=screenshot_baml,
        task=action,
        active_elements=active_elements,
        previous_failure=previous_failure_text,
        baml_options=baml_options,
    )
    logger.info("DOM-RAG candidate decision: %s", dom_rag_decision_to_trace(decision))
    return decision


def dom_rag_decision_to_action_code(decision, candidates: list[DOMCandidate]) -> str:
    action_type = _normalize_text(getattr(decision, "action_type", "no_answer"))
    selected_label = getattr(decision, "selected_label", None)
    confidence = float(getattr(decision, "confidence", 0.0) or 0.0)
    fallback_needed = bool(getattr(decision, "fallback_needed", False))

    if fallback_needed or confidence < 0.70:
        return "no_answer()"

    if action_type in {"no_answer", "none"}:
        return "no_answer()"
    if action_type == "finished":
        return "finished()"
    if action_type == "wait":
        return "wait()"
    if action_type == "scroll_up":
        return "scroll_up()"
    if action_type == "scroll_down":
        return "scroll_down()"
    if action_type == "press":
        key = _python_string(getattr(decision, "key", None) or "Enter")
        return f"press(key={key})"

    candidate = _candidate_by_label(candidates, selected_label)
    if candidate is None:
        return "no_answer()"

    if action_type == "click":
        return f'click_by_label(label="{candidate.label}")'

    if action_type in {"type", "select"}:
        content = _python_string(getattr(decision, "input_text", None) or "")
        return f'type(label="{candidate.label}", content={content})'

    return "no_answer()"


def dom_rag_decision_to_trace(decision) -> dict[str, Any]:
    return {
        "action_type": getattr(decision, "action_type", None),
        "selected_label": getattr(decision, "selected_label", None),
        "input_text": getattr(decision, "input_text", None),
        "key": getattr(decision, "key", None),
        "confidence": getattr(decision, "confidence", None),
        "reason": getattr(decision, "reason", None),
        "rejected_labels": list(getattr(decision, "rejected_labels", []) or []),
        "fallback_needed": getattr(decision, "fallback_needed", None),
    }


def _candidate_by_label(candidates: list[DOMCandidate], label: Any) -> DOMCandidate | None:
    try:
        target_label = int(label)
    except (TypeError, ValueError):
        return None
    return next((candidate for candidate in candidates if candidate.label == target_label), None)


def _python_string(value: str) -> str:
    return json.dumps(str(value))


def format_dom_candidates(candidates: list[DOMCandidate]) -> str:
    lines: list[str] = []

    for candidate in candidates:
        text = _shorten(
            candidate.text
            or candidate.aria_label
            or candidate.title
            or candidate.placeholder
            or candidate.value,
            120,
        )
        context = _shorten(candidate.context, 180)

        lines.append(
            f"[{candidate.label}] -> "
            f"score={candidate.score:.3f} "
            f"role='{candidate.role}' tag='{candidate.tag}' type='{candidate.type}' "
            f"text='{text}' aria_label='{_shorten(candidate.aria_label, 80)}' "
            f"title='{_shorten(candidate.title, 80)}' "
            f"placeholder='{_shorten(candidate.placeholder, 80)}' "
            f"name='{_shorten(candidate.name, 80)}' "
            f"value='{_shorten(candidate.value, 80)}' "
            f"context='{context}' "
            f"selector_hint='{_shorten(candidate.selector_hint, 120)}' "
            f"xpath='{_shorten(candidate.xpath, 160)}' "
            f"rect={candidate.rect}"
        )

    return "\n".join(lines)


def collect_dom_candidates(page: Page, *, max_candidates: int = 500) -> list[DOMCandidate]:
    data = page.evaluate(
        """
        (maxCandidates) => {
          const trim = (s, limit = 500) =>
            String(s || '').replace(/\\s+/g, ' ').trim().slice(0, limit);

          const isVisible = (el) => {
            const style = window.getComputedStyle(el);
            const rect = el.getBoundingClientRect();

            return style &&
              style.visibility !== 'hidden' &&
              style.display !== 'none' &&
              Number(style.opacity || '1') > 0 &&
              rect.width > 0 &&
              rect.height > 0;
          };

          const textOf = (el) => trim(el.innerText || el.textContent || '', 500);

          const xpathFor = (el) => {
            if (el === document.body) return '/html/body';

            const parts = [];
            let node = el;

            while (node && node.nodeType === Node.ELEMENT_NODE && node !== document) {
              let idx = 1;
              let sib = node.previousElementSibling;

              while (sib) {
                if (sib.tagName === node.tagName) idx += 1;
                sib = sib.previousElementSibling;
              }

              parts.unshift(`${node.tagName.toLowerCase()}[${idx}]`);
              node = node.parentElement;
            }

            return '/' + parts.join('/');
          };

          const cssEscape = (value) =>
            (window.CSS && CSS.escape)
              ? CSS.escape(value)
              : String(value).replace(/"/g, '\\\\"');

          const selectorFor = (el) => {
            if (el.id) return `#${cssEscape(el.id)}`;

            const testId = el.getAttribute('data-testid') || el.getAttribute('data-test-id');
            if (testId) return `[data-testid="${cssEscape(testId)}"]`;

            const name = el.getAttribute('name');
            if (name) return `${el.tagName.toLowerCase()}[name="${cssEscape(name)}"]`;

            const aria = el.getAttribute('aria-label');
            if (aria) return `${el.tagName.toLowerCase()}[aria-label="${cssEscape(aria)}"]`;

            return xpathFor(el);
          };

          const implicitRole = (el) => {
            const tag = el.tagName.toLowerCase();
            const type = (el.getAttribute('type') || '').toLowerCase();

            if (tag === 'a' && el.getAttribute('href')) return 'link';
            if (tag === 'button') return 'button';
            if (tag === 'select') return 'combobox';
            if (tag === 'textarea') return 'textbox';
            if (tag === 'li') return 'listitem';
            if (tag === 'summary') return 'button';

            if (tag === 'input') {
              if (['button', 'submit', 'reset'].includes(type)) return 'button';
              if (type === 'checkbox') return 'checkbox';
              if (type === 'radio') return 'radio';
              return 'textbox';
            }

            return '';
          };

          const contextOf = (el) => {
            const pieces = [];
            const ownText = textOf(el);
            let node = el.parentElement;
            let depth = 0;

            while (node && node !== document.body && depth < 4) {
              const role = node.getAttribute('role') || '';
              const aria = node.getAttribute('aria-label') || '';

              const heading = Array.from(node.querySelectorAll('h1,h2,h3,h4,h5,h6'))
                .slice(0, 2)
                .map((h) => textOf(h))
                .filter(Boolean)
                .join(' | ');

              const parentText = textOf(node);

              if (aria) pieces.push(`aria:${aria}`);
              if (role) pieces.push(`role:${role}`);
              if (heading) pieces.push(`heading:${heading}`);
              if (parentText && parentText !== ownText) pieces.push(parentText.slice(0, 180));

              node = node.parentElement;
              depth += 1;
            }

            return trim(pieces.join(' || '), 500);
          };

          const isActionable = (el) => {
            const style = window.getComputedStyle(el);

            if (el.matches('a,button,input,textarea,select,summary,label')) return true;
            if (el.matches('[role],[contenteditable="true"],[tabindex]')) return true;
            if (el.getAttribute('onclick')) return true;
            if (style.cursor === 'pointer') return true;

            return false;
          };

          const nodes = Array.from(document.querySelectorAll('body *'));

          return nodes
            .filter((el) => isVisible(el) && isActionable(el))
            .slice(0, maxCandidates)
            .map((el, i) => {
              const rect = el.getBoundingClientRect();

              return {
                label: i + 1,
                xpath: xpathFor(el),
                tag: el.tagName.toLowerCase(),
                role: el.getAttribute('role') || implicitRole(el),
                type: el.getAttribute('type') || '',
                text: textOf(el).slice(0, 300),
                aria_label: el.getAttribute('aria-label') || '',
                title: el.getAttribute('title') || '',
                placeholder: el.getAttribute('placeholder') || '',
                name: el.getAttribute('name') || '',
                value: el.value || el.getAttribute('value') || '',
                href: el.href || el.getAttribute('href') || '',
                context: contextOf(el),
                selector_hint: selectorFor(el),
                disabled: Boolean(el.disabled || el.getAttribute('aria-disabled') === 'true'),
                rect: {
                  x: Math.round(rect.x),
                  y: Math.round(rect.y),
                  width: Math.round(rect.width),
                  height: Math.round(rect.height)
                }
              };
            });
        }
        """,
        int(max_candidates),
    )

    return [DOMCandidate(**item) for item in data]


def retrieve_dom_candidates_hybrid(
    *,
    action: str,
    candidates: list[DOMCandidate],
    llm_top_k: int,
    dual_top_k: int,
    cross_top_k: int,
    ranker: DomRagRanker,
) -> list[DOMCandidate]:
    """
    DOM-RAG retrieval without local semantic heuristics.

    Stage 1: DMR-style dual encoder retrieval over all visible/actionable DOM candidates.
    Stage 2: MindAct-style cross encoder reranking over the dual-encoder shortlist.
    Stage 3: return compact top-k candidates for LLM grounding.
    """

    active_candidates = [
        candidate
        for candidate in candidates
        if not candidate.disabled
    ]

    if not active_candidates:
        return []

    # Stage 1: dual encoder retrieval over all candidates.
    stage1 = ranker.dual_retrieve(
        action,
        active_candidates,
        top_k=min(dual_top_k, len(active_candidates)),
    )

    if not stage1:
        return []

    # Stage 2: cross encoder reranking over the dense shortlist.
    final = ranker.cross_rerank(
        action,
        stage1,
        top_k=min(cross_top_k, len(stage1)),
    )

    return final[:llm_top_k]

def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").casefold()).strip()


def _shorten(text: str, limit: int) -> str:
    text = str(text or "").replace("\n", " ").strip()
    return text if len(text) <= limit else text[:limit] + "…"
