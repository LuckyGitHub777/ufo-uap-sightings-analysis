from __future__ import annotations

import math
import random
from collections.abc import Sequence


def mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("mean requires at least one value")
    return sum(values) / len(values)


def pearson_r(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) != len(ys):
        raise ValueError("paired values must have the same length")
    if len(xs) < 2:
        return 0.0
    x_mean = mean(xs)
    y_mean = mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys, strict=True))
    x_ss = sum((x - x_mean) ** 2 for x in xs)
    y_ss = sum((y - y_mean) ** 2 for y in ys)
    denominator = math.sqrt(x_ss * y_ss)
    return 0.0 if denominator == 0 else numerator / denominator


def simple_linear_regression(xs: Sequence[float], ys: Sequence[float]) -> tuple[float, float, float]:
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("regression requires at least two paired values")
    x_mean = mean(xs)
    y_mean = mean(ys)
    x_ss = sum((x - x_mean) ** 2 for x in xs)
    if x_ss == 0:
        return 0.0, y_mean, 0.0
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys, strict=True)) / x_ss
    intercept = y_mean - slope * x_mean
    predictions = [intercept + slope * x for x in xs]
    total_ss = sum((y - y_mean) ** 2 for y in ys)
    residual_ss = sum((y - p) ** 2 for y, p in zip(ys, predictions, strict=True))
    r_squared = 0.0 if total_ss == 0 else 1 - residual_ss / total_ss
    return slope, intercept, r_squared


def permutation_p_value(
    group_a: Sequence[float],
    group_b: Sequence[float],
    *,
    iterations: int = 4000,
    seed: int = 20241205,
) -> float:
    if not group_a or not group_b:
        raise ValueError("both groups must contain values")
    observed = abs(mean(group_a) - mean(group_b))
    combined = list(group_a) + list(group_b)
    split = len(group_a)
    rng = random.Random(seed)
    extreme = 0
    for _ in range(iterations):
        shuffled = list(combined)
        rng.shuffle(shuffled)
        delta = abs(mean(shuffled[:split]) - mean(shuffled[split:]))
        if delta >= observed:
            extreme += 1
    return (extreme + 1) / (iterations + 1)
