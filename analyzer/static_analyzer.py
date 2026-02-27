"""
static_analyzer.py — Core AST analysis engine for Flint-X.

Walks Python source files and detects performance anti-patterns.
Returns a structured dict ready for JSON serialization.
"""

import ast
import os
from typing import Any
from patterns import (
    EXPENSIVE_CALLS,
    EXPENSIVE_ATTR_CALLS,
    COMPLEXITY_THRESHOLD,
    LOOP_DEPTH_THRESHOLD,
    FUNCTION_LENGTH_THRESHOLD,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_call_name(node: ast.Call) -> tuple[str, str] | None:
    """Extract (module, func) or (None, func) from a Call node."""
    if isinstance(node.func, ast.Attribute):
        if isinstance(node.func.value, ast.Name):
            return (node.func.value.id, node.func.attr)
    if isinstance(node.func, ast.Name):
        return (None, node.func.id)
    return None


def _is_expensive_call(node: ast.Call) -> bool:
    name = _get_call_name(node)
    if name is None:
        return False
    module, func = name
    if (module, func) in EXPENSIVE_ATTR_CALLS:
        return True
    if func in EXPENSIVE_CALLS:
        return True
    return False


# ── Loop Depth Detector ───────────────────────────────────────────────────────

class LoopDepthVisitor(ast.NodeVisitor):
    """
    Finds all loops and measures their nesting depth.
    Also collects expensive calls found inside loops.
    """

    def __init__(self):
        self.findings = []          # list of dicts per loop finding
        self._depth = 0
        self._loop_stack = []       # stack of (depth, lineno)

    def _visit_loop(self, node):
        self._depth += 1
        self._loop_stack.append((self._depth, node.lineno))

        # Scan for expensive calls at this loop level
        expensive_found = []
        for child in ast.walk(node):
            if child is node:
                continue
            # Don't descend into nested loops for call detection here
            if isinstance(child, (ast.For, ast.While)) and child is not node:
                break
            if isinstance(child, ast.Call) and _is_expensive_call(child):
                call_name = _get_call_name(child)
                if call_name:
                    expensive_found.append(
                        f"{call_name[0]}.{call_name[1]}"
                        if call_name[0]
                        else call_name[1]
                    )

        if self._depth >= LOOP_DEPTH_THRESHOLD or expensive_found:
            self.findings.append({
                "line": node.lineno,
                "loop_depth": self._depth,
                "flagged_nested": self._depth >= LOOP_DEPTH_THRESHOLD,
                "expensive_calls_inside": list(set(expensive_found)),
            })

        self.generic_visit(node)
        self._depth -= 1
        self._loop_stack.pop()

    def visit_For(self, node):
        self._visit_loop(node)

    def visit_While(self, node):
        self._visit_loop(node)


# ── Recursion Detector ────────────────────────────────────────────────────────

class RecursionVisitor(ast.NodeVisitor):
    """
    Detects functions that call themselves directly (direct recursion).
    """

    def __init__(self):
        self.recursive_functions = []
        self._current_function = None

    def visit_FunctionDef(self, node):
        previous = self._current_function
        self._current_function = node.name
        self.generic_visit(node)
        self._current_function = previous

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Call(self, node):
        if self._current_function:
            name = _get_call_name(node)
            if name and name[1] == self._current_function:
                self.recursive_functions.append({
                    "function": self._current_function,
                    "line": node.lineno,
                    "note": "Direct recursion detected — no memoization check possible statically",
                })
        self.generic_visit(node)


# ── Cyclomatic Complexity Calculator ─────────────────────────────────────────

class ComplexityVisitor(ast.NodeVisitor):
    """
    Computes a per-function cyclomatic complexity estimate.
    Complexity = 1 + number of decision points (if/elif/for/while/except/and/or)
    """

    def __init__(self):
        self.functions = []

    def visit_FunctionDef(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While,
                                   ast.ExceptHandler, ast.With,
                                   ast.Assert)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        length = node.end_lineno - node.lineno + 1 if hasattr(node, "end_lineno") else 0

        self.functions.append({
            "function": node.name,
            "line": node.lineno,
            "complexity": complexity,
            "length_lines": length,
            "flagged_complexity": complexity >= COMPLEXITY_THRESHOLD,
            "flagged_length": length >= FUNCTION_LENGTH_THRESHOLD,
        })

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)


# ── Data Parallel Pattern Detector ───────────────────────────────────────────

