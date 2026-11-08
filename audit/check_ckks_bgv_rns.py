#!/usr/bin/env python3
"""Deterministic algebraic checks supporting the CKKS/BGV/RNS academic audit.

These checks use tiny parameters, not secure parameters. They test the stated
identities/bounds and exhibit counterexamples to the original statements; they
are not a security proof or an implementation of full bootstrapping.
Run: python audit/check_ckks_bgv_rns.py [--json]
"""
from __future__ import annotations
import argparse
import cmath
import json
import math
from fractions import Fraction as F

RESULTS = []


def centered(a: int, q: int) -> int:
    """Integer in [-q/2,q/2); all rounding tests below use odd moduli."""
    return (a + q // 2) % q - q // 2


def nearest(a: F) -> int:
    return (2 * a.numerator + a.denominator) // (2 * a.denominator)


def crt_sum(x: int, base: tuple[int, ...]) -> int:
    q = math.prod(base)
    return sum(centered(x * pow(q // p, -1, p), p) * (q // p) for p in base)


def negacyclic(a, b):
    n = len(a)
    out = [0] * n
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[(i + j) % n] += ai * bj * (-1 if i + j >= n else 1)
    return out


def automorphism(a, k):
    n = len(a)
    out = [0] * n
    for i, ai in enumerate(a):
        e = (i * k) % (2 * n)
        out[e % n] += ai * (-1 if e >= n else 1)
    return out


def add_result(name, findings, checks, detail):
    RESULTS.append(dict(name=name, findings=findings, checked_cases=checks, detail=detail))


def check_embedding():
    checks = 0
    for n in (4, 8, 16):
        z = [complex(j / 3 - 1, (-1) ** j * (j + 2) / 7) for j in range(n // 2)]
        exponents = [pow(5, j, 2 * n) for j in range(n // 2)]
        roots = [cmath.exp(1j * math.pi * e / n) for e in exponents]
        full_roots = roots + [x.conjugate() for x in roots]
        full_z = z + [x.conjugate() for x in z]
        coeff = [sum(v * r.conjugate() ** k for v, r in zip(full_z, full_roots)) / n
                 for k in range(n)]
        assert max(abs(x.imag) for x in coeff) < 1e-12
        decoded = [sum(c * r ** k for k, c in enumerate(coeff)) for r in roots]
        assert max(abs(a - b) for a, b in zip(decoded, z)) < 1e-11
        rounded = [round(1024 * c.real) for c in coeff]
        err = max(abs(sum(c * r ** k for k, c in enumerate(rounded)) / 1024 - v)
                  for r, v in zip(roots, z))
        assert err <= n / 2048 + 1e-12
        rotated = automorphism(rounded, 5)
        z_rot = [sum(c * r ** k for k, c in enumerate(rotated)) for r in roots]
        z_orig = [sum(c * r ** k for k, c in enumerate(rounded)) for r in roots]
        assert max(abs(a - b) for a, b in zip(z_rot, z_orig[1:] + z_orig[:1])) < 1e-8
        checks += n
    m = [2.3, .825 * math.sqrt(2), 1.45, 2.025 * math.sqrt(2)]
    encoded = [round(1024 * x) for x in m]
    assert encoded == [2355, 1195, 1485, 2933]
    assert round(m[1], 4) == 1.1667
    add_result('canonical_embedding_and_example', ['CBR-002', 'CBR-003', 'CBR-011'], checks,
               {'correct_m1': m[1], 'encoded': encoded, 'rotation': 'left by one under 5^j ordering'})


def check_rounding_and_scale():
    assert nearest(F(2, 5)) + nearest(F(2, 5)) == 0
    assert nearest(F(4, 5)) == 1
    assert 2 * nearest(F(2, 5)) == 0 and nearest(F(4, 5)) == 1
    a, b, s, w = 2, 2, 2, 5
    actual = nearest(F(b, w)) + nearest(F(a, w)) * s
    raw_scaled = F(b + a * s, w)
    ra, rb = F(nearest(F(a, w))) - F(a, w), F(nearest(F(b, w))) - F(b, w)
    assert actual == raw_scaled + rb + ra * s
    assert actual != nearest(raw_scaled)
    delta, dropped = 16, 17
    assert F(delta * delta, dropped) != delta
    x, q0 = 1, 100
    unscaled = math.sin(2 * math.pi * x / q0)
    scaled = q0 / (2 * math.pi) * unscaled
    assert abs(scaled - x) < .001 and abs(unscaled - x) > .9
    add_result('rounding_scale_and_evalexp_constant', ['CBR-007', 'CBR-008', 'CBR-014'], 6,
               {'component_rounding_phase': actual, 'single_phase_rounding': nearest(raw_scaled),
                'actual_output_scale': str(F(delta * delta, dropped)), 'unscaled_sine': unscaled,
                'scaled_sine': scaled})


def check_sparse_trace():
    checks = 0
    for n in (8, 16, 32):
        for nprime in (2, 4):
            if nprime >= n:
                continue
            d = n // nprime
            a = [(-1) ** j * (j + 1) for j in range(n)]
            out = a[:]
            for j in range(d.bit_length() - 1):
                shift = (nprime // 2) * 2 ** j
                rot = automorphism(out, pow(5, shift, 2 * n))
                out = [x + y for x, y in zip(out, rot)]
            assert out == [d * ai if i % d == 0 else 0 for i, ai in enumerate(a)]
            checks += n
    add_result('sparse_bootstrap_partial_sum', ['CBR-012', 'CBR-015'], checks,
               'Trace kills nonmultiples of n/nprime and scales retained coefficients by n/nprime.')


def check_bgv_switch():
    checks = 0
    t, q, qnew = 3, 91, 13
    for s in range(-2, 3):
        for a in range(-q // 2 + 1, q // 2 + 1):
            for b in range(-q // 2 + 1, q // 2 + 1):
                f = centered(b + a * s, q)
                k = (b + a * s - f) // q
                def switch(v):
                    rounded = nearest(F(qnew * v, q))
                    eps = qnew * v - q * rounded
                    h = centered(pow(q, -1, t) * eps, t)
                    return rounded + h
                aa, bb = switch(a), switch(b)
                y = bb + aa * s - k * qnew
                bound = F(qnew, q) * abs(f) + F(t + 1, 2) * (1 + abs(s))
                if bound < F(qnew, 2):
                    assert centered(bb + aa * s, qnew) == y
                    assert (y - f) % t == 0
                    checks += 1
    qbig, w, qsmall = 91, 7, 13
    for a in range(-45, 46):
        d = t * centered(pow(t, -1, w) * a, w)
        assert (a - d) % w == 0
        aa = (a - d) // w
        assert (aa - a) % t == 0
        assert (pow(w, -1, qsmall) * (a - d) - aa) % qsmall == 0
        checks += 1
    # Plain nearest rounding or rounding to a multiple of t does not preserve a residue.
    assert nearest(F(1, 7)) % 3 != 1 % 3
    assert (3 * nearest(F(1, 3))) % 3 != 1 % 3
    add_result('bgv_congruence_preserving_modulus_switch', ['CBR-020', 'CBR-021', 'CBR-031'], checks,
               'Exhaustive scalar checks enforce the full sufficient phase bound; bare rounding fails for m=1.')


def check_bgv_digits_and_noise():
    p, r, eps = 3, 1, 4
    gap = p ** (eps - r)
    count = 0
    for m in range(-(p ** r // 2), p ** r // 2 + 1):
        for k in range(-(gap // 2), gap // 2 + 1):
            w = centered(gap * m + k, p ** eps)
            assert centered(nearest(F(w, gap)), p ** r) == m
            z = w
            for _ in range(eps - r):
                digit = centered(z, p)
                z = (z - digit) // p
            assert centered(z, p ** r) == m
            count += 1
    assert (-1) // gap == -1 and nearest(F(-1, gap)) == 0
    q, j, value, error = 101, 3, 2, 1
    phase = p * value + p ** j * error
    divided = centered(pow(p, -1, q) * phase, q)
    assert divided == value + p ** (j - 1) * error
    assert divided % (p ** (j - 1)) == value
    assert divided % (p ** j) != value  # The old plaintext modulus is no longer correct.
    t, m1, m2, e1, e2 = 3, 2, -1, 1, 2
    product = (m1 + t * e1) * (m2 + t * e2)
    error_product = m1 * e2 + m2 * e1 + t * e1 * e2
    assert product == m1 * m2 + t * error_product
    add_result('bgv_balanced_digits_and_fixed_t', ['CBR-021', 'CBR-022', 'CBR-023', 'CBR-024'], count + 3,
               {'negative_floor_counterexample': [-1, gap, -1],
                'division_phase': divided, 'new_plaintext_modulus': p ** (j - 1)})


def check_fast_conversion():
    base = (5, 7, 11)
    q = math.prod(base)
    count = 0
    witness = None
    for x in range(-(q // 2), q // 2 + 1):
        lift = crt_sum(x, base)
        assert (lift - x) % q == 0
        u = (lift - x) // q
        assert abs(u) <= len(base) // 2
        if u and witness is None:
            witness = {'x': x, 'CRT_sum': lift, 'q_multiple': u}
        count += 1
    add_result('fast_base_conversion_centered_bound', ['CBR-025'], count, witness)


def check_small_montgomery():
    base, dest = (5, 7, 11), (17, 19)
    q, b, aux = math.prod(base), math.prod(dest), 13
    assert aux > len(base) // 2 + F(1, 2)
    count = 0
    wrong_nested = None
    residual = None
    for x in range(-(q // 2), q // 2 + 1):
        lift = crt_sum(aux * x, base)
        correction = centered(lift * pow(q, -1, aux), aux)
        assert (lift - q * correction) % aux == 0
        result = (lift - q * correction) // aux
        assert (result - x) % q == 0 and abs((result - x) // q) <= 1
        if result != x and residual is None:
            residual = {'x': x, 'lifted_result': result}
        wrong = centered(centered(lift, b) * pow(q, -1, aux), aux)
        if wrong != correction and wrong_nested is None:
            wrong_nested = {'x': x, 'correct_aux_correction': correction, 'nested_reduction_correction': wrong}
        for p in dest:
            assert ((lift - q * correction) * pow(aux, -1, p) - result) % p == 0
        count += 1
    assert wrong_nested is not None
    add_result('small_montgomery_bound_and_auxiliary_residue', ['CBR-026'], count,
               {'nested_reduction_counterexample': wrong_nested, 'nonexact_example': residual})


def check_exact_base_conversion():
    base, aux, target = (5, 7), 17, 13
    b = math.prod(base)
    count = 0
    outside = None
    for x in range(-b * aux, b * aux + 1):
        xhat = centered(x, b)
        lift = crt_sum(xhat, base)
        mu, u = (xhat - x) // b, (lift - xhat) // b
        correction = centered((lift - x) * pow(b, -1, aux), aux)
        out = (lift - correction * b) % target
        if abs(mu + u) < F(aux, 2):
            assert out == x % target
            count += 1
        elif out != x % target and outside is None:
            outside = {'x': x, 'mu_plus_u': mu + u, 'recovered': out, 'expected': x % target}
    assert outside is not None
    add_result('exact_conversion_range_condition', ['CBR-032', 'CBR-038'], count,
               {'outside_bound_counterexample': outside})


def check_rns_modswitch():
    count = 0
    example = None
    for bbase in ((5,), (5, 7)):
        b, q = math.prod(bbase), 13
        for x in range(-(q * b // 2), q * b // 2 + 1):
            residual = centered(x, b)
            lift = crt_sum(residual, bbase)
            u = (lift - residual) // b
            got = ((x - lift) * pow(b, -1, q)) % q
            want = (nearest(F(x, b)) - u) % q
            assert got == want
            assert abs(u) <= len(bbase) // 2
            if len(bbase) == 1:
                assert u == 0
            elif u and example is None:
                example = {'x': x, 'b': b, 'base_error': -u}
            count += 1
    add_result('rns_modswitch_exact_error', ['CBR-029'], count, example)


def check_bfv_decrypt():
    base, t, gamma = (5, 7, 11), 3, 13
    q = math.prod(base)
    u_bound = len(base) // 2
    guaranteed = 0
    counterexample = None
    for x in range(-(q // 2), q // 2 + 1):
        m0 = nearest(F(t * x, q))
        delta = F(t * x, q) - m0
        v = centered(t * gamma * x, q)
        lift = crt_sum(v, base)
        u = (lift - v) // q
        y_gamma = centered(-lift * pow(q, -1, gamma), gamma)
        y_t = centered(-lift * pow(q, -1, t), t)
        got = centered((y_t - y_gamma) * pow(gamma, -1, t), t)
        eta = nearest(gamma * delta) - u
        if abs(eta) < F(gamma, 2):
            assert got == centered(m0, t)
        if gamma * abs(delta) + F(1, 2) + u_bound < F(gamma, 2):
            assert got == centered(m0, t)
            guaranteed += 1
        if got != centered(m0, t) and counterexample is None:
            counterexample = {'x': x, 'eta': eta, 'gamma': gamma, 'got': got,
                              'correct_rounding': centered(m0, t)}
    assert counterexample is not None  # An arbitrary coprime gamma is insufficient.
    assert nearest(F(7 * 15, 105)) == 1
    assert nearest(F(7 * 15, 35)) == 3
    assert math.gcd(105, 35) != 1
    add_result('bfv_decryption_margin_and_moddrop_counterexamples', ['CBR-028', 'CBR-030', 'CBR-031'], guaranteed,
               {'gamma_counterexample': counterexample, 'moddrop_message': '1 becomes 3',
                'invalid_BFV_decoder_reuse': '105 has no inverse modulo 35'})


def check_gadget_and_multiplication():
    q, beta, length = 97, 8, 3
    for x in range(q):
        digits = [(x // beta ** i) % beta for i in range(length)]
        assert sum(d * beta ** i for i, d in enumerate(digits)) == x
    assert F(q, beta ** length).denominator != 1
    base = (5, 7, 11)
    q = math.prod(base)
    for x in range(q):
        weights = [(q // p) * pow(q // p, -1, p) for p in base]
        assert (sum(centered(x, p) * g for p, g in zip(base, weights)) - x) % q == 0
    # Scalar residue multiplication is not polynomial coefficient-wise multiplication.
    product = negacyclic([1, 1, 0, 0], [1, 1, 0, 0])
    assert product == [1, 2, 1, 0]
    assert product != [1, 1, 0, 0]
    # b > Delta does not control t times ciphertext products/convolution.
    q, t, b, n = 17, 3, 7, 8
    delta = q // t
    assert b > delta
    a = [q // 2] * n
    cross = [2 * x for x in negacyclic(a, a)]
    assert max(abs(t * x) for x in cross) > F(q * b, 2)
    add_result('integer_gadgets_and_polynomial_products', ['CBR-006', 'CBR-033', 'CBR-034'], 97 + 385 + 2,
               {'bad_auxiliary_rule': {'q': q, 't': t, 'b': b, 'n': n},
                'convolution': product})


def check_meta_and_complexity():
    m, error = F(3, 2), F(1, 100)
    c1 = m + error
    assert c1 - (m - c1) == m + 2 * error
    assert c1 - (c1 - m) == m
    # Horner evaluates any degree-d polynomial using d multiplications.
    d = 100
    multiplications = 0
    value = F(1)
    for _ in range(d):
        value = value * F(1, 2) + 1
        multiplications += 1
    assert multiplications == d
    assert abs(math.asin(math.sin(math.pi)) - math.pi) > 3
    add_result('meta_bts_sign_polynomial_cost_and_arcsin_domain', ['CBR-014', 'CBR-016', 'CBR-017'], 4,
               {'wrong_sign_output': str(m + 2 * error), 'horner_degree': d,
                'horner_multiplications': multiplications, 'arcsin_sin_pi': math.asin(math.sin(math.pi))})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='emit structured check results')
    args = parser.parse_args()
    checks = [check_embedding, check_rounding_and_scale, check_sparse_trace, check_bgv_switch,
              check_bgv_digits_and_noise, check_fast_conversion, check_small_montgomery,
              check_exact_base_conversion, check_rns_modswitch, check_bfv_decrypt,
              check_gadget_and_multiplication, check_meta_and_complexity]
    for check in checks:
        check()
    if args.json:
        print(json.dumps({'status': 'pass', 'groups': len(RESULTS), 'results': RESULTS},
                         ensure_ascii=False, indent=2))
    else:
        for result in RESULTS:
            print(f"PASS {result['name']}: {result['checked_cases']} cases; "
                  f"{', '.join(result['findings'])}")
            print('  ' + json.dumps(result['detail'], ensure_ascii=False))
        print(f'PASS: {len(RESULTS)} algebraic check groups; this is not a cryptographic security proof.')


if __name__ == '__main__':
    main()
