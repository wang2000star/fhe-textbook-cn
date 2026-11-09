#!/usr/bin/env python3
"""Reproducible checks of the conditional CKKS/Meta-BTS follow-up proof.

The residual recursion and counterexamples use exact rational arithmetic.
The final polynomial example is a floating-point sanity check of a separately
proved analytic bound, NOT a certified CKKS implementation or a security test.
Real OpenFHE execution is recorded separately by run_openfhe_meta_bts.py.
Run: python audit/check_meta_bts.py [--json]
"""
from __future__ import annotations

import argparse
import cmath
import itertools
import json
import math
from fractions import Fraction as F

RESULTS = []


def result(name, cases, evidence, kind="exact_rational"):
    RESULTS.append({"name": name, "checked_cases": cases, "kind": kind,
                    "findings": ["CBR-016", "CBR-017"], "evidence": evidence})


def prod(values):
    return math.prod(values)


def nearest(x):
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def centered(x, q):
    return (x + q // 2) % q - q // 2


class BoundedOracle:
    """A deterministic, possibly correlated/adaptive decoded-error oracle."""

    def __init__(self, eps, rho, mode, shared_sign):
        self.eps, self.rho = eps, rho
        self.mode, self.shared_sign = mode, shared_sign
        self.calls, self.inputs, self.last_error = 0, [], None

    def sign(self, x, salt=0):
        if self.mode == "shared":
            return self.shared_sign
        if self.mode == "adaptive":
            return self.shared_sign * (1 if x >= 0 else -1)
        return self.shared_sign * (1 if (self.calls + salt) % 2 else -1)

    def bootstrap(self, x):
        assert abs(x) <= 1, ("base input exceeds contract", x)
        self.inputs.append(x)
        self.last_error = self.eps * self.sign(x)
        self.calls += 1
        return x + self.last_error

    def rescale_error(self, x, lower_product):
        return self.rho * self.sign(x, salt=1) / lower_product


def recursive_meta(depth, x, gains, oracle, delta=F(4096)):
    """Exact decoded model; explicit physical phases keep all scale changes."""
    if depth == 1:
        return oracle.bootstrap(x)
    lower_product = prod(gains[:depth - 2])
    gain = gains[depth - 2]
    out_product = lower_product * gain
    r = oracle.rescale_error(x, lower_product)
    y = recursive_meta(depth - 1, x + r, gains, oracle, delta)
    h_phase = gain * lower_product * delta * y
    input_phase = out_product * delta * x
    residual_at_base_scale = (h_phase - input_phase) / delta
    corrected_residual = oracle.bootstrap(residual_at_base_scale)
    out = (h_phase - delta * corrected_residual) / (out_product * delta)
    assert out == x - oracle.last_error / out_product
    return out


def check_correlated_recursion():
    eps, rho = F(1, 32), F(1, 128)
    cases = 0
    gain_sets = [(2, 2, 2, 2), (3, 5, 7, 11), (17, 13, 11, 7), (2, 3, 5, 7)]
    for gains, depth, mode, sign, numerator in itertools.product(
            gain_sets, range(1, 6), ["shared", "adaptive", "alternating"],
            [-1, 1], range(-14, 15)):
        x = F(numerator, 16)
        factors = gains[:depth - 1]
        products = [prod(factors[:j]) for j in range(depth)]
        assert all(a * (rho + eps) <= 1 for a in factors)
        assert abs(x) + rho * sum(F(1, p) for p in products[:-1]) <= 1
        oracle = BoundedOracle(eps, rho, mode, sign)
        y = recursive_meta(depth, x, gains, oracle)
        assert oracle.calls == depth
        expected_error = oracle.last_error if depth == 1 else -oracle.last_error / products[-1]
        assert y - x == expected_error
        assert abs(y - x) <= eps / products[-1]
        cases += 1
    result("correlated_and_adaptive_residual_recursion", cases,
           {"base_epsilon": str(eps), "rescale_rho": str(rho),
            "depths": [1, 2, 3, 4, 5],
            "statement": "First rescale and all preceding errors cancel pathwise; no independence used."})


def check_headroom_and_rns():
    a, eps, rho = 256, F(1, 256), F(1, 65536)
    assert a * (eps + rho) == F(257, 256) > 1
    assert F(1) + rho > 1
    smaller_gain = 128
    assert smaller_gain * (eps + rho) < 1
    # The exact RNS factor and its nominal power of two differ by only 1.
    nominal, actual, x = 65536, 65537, F(1, 2)
    b = -F(3, 4 * nominal)
    wrong_residual = (nominal - actual) * x + nominal * b
    exact_residual = actual * b
    assert wrong_residual == -F(5, 4)
    assert abs(exact_residual) < 1 < abs(wrong_residual)
    d1, d2, w = F(2**40), F(2**39), 2**40 + 87
    assert d1 * d2 / w != d2
    phase, scale = F(17), F(8)
    assert phase / (scale * 4) == (phase / scale) / 4
    assert (phase * 4) / (scale * 4) == phase / scale
    result("input_headroom_and_actual_rns_factor", 8,
           {"no_slack_residual": str(a * (eps + rho)),
            "nominal_factor_residual": str(wrong_residual),
            "actual_factor_residual": str(exact_residual),
            "actual_product_rescale_scale": str(d1 * d2 / w)})


def negacyclic(a, b):
    n = len(a)
    out = [F(0)] * n
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[(i + j) % n] += x * y * (-1 if i + j >= n else 1)
    return out


def check_rounding_bound():
    cases = 0
    for n, w, seed in itertools.product((2, 4, 8), (3, 5, 17), range(-8, 9)):
        s = [(j + seed) % 3 - 1 for j in range(n)]
        aa = [43 * seed + 7 * j for j in range(n)]
        bb = [-31 * seed + 9 * j for j in range(n)]
        ra = [F(nearest(F(a, w))) - F(a, w) for a in aa]
        rb = [F(nearest(F(b, w))) - F(b, w) for b in bb]
        err = [x + y for x, y in zip(rb, negacyclic(ra, s))]
        t_bound = F(n, 2) * (1 + sum(abs(v) for v in s))
        assert all(abs(x) <= F(1, 2) for x in ra + rb)
        assert sum(abs(x) for x in err) <= t_bound
        q = 101
        input_phase = [centered(b + x, w * q)
                       for b, x in zip(bb, negacyclic(aa, s))]
        out_phase = [centered(nearest(F(b, w)) + x, q)
                     for b, x in zip(bb, negacyclic([nearest(F(a, w)) for a in aa], s))]
        for old, new, r in zip(input_phase, out_phase, err):
            candidate = F(old, w) + r
            assert candidate.denominator == 1
            assert centered(candidate, q) == new
        cases += 1
    result("component_rescale_phase_and_canonical_norm_bound", cases,
           "Exact negacyclic phase identities, including input wraps; coefficient l1 implies the canonical norm bound.")


def check_modulus_reduction():
    cases = 0
    for q in (7, 11, 17):
        big_q = 19 * q
        for original in range(-big_q // 2 + 5, big_q // 2 - 5):
            for residual in range(-q // 2 + 1, q // 2 + 1):
                newer = original + residual
                assert centered(centered(newer, q) - centered(original, q), q) == residual
                cases += 1
    assert centered(4, 7) == -3  # A residual outside the centered range is not recovered.
    q, big_q, x, y = 7, 100, 49, 49
    assert centered(centered(x + y, big_q), q) != centered(x + y, q)
    factors, small_q, big_q = (3, 5, 7), 101, 3 * 5 * 7 * 101
    assert prod(factors) * small_q == big_q
    assert prod(factors + (11,)) * small_q > big_q
    result("moddrop_homomorphism_residual_range_and_capacity", cases + 4,
           "Individual reductions may wrap; their small difference survives. Nondivisible moduli and residual overflow fail.")


def check_old_error_and_contract():
    m, old = F(3, 16), F(1, 1024)
    eps, p = F(1, 2**20), 2**20
    out = m + old - eps / p
    assert out - m >= old - eps / p > old * F(999, 1000)
    # Accurate on all three chosen fresh inputs does not imply accuracy on a derived residual.
    eps, gain, residual = F(1, 32), 8, F(1, 4)
    def bad_on_residual(x):
        return x + (F(1, 2) if x == residual else eps)
    assert all(abs(bad_on_residual(x) - x) == eps for x in [F(-1, 2), F(0), F(1, 2)])
    first = bad_on_residual(F(0))
    assert gain * first == residual
    corrected = first - bad_on_residual(residual) / gain
    assert abs(corrected) == F(1, 16) > eps / gain
    # Valid marginal bounds give a union bound without independence. A product rule is unjustified.
    event1, event2 = set(range(10)), set(range(10, 20))
    union = F(len(event1 | event2), 100)
    assert union == F(1, 5)
    assert union > 1 - F(9, 10) ** 2
    assert F(len(event2), 90) > F(1, 10)  # Conditional bound changes with history.
    result("old_error_preservation_and_adaptive_contract", 7,
           {"retained_old_error": str(out - m),
            "failure_of_fresh_sample_bound": str(abs(corrected)),
            "disjoint_event_union": str(union)})


def gc_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def gc_mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def gc_scale(a, scalar):
    return (a[0] * scalar, a[1] * scalar)


def gc_norm2(a):
    return a[0]**2 + a[1]**2


def gc_poly(coefficients, z):
    out = (F(0), F(0))
    for a in reversed(coefficients):
        out = gc_add(gc_mul(out, z), (a, F(0)))
    return out


def arcsin_coeff(j):
    return F(math.comb(2*j, j), 4**j * (2*j + 1))


def check_complex_polynomial_bounds():
    cases = 0
    for degree_index in range(8):
        coeffs = [F(0)] * (2 * degree_index + 2)
        for j in range(degree_index + 1):
            coeffs[2*j + 1] = arcsin_coeff(j)
        radius = F(3, 4)
        derivative = sum(i * abs(a) * radius**(i - 1)
                         for i, a in enumerate(coeffs) if i)
        points = [(F(x, 8), F(y, 8)) for x, y in itertools.product(range(-4, 5), repeat=2)]
        for first, second in zip(points, reversed(points)):
            assert gc_norm2(first) <= radius**2 and gc_norm2(second) <= radius**2
            difference = gc_add(gc_poly(coeffs, first), gc_scale(gc_poly(coeffs, second), -1))
            displacement = gc_add(first, gc_scale(second, -1))
            assert gc_norm2(difference) <= derivative**2 * gc_norm2(displacement)
            cases += 1
        # Coefficients decrease; the whole remaining series is bounded by a geometric tail.
        assert arcsin_coeff(degree_index + 1) < arcsin_coeff(degree_index)
        for r in [F(1, 8), F(1, 4), F(1, 2), F(3, 4), F(9, 10)]:
            partial_tail = sum(arcsin_coeff(j) * r**(2*j + 1)
                               for j in range(degree_index + 1, degree_index + 40))
            bound = arcsin_coeff(degree_index + 1) * r**(2*degree_index + 3) / (1-r*r)
            assert partial_tail <= bound
            cases += 1
    # T_40 is <= 1 on [-1,1], but that real bound does not extend to a complex neighborhood.
    z = (F(0), F(1, 5))
    t0, t1 = (F(1), F(0)), z
    for _ in range(2, 41):
        t0, t1 = t1, gc_add(gc_scale(gc_mul(z, t1), 2), gc_scale(t0, -1))
    assert gc_norm2(t1) > 1000**2
    result("complex_derivative_and_arcsin_tail_bounds", cases + 1,
           {"chebyshev_real_bound": 1, "chebyshev_complex_magnitude_exceeds": 1000,
            "tail": "a_(d+1) r^(2d+3)/(1-r^2), with decreasing positive arcsin coefficients"})


def check_arcsin_domains():
    cases = 0
    for integer, numerator in itertools.product(range(-3, 4), range(-31, 32)):
        remainder = numerator / 128
        value = math.asin(math.sin(2 * math.pi * (integer + remainder))) / (2 * math.pi)
        assert abs(value - remainder) < 2e-14
        cases += 1
    outside = math.asin(math.sin(2 * math.pi * .3)) / (2 * math.pi)
    assert abs(outside - .2) < 1e-15 and abs(outside - .3) > .09
    result("arcsin_principal_neighborhood", cases + 1,
           {"outside_input": .3, "wrong_remainder": outside}, "floating_sanity_check")


def check_joint_polynomial_budget():
    k, h = 1, 1/32
    ds, da = 19, 7  # Sine degree 39 and arcsin degree 15, for this toy domain only.
    ec, hs, ha, el, linear_norm = 1e-15, 1e-15, 1e-15, 2e-14, 8.0
    radius = k + h + ec
    x_max = 2 * math.pi * (k + h)
    eps_s = x_max**(2*ds + 3) / math.factorial(2*ds + 3)
    ls = sum((2*math.pi)**(2*j + 1) * radius**(2*j) / math.factorial(2*j)
             for j in range(ds + 1))
    es = ls*ec + eps_s + hs
    sh = math.sin(2 * math.pi * h)
    y_max = sh + es
    assert y_max < 1
    eps_a = float(arcsin_coeff(da + 1)) * sh**(2*da + 3) / (1-sh*sh)
    la = sum((2*j + 1)*float(arcsin_coeff(j))*y_max**(2*j) for j in range(da + 1))
    er = (eps_a + la*es + ha) / (2*math.pi)
    bound = linear_norm*er + el

    def inner(z):
        x = 2*math.pi*z
        return sum((-1)**j*x**(2*j+1)/math.factorial(2*j+1) for j in range(ds+1))
    def outer(z):
        return sum(float(arcsin_coeff(j))*z**(2*j+1) for j in range(da+1))

    max_error, cases = 0.0, 0
    directions = (1, -1, 1j, -1j)
    for integer, offset, dc, dh in itertools.product(range(-k, k+1), range(-8, 9), directions, directions):
        remainder = h*offset/8
        inner_value = inner(integer + remainder + ec*dc) + hs*dh
        out = linear_norm*(outer(inner_value) + ha*dc)/(2*math.pi) + el*dh
        err = abs(out - linear_norm*remainder)
        assert err <= bound
        max_error = max(max_error, err)
        cases += 1
    result("combined_complex_perturbation_error_budget", cases,
           {"K": k, "h": h, "sine_degree": 2*ds+1, "arcsin_degree": 2*da+1,
            "E_C": ec, "H_s": hs, "H_a": ha, "L_s_bound": ls,
            "epsilon_s_bound": eps_s, "epsilon_a_bound": eps_a,
            "L_a_bound": la, "Y": y_max, "linear_norm": linear_norm,
            "E_L": el, "analytic_formula_evaluated_in_float": bound,
            "sample_max_error": max_error,
            "limitation": "Artificial bounded errors, no CKKS ciphertext execution, no secure parameter guarantee; proof is in ckks-followup.md."},
           "floating_sanity_check")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    for test in [check_correlated_recursion, check_headroom_and_rns, check_rounding_bound,
                 check_modulus_reduction, check_old_error_and_contract,
                 check_complex_polynomial_bounds, check_arcsin_domains,
                 check_joint_polynomial_budget]:
        test()
    output = {"status": "pass", "groups": len(RESULTS),
              "checked_cases": sum(x["checked_cases"] for x in RESULTS), "results": RESULTS,
              "scope": "Conditional algebraic proof checks and explicitly bounded toy polynomial examples; not a production/bootstrap-security certification."}
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"PASS: {output['groups']} groups, {output['checked_cases']} checked cases")
        for item in RESULTS:
            print(f"  {item['name']}: {item['checked_cases']} ({item['kind']})")


if __name__ == "__main__":
    main()
