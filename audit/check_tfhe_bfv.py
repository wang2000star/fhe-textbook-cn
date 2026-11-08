#!/usr/bin/env python3
"""Exact-arithmetic checks for the TFHE/BFV academic review.

Run from any directory: python audit/check_tfhe_bfv.py
No cryptographic security claim is made by these deliberately small fixtures.
The tests distinguish counterexamples to old claims from checks of corrected
identities. Fractions avoid introducing floating-point rounding ambiguity.
"""
from fractions import Fraction as F
from itertools import product
from math import gcd
import json
import random

RNG = random.Random(20261108)
RESULTS = []


def record(name, finding, **data):
    RESULTS.append(dict(check=name, findings=finding, status="pass", **data))


def nearest(x):
    x = F(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def center(x, q):
    return (x + q // 2) % q - q // 2


def add(*polys):
    return [sum(v) for v in zip(*polys)]


def scale(a, c):
    return [c * x for x in a]


def mul(a, b):
    assert len(a) == len(b)
    n = len(a)
    out = [0] * n
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            h = i + j
            out[h % n] += (-1 if h >= n else 1) * x * y
    return out


def reduced(a, q):
    return [x % q for x in a]


def rotate(a, exponent):
    n = len(a)
    out = [0] * n
    for j, x in enumerate(a):
        h = (j + exponent) % (2 * n)
        out[h % n] += (-1 if h >= n else 1) * x
    return out


def lut(a, phase):
    return rotate(a, -phase)[0]


def decode_bfv(phase, q, t):
    return [center(nearest(F(t * center(x, q), q)), t) for x in phase]


def matvec(a, v, q):
    return [sum(x * y for x, y in zip(row, v)) % q for row in a]


def matmul(a, b, q):
    return [[sum(x * y for x, y in zip(row, col)) % q
             for col in zip(*b)] for row in a]


def matrices(n, t, omega):
    exps = [pow(5, i, 2*n) for i in range(n//2)]
    exps += [(-x) % (2*n) for x in exps]
    columns = list(reversed(exps[:n//2])) + list(reversed(exps[n//2:]))
    decoding = [[pow(omega, e*j, t) for j in range(n)] for e in exps]
    what = [[pow(omega, e*j, t) for e in columns] for j in range(n)]
    return decoding, what


def encode(v, t, omega):
    n = len(v)
    dec, what = matrices(n, t, omega)
    m = scale(matvec(what, list(reversed(v)), t), pow(n, -1, t))
    m = reduced(m, t)
    assert matvec(dec, m, t) == reduced(v, t)
    return m


def automorphism(a, exponent):
    n = len(a)
    out = [0] * n
    for j, x in enumerate(a):
        h = (j * exponent) % (2*n)
        out[h % n] += (-1 if h >= n else 1) * x
    return out


def check_noise_and_tfhe():
    sums = [sum(e) for e in product((-1, 1), repeat=4)]
    assert sum(sums) == 0
    assert F(sum(e*e for e in sums), len(sums)) == 4
    assert F(sum((4*e)**2 for e in (-1, 1)), 2) == 16
    record("zero_mean_does_not_bound_variance", ["TB-002"],
           independent_variance=4, repeated_ciphertext_variance=16)

    a = [8, -28, 4, -32, 0, 31, -6, 7]
    s = [1, 0, 0, 1, 1, 1, 0, 1]
    ah = [nearest(F(x, 2)) for x in a]
    bh = nearest(F(24, 2))
    phase = center(bh - sum(x*y for x, y in zip(ah, s)), 32)
    assert phase == 4
    assert phase - 4 == 0 != nearest(F(2, 2))
    record("tfhe_component_rounding", ["TB-005", "TB-007"],
           switched_mask=ah, switched_phase=phase, true_error=0,
           incorrectly_scaled_old_error=1)

    old = [0]*4 + [1]*4 + [2]*4 + [1]*4
    new = [0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 0, 0]
    assert lut(old, 3) == 0 != 1
    for m in (-2, -1, 0, 1):
        for e in (-1, 0, 1):
            assert lut(new, 4*m+e) == m
    for j in range(32):
        assert lut(new, j+16) == -lut(new, j)
    record("centered_negacyclic_lookup", ["TB-006", "TB-007"],
           old_lookup_at_phase_3=0, required_message=1,
           corrected_cases=12, antiperiodic_cases=32)

    cases = 0
    for n in (2, 4, 8):
        for k in (1, 2):
            q, delta = 257, 16
            keys = [[RNG.randrange(2) for _ in range(n)] for _ in range(k)]
            masks = [[RNG.randrange(q) for _ in range(n)] for _ in range(k)]
            m = [RNG.randrange(-3, 4) for _ in range(n)]
            e = [RNG.randrange(-1, 2) for _ in range(n)]
            b = reduced(add(*(mul(a, s) for a, s in zip(masks, keys)),
                            scale(m, delta), e), q)
            sf = sum(keys, [])
            for h in range(n):
                af = [a[h-j] if j <= h else -a[n+h-j]
                      for a in masks for j in range(n)]
                assert (b[h] - sum(x*y for x, y in zip(af, sf))
                        - delta*m[h] - e[h]) % q == 0
                cases += 1
    record("sample_extraction_sign_and_index", [], cases=cases,
           note="Original sample-extraction formula was confirmed, not corrected.")

    v, a = [2, -1, 3, 4, 0, 5, -2, 1], [1, 3, -4, 2]
    cases = 0
    for s in product((0, 1), repeat=4):
        for b in range(-8, 9):
            acc = rotate(v, -b)
            for ai, si in zip(a, s):
                acc = add(acc, scale(add(rotate(acc, ai), scale(acc, -1)), si))
            assert acc == rotate(v, -(b-sum(x*y for x, y in zip(a, s))))
            cases += 1
    record("blind_rotation_minus_phase", [], cases=cases,
           note="For b-a.s the conditional exponent +a_i*s_i is correct.")

    gate = [1] * 8
    correct_index = nearest(F(-4+1, 2))
    wrong_index = nearest(F(-1+1, 2))
    assert lut(gate, correct_index) == -1
    assert lut(gate, wrong_index) == 1
    record("gate_encoded_affine_offset", ["TB-008"],
           correct_boolean=0, wrong_unscaled_offset_boolean=1)


def check_bfv_arithmetic():
    q, t = 31, 8
    delta = q//t
    old_unsigned = nearest(F(30, delta)) % t
    old_centered = nearest(F(-1, delta)) % t
    standard = nearest(F(t*30, q)) % t
    assert (old_unsigned, old_centered, standard) == (2, 0, 0)
    record("bfv_decoder_representative_dependence", ["TB-015"],
           q=q, t=t, delta=delta, m=0, e=-1,
           old_unsigned=old_unsigned, old_centered=old_centered,
           canonical_decoder=standard)

    # A valid, noiseless input pair. Ideal noiseless relin suffices to refute
    # the omission of q*r_q*K1*K2/delta from the teaching variant's error.
    Q = q*delta
    A1 = A2 = 15
    B1 = B2 = 16
    D0, D1, D2 = B1*B2 % Q, (A1*B2+A2*B1) % Q, A1*A2 % Q
    As, Bs = D1, (D0+D2) % Q
    Ca, Cb = nearest(F(As, delta)), nearest(F(Bs, delta))
    assert (A1+B1) % q == 0 == (A2+B2) % q
    eta = F(q*(q-t*delta), delta) + (Cb-F(Bs, delta))
    assert eta == 72
    assert (Ca+Cb-eta) % q == 0
    wrong = decode_bfv([Ca+Cb], q, t)[0]
    assert wrong == 3 != 0
    record("bfv_inverse_delta_carry_counterexample", ["TB-017", "TB-018"],
           q=q, t=t, delta=delta, Q=Q, input_messages=[0, 0],
           input_noise=[0, 0], ideal_relin_noise=0,
           output_phase=Ca+Cb, eta=int(eta), decoded=wrong)

    # The same failure persists with q much larger than t in a ring example.
    q_large, t_large = 8191, 17
    dl = q_large//t_large
    Ql = q_large*dl
    sl, al, bl = [1, 1], [8190, 8190], [0, 2]
    assert add(mul(al, sl), bl) == [0, 2*q_large]
    ast = reduced(scale(mul(al, bl), 2), Ql)
    bst = reduced(add(mul(bl, bl), mul(mul(al, al), mul(sl, sl))), Ql)
    cal = [nearest(F(x, dl)) for x in ast]
    cbl = [nearest(F(x, dl)) for x in bst]
    phase_large = add(mul(cal, sl), cbl)
    decoded_large = decode_bfv(phase_large, q_large, t_large)
    assert decoded_large == [-2, 0]
    record("bfv_inverse_delta_large_ratio_counterexample", ["TB-018"],
           q=q_large, t=t_large, delta=dl, Q=Ql, S=sl,
           both_input_ciphertexts=[al, bl], input_message=[0, 0],
           input_noise=[0, 0], ideal_relin_noise=0,
           output_phase=phase_large, decoded=decoded_large)

    # Full rational identity, including lift terms, relin error and separate
    # rounding errors for both ciphertext components, in polynomial rings.
    cases, successful_bounds = 0, 0
    for q, t in ((31, 8), (257, 17), (4096, 8)):
        delta, rq = q//t, q % t
        Q = q*delta
        for n in (2, 4):
            for _ in range(30):
                s = [RNG.randrange(-1, 2) for _ in range(n)]
                inputs = []
                for _i in (0, 1):
                    m = [RNG.randrange(-2, 3) for _ in range(n)]
                    e = [RNG.randrange(-1, 2) for _ in range(n)]
                    a = [RNG.randrange(q) for _ in range(n)]
                    b = reduced(add(scale(m, delta), e, scale(mul(a, s), -1)), q)
                    L = add(mul(a, s), b)
                    lift = [F(x-delta*mi-ei, q) for x, mi, ei in zip(L, m, e)]
                    assert all(x.denominator == 1 for x in lift)
                    inputs.append((m, e, a, b, lift))
                m1, e1, a1, b1, k1 = inputs[0]
                m2, e2, a2, b2, k2 = inputs[1]
                erl = [RNG.randrange(-1, 2) for _ in range(n)]
                ast = reduced(add(mul(a1, b2), mul(a2, b1)), Q)
                bst = reduced(add(mul(b1, b2), mul(mul(a1, a2), mul(s, s)), erl), Q)
                ca = [nearest(F(x, delta)) for x in ast]
                cb = [nearest(F(x, delta)) for x in bst]
                ra = [x-F(y, delta) for x, y in zip(ca, ast)]
                rb = [x-F(y, delta) for x, y in zip(cb, bst)]
                eta = add(mul(m1, e2), mul(m2, e1),
                          scale(add(mul(e1, k2), mul(e2, k1)), F(q, delta)),
                          scale(mul(k1, k2), F(q*rq, delta)),
                          scale(add(mul(e1, e2), erl), F(1, delta)),
                          mul(ra, s), rb)
                phase = add(mul(ca, s), cb)
                mp = mul(m1, m2)
                difference = add(phase, scale(mp, -delta), scale(eta, -1))
                assert all(x.denominator == 1 and x % q == 0 for x in difference)
                mout = [center(x, t) for x in mp]
                carry = [F(x-y, t) for x, y in zip(mp, mout)]
                eout = add(eta, scale(carry, -rq))
                if max(abs(t*e-rq*m) for e, m in zip(eout, mout)) < F(q, 2):
                    assert decode_bfv(phase, q, t) == mout
                    successful_bounds += 1
                cases += 1
    assert successful_bounds > 0
    record("bfv_inverse_delta_complete_ring_identity", ["TB-018"],
           exact_identity_cases=cases, sufficient_bound_cases=successful_bounds)

    n, q, t = 16, 257, 17
    delta = q//t
    a, s, b = [q-1]*n, [1]*n, [0]*(n-1)+[q-1]
    phase = add(mul(a, s), b)
    assert phase[-1] == 4352 > q*delta
    record("modraise_is_not_a_no_wrap_guarantee", ["TB-017"],
           n=n, q=q, t=t, auxiliary_modulus=q*delta, phase_coefficient=phase[-1])

    assert mul([1]*4, [4]*4)[-1] == 16
    record("ring_convolution_missing_dimension", ["TB-019"],
           n=4, coefficient_bounds=[1, 4], product_coefficient=16)

    # q not a power of beta: increasing integer gadget remains exact.
    Q, beta, ell = 103, 4, 4
    for x in range(Q):
        digits = [(x//(beta**i)) % beta for i in range(ell)]
        assert sum(d*beta**i for i, d in enumerate(digits)) == x
    possible = {(8*d1+4*d2) % 16 for d1 in range(2) for d2 in range(2)}
    assert 1 not in possible
    record("gadget_integer_weights_and_truncation", ["TB-003", "TB-020"],
           exact_general_modulus_cases=Q,
           truncated_q16_beta2_l2_unrepresentable=1)


def check_encoding_rotation():
    # Integer polynomial evaluation is not well-defined on R_t without bounds.
    x = [0, 1]
    squared = mul(x, x)
    assert squared == [-1, 0]
    assert sum(c*2**j for j, c in enumerate(squared)) == -1 != 2*2
    record("single_value_degree_wrap", ["TB-012"], n=2,
           expected_integer_product=4, quotient_ring_decoding=-1)

    units = [x for x in range(9) if gcd(x, 9) == 1]
    assert 8 % 8 == 0  # t-1 divisible by 2n alone is insufficient for t composite.
    assert not any(pow(x, 8, 9) == 1 and pow(x, 4, 9) != 1 for x in units)
    record("composite_plaintext_modulus_split_condition", ["TB-013"],
           t=9, n=4, primitive_order_8_roots=0)

    cases = []
    for n, t, omega in ((4, 17, 9), (8, 17, 3), (16, 97, 19)):
        assert pow(omega, n, t) == t-1 and pow(omega, 2*n, t) == 1
        dec, what = matrices(n, t, omega)
        identity = [[n % t if i+j == n-1 else 0 for j in range(n)] for i in range(n)]
        assert matmul(dec, what, t) == identity
        cases.append(n)
    v1, v2 = [10, 3, 5, 13], [2, 4, 3, 6]
    m1, m2 = encode(v1, 17, 9), encode(v2, 17, 9)
    assert m1 == [12, 11, 12, 1]
    assert m2 == [8, 5, 14, 6]
    dec, _ = matrices(4, 17, 9)
    assert matvec(dec, add(m1, m2), 17) == [12, 7, 8, 2]
    # Negacyclic multiplication corresponds to slot multiplication.
    assert matvec(dec, mul(m1, m2), 17) == [x*y % 17 for x, y in zip(v1, v2)]
    v = list(range(1, 9))
    m = encode(v, 17, 3)
    assert m == [13, 16, 10, 5, 9, 12, 7, 1]
    dec, _ = matrices(8, 17, 3)
    vrot = matvec(dec, automorphism(m, pow(5, 3, 16)), 17)
    assert vrot == [4, 1, 2, 3, 8, 5, 6, 7]
    record("batch_encoding_and_rotation_examples", ["TB-014", "TB-023"],
           matrix_dimensions=cases, encoding_examples=[m1, m2, m],
           rotated_slots=vrot)

    v = [1, 2, 3, 4]
    row_rotation = [2, 1, 4, 3]
    full_rotation = [2, 3, 4, 1]
    assert row_rotation != full_rotation
    record("two_rows_are_not_one_cyclic_slot_vector", ["TB-024"],
           row_rotation=row_rotation, required_full_rotation=full_rotation)


def balanced_digit(z, p):
    return center(z, p) if p % 2 else z % p


def interpolate_h(z, p, j):
    modulus = p**j
    digits = list(range(-(p//2), p//2+1)) if p % 2 else [0, 1]
    answer = 0
    for d in digits:
        numerator, denominator = 1, 1
        for other in digits:
            if other != d:
                numerator = numerator * (z-other) % modulus
                denominator = denominator * (d-other) % modulus
        answer += ((d**p-d)//p) * numerator * pow(denominator, -1, modulus)
    return answer % modulus


def lifting(z, p, j):
    return (pow(z, p, p**(j+1))-p*interpolate_h(z, p, j)) % (p**(j+1))


def lowest_digit_lift(z, p, eps):
    # Evaluate each polynomial modulo the final modulus, preserving higher digits;
    # interpolation coefficients may be any integer lifts of their residue class.
    current = z
    for j in range(1, eps):
        current = (pow(current, p, p**eps)-p*interpolate_h(current, p, j)) % (p**eps)
    return current


def check_bootstrap_digits():
    assert 8//9 == 0 != nearest(F(8, 9)) == 1
    assert 7//8 == 0 != (7+4)//8 == 1
    cases = 0
    for p in (3, 5, 7):
        for eps in (2, 3, 4):
            for r in range(1, eps):
                for z in range(p**eps):
                    u = z
                    for _ in range(eps-r):
                        d = balanced_digit(u, p)
                        assert (u-d) % p == 0
                        u = (u-d)//p
                    assert u % (p**r) == nearest(F(z, p**(eps-r))) % (p**r)
                    cases += 1
    record("balanced_digit_deletion_rounds", ["TB-028"],
           counterexamples=[dict(p=3, z=8, divisor=9), dict(p=2, z=7, divisor=8)],
           exact_rounding_cases=cases)

    cases = 0
    for p in (2, 3, 5, 7):
        digits = list(range(-(p//2), p//2+1)) if p % 2 else [0, 1]
        for j in (1, 2, 3):
            for d in digits:
                for u in range(-p, p+1):
                    assert lifting(d+p**j*u, p, j) == d % (p**(j+1))
                    cases += 1
        for eps in (2, 3, 4):
            for z in range(p**eps):
                d = balanced_digit(z, p)
                lifted = lowest_digit_lift(z, p, eps)
                assert lifted == d % (p**eps)
                assert (z-lifted) % p == 0
                # Exact quotient is defined modulo the smaller plaintext modulus.
                assert ((z-lifted)//p) % (p**(eps-1)) == ((z-d)//p) % (p**(eps-1))
                cases += 1
    record("lifting_polynomial_and_exact_digit_quotient", ["TB-029", "TB-030", "TB-032"],
           exact_cases=cases)

    # Mod-p interpolation alone does not fix a lift to modulus p^3.
    # f1=X^2+2X and f2=0 have the desired base-3 digit values modulo 3,
    # but using those coefficient representatives produces F2(1)=19 mod27.
    assert [(d*d+2*d) % 3 for d in range(3)] == [0, 0, 2]
    assert (1**3-3*(1**2+2*1)) % 27 == 19 != 1
    record("lifting_interpolation_requires_higher_precision", ["TB-030"],
           p=3, precision=3, digit=1, naive_result=19, required=1)

    q, p, j, w = 100, 3, 3, 4
    dj, previous = q//(p**j), q//(p**(j-1))
    drift_coefficient = previous-p*dj
    phase = dj*p*w
    assert (dj, previous, drift_coefficient) == (3, 11, 2)
    assert phase == previous*w-drift_coefficient*w
    assert phase-previous*w == -8
    assert abs(phase-previous*w) > dj
    record("scale_reinterpretation_drift", ["TB-031"],
           q=q, p=p, j=j, w=w, old_scale=dj, new_scale=previous,
           unaccounted_drift=-8)


def main():
    check_noise_and_tfhe()
    check_bfv_arithmetic()
    check_encoding_rotation()
    check_bootstrap_digits()
    print(json.dumps({"status": "pass", "groups": len(RESULTS),
                      "arithmetic": "exact integers and fractions",
                      "seed": 20261108, "checks": RESULTS}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
