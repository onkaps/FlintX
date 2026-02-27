"""
patterns.py — Pattern definitions for Flint-X static analysis.

Defines:
  - Which function calls are considered "expensive"
  - Which patterns indicate data-parallel workloads
  - Complexity thresholds
"""

# Calls that are expensive inside loops
EXPENSIVE_CALLS = {
    # Math operations
    "sqrt", "pow", "log", "log2", "log10", "exp",
    "sin", "cos", "tan", "atan2", "hypot",
    # IO / network
    "sleep", "open", "read", "write", "connect", "send", "recv",
    # Sorting / searching
    "sort", "sorted", "min", "max", "sum",
    # String ops
    "join", "split", "replace", "encode", "decode",
    # Subprocess
    "run", "call", "Popen",
    # Recursive triggers (common names)
    "fibonacci", "factorial", "fib",
}

# Attribute calls considered expensive: e.g. time.sleep, math.sqrt
EXPENSIVE_ATTR_CALLS = {
    ("math", "sqrt"), ("math", "pow"), ("math", "log"),
    ("math", "sin"),  ("math", "cos"), ("math", "exp"),
    ("time", "sleep"), ("os", "system"), ("random", "random"),
    ("random", "uniform"), ("random", "randint"),
}

# Patterns that suggest data-parallel workloads
DATA_PARALLEL_PATTERNS = {
    "element_wise_loop",     # loop over rows + loop over cols applying same op
    "map_pattern",           # applying same function to every element
    "reduction_loop",        # accumulating sum/product manually
    "matrix_row_operation",  # operating on each row independently
}

# Thresholds
COMPLEXITY_THRESHOLD       = 7    # cyclomatic complexity above this → flagged
LOOP_DEPTH_THRESHOLD       = 2    # nested loops at this depth → flagged
FUNCTION_LENGTH_THRESHOLD  = 40   # lines above this → flagged
RECURSION_DEPTH_WARNING    = 1    # any recursion → flagged