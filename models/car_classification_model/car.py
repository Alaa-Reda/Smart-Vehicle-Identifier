"""
===========================================================
Car Classification Model — 1992 to 2012
===========================================================

Importable module for vehicle make/model/year classification.

Usage
-----
from models.car_classification_model.car_classifier import CarClassifier

classifier = CarClassifier()
results = classifier.predict(image)   # PIL Image or path
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Union

import torch
from PIL import Image
from transformers import AutoImageProcessor, ConvNextForImageClassification

logger = logging.getLogger(__name__)

# ==========================================================
# Default Model Path
# ==========================================================

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "car_model"


# ==========================================================
# Result Class
# ==========================================================

class CarPrediction:
    """Single prediction result."""

    def __init__(self, label: str, score: float, rank: int):
        self.label = label        # e.g. "2010 Ford Mustang Coupe"
        self.score = score        # confidence 0.0 → 1.0
        self.rank = rank          # 1 = top prediction

        # Parse label parts (format: "YEAR MAKE MODEL BODY")
        parts = label.split(" ", 2)
        self.year  = parts[0] if len(parts) > 0 else None
        self.make  = parts[1] if len(parts) > 1 else None
        self.model = parts[2] if len(parts) > 2 else None

    @property
    def confidence_pct(self) -> float:
        return round(self.score * 100, 2)

    def to_dict(self) -> dict:
        return {
            "rank":       self.rank,
            "label":      self.label,
            "score":      round(self.score, 6),
            "confidence": self.confidence_pct,
            "year":       self.year,
            "make":       self.make,
            "model":      self.model,
        }

    def __repr__(self) -> str:
        return (
            f"CarPrediction(rank={self.rank}, "
            f"label='{self.label}', "
            f"confidence={self.confidence_pct}%)"
        )


# ==========================================================
# Classifier
# ==========================================================

class CarClassifier:
    """
    Wraps ConvNext car classification model (1992–2012).

    Parameters
    ----------
    model_path : str | Path | None
        Path to the local model directory.
        Defaults to 'car_model/' next to this file.

    device : str | None
        'cuda', 'cpu', or None (auto-detect).

    top_k : int
        Number of top predictions to return. Default: 5.
    """

    def __init__(
        self,
        model_path: Union[str, Path, None] = None,
        device: Union[str, None] = None,
        top_k: int = 5,
    ) -> None:

        self.model_path = Path(model_path or DEFAULT_MODEL_PATH)
        self.top_k = top_k
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self._processor = None
        self._model = None

        self._load()

    # ----------------------------------------------------------
    # Private — Load
    # ----------------------------------------------------------

    def _load(self) -> None:
        """Load processor and model from disk."""

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model directory not found: {self.model_path}\n"
                "Make sure the 'car_model' folder is in the right place."
            )

        logger.info("Loading car classification model from: %s", self.model_path)

        self._processor = AutoImageProcessor.from_pretrained(
            str(self.model_path)
        )

        self._model = ConvNextForImageClassification.from_pretrained(
            str(self.model_path)
        )

        self._model.eval()
        self._model.to(self.device)

        num_classes = len(self._model.config.id2label)
        logger.info(
            "Model loaded — %d classes — device: %s",
            num_classes,
            self.device,
        )

    # ----------------------------------------------------------
    # Private — Prepare Image
    # ----------------------------------------------------------

    def _prepare_image(
        self,
        image: Union[str, Path, Image.Image],
    ) -> Image.Image:
        """Accept PIL Image or file path and return RGB PIL Image."""

        if isinstance(image, (str, Path)):
            image = Image.open(image)

        if not isinstance(image, Image.Image):
            raise TypeError(
                f"Expected PIL Image or file path, got {type(image)}"
            )

        return image.convert("RGB")

    # ----------------------------------------------------------
    # Public — Predict
    # ----------------------------------------------------------

    def predict(
        self,
        image: Union[str, Path, Image.Image],
        top_k: Union[int, None] = None,
    ) -> list[CarPrediction]:
        """
        Run inference on a single image.

        Parameters
        ----------
        image : str | Path | PIL.Image
            Input image.

        top_k : int | None
            Override default top_k for this call.

        Returns
        -------
        list[CarPrediction]
            Sorted by confidence descending (index 0 = best match).
        """

        k = top_k or self.top_k

        pil_image = self._prepare_image(image)

        inputs = self._processor(
            images=pil_image,
            return_tensors="pt",
        )

        # Move inputs to same device as model
        inputs = {key: val.to(self.device) for key, val in inputs.items()}

        with torch.no_grad():
            outputs = self._model(**inputs)

        probs = torch.softmax(outputs.logits, dim=-1)
        top_probs, top_ids = torch.topk(probs, k=k)

        results: list[CarPrediction] = []

        for rank, (score, idx) in enumerate(
            zip(top_probs[0], top_ids[0]), start=1
        ):
            label = self._model.config.id2label[idx.item()]

            results.append(
                CarPrediction(
                    label=label,
                    score=score.item(),
                    rank=rank,
                )
            )

        return results

    def predict_top1(
        self,
        image: Union[str, Path, Image.Image],
    ) -> CarPrediction:
        """Return only the single best prediction."""
        return self.predict(image, top_k=1)[0]

    def predict_dict(
        self,
        image: Union[str, Path, Image.Image],
        top_k: Union[int, None] = None,
    ) -> list[dict]:
        """Return predictions as a list of dicts (easy for APIs/JSON)."""
        return [p.to_dict() for p in self.predict(image, top_k=top_k)]

    # ----------------------------------------------------------
    # Info
    # ----------------------------------------------------------

    @property
    def num_classes(self) -> int:
        return len(self._model.config.id2label)

    @property
    def labels(self) -> list[str]:
        return list(self._model.config.id2label.values())

    def get_info(self) -> dict:
        return {
            "model_path": str(self.model_path),
            "num_classes": self.num_classes,
            "device": self.device,
            "top_k": self.top_k,
        }

    def __repr__(self) -> str:
        return (
            f"CarClassifier("
            f"classes={self.num_classes}, "
            f"device='{self.device}')"
        )