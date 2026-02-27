"""
analytics.py — Flint-X Demo Target

Intentionally written with performance anti-patterns:
  - Nested O(n²) loops
  - Expensive operations inside loops
  - CPU-bound numeric computation
  - Data-parallel patterns (unvectorized)
  - No caching
"""

import math
import time


# ── Anti-pattern 1: Nested O(n²) loop ─────────────────────────────────────────
def compute_similarity_matrix(vectors):
    """
    Computes pairwise similarity between all vectors.
    O(n²) — classic GPU-offload candidate.
    """
    n = len(vectors)
    matrix = []

    for i in range(n):
        row = []
        for j in range(n):
            # Expensive dot product computed manually inside nested loop
            dot = 0.0
            for k in range(len(vectors[i])):
                dot += vectors[i][k] * vectors[j][k]

            mag_i = math.sqrt(sum(x ** 2 for x in vectors[i]))
            mag_j = math.sqrt(sum(x ** 2 for x in vectors[j]))

            if mag_i == 0 or mag_j == 0:
                similarity = 0.0
            else:
                similarity = dot / (mag_i * mag_j)

            row.append(similarity)
        matrix.append(row)

    return matrix


# ── Anti-pattern 2: CPU-bound loop with math.sqrt inside ──────────────────────
def normalize_dataset(data):
    """
    Normalizes each row in a 2D dataset.
    Calls math.sqrt inside a loop — no vectorization.
    """
    normalized = []

    for row in data:
        total = 0.0
        for val in row:
            total += val ** 2
        magnitude = math.sqrt(total)

        if magnitude == 0:
            normalized.append(row)
        else:
            normalized.append([v / magnitude for v in row])

    return normalized


# ── Anti-pattern 3: Repeated expensive computation, no caching ────────────────
def score_all_pairs(data):
    """
    Scores every pair. Recomputes magnitude every time — no memoization.
    """
    results = []
    n = len(data)

    for i in range(n):
        for j in range(i + 1, n):
            # Recomputes magnitude of i every inner iteration
            mag_i = math.sqrt(sum(x ** 2 for x in data[i]))
            mag_j = math.sqrt(sum(x ** 2 for x in data[j]))
            score = abs(mag_i - mag_j)
            results.append((i, j, score))

    return results


# ── Anti-pattern 4: Data-parallel pattern — unvectorized element-wise ops ─────
def apply_activation(data, alpha=0.01):
    """
    Applies a leaky ReLU activation to every element.
    Perfectly data-parallel — ideal NumPy / GPU candidate.
    Written as plain Python loops instead.
    """
    output = []

    for row in data:
        activated_row = []
        for val in row:
            if val >= 0:
                activated_row.append(val)
            else:
                activated_row.append(alpha * val)
        output.append(activated_row)

    return output


# ── Anti-pattern 5: Accumulation loop that could be a reduction ───────────────
def compute_statistics(data):
    """
    Computes mean and variance manually.
    Could be replaced with numpy.mean / numpy.var.
    """
    flat = [val for row in data for val in row]
    n = len(flat)

    mean = sum(flat) / n

    variance = 0.0
    for val in flat:
        variance += (val - mean) ** 2
    variance /= n

    std_dev = math.sqrt(variance)

    return {"mean": mean, "variance": variance, "std_dev": std_dev}