class DataParallelVisitor(ast.NodeVisitor):
    """
    Detects patterns that are inherently data-parallel:
      - Element-wise loops (nested for loops applying same op to each element)
      - Reduction loops (accumulating into a single variable)
      - Map patterns (appending transformed values to a list)
    """

    def __init__(self):
        self.patterns = []

    def visit_FunctionDef(self, node):
        outer_loops = [n for n in ast.walk(node) if isinstance(n, ast.For)]

        for loop in outer_loops:
            # Check for append inside loop → map pattern
            appends = [
                n for n in ast.walk(loop)
                if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr == "append"
            ]

            # Check for augmented assign inside loop → reduction
            reductions = [
                n for n in ast.walk(loop)
                if isinstance(n, ast.AugAssign)
            ]

            # Check for nested for loop → potential matrix / element-wise
            nested_fors = [
                n for n in ast.walk(loop)
                if isinstance(n, ast.For) and n is not loop
            ]

            if nested_fors and appends:
                self.patterns.append({
                    "function": node.name,
                    "line": loop.lineno,
                    "pattern": "element_wise_loop",
                    "description": "Nested loop with append — data-parallel candidate (vectorization / GPU)",
                })

            if reductions and not nested_fors:
                self.patterns.append({
                    "function": node.name,
                    "line": loop.lineno,
                    "pattern": "reduction_loop",
                    "description": "Manual accumulation loop — candidate for numpy reduction or parallel reduce",
                })

            if appends and not nested_fors and not reductions:
                self.patterns.append({
                    "function": node.name,
                    "line": loop.lineno,
                    "pattern": "map_pattern",
                    "description": "Loop with append — candidate for list comprehension, map(), or vectorization",
                })

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)


# ── Main Analyzer ─────────────────────────────────────────────────────────────

def analyze_file(filepath: str) -> dict[str, Any]:
    """
    Runs all AST visitors on a single Python file.
    Returns a structured analysis dict.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        return {
            "file": filepath,
            "error": f"SyntaxError: {e}",
            "loops": [],
            "recursion": [],
            "complexity": [],
            "data_parallel_patterns": [],
            "summary": {},
        }

    # Run all visitors
    loop_visitor = LoopDepthVisitor()
    loop_visitor.visit(tree)

    recursion_visitor = RecursionVisitor()
    recursion_visitor.visit(tree)

    complexity_visitor = ComplexityVisitor()
    complexity_visitor.visit(tree)

    parallel_visitor = DataParallelVisitor()
    parallel_visitor.visit(tree)

    # Build summary flags
    has_nested_loops      = any(f["flagged_nested"] for f in loop_visitor.findings)
    has_expensive_in_loop = any(f["expensive_calls_inside"] for f in loop_visitor.findings)
    has_recursion         = len(recursion_visitor.recursive_functions) > 0
    has_high_complexity   = any(f["flagged_complexity"] for f in complexity_visitor.functions)
    has_parallel_patterns = len(parallel_visitor.patterns) > 0

    gpu_offload_candidate = has_nested_loops or has_parallel_patterns
    cpu_bound_indicator   = has_nested_loops or has_expensive_in_loop or has_high_complexity

    return {
        "file": filepath,
        "loops": loop_visitor.findings,
        "recursion": recursion_visitor.recursive_functions,
        "complexity": complexity_visitor.functions,
        "data_parallel_patterns": parallel_visitor.patterns,
        "summary": {
            "has_nested_loops": has_nested_loops,
            "has_expensive_calls_in_loops": has_expensive_in_loop,
            "has_recursion": has_recursion,
            "has_high_complexity": has_high_complexity,
            "has_data_parallel_patterns": has_parallel_patterns,
            "gpu_offload_candidate": gpu_offload_candidate,
            "cpu_bound_indicator": cpu_bound_indicator,
        },
    }


def analyze_directory(dirpath: str) -> dict[str, Any]:
    """
    Analyzes all .py files in a directory.
    Returns a combined report.
    """
    results = []
    for root, _, files in os.walk(dirpath):
        for fname in files:
            if fname.endswith(".py"):
                full_path = os.path.join(root, fname)
                results.append(analyze_file(full_path))

    # Aggregate summary across all files
    combined_summary = {
        "has_nested_loops":              any(r["summary"].get("has_nested_loops") for r in results),
        "has_expensive_calls_in_loops":  any(r["summary"].get("has_expensive_calls_in_loops") for r in results),
        "has_recursion":                 any(r["summary"].get("has_recursion") for r in results),
        "has_high_complexity":           any(r["summary"].get("has_high_complexity") for r in results),
        "has_data_parallel_patterns":    any(r["summary"].get("has_data_parallel_patterns") for r in results),
        "gpu_offload_candidate":         any(r["summary"].get("gpu_offload_candidate") for r in results),
        "cpu_bound_indicator":           any(r["summary"].get("cpu_bound_indicator") for r in results),
        "files_analyzed":                len(results),
    }

    return {
        "type": "directory",
        "path": dirpath,
        "files": results,
        "summary": combined_summary,
    }