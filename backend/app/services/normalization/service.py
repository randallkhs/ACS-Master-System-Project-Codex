from __future__ import annotations

import re
from collections.abc import Iterable

from app.domain.intake import DetectionResult, NormalizedIntake, RawIntakePayload, TimeWindow

STATE_MARKERS = ("DE", "MD", "PA", "NJ")
CANCELLATION_KEYWORDS = {
    "canceled": 1.0,
    "cancelled": 1.0,
    "canseled": 0.82,
    "cancelld": 0.82,
    "canneled": 0.82,
    "cancel": 0.75,
}
WATER_EMERGENCY_KEYWORDS = {
    "water emergency": 0.98,
    "water damage": 0.95,
    "sewage backup": 0.95,
    "burst pipe": 0.95,
    "extraction": 0.92,
    "flood": 0.9,
    "flooding": 0.9,
    "drying": 0.85,
    "moisture": 0.85,
    "dehumidifier": 0.85,
}
MARKER_PATTERN = re.compile(r"(?<![A-Z0-9])(?P<marker>AM|PM|DE|MD|PA|NJ)(?![A-Z0-9])")
WHITESPACE_PATTERN = re.compile(r"\s+")


class IntakeNormalizationService:
    def normalize(self, payload: RawIntakePayload) -> NormalizedIntake:
        title = clean_text(payload.title) or ""
        customer_name = clean_text(payload.customer_name)
        location = clean_text(payload.location)
        description = clean_text(payload.description)
        combined_text = " ".join(
            value for value in (title, description, location, customer_name) if value
        )
        markers = extract_markers(combined_text)

        return NormalizedIntake(
            raw=payload,
            title=title,
            customer_name=customer_name,
            location=location,
            scheduled_date=payload.scheduled_date,
            description=description,
            combined_text=combined_text,
            time_windows=tuple(
                TimeWindow(marker) for marker in markers if marker in TimeWindow.__members__
            ),
            states=tuple(marker for marker in markers if marker in STATE_MARKERS),
            cancellation=detect_keywords(combined_text, CANCELLATION_KEYWORDS),
            water_emergency=detect_keywords(combined_text, WATER_EMERGENCY_KEYWORDS),
            metadata={
                "normalization_steps": (
                    "whitespace_cleanup",
                    "marker_extraction",
                    "keyword_detection",
                ),
            },
        )


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = WHITESPACE_PATTERN.sub(" ", value).strip()
    return normalized or None


def extract_markers(value: str) -> tuple[str, ...]:
    matches = (match.group("marker") for match in MARKER_PATTERN.finditer(value.upper()))
    return dedupe_preserving_order(matches)


def detect_keywords(value: str, keyword_scores: dict[str, float]) -> DetectionResult:
    normalized_value = value.lower()
    matches = tuple(
        keyword for keyword in keyword_scores if keyword_pattern(keyword).search(normalized_value)
    )
    if not matches:
        return DetectionResult()
    return DetectionResult(
        detected=True,
        confidence=max(keyword_scores[match] for match in matches),
        keyword_matches=matches,
    )


def keyword_pattern(keyword: str) -> re.Pattern[str]:
    escaped = re.escape(keyword)
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])")


def dedupe_preserving_order(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


normalization_service = IntakeNormalizationService()
