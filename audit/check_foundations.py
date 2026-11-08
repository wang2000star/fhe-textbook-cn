#!/usr/bin/env python3
"""Reproduce the algebraic counterexamples in foundations-review.md.

Only the Python standard library is required. All integer rounding uses the
explicit convention R(x) = floor(x + 1/2), including negative half-integers.
These finite checks supplement the written derivations; they are neither a
cryptographic security estimate nor a proof for an unbounded parameter family.
Run from any directory: python3 audit/check_foundations.py
"""

from fractions import Fraction
from itertools import product
from math import gcd
import cmath
import json
import random
import sys


def nearest(x):
    x = Fraction(x) + Fraction(1, 2)
    return x.numerator // x.denominator


def centered(x, q):
    x %= q
    return x - q if 2 * x >= q else x


def decode(phase, q, t):
    return nearest(Fraction(centered(phase, q), q // t)) % t


def negacyclic(a, b, modulus=None):
    assert len(a) == len(b)
    n = len(a)
    out = [0] * n
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[(i + j) % n] += x * y * (1 if i + j < n else -1)
    return [x % modulus for x in out] if modulus else out


def matvec(a, x, modulus=None):
    y = [sum(u * v for u, v in zip(row, x)) for row in a]
    return [v % modulus for v in y] if modulus else y


def transpose(a):
    return [list(row) for row in zip(*a)]


def matmul(a, b, modulus=None):
    cols = transpose(b)
    out = [[sum(x * y for x, y in zip(row, col)) for col in cols] for row in a]
    return [[v % modulus for v in row] for row in out] if modulus else out


def inverse_mod(a, p):
    n = len(a)
    aug = [[x % p for x in row] + [int(i == j) for j in range(n)]
           for i, row in enumerate(a)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if aug[i][j] % p)
        aug[pivot], aug[j] = aug[j], aug[pivot]
        scale = pow(aug[j][j], -1, p)
        aug[j] = [x * scale % p for x in aug[j]]
        for i in range(n):
            if i != j:
                factor = aug[i][j]
                aug[i] = [(x - factor * y) % p for x, y in zip(aug[i], aug[j])]
    return [row[n:] for row in aug]


def check_modular_domains():
    assert centered(101, 7) == 3  # more than one subtraction is necessary
    assert (2 * 1) % 6 == (2 * 4) % 6 and 1 % 6 != 4 % 6
    assert 1 % (6 // gcd(2, 6)) == 4 % (6 // gcd(2, 6))
    assert not any((0 * x) % 7 == 1 for x in range(7))
    return {"FND": ["001"], "centered_101_mod_7": 3, "zero_has_inverse": False}


def check_descending_gadget():
    q, beta, ell = 16, 2, 2
    weights = [q // beta**i for i in range(1, ell + 1)]
    representable = sorted({sum(x * w for x, w in zip(ds, weights))
                            for ds in product(range(beta), repeat=ell)})
    assert representable == [0, 4, 8, 12] and 1 not in representable
    full = [8, 4, 2, 1]
    assert {sum(x * w for x, w in zip(ds, full))
            for ds in product(range(2), repeat=4)} == set(range(16))
    # Rounding 15 to the nearest multiple of 4 gives 16, represented by 0 mod 16.
    rounded = nearest(Fraction(15, 4)) * 4
    assert rounded == 16 and centered(15 - rounded, 16) == -1
    # An ascending integer gadget also works for q that is not a radix power.
    for value in range(13):
        digits = [(value // (3**i)) % 3 for i in range(3)]
        assert sum(d * 3**i for i, d in enumerate(digits)) == value
    return {"FND": ["005", "006"], "truncated_representable": representable,
            "wraparound_residual": -1}


def check_cyclotomic_domains():
    assert not any((x*x + 1) % 3 == 0 for x in range(3))
    assert all((x*x + x + 1 - (x-1)**2) % 3 == 0 for x in range(3))
    assert 1**1 == 1  # the root of Phi_3 mod 3 has order 1, not 3
    assert len({(1j)**2, (-1j)**2}) == 1  # the root map is not bijective
    # Leading coefficients alone do not establish integrality of both factors.
    left_factor, right_factor = [-2, 2], [Fraction(1, 2), Fraction(1, 2)]
    coefficients = [sum(left_factor[i] * right_factor[j]
                        for i in range(2) for j in range(2) if i+j == k)
                    for k in range(3)]
    assert coefficients == [-1, 0, 1] and right_factor[0].denominator == 2
    assert sum(gcd(i, 1) == 1 for i in range(1, 2)) == 1
    return {"FND": ["007", "008", "009", "010"],
            "Phi4_roots_in_F3": [], "Phi3_mod_3": "(X-1)^2"}


def check_projection_and_modules():
    a, b = [-1, 0], [1, 0]
    signed = sum(x*y for x, y in zip(a, b))
    assert signed == -1 and abs(signed) == 1
    # Rows p0=(1,0), p1=(1,1); v=p1 has coordinates (0,1), not P v=(1,2).
    p, v, coordinates = [[1, 0], [1, 1]], [1, 1], [0, 1]
    assert matvec(transpose(p), coordinates) == v
    assert matvec(p, v) == [1, 2] != coordinates
    assert 3 * 2 - 2 * 3 == 0 and 3 % 2 != 0 and 2 % 3 != 0
    # Neither member of {2,3} is an integer multiple of the other, yet dependent.
    return {"FND": ["011", "012"], "signed_projection": signed,
            "basis_coordinates": coordinates, "matrix_product_Pv": [1, 2]}


def check_evaluation_isomorphism():
    # Arbitrary distinct nodes give a linear interpolation bijection, but not
    # the multiplication law of F_5[X]/(X^2+1): X^2=-1 evaluates to 4 at 0.
    assert 0**2 % 5 != (-1) % 5
    # Conjugate-symmetric data have real interpolation coefficients at odd roots.
    n = 4
    roots = [cmath.exp(1j * cmath.pi * (2*j+1) / n) for j in range(n)]
    coeffs = [2, -3, 1, 4]
    values = [sum(a * z**i for i, a in enumerate(coeffs)) for z in roots]
    assert all(abs(values[j].conjugate() - values[n-1-j]) < 1e-12
               for j in range(n))
    assert max(abs(1j * values[j] - (1j * values[n-1-j]).conjugate())
               for j in range(n)) > 1
    return {"FND": ["013", "014"], "arbitrary_nodes_ring_map": False,
            "conjugate_symmetry_closed_under_i": False}


def check_vandermonde():
    n, p, omega = 3, 7, 3
    assert pow(omega, 2*n, p) == 1
    assert all(pow(omega, k, p) != 1 for k in range(1, 2*n))
    nodes = [pow(omega, 2*j+1, p) for j in range(n)]
    v = [[pow(z, i, p) for i in range(n)] for z in nodes]
    expected = [[n if i+j == n-1 else 0 for j in range(n)] for i in range(n)]
    assert matmul(v, transpose(v), p) == expected
    a = [1, 0, 0]
    y = matvec(v, a, p)
    assert matvec(transpose(v), a, p) != y
    assert matvec(inverse_mod(v, p), y, p) == a
    return {"FND": ["015", "016"], "n": n, "p": p,
            "nodes": nodes, "VVt": expected, "V_a": y}


def check_rounding_congruences():
    # Congruent integer lifts differ by h*q; rounding commutes with integer h*q'.
    tested = 0
    for q, qp in [(8, 2), (13, 5), (30, 3)]:
        r = Fraction(qp, q)
        for a in range(-2*q, 2*q+1):
            for h in range(-3, 4):
                b = a + h*q
                assert (nearest(r*a) - nearest(r*b)) % qp == 0
                tested += 1
    assert nearest(Fraction(2, 8)*0) == nearest(Fraction(2, 8)*1) == 0
    assert 0 % 8 != 1 % 8  # reverse implication is false
    r = Fraction(1, 2)
    a, c, b, d = 1, 1, 2, 0
    eta = nearest(r*a) + nearest(r*c) - nearest(r*b) - nearest(r*d)
    assert a+c == b+d and eta == 1
    assert nearest(r*2) * nearest(r*2) == 1 != nearest(r*4)
    return {"FND": ["017"], "exact_forward_cases": tested,
            "separate_sum_rounding_error": eta, "reverse_implication": False}


def check_crt():
    moduli = [3, 5, 7]
    n = 105
    coefficients = [(n//p) * pow(n//p, -1, p) for p in moduli]
    for x in range(n):
        residues = [x % p for p in moduli]
        assert sum(r*c for r, c in zip(residues, coefficients)) % n == x
    x, y = 100, 12
    assert [(x+y) % p for p in moduli] == [1, 2, 0]
    assert (x+y) % n == 7  # coordinates must reduce modulo 3,5,7 respectively
    return {"FND": ["018"], "roundtrip_cases": n,
            "sum_residues": [1, 2, 0], "sum_mod_N": 7}


def check_taylor():
    x = Fraction(1, 10)
    f = 1 + x - 100*x*x
    errors = [abs(f - t) for t in [1, 1+x, 1+x-100*x*x]]
    assert errors == [Fraction(9, 10), 1, 0]
    return {"FND": ["019"], "errors_degree_0_1_2": list(map(str, errors))}


def check_negacyclic_ntt():
    n, p, omega = 4, 17, 2
    assert pow(omega, n, p) == p-1 and pow(omega, 2*n, p) == 1
    nodes = [pow(omega, 2*j+1, p) for j in range(n)]
    v = [[pow(z, i, p) for i in range(n)] for z in nodes]
    vinv = inverse_mod(v, p)
    rng = random.Random(1604)
    for _ in range(40):
        a = [rng.randrange(p) for _ in range(n)]
        b = [rng.randrange(p) for _ in range(n)]
        ya, yb = matvec(v, a, p), matvec(v, b, p)
        out = matvec(vinv, [x*y % p for x, y in zip(ya, yb)], p)
        assert out == negacyclic(a, b, p)
    assert negacyclic([0, 0, 0, 1], [0, 1, 0, 0], p) == [16, 0, 0, 0]
    return {"FND": ["020"], "products_checked": 40,
            "X3_times_X": "-1 mod (X^4+1)"}


def check_decoder_and_overflow():
    q, t, delta, m, e = 32, 4, 8, 1, -1
    phase = delta*m+e
    assert phase // delta == 0 and decode(phase, q, t) == 1
    assert not (abs(-100) < delta/2) and -100 < delta/2
    q, t, m, e = 1024, 3, 513, 0
    delta, v = q//t, m//t
    phase = (delta*m+e) % q
    assert (delta, v, phase, centered(phase, q)) == (341, 171, 853, -171)
    assert decode(phase, q, t) == 2 != m % t
    assert e-(q % t)*v == -171
    return {"FND": ["022", "023"], "right_shift_result": 0,
            "nearest_decode_result": 1, "overflow_phase": -171,
            "overflow_wrong_message": 2}


def check_scalar_public_key_attack():
    # This family attacks the original unrestricted construction with n=1,
    # even when its LWE vector dimension k is 32. It is not a ring-LWE attack.
    rng = random.Random(4004)
    q, t, k, noise_bound = 2**20, 4, 32, 2
    delta = q//t
    a = [rng.randrange(q) for _ in range(k)]
    s = [rng.choice([-1, 0, 1]) for _ in range(k)]
    pk1 = (sum(x*y for x, y in zip(a, s)) + 1) % q
    recovered = 0
    for u, m in product([-1, 0, 1], range(t)):
        e2 = [rng.randint(-noise_bound, noise_bound) for _ in range(k)]
        e1 = rng.randint(-noise_bound, noise_bound)
        d = [(x*u+e) % q for x, e in zip(a, e2)]
        b = (pk1*u+delta*m+e1) % q
        candidates = [guess for guess in [-1, 0, 1]
                      if all(abs(centered(di-ai*guess, q)) <= noise_bound
                             for di, ai in zip(d, a))]
        assert candidates == [u]
        assert decode(b-pk1*candidates[0], q, t) == m
        if u == 0:
            assert decode(b, q, t) == m
        recovered += 1
    bound = 2 * Fraction(4*noise_bound+2, q)**k
    assert bound < Fraction(1, 10**150)
    return {"FND": ["024"], "LWE_dimension_k": k,
            "public_randomizer_candidates": 3, "messages_recovered": recovered,
            "Pr_U_zero": "1/3", "conditional_false_candidate_bound": str(bound)}


def check_glev_and_units():
    q, beta = 16, 4
    assert ((q//beta)*0) % q == ((q//beta)*4) % q
    assert negacyclic([-2, 1], [2, 1], 5) == [0, 0]
    assert [-2 % 5, 1] != [0, 0] and [2, 1] != [0, 0]
    return {"FND": ["026", "027"], "first_row_message_0_equals_4": True,
            "nonzero_nonunit": "X-2 in F5[X]/(X^2+1)"}


def check_addition_and_convolution_noise():
    # Uniform e in {-1,+1}: Var(e)=1, Var(e+e)=4.
    variance = sum(x*x for x in [-1, 1]) / 2
    doubled_variance = sum((2*x)**2 for x in [-1, 1]) / 2
    assert variance == 1 and doubled_variance == 4
    assert abs(3) < 8/2 and abs(3+3) >= 8/2
    assert decode(3, 32, 4) == 0 and decode(6, 32, 4) == 1
    out = negacyclic([1]*4, [1]*4)
    assert out == [-2, 0, 2, 4] and max(map(abs, out)) == 4
    # An unsigned radix-4 digit can be 3, larger than the claimed beta/2=2.
    assert max(range(4)) == 3 > 4/2
    return {"FND": ["028", "030", "031"],
            "variance_e_plus_e": doubled_variance, "convolution": out}


def check_modulus_switch():
    # Textbook example, with every tie rounded toward +infinity.
    q, qp, t = 64, 32, 4
    r = Fraction(qp, q)
    a, s, b = [-25, 12, -3, 7], [0, 1, 1, 0], 26
    ap, bp = [nearest(r*x) for x in a], nearest(r*b)
    assert ap + [bp] == [-12, 6, -1, 4, 13]
    phase = bp-sum(x*y for x, y in zip(ap, s))
    assert phase == 8 and phase-(qp//t)*1 == 0
    rounded_old_error = nearest(r*1)
    assert rounded_old_error == 1 and 0-rounded_old_error == -1
    # A zero-noise input can fail after switching if rounding budget is omitted.
    q, qp, t, a, s, b = 16, 4, 2, [2]*4, [1]*4, -8
    assert centered(b-sum(x*y for x, y in zip(a, s)), q) == 0
    r = Fraction(qp, q)
    ap, bp = [nearest(r*x) for x in a], nearest(r*b)
    new_phase = centered(bp-sum(x*y for x, y in zip(ap, s)), qp)
    assert new_phase == -2 and decode(new_phase, qp, t) == 1
    assert Fraction(1 + sum(map(abs, s)), 2) == Fraction(5, 2)
    return {"FND": ["032", "033"], "textbook_new_error": 0,
            "textbook_auxiliary_epsilon": -1, "zero_noise_input_new_phase": -2,
            "zero_noise_input_wrong_decoding": 1}


def check_key_switch():
    q, old_s, new_s, a, delta, m, error = 16, 1, 3, 13, 4, 1, 1
    b = (a*old_s+delta*m+error) % q
    weights, digits = [8, 4, 2, 1], [1, 1, 0, 1]
    masks, errors = [3, 5, 7, 9], [1, -1, 0, 1]
    ks_b = [(u*new_s+g*old_s+e) % q
            for u, g, e in zip(masks, weights, errors)]
    ap = -sum(d*u for d, u in zip(digits, masks)) % q
    bp = (b-sum(d*v for d, v in zip(digits, ks_b))) % q
    expected_error = error-sum(d*e for d, e in zip(digits, errors))
    assert expected_error == 0
    assert centered(bp-ap*new_s-delta*m, q) == expected_error
    assert decode(bp-ap*new_s, q, q//delta) == m
    # Truncation to weights (8,4) leaves rho=1 for a=13.
    delta, m, error = 2, 0, 0
    b = a*old_s
    rho = a-(8+4)
    phase = b-(8+4)*old_s
    assert rho == 1 and phase == 1 and decode(phase, q, q//delta) == 1 != m
    return {"FND": ["034"], "exact_new_error": expected_error,
            "truncated_residual": rho, "truncated_wrong_message": 1}


def check_matrix_claims():
    identity = [[1, 0], [0, 1]]
    a = [[1, 2], [3, 4]]
    assert matmul(a, identity) == matmul(identity, a)
    x, y = [1, 2], [1, 2]
    twice = [[2, 0], [0, 2]]
    left = matvec(twice, [u*v for u, v in zip(x, y)])
    right = [u*v for u, v in zip(matvec(twice, x), matvec(twice, y))]
    assert left == [2, 8] != right == [4, 16]
    return {"FND": ["036"], "AI_equals_IA": True,
            "Hadamard_left": left, "Hadamard_right": right}


CHECKS = [
    check_modular_domains, check_descending_gadget, check_cyclotomic_domains,
    check_projection_and_modules, check_evaluation_isomorphism,
    check_vandermonde, check_rounding_congruences, check_crt, check_taylor,
    check_negacyclic_ntt, check_decoder_and_overflow, check_scalar_public_key_attack,
    check_glev_and_units, check_addition_and_convolution_noise, check_modulus_switch,
    check_key_switch, check_matrix_claims,
]


def main():
    results = []
    for check in CHECKS:
        result = check()
        result["check"] = check.__name__
        results.append(result)
        if "--json" not in sys.argv:
            print("PASS", check.__name__, json.dumps(result, ensure_ascii=False))
    report = {"status": "pass", "checks": len(results), "results": results,
              "scope": "finite deterministic algebraic examples; not a security proof"}
    if "--json" in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"PASS: {len(results)} mathematical checks; no security claim inferred.")


if __name__ == "__main__":
    main()
