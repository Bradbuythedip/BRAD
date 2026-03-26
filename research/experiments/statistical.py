"""
statistical.py — Statistical Testing Utilities

Provides non-parametric statistical tests for comparing experimental
conditions. Implements tests without external dependencies (no scipy).

Tests:
    - Mann-Whitney U test (non-parametric, two-sample)
    - Bootstrap confidence intervals
    - Cohen's d effect size
    - Permutation test
    - Bonferroni correction for multiple comparisons

All tests are implemented from scratch for reproducibility and
to avoid dependency on scipy/numpy.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import math
import random


@dataclass
class TestResult:
    """Result of a statistical test."""
    test_name: str
    statistic: float
    p_value: float
    effect_size: float  # Cohen's d
    ci_lower: float = 0.0
    ci_upper: float = 0.0
    significant_05: bool = False
    significant_01: bool = False
    significant_001: bool = False
    n1: int = 0
    n2: int = 0

    def __post_init__(self):
        self.significant_05 = self.p_value < 0.05
        self.significant_01 = self.p_value < 0.01
        self.significant_001 = self.p_value < 0.001

    @property
    def significance_stars(self) -> str:
        if self.significant_001:
            return "***"
        if self.significant_01:
            return "**"
        if self.significant_05:
            return "*"
        return "ns"


# ============================================================================
# DESCRIPTIVE STATISTICS
# ============================================================================

def mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def variance(values: List[float], ddof: int = 1) -> float:
    if len(values) <= ddof:
        return 0.0
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / (len(values) - ddof)


def std(values: List[float], ddof: int = 1) -> float:
    return math.sqrt(variance(values, ddof))


def median(values: List[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    if n % 2 == 0:
        return (s[n // 2 - 1] + s[n // 2]) / 2
    return s[n // 2]


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * p / 100
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[int(f)] * (c - k) + s[int(c)] * (k - f)


def descriptive_stats(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"n": 0, "mean": 0, "std": 0, "median": 0,
                "min": 0, "max": 0, "q25": 0, "q75": 0}
    return {
        "n": len(values),
        "mean": mean(values),
        "std": std(values),
        "median": median(values),
        "min": min(values),
        "max": max(values),
        "q25": percentile(values, 25),
        "q75": percentile(values, 75),
    }


# ============================================================================
# EFFECT SIZE
# ============================================================================

def cohens_d(group1: List[float], group2: List[float]) -> float:
    """
    Cohen's d effect size (pooled standard deviation).

    d = (M1 - M2) / S_pooled

    where S_pooled = sqrt(((n1-1)*s1^2 + (n2-1)*s2^2) / (n1+n2-2))

    Interpretation:
        |d| < 0.2: negligible
        0.2 <= |d| < 0.5: small
        0.5 <= |d| < 0.8: medium
        |d| >= 0.8: large
    """
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0

    m1, m2 = mean(group1), mean(group2)
    v1, v2 = variance(group1), variance(group2)

    pooled_var = ((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2)
    if pooled_var == 0:
        return 0.0  # Both groups constant — no meaningful effect size

    pooled_std = math.sqrt(pooled_var)
    return (m1 - m2) / pooled_std


def effect_size_interpretation(d: float) -> str:
    d = abs(d)
    if d < 0.2:
        return "negligible"
    if d < 0.5:
        return "small"
    if d < 0.8:
        return "medium"
    return "large"


# ============================================================================
# MANN-WHITNEY U TEST
# ============================================================================

def mann_whitney_u(group1: List[float], group2: List[float]) -> TestResult:
    """
    Mann-Whitney U test (Wilcoxon rank-sum test).

    Non-parametric test for whether two independent samples come from
    the same distribution. Does not assume normality.

    Uses normal approximation for p-value (valid for n >= 20).

    H0: The distributions of both groups are equal.
    H1: The distributions differ.
    """
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return TestResult("mann_whitney_u", 0, 1.0, 0.0, n1=n1, n2=n2)

    # Rank all values
    combined = [(v, 0) for v in group1] + [(v, 1) for v in group2]
    combined.sort(key=lambda x: x[0])

    # Assign ranks (handle ties by averaging)
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2  # 1-indexed
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    # Sum ranks for group 1
    r1 = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 0)

    # U statistic
    u1 = r1 - n1 * (n1 + 1) / 2
    u2 = n1 * n2 - u1
    u = min(u1, u2)

    # Normal approximation
    mu = n1 * n2 / 2
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)

    if sigma == 0:
        return TestResult("mann_whitney_u", u, 1.0, cohens_d(group1, group2),
                         n1=n1, n2=n2)

    z = (u - mu) / sigma
    # Two-tailed p-value from z using approximation
    p = 2 * _normal_cdf(-abs(z))

    d = cohens_d(group1, group2)

    return TestResult(
        test_name="mann_whitney_u",
        statistic=u,
        p_value=p,
        effect_size=d,
        n1=n1,
        n2=n2,
    )


# ============================================================================
# PERMUTATION TEST
# ============================================================================

def permutation_test(group1: List[float], group2: List[float],
                     num_permutations: int = 10000,
                     seed: int = 42) -> TestResult:
    """
    Permutation test for difference in means.

    Non-parametric, exact (up to number of permutations).
    No distributional assumptions.
    """
    rng = random.Random(seed)
    n1 = len(group1)
    observed_diff = abs(mean(group1) - mean(group2))

    combined = group1 + group2
    count_extreme = 0

    for _ in range(num_permutations):
        rng.shuffle(combined)
        perm_diff = abs(mean(combined[:n1]) - mean(combined[n1:]))
        if perm_diff >= observed_diff:
            count_extreme += 1

    p = (count_extreme + 1) / (num_permutations + 1)
    d = cohens_d(group1, group2)

    return TestResult(
        test_name="permutation_test",
        statistic=observed_diff,
        p_value=p,
        effect_size=d,
        n1=len(group1),
        n2=len(group2),
    )


# ============================================================================
# BOOTSTRAP CONFIDENCE INTERVAL
# ============================================================================

def bootstrap_ci(values: List[float], confidence: float = 0.95,
                 num_bootstrap: int = 10000,
                 seed: int = 42) -> Tuple[float, float, float]:
    """
    Bootstrap confidence interval for the mean.

    Returns (mean, ci_lower, ci_upper).
    """
    rng = random.Random(seed)
    n = len(values)
    if n == 0:
        return (0.0, 0.0, 0.0)

    bootstrap_means = []
    for _ in range(num_bootstrap):
        sample = [values[rng.randint(0, n - 1)] for _ in range(n)]
        bootstrap_means.append(mean(sample))

    bootstrap_means.sort()
    alpha = 1 - confidence
    lower_idx = int(alpha / 2 * num_bootstrap)
    upper_idx = int((1 - alpha / 2) * num_bootstrap)

    return (
        mean(values),
        bootstrap_means[lower_idx],
        bootstrap_means[min(upper_idx, num_bootstrap - 1)],
    )


def bootstrap_difference_ci(group1: List[float], group2: List[float],
                             confidence: float = 0.95,
                             num_bootstrap: int = 10000,
                             seed: int = 42) -> Tuple[float, float, float]:
    """
    Bootstrap CI for the difference in means (group1 - group2).

    If the CI excludes 0, the difference is significant.
    """
    rng = random.Random(seed)
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return (0.0, 0.0, 0.0)

    diffs = []
    for _ in range(num_bootstrap):
        s1 = [group1[rng.randint(0, n1 - 1)] for _ in range(n1)]
        s2 = [group2[rng.randint(0, n2 - 1)] for _ in range(n2)]
        diffs.append(mean(s1) - mean(s2))

    diffs.sort()
    alpha = 1 - confidence
    lower_idx = int(alpha / 2 * num_bootstrap)
    upper_idx = int((1 - alpha / 2) * num_bootstrap)

    return (
        mean(group1) - mean(group2),
        diffs[lower_idx],
        diffs[min(upper_idx, num_bootstrap - 1)],
    )


# ============================================================================
# MULTIPLE COMPARISONS CORRECTION
# ============================================================================

def bonferroni_correction(p_values: List[float]) -> List[float]:
    """Bonferroni correction: multiply p-values by number of comparisons."""
    n = len(p_values)
    return [min(1.0, p * n) for p in p_values]


def holm_bonferroni_correction(p_values: List[float]) -> List[float]:
    """Holm-Bonferroni step-down correction (less conservative)."""
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    corrected = [0.0] * n

    for rank, (orig_idx, p) in enumerate(indexed):
        corrected[orig_idx] = min(1.0, p * (n - rank))

    # Enforce monotonicity
    for i in range(1, n):
        orig_idx = indexed[i][0]
        prev_idx = indexed[i - 1][0]
        corrected[orig_idx] = max(corrected[orig_idx], corrected[prev_idx])

    return corrected


# ============================================================================
# COMPARISON FRAMEWORK
# ============================================================================

def compare_conditions(control: List[float], conditions: Dict[str, List[float]],
                       test: str = "permutation",
                       seed: int = 42) -> Dict[str, TestResult]:
    """
    Compare multiple conditions against a control.

    Args:
        control: Values from the control condition (FULL architecture).
        conditions: {condition_name: values} for each ablation.
        test: "mann_whitney" or "permutation".
        seed: Random seed for permutation test.

    Returns:
        {condition_name: TestResult}
    """
    results = {}
    p_values = []

    for name, values in conditions.items():
        if test == "mann_whitney":
            result = mann_whitney_u(control, values)
        else:
            result = permutation_test(control, values, seed=seed)

        # Add bootstrap CI
        diff, ci_lo, ci_hi = bootstrap_difference_ci(
            control, values, seed=seed)
        result.ci_lower = ci_lo
        result.ci_upper = ci_hi

        results[name] = result
        p_values.append(result.p_value)

    # Apply Holm-Bonferroni correction
    corrected = holm_bonferroni_correction(p_values)
    for i, (name, result) in enumerate(results.items()):
        result.p_value = corrected[i]
        result.significant_05 = result.p_value < 0.05
        result.significant_01 = result.p_value < 0.01
        result.significant_001 = result.p_value < 0.001

    return results


def print_comparison_table(results: Dict[str, TestResult],
                            metric_name: str = "metric"):
    """Print a formatted comparison table."""
    print(f"\n  Statistical comparison: {metric_name}")
    print(f"  {'Condition':<18} {'U/T':>8} {'p':>8} {'d':>8} "
          f"{'CI_lo':>8} {'CI_hi':>8} {'Sig':>5}")
    print(f"  {'-'*18} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*5}")

    for name, result in results.items():
        d_display = max(-99.99, min(99.99, result.effect_size))
        print(f"  {name:<18} {result.statistic:>8.1f} {result.p_value:>8.4f} "
              f"{d_display:>8.3f} {result.ci_lower:>8.4f} "
              f"{result.ci_upper:>8.4f} {result.significance_stars:>5}")


# ============================================================================
# INTERNAL: Normal CDF approximation
# ============================================================================

def _normal_cdf(x: float) -> float:
    """Approximation of the standard normal CDF.

    Uses Abramowitz and Stegun approximation (error < 1.5e-7).
    """
    if x < -8:
        return 0.0
    if x > 8:
        return 1.0

    # Constants
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911

    sign = 1
    if x < 0:
        sign = -1
    x = abs(x) / math.sqrt(2)

    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)

    return 0.5 * (1.0 + sign * y)
