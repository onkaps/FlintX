"""
runner.py — Flint-X Demo Entry Point

Runs all analytics functions in sequence.
This is the script Flint-X will profile.
"""

import time
from analytics import (
    compute_similarity_matrix,
    normalize_dataset,
    score_all_pairs,
    apply_activation,
    compute_statistics,
)
from data_utils import (
    generate_random_vectors,
    generate_random_matrix,
    compute_fibonacci_sequence,
    fetch_data_simulation,
)


def main():
    print("=" * 55)
    print("  Flint-X Demo Analytics Backend")
    print("=" * 55)

    # ── Stage 1: Similarity Matrix (O(n²) nested loops) ───────────────────────
    print("\n[1/5] Computing similarity matrix (50 vectors, dim=20)...")
    t0 = time.time()
    vectors = generate_random_vectors(n=50, dim=20)
    matrix = compute_similarity_matrix(vectors)
    t1 = time.time()
    print(f"      Done. Matrix shape: {len(matrix)}x{len(matrix[0])}  [{t1-t0:.3f}s]")

    # ── Stage 2: Normalize Dataset ────────────────────────────────────────────
    print("\n[2/5] Normalizing dataset (200 rows, 50 cols)...")
    t0 = time.time()
    raw_data = generate_random_matrix(rows=200, cols=50)
    normalized = normalize_dataset(raw_data)
    t1 = time.time()
    print(f"      Done. Normalized {len(normalized)} rows  [{t1-t0:.3f}s]")

    # ── Stage 3: Score All Pairs ──────────────────────────────────────────────
    print("\n[3/5] Scoring all pairs (100 rows)...")
    t0 = time.time()
    data_for_pairs = generate_random_matrix(rows=100, cols=20)
    scores = score_all_pairs(data_for_pairs)
    t1 = time.time()
    print(f"      Done. {len(scores)} pairs scored  [{t1-t0:.3f}s]")

    # ── Stage 4: Apply Activation + Compute Stats ─────────────────────────────
    print("\n[4/5] Applying activation + computing statistics...")
    t0 = time.time()
    activated = apply_activation(normalized)
    stats = compute_statistics(activated)
    t1 = time.time()
    print(f"      Done. mean={stats['mean']:.4f}  std={stats['std_dev']:.4f}  [{t1-t0:.3f}s]")

    # ── Stage 5: Fibonacci (recursive, no memoization) ────────────────────────
    print("\n[5/5] Computing Fibonacci sequence (limit=25, recursive)...")
    t0 = time.time()
    fib_seq = compute_fibonacci_sequence(limit=25)
    t1 = time.time()
    print(f"      Done. fib(24)={fib_seq[-1]}  [{t1-t0:.3f}s]")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  All stages complete.")
    print("  This workload is ready for Flint-X analysis.")
    print("=" * 55)


if __name__ == "__main__":
    main()