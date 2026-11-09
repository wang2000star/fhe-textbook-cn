#!/usr/bin/env python3
"""Finite checks for audit/security-followup.md (not a hardness estimator).

The distribution comparisons below use exact integer counts, not random trials.
They check algebraic reductions and explicit counterexamples only. Passing them
does not establish LWE/RLWE hardness or a concrete cryptographic security level.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from itertools import product
import json
from math import gcd


def add(a: tuple[int, ...], b: tuple[int, ...], q: int) -> tuple[int, ...]:
    return tuple((x + y) % q for x, y in zip(a, b))


def neg(a: tuple[int, ...], q: int) -> tuple[int, ...]:
    return tuple(-x % q for x in a)


def sub(a: tuple[int, ...], b: tuple[int, ...], q: int) -> tuple[int, ...]:
    return add(a, neg(b, q), q)


def mul(a: tuple[int, ...], b: tuple[int, ...], q: int) -> tuple[int, ...]:
    """Product in Z_q[X]/(X^n+1)."""
    assert len(a) == len(b)
    n = len(a)
    out = [0] * n
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[(i + j) % n] += (-1 if i + j >= n else 1) * x * y
    return tuple(x % q for x in out)


def centered(x: int, q: int) -> int:
    return (x + q // 2) % q - q // 2


def nearest_div(x: int, d: int) -> int:
    return (2 * x + d) // (2 * d)


def check_adaptive_uniform_messages() -> dict:
    """After replacing the sample bodies, adaptive offsets hide the bit exactly."""
    q = 5
    distributions = []
    for bit in (0, 1):
        counts = Counter()
        for a0, z0, a1, z1 in product(range(q), repeat=4):
            m0 = (1, 4)[bit]
            b0 = (z0 + m0) % q
            # A second left/right message pair chosen from the entire first view.
            choices = ((a0 + b0) % q, (a0 * b0 + 2) % q)
            b1 = (z1 + choices[bit]) % q
            counts[(a0, b0, a1, b1)] += 1
        distributions.append(counts)
    assert distributions[0] == distributions[1]
    assert set(distributions[0].values()) == {1}
    return {"transcripts_per_bit": q**4, "equal_distributions": True}


def check_scalar_normal_form() -> dict:
    q = 9
    matrix = ((1, 2), (3, 2))
    det = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % q
    inv_det = pow(det, -1, q)
    inverse = (
        (inv_det * matrix[1][1] % q, -inv_det * matrix[0][1] % q),
        (-inv_det * matrix[1][0] % q, inv_det * matrix[0][0] % q),
    )
    dot = lambda a, b: sum(x * y for x, y in zip(a, b)) % q
    secret = (2, 5)
    cases = 0
    mapped_masks = set()
    error_counts = Counter()
    for e0 in product((-1, 0, 1), repeat=2):
        b0 = tuple((dot(row, secret) + e) % q for row, e in zip(matrix, e0))
        error_counts[tuple((b - dot(row, secret)) % q for row, b in zip(matrix, b0))] += 1
        for a in product(range(q), repeat=2):
            a_inv = tuple(sum(a[i] * inverse[i][j] for i in range(2)) % q for j in range(2))
            a_prime = tuple(-x % q for x in a_inv)
            mapped_masks.add(a_prime)
            for e in (-1, 0, 1):
                b = (dot(a, secret) + e) % q
                b_prime = (b - dot(a_inv, b0)) % q
                assert b_prime == (dot(a_prime, e0) + e) % q
                cases += 1
    assert len(mapped_masks) == q**2
    assert error_counts == Counter({tuple(x % q for x in e): 1 for e in product((-1, 0, 1), repeat=2)})
    # Invertibility over Z_9 is full rank modulo 3, not nonzero determinant modulo 9.
    nonunit_nonzero = 0
    for a, b, c, d in product(range(q), repeat=4):
        det = (a * d - b * c) % q
        assert (gcd(det, q) == 1) == (det % 3 != 0)
        nonunit_nonzero += int(det != 0 and gcd(det, q) != 1)
    assert nonunit_nonzero > 0
    return {"normal_form_identities": cases, "uniform_mask_permutation_size": q**2,
            "matrix_unit_checks": q**4, "nonzero_nonunit_determinants": nonunit_nonzero}


def check_ring_normal_form() -> dict:
    q = 8
    ring = list(product(range(q), repeat=2))
    one = (1, 0)
    inverses = {}
    for a in ring:
        candidates = [b for b in ring if mul(a, b, q) == one]
        assert bool(candidates) == (sum(a) % 2 == 1)
        if candidates:
            assert len(candidates) == 1
            inverses[a] = candidates[0]
    assert len(inverses) == len(ring) // 2
    a0 = (1, 2)
    a0_inv = inverses[a0]
    secret = (1, q - 1)
    small = [tuple(x % q for x in e) for e in product((-1, 0, 1), repeat=2)]
    count = 0
    masks = set()
    for e0 in small:
        b0 = add(mul(a0, secret, q), e0, q)
        for a in ring:
            quotient = mul(a, a0_inv, q)
            a_prime = neg(quotient, q)
            masks.add(a_prime)
            for e in small:
                b = add(mul(a, secret, q), e, q)
                b_prime = sub(b, mul(quotient, b0, q), q)
                assert b_prime == add(mul(a_prime, e0, q), e, q)
                count += 1
    assert len(masks) == len(ring)
    # X^2+1 splits at q=5, with unit density (1-1/q)^2.
    q_split = 5
    split_ring = list(product(range(q_split), repeat=2))
    units = sum(any(mul(a, b, q_split) == one for b in split_ring) for a in split_ring)
    assert Fraction(units, len(split_ring)) == Fraction(4, 5) ** 2
    return {"ring_identities": count, "units_mod_8": len(inverses),
            "ring_size_mod_8": len(ring), "split_units_mod_5": units}


def check_public_key_hybrids() -> dict:
    """Check row placement and the H1 = two-RLWE-sample identity, not hardness."""
    q = 5
    real_h1 = Counter()
    oracle_h1 = Counter()
    error = (-1, 0, 1)
    for a, p, u, e1, e2 in product(range(q), range(q), range(q), error, error):
        message = (a + 2 * p) % q  # May be chosen after seeing the public key.
        direct = (a, p, (a * u + e2) % q, (p * u + e1 + message) % q)
        real_h1[direct] += 1
        samples = ((a, (a * u + e2) % q), (p, (p * u + e1) % q))
        simulated = (samples[0][0], samples[1][0], samples[0][1],
                     (samples[1][1] + message) % q)
        oracle_h1[simulated] += 1
    assert real_h1 == oracle_h1
    h2 = []
    for bit in (0, 1):
        counts = Counter()
        for a, p, z2, z1 in product(range(q), repeat=4):
            message_pair = ((a + p) % q, (a * p + 1) % q)
            counts[(a, p, z2, (z1 + message_pair[bit]) % q)] += 1
        h2.append(counts)
    assert h2[0] == h2[1]
    assert set(h2[0].values()) == {1}
    return {"H1_exact_cases": sum(real_h1.values()), "H2_transcripts_per_bit": q**4}


def check_public_seed_joint_distribution() -> dict:
    q, h = 5, 4
    generator = lambda d: (d % q, (d * d + 2 * d) % q)
    real_accept = sum(generator(d) == generator(d) for d in range(2**h))
    uniform_accept = sum(a == generator(d) for d in range(2**h)
                         for a in product(range(q), repeat=2))
    p_real = Fraction(real_accept, 2**h)
    p_uniform = Fraction(uniform_accept, 2**h * q**2)
    assert p_real == 1 and p_uniform == Fraction(1, q**2)
    return {"real_acceptance": str(p_real), "uniform_acceptance": str(p_uniform),
            "distinguishing_gap": str(p_real - p_uniform),
            "meaning": "refutes the public-seed PRG hybrid, not seeded ciphertext security"}


def check_reused_mask_attack() -> dict:
    q, t, delta = 64, 4, 16
    correct = total = 0
    for a, secret, e0, e1, bit in product(range(q), (-1, 0, 1), range(-2, 3), range(-2, 3), (0, 1)):
        c0 = (a * secret + e0) % q
        challenge = (a * secret + delta * bit + e1) % q
        guessed = nearest_div(centered(challenge - c0, q), delta) % t
        correct += int(guessed == bit)
        total += 1
    assert correct == total
    return {"cases": total, "success_probability": str(Fraction(correct, total))}


def check_rom_bad_event_bound() -> dict:
    size, query_count, hash_queries = 16, 3, 2
    prequeried = {0, 1}
    bad = 0
    for seeds in product(range(size), repeat=query_count):
        bad += int(bool(prequeried.intersection(seeds)) or len(set(seeds)) < query_count)
    exact = Fraction(bad, size**query_count)
    complement = Fraction(1) - Fraction(14 * 13 * 12, size**query_count)
    bound = Fraction(query_count * hash_queries + query_count * (query_count - 1) // 2, size)
    assert exact == complement and exact <= bound
    return {"finite_seed_sequences": size**query_count,
            "bad_probability_fixed_prequeries": str(exact), "union_bound": str(bound),
            "meaning": "checks constants in one finite case; adaptive bound is proved in the report"}


def adaptive_affine_distribution(q: int, secret: int, bit: int, simulated: bool,
                                 uniform_oracle: bool = False) -> Counter:
    """Two-query KDM game, with the second affine function chosen adaptively."""
    bodies = range(q) if uniform_oracle else (-1, 1)
    counts = Counter()
    for a0, e0, a1, e1 in product(range(q), bodies, range(q), bodies):
        transcript = []
        for index, (a, e) in enumerate(((a0, e0), (a1, e1))):
            if index == 0:
                linear, constant = 2, 1
            else:
                old_a, old_b = transcript[0]
                linear, constant = (old_a + old_b) % q, (old_a * old_b + 1) % q
            if simulated:
                z = e if uniform_oracle else (a * secret + e) % q
                pair = ((a - bit * linear) % q, (z + bit * constant) % q)
            else:
                pair = (a, (a * secret + e + bit * (linear * secret + constant)) % q)
            transcript.append(pair)
        counts[tuple(transcript)] += 1
    return counts


def check_adaptive_affine_kdm() -> dict:
    q = 5
    comparisons = 0
    for secret in range(q):
        for bit in (0, 1):
            direct = adaptive_affine_distribution(q, secret, bit, False)
            simulated = adaptive_affine_distribution(q, secret, bit, True)
            assert direct == simulated
            comparisons += 1
    uniform = [adaptive_affine_distribution(q, 0, b, True, True) for b in (0, 1)]
    assert uniform[0] == uniform[1]
    assert set(uniform[0].values()) == {1}
    # Nontrivial polynomial multiplication, not merely scalar/vector notation.
    q_ring = 5
    ring = list(product(range(q_ring), repeat=2))
    linear, constant = (2, 3), (1, 4)
    ring_checks = 0
    for secret in ring:
        for a_prime in ring:
            for error in ((0, 0), (1, q_ring - 1)):
                a = sub(a_prime, linear, q_ring)
                z = add(mul(a_prime, secret, q_ring), error, q_ring)
                lhs = add(z, constant, q_ring)
                rhs = add(add(mul(a, secret, q_ring), error, q_ring),
                          add(mul(linear, secret, q_ring), constant, q_ring), q_ring)
                assert lhs == rhs
                ring_checks += 1
    return {"adaptive_distribution_comparisons": comparisons,
            "uniform_transcripts_per_bit": q**4, "ring_mask_shift_identities": ring_checks}


def check_encoding_affineness() -> dict:
    q, t, delta = 17, 4, 4
    nonnegative = {s: delta * (s % t) % q for s in (-1, 0, 1)}
    centered_values = {s: delta * centered(2 * s, t) % q for s in (-1, 0, 1)}
    assert nonnegative == {-1: 12, 0: 0, 1: 4}
    assert centered_values == {-1: 9, 0: 0, 1: 9}
    for values in (nonnegative, centered_values):
        assert not any(all((linear * s + constant) % q == value for s, value in values.items())
                       for linear, constant in product(range(q), repeat=2))
    divisible_cases = 0
    for q_div, t_div in ((16, 4), (18, 3), (24, 8)):
        scale = q_div // t_div
        for s, linear, constant in product(range(-5, 6), range(-3, 4), range(-2, 3)):
            value = linear * s + constant
            assert scale * (value % t_div) % q_div == scale * value % q_div
            assert scale * centered(value, t_div) % q_div == scale * value % q_div
            divisible_cases += 1
    return {"nonnegative_q17_t4": nonnegative, "centered_q17_t4": centered_values,
            "divisible_modulus_checks": divisible_cases}


def check_non_ring_affine_functions() -> dict:
    q, n = 17, 4
    zero, one, minus_one = (0,) * n, (1, 0, 0, 0), (q - 1, 0, 0, 0)
    x, x3 = (0, 1, 0, 0), (0, 0, 0, 1)
    # sigma_3(0)=0, sigma_3(1)=1 force c=0,L=1, but sigma_3(X)=X^3.
    assert mul(one, x, q) != x3
    # Constant coefficient extraction also forces c=0,L=1, contradicting X -> 0.
    assert mul(one, x, q) != zero
    # Squaring at 0 and 1 forces c=0,L=1, contradicted at -1.
    assert mul(minus_one, minus_one, q) == one
    assert mul(one, minus_one, q) != one
    return {"counterexamples": ["S(X^3)", "constant-coefficient extraction", "S^2"],
            "ring": "Z_17[X]/(X^4+1)"}


def reverse_topological_order(nodes: tuple[int, ...], edges: tuple[tuple[int, int], ...]) -> list[int]:
    remaining = set(nodes)
    order = []
    while remaining:
        sinks = sorted(v for v in remaining if not any(u == v and w in remaining for u, w in edges))
        if not sinks:
            raise ValueError("cycle prevents this DAG simulation order")
        for v in sinks:
            remaining.remove(v)
            order.append(v)
    return order


def check_dag_simulation_dependencies() -> dict:
    nodes = (0, 1, 2, 3)
    edges = ((0, 1), (0, 2), (1, 3), (2, 3))
    order = reverse_topological_order(nodes, edges)
    replaced = set()
    checks = 0
    for unknown in order:
        # A message depending on the currently unknown key only goes to an
        # already replaced destination; all real incoming messages are known.
        for source, destination in edges:
            if source == unknown:
                assert destination in replaced
            if destination == unknown:
                assert source != unknown
            checks += 1
        replaced.add(unknown)
    try:
        reverse_topological_order((0, 1), ((0, 1), (1, 0)))
    except ValueError:
        cycle_obstructs_this_order = True
    else:
        cycle_obstructs_this_order = False
    assert cycle_obstructs_this_order
    return {"reverse_topological_order": order, "edge_dependency_checks": checks,
            "cycle_obstructs_this_order": True,
            "meaning": "a cycle blocks this simulation; this is not a cycle insecurity proof"}


def check_noise_union_bound() -> dict:
    # Exact union probability for a finite error law; no Gaussian truncation is
    # used as evidence for an infinite-tail bound.
    error_values = (-3, -2, -1, 0, 1, 2, 3)
    coefficient_count, bound = 3, 2
    bad = sum(any(abs(e) > bound for e in errors)
              for errors in product(error_values, repeat=coefficient_count))
    exact = Fraction(bad, len(error_values)**coefficient_count)
    per_coefficient = Fraction(sum(abs(e) > bound for e in error_values), len(error_values))
    assert exact <= coefficient_count * per_coefficient
    inequalities = 0
    for threshold, index in product(range(8), range(40)):
        assert (threshold + 1 + index)**2 >= (threshold + 1)**2 + index * (2 * threshold + 3)
        inequalities += 1
    return {"finite_union_probability": str(exact),
            "union_bound": str(coefficient_count * per_coefficient),
            "gaussian_geometric_exponent_inequalities": inequalities}


CHECKS = (
    check_adaptive_uniform_messages,
    check_scalar_normal_form,
    check_ring_normal_form,
    check_public_key_hybrids,
    check_public_seed_joint_distribution,
    check_reused_mask_attack,
    check_rom_bad_event_bound,
    check_adaptive_affine_kdm,
    check_encoding_affineness,
    check_non_ring_affine_functions,
    check_dag_simulation_dependencies,
    check_noise_union_bound,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="write exact check results as JSON")
    args = parser.parse_args()
    results = []
    for check in CHECKS:
        detail = check()
        results.append({"check": check.__name__, "status": "passed", "details": detail})
    output = {
        "scope": "finite identities and counterexamples; not a proof of computational hardness",
        "groups_passed": len(results),
        "results": results,
    }
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"PASS {result['check']}: {json.dumps(result['details'], ensure_ascii=False, sort_keys=True)}")
        print(f"Passed {len(results)} finite check groups; no concrete security level is asserted.")


if __name__ == "__main__":
    main()
