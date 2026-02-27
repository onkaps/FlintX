"""
data_utils.py — Flint-X Demo Target

Contains:
  - Recursive function (no memoization)
  - Expensive call inside a loop
  - Data generation utilities
"""

import math
import random
import time


# ── Anti-pattern 6: Recursion without memoization ─────────────────────────────
def recursive_fibonacci(n):
    """
    Classic exponential recursion — O(2^n).
    No memoization. Detected as high-complexity recursion.
    """
    if n <= 1:
        return n
    return recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2)


# ── Anti-pattern 7: Expensive call inside a loop ──────────────────────────────
def compute_fibonacci_sequence(limit):
    """
    Calls recursive_fibonacci() for each value up to limit.
    Exponential work repeated in a loop.
    """
    sequence = []
    for i in range(limit):
        sequence.append(recursive_fibonacci(i))
    return sequence


# ── Anti-pattern 8: time.sleep inside a loop (IO stall simulation) ────────────
def fetch_data_simulation(n_records):
    """
    Simulates slow data fetching.
    Artificial stall to make profiler hotspots visible.
    """
    records = []
    for i in range(n_records):
        time.sleep(0.001)   # 1ms stall per record
        records.append({
            "id": i,
            "value": math.sin(i) * math.cos(i),
        })
    return records


# ── Data generation ───────────────────────────────────────────────────────────
def generate_random_vectors(n, dim, seed=42):
    """
    Generates n random vectors of dimension dim.
    Used as input for analytics.py functions.
    """
    random.seed(seed)
    return [
        [random.uniform(-1.0, 1.0) for _ in range(dim)]
        for _ in range(n)
    ]


def generate_random_matrix(rows, cols, seed=42):
    """
    Generates a random 2D matrix.
    """
    random.seed(seed)
    return [
        [random.uniform(0.0, 1.0) for _ in range(cols)]
        for _ in range(rows)
    ]