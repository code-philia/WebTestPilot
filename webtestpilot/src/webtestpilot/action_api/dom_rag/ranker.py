import logging
import math

import numpy as np

from webtestpilot.action_api.dom_rag.types import DOMCandidate

logger = logging.getLogger(__name__)


def normalize_scores(values: list[float]) -> list[float]:
    if not values:
        return values

    lo = min(values)
    hi = max(values)

    if math.isclose(lo, hi):
        return [0.5 for _ in values]

    return [(v - lo) / (hi - lo) for v in values]


def with_score(candidate: DOMCandidate, score: float) -> DOMCandidate:
    return DOMCandidate(**{**candidate.__dict__, "score": float(score)})


def candidate_to_ranking_text(candidate: DOMCandidate) -> str:
    parts = [
        f"tag: {candidate.tag}",
        f"role: {candidate.role}",
        f"type: {candidate.type}",
        f"text: {candidate.text}",
        f"aria_label: {candidate.aria_label}",
        f"title: {candidate.title}",
        f"placeholder: {candidate.placeholder}",
        f"name: {candidate.name}",
        f"value: {candidate.value}",
        f"href: {candidate.href}",
        f"context: {candidate.context}",
        f"selector: {candidate.selector_hint}",
        f"xpath: {candidate.xpath}",
        f"rect: {candidate.rect}",
    ]

    return " | ".join(p for p in parts if p and not p.endswith(": "))


class DomRagRanker:
    """
    Model-based DOM ranker.

    Stage 1: DMR-style dual encoder retrieval.
    Stage 2: MindAct-style cross encoder reranking.
    """

    def __init__(
        self,
        *,
        dual_model_name: str,
        cross_model_name: str,
        enable_dual: bool = True,
        enable_cross: bool = True,
        device: str | None = None,
    ) -> None:
        self.dual_model_name = dual_model_name
        self.cross_model_name = cross_model_name
        self.enable_dual = enable_dual
        self.enable_cross = enable_cross
        self.device = device

        self._dual_model = None
        self._cross_model = None
        self._cross_tokenizer = None

    @property
    def dual_model(self):
        if self._dual_model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading DOM-RAG dual encoder: %s", self.dual_model_name)
            self._dual_model = SentenceTransformer(
                self.dual_model_name,
                device=self.device,
            )

        return self._dual_model

    def _load_cross_encoder(self) -> None:
        if self._cross_model is not None:
            return

        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        logger.info("Loading DOM-RAG cross encoder: %s", self.cross_model_name)

        self._cross_tokenizer = AutoTokenizer.from_pretrained(self.cross_model_name)
        self._cross_model = AutoModelForSequenceClassification.from_pretrained(
            self.cross_model_name
        )

        if self.device:
            self._cross_model.to(self.device)

        self._cross_model.eval()

    def dual_retrieve(
        self,
        query: str,
        candidates: list[DOMCandidate],
        *,
        top_k: int,
    ) -> list[DOMCandidate]:
        if not self.enable_dual or not candidates:
            return candidates[:top_k]

        texts = [candidate_to_ranking_text(candidate) for candidate in candidates]

        query_emb = self.dual_model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        cand_embs = self.dual_model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        # Embeddings are normalized, so dot product is cosine similarity.
        sims = np.asarray(cand_embs @ query_emb, dtype=float)
        sim_norm = normalize_scores(sims.tolist())

        reranked: list[DOMCandidate] = []
        for candidate, dense_score in zip(candidates, sim_norm):
            reranked.append(with_score(candidate, dense_score))

        reranked.sort(key=lambda item: item.score, reverse=True)
        return reranked[:top_k]

    def cross_rerank(
        self,
        query: str,
        candidates: list[DOMCandidate],
        *,
        top_k: int,
        batch_size: int = 16,
    ) -> list[DOMCandidate]:
        if not self.enable_cross or not candidates:
            return candidates[:top_k]

        self._load_cross_encoder()

        pairs = [(query, candidate_to_ranking_text(candidate)) for candidate in candidates]
        raw_scores = self._predict_cross_scores(pairs, batch_size=batch_size)
        cross_norm = normalize_scores(raw_scores)

        reranked: list[DOMCandidate] = []
        for candidate, cross_score in zip(candidates, cross_norm):
            # Cross encoder is the precision stage, so it gets more weight.
            combined_score = 0.25 * candidate.score + 0.75 * cross_score
            reranked.append(with_score(candidate, combined_score))

        reranked.sort(key=lambda item: item.score, reverse=True)
        return reranked[:top_k]

    def _predict_cross_scores(
        self,
        pairs: list[tuple[str, str]],
        *,
        batch_size: int,
    ) -> list[float]:
        import torch

        assert self._cross_model is not None
        assert self._cross_tokenizer is not None

        scores: list[float] = []

        for start in range(0, len(pairs), batch_size):
            batch = pairs[start : start + batch_size]
            queries = [query for query, _ in batch]
            docs = [doc for _, doc in batch]

            encoded = self._cross_tokenizer(
                queries,
                docs,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )

            if self.device:
                encoded = {key: value.to(self.device) for key, value in encoded.items()}

            with torch.no_grad():
                logits = self._cross_model(**encoded).logits

            batch_scores = self._positive_class_scores(logits).detach().cpu().tolist()
            scores.extend(float(score) for score in batch_scores)

        return scores

    def _positive_class_scores(self, logits):
        """
        Convert classification logits into a single relevance score.

        For binary classifiers, the positive class is usually index 1.
        If label names are available, prefer labels that look positive/relevant.
        """
        if logits.shape[-1] == 1:
            return logits.squeeze(-1)

        id2label = getattr(self._cross_model.config, "id2label", {}) or {}

        positive_idx = None
        for idx, label in id2label.items():
            label_lower = str(label).lower()
            if label_lower in {"label_1", "positive", "relevant", "entailment"}:
                positive_idx = int(idx)
                break

        if positive_idx is None:
            positive_idx = logits.shape[-1] - 1

        return logits[:, positive_idx]
