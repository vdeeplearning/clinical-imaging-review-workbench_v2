from __future__ import annotations

import math
from typing import Iterable, Sequence


def euclidean_distance_3d(
    x1: float,
    y1: float,
    z1: float,
    x2: float,
    y2: float,
    z2: float,
) -> float:
    """
    Compute 3D Euclidean distance between two points.
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def total_lesion_burden(long_diameters: Iterable[float]) -> float:
    """
    Sum long diameters across lesions for a scan.
    """
    return sum(long_diameters)


def endpoints_are_identical(
    x1: float,
    y1: float,
    z1: float,
    x2: float,
    y2: float,
    z2: float,
) -> bool:
    """
    Return True if both endpoints are exactly the same.
    """
    return x1 == x2 and y1 == y2 and z1 == z2


def short_greater_than_long(long_diameter: float, short_diameter: float) -> bool:
    """
    Soft warning condition: short axis exceeds long axis.
    """
    return short_diameter > long_diameter


def duplicate_labels(labels: Sequence[str]) -> list[str]:
    """
    Return duplicate lesion labels (case-insensitive, trimmed).
    """
    normalized_seen: set[str] = set()
    duplicates: set[str] = set()

    for label in labels:
        normalized = label.strip().lower()
        if not normalized:
            continue
        if normalized in normalized_seen:
            duplicates.add(label.strip())
        else:
            normalized_seen.add(normalized)

    return sorted(duplicates)
    