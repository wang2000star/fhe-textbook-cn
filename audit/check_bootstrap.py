#!/usr/bin/env python3
"""Exact, public-ciphertext BFV bootstrapping fixtures for the academic audit.

This is deliberately slow, unoptimized, tiny-ring research code, NOT a secure
cryptosystem. It uses only Python's standard library and exact integers/Fractions.
The evaluator receives ciphertexts and evaluation keys, never a secret key or a
decryption callback. A separate auditor checks the saved public operation graph
after evaluation. See bootstrap-followup.md for the conditional proof and scope.

Run: python3 audit/check_bootstrap.py [--json result.json]
     python3 audit/check_bootstrap.py --json-shards audit/bootstrap-results.json
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from math import gcd
from pathlib import Path
import random


def nearest(x):
    x = F(x)
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def center(x, modulus):
    return (x + modulus // 2) % modulus - modulus // 2


def norm(a):
    return max(map(abs, a), default=0)


def add(*a):
    return tuple(map(sum, zip(*a)))


def scale(a, c):
    return tuple(c * x for x in a)


def matvec(a, x, modulus):
    return tuple(sum(u * v for u, v in zip(row, x)) % modulus for row in a)


def inverse_matrix(a, modulus):
    n = len(a)
    rows = [list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(a)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if gcd(rows[i][j], modulus) == 1)
        rows[j], rows[pivot] = rows[pivot], rows[j]
        rows[j] = [(x * pow(rows[j][j], -1, modulus)) % modulus for x in rows[j]]
        for i in range(n):
            if i != j:
                c = rows[i][j]
                rows[i] = [(x - c * y) % modulus for x, y in zip(rows[i], rows[j])]
    assert all(rows[i][j] == int(i == j) for i in range(n) for j in range(n))
    return tuple(tuple(row[n:]) for row in rows)


def poly_remainder(a, monic):
    n = len(monic) - 1
    assert monic[-1] == 1
    a = list(a) + [0] * max(0, n - len(a))
    for j in range(len(a) - 1, n - 1, -1):
        for h in range(n):
            a[j - n + h] -= a[j] * monic[h]
    return tuple(a[:n])


class Ring:
    """Integer polynomial ring modulo a supplied cyclotomic polynomial."""

    def __init__(self, cyclotomic_index, polynomial):
        self.m, self.phi = cyclotomic_index, tuple(polynomial)
        self.n = len(polynomial) - 1
        self.zero = (0,) * self.n
        self.one = (1,) + (0,) * (self.n - 1)
        self.basis = tuple(tuple(int(i == j) for i in range(self.n)) for j in range(self.n))
        self.units = tuple(a for a in range(1, self.m) if gcd(a, self.m) == 1)
        assert len(self.units) == self.n
        products = [self.mul(x, y) for x in self.basis for y in self.basis]
        self.C = max(sum(abs(c[h]) for c in products) for h in range(self.n))

    def reduce(self, a, modulus):
        return tuple(center(x, modulus) for x in a)

    def mul(self, a, b):
        c = [0] * (2 * self.n - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                c[i + j] += x * y
        return poly_remainder(c, self.phi)

    def auto(self, a, exponent):
        c = [0] * (exponent * (self.n - 1) + 1)
        for j, x in enumerate(a):
            c[exponent * j] += x
        return poly_remainder(c, self.phi)

    def mul_norm(self, a):
        columns = [self.mul(a, e) for e in self.basis]
        return max(sum(abs(c[h]) for c in columns) for h in range(self.n))

    def auto_norm(self, exponent):
        columns = [self.auto(e, exponent) for e in self.basis]
        return max(sum(abs(c[h]) for c in columns) for h in range(self.n))

    def trace(self, a):
        tr = add(*(self.auto(a, exponent) for exponent in self.units))
        assert all(x == 0 for x in tr[1:])
        return tr[0]

    def trace_dual(self, modulus):
        gram = [[self.trace(self.mul(a, b)) for b in self.basis] for a in self.basis]
        inv = inverse_matrix(gram, modulus)
        dual = tuple(self.reduce(tuple(inv[i][j] for i in range(self.n)), modulus)
                     for j in range(self.n))
        assert all(self.trace(self.mul(b, e)) % modulus == int(i == j)
                   for j, b in enumerate(dual) for i, e in enumerate(self.basis))
        return dual

    def compile_linear(self, matrix, modulus):
        """T(z) = sum_a kappa[a] * tau_a(z), via a trace-dual basis."""
        dual = self.trace_dual(modulus)
        images = [tuple(matrix[i][j] for i in range(self.n)) for j in range(self.n)]
        coefficients = {
            a: self.reduce(add(*(self.mul(image, self.auto(b, a))
                                 for image, b in zip(images, dual))), modulus)
            for a in self.units
        }
        for e in self.basis:
            value = self.reduce(add(*(self.mul(c, self.auto(e, a))
                                      for a, c in coefficients.items())), modulus)
            assert value == self.reduce(matvec(matrix, e, modulus), modulus)
        return coefficients


def crt_maps(ring, factors, modulus):
    """d scalar-slot packing maps and d inverse maps; no split-slot assumption."""
    degrees = [len(f) - 1 for f in factors]
    assert len(set(degrees)) == 1 and sum(degrees) == ring.n
    factor_product = [1]
    for factor in factors:
        factor_product = polynomial_multiply(factor_product,factor,modulus)
    assert [x%modulus for x in factor_product] == [x%modulus for x in ring.phi]
    d, ell = degrees[0], len(factors)
    columns = [sum((poly_remainder(e, f) for f in factors), ()) for e in ring.basis]
    crt = tuple(tuple(columns[j][i] % modulus for j in range(ring.n))
                for i in range(ring.n))
    inv = inverse_matrix(crt, modulus)
    pack, unpack = [], []
    for u in range(d):
        pmat = [[0] * ring.n for _ in range(ring.n)]
        umat = [[0] * ring.n for _ in range(ring.n)]
        for h in range(ell):
            j = u * ell + h
            for k in range(ring.n):
                pmat[k][j] = inv[k][h * d]
                umat[j][k] = crt[h * d][k]
        pack.append(tuple(map(tuple, pmat)))
        unpack.append(tuple(map(tuple, umat)))
    for e in ring.basis:
        recovered = add(*(matvec(u, matvec(p, e, modulus), modulus)
                          for p, u in zip(pack, unpack)))
        assert ring.reduce(recovered, modulus) == ring.reduce(e, modulus)
        for u, p in enumerate(pack):
            slots = matvec(crt, matvec(p, e, modulus), modulus)
            assert all(slots[h*d+j] == 0 for h in range(ell) for j in range(1, d))
            assert all(slots[h*d] == e[u*ell+h] % modulus for h in range(ell))
    return pack, unpack, crt


@dataclass(frozen=True)
class Ciphertext:
    a: tuple
    b: tuple
    T: int
    bound: F
    node: int


class PublicEvaluator:
    """Public evaluation boundary: no sk, plaintext messages, or decrypt method."""

    def __init__(self, ring, Q, secret_norm_bound, base, keys):
        self.ring, self.Q, self.sigma = ring, Q, secret_norm_bound
        self.base, self.keys = base, keys
        self.length = 0
        while base ** self.length < Q:
            self.length += 1
        self.key_bound = ring.C * self.length * (base - 1)  # each row error <= 1
        self.graph = []

    def node(self, a, b, T, bound, operation, parents=(), **parameters):
        bound = F(bound)
        # Round the certificate upward, never the actual arithmetic. This keeps
        # a long multiplication ledger compact and remains a rigorous bound.
        bound = F((bound.numerator+bound.denominator-1)//bound.denominator)
        assert bound < F(self.Q, 2*T), (operation, T, bound, self.Q)
        ct = Ciphertext(self.ring.reduce(a, self.Q), self.ring.reduce(b, self.Q),
                        T, bound, len(self.graph))
        self.graph.append(dict(ciphertext=ct, operation=operation,
                               parents=tuple(c.node for c in parents), parameters=parameters))
        return ct

    def root(self, a, b, T, bound, name):
        return self.node(a, b, T, bound, "root", name=name)

    def add(self, x, y, subtract=False):
        assert x.T == y.T
        sign = -1 if subtract else 1
        return self.node(add(x.a, scale(y.a, sign)), add(x.b, scale(y.b, sign)),
                         x.T, x.bound+y.bound, "sub" if subtract else "add", (x,y))

    def plain_mul(self, x, c):
        c = self.ring.reduce(c, x.T)
        return self.node(self.ring.mul(x.a, c), self.ring.mul(x.b, c), x.T,
                         self.ring.mul_norm(c)*x.bound, "plain_mul", (x,), c=c)

    def plain_add(self, x, c):
        c = self.ring.reduce(c, x.T)
        delta, remainder = divmod(self.Q, x.T)
        return self.node(x.a, add(x.b, scale(c, delta)), x.T,
                         x.bound+F(remainder, x.T)*norm(c), "plain_add", (x,), c=c)

    def _keyswitch(self, component, name):
        digits = [[0]*self.ring.n for _ in range(self.length)]
        for h, value in enumerate(component):
            value %= self.Q
            for i in range(self.length):
                value, digits[i][h] = divmod(value, self.base)
            assert value == 0
        rows = self.keys[name]
        a = add(*(self.ring.mul(d, row[0]) for d, row in zip(digits, rows)))
        b = add(*(self.ring.mul(d, row[1]) for d, row in zip(digits, rows)))
        return a, b

    def automorphism(self, x, exponent):
        if exponent == 1:
            return x
        a, b = self._keyswitch(self.ring.auto(x.a, exponent), ("auto", exponent))
        b = add(b, self.ring.auto(x.b, exponent))
        return self.node(a, b, x.T,
                         self.ring.auto_norm(exponent)*x.bound+self.key_bound,
                         "auto", (x,), exponent=exponent)

    def multiply(self, x, y):
        """Standard FV: integer tensor, T/Q rounding, then relinearization."""
        assert x.T == y.T
        r, T, Q = self.ring, x.T, self.Q
        raw = (r.mul(x.b,y.b), add(r.mul(x.a,y.b), r.mul(y.a,x.b)), r.mul(x.a,y.a))
        scaled = [tuple(nearest(F(T*z,Q)) for z in c) for c in raw]
        a, b = self._keyswitch(scaled[2], "relin")
        a, b = add(a, scaled[1]), add(b, scaled[0])
        kx, ky = F(self.sigma+2,2)+x.bound/Q, F(self.sigma+2,2)+y.bound/Q
        bound = (r.C*(F(T,2)*(x.bound+y.bound)
                      +T*(kx*y.bound+ky*x.bound)+F(T,Q)*x.bound*y.bound)
                 +F(1+self.sigma+self.sigma**2,2)+self.key_bound)
        return self.node(a, b, T, bound, "multiply", (x,y))

    def power(self, x, exponent):
        assert exponent >= 1
        result = None
        while exponent:
            if exponent & 1:
                result = x if result is None else self.multiply(result, x)
            exponent //= 2
            if exponent:
                x = self.multiply(x, x)
        return result

    def exact_divide(self, x, p):
        assert x.T % p == 0
        # Public algorithm knows divisibility from the preceding digit circuit.
        # It performs NO inverse-mod-Q multiplication or component rounding.
        return self.node(x.a, x.b, x.T//p, x.bound, "exact_divide", (x,), p=p)

    def linear(self, x, coefficients):
        terms = [self.plain_mul(self.automorphism(x, a), c)
                 for a, c in coefficients.items() if any(c)]
        assert terms
        result = terms[0]
        for term in terms[1:]:
            result = self.add(result, term)
        return result

    def polynomial(self, x, coefficients):
        terms = []
        for i, c in enumerate(coefficients):
            if i and c:
                terms.append(self.plain_mul(self.power(x,i), scale(self.ring.one,c)))
        if terms:
            result = terms[0]
            for term in terms[1:]:
                result = self.add(result,term)
        else:
            result = self.plain_mul(x,self.ring.zero)
        if coefficients[0]:
            result = self.plain_add(result,scale(self.ring.one,coefficients[0]))
        return result


def polynomial_multiply(a,b,modulus):
    c = [0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            c[i+j] = (c[i+j]+x*y)%modulus
    return c


def lifting_polynomial(p,j):
    """F_j=X^p-p H_j, with H_j interpolated at p consecutive digit reps."""
    modulus = p**j
    digits = range(p) if p == 2 else range(-(p//2),p//2+1)
    h = [0]*p
    for digit in digits:
        basis, denominator = [1],1
        for other in digits:
            if other != digit:
                basis = polynomial_multiply(basis,[-other,1],modulus)
                denominator = denominator*(digit-other)%modulus
        value = ((digit**p-digit)//p)*pow(denominator,-1,modulus)
        for i,c in enumerate(basis):
            h[i] = (h[i]+value*c)%modulus
    f = [center(-p*c,p**(j+1)) for c in h]+[1]
    for z in range(p**(j+1)):
        digit = z%p if p == 2 else center(z,p)
        if (z-digit)%(p**j) == 0:
            assert sum(c*z**i for i,c in enumerate(f))%(p**(j+1)) == digit%(p**(j+1))
    return f


def digit_extract(evaluator, x, p, epsilon, precision):
    if p == 2:
        x = evaluator.plain_add(x,scale(evaluator.ring.one,2**(epsilon-precision-1)))
    for current in range(epsilon,precision,-1):
        lowest = x
        for j in range(1,current):
            lowest = evaluator.polynomial(lowest,lifting_polynomial(p,j))
        x = evaluator.exact_divide(evaluator.add(x,lowest,subtract=True),p)
    return x


def encrypt(ring,Q,T,secret,message,error,rng):
    a = tuple(rng.randrange(-Q//2,Q//2) for _ in range(ring.n))
    b = add(scale(message,Q//T),error,scale(ring.mul(a,secret),-1))
    return ring.reduce(a,Q),ring.reduce(b,Q)


def evaluation_keys(ring,Q,secret,base,rng):
    length = 0
    while base**length < Q:
        length += 1
    targets = {"relin":ring.mul(secret,secret)}
    targets.update({("auto",a):ring.auto(secret,a) for a in ring.units if a != 1})
    keys = {}
    nonzero_error_rows = 0
    for name,target in targets.items():
        rows = []
        for i in range(length):
            a = tuple(rng.randrange(-Q//2,Q//2) for _ in range(ring.n))
            e = tuple(rng.choice((-1,1)) for _ in range(ring.n))
            b = add(scale(target,base**i),e,scale(ring.mul(a,secret),-1))
            rows.append((ring.reduce(a,Q),ring.reduce(b,Q)))
            nonzero_error_rows += int(any(e))
        keys[name] = tuple(rows)
    return keys,nonzero_error_rows


def public_bootstrap(evaluator, input_ciphertext, input_modulus, boot_key,
                     pack_coefficients, unpack_coefficients, p, epsilon, precision):
    """All evaluation below is public; secrets are absent from this signature."""
    P = p**epsilon
    a,b = (tuple(nearest(F(P*z,input_modulus)) for z in component)
           for component in input_ciphertext)
    encrypted_phase = evaluator.plain_add(evaluator.plain_mul(boot_key,a),b)
    packed = [evaluator.linear(encrypted_phase,c) for c in pack_coefficients]
    extracted = [digit_extract(evaluator,c,p,epsilon,precision) for c in packed]
    terms = [evaluator.linear(c,coefficients)
             for c,coefficients in zip(extracted,unpack_coefficients)]
    output = terms[0]
    for term in terms[1:]:
        output = evaluator.add(output,term)
    return output, (a,b)


def audit_graph(evaluator, secret, root_messages):
    """Independent post-evaluation observer; never called by the evaluator."""
    ring,Q = evaluator.ring,evaluator.Q
    expected,errors = {},{}
    max_budget_ratio = F(0)
    max_actual_to_bound = F(0)
    exact_divisions = []
    ledger = []
    for node in evaluator.graph:
        ct,op,params = node["ciphertext"],node["operation"],node["parameters"]
        values = [expected[i] for i in node["parents"]]
        if op == "root":
            message = root_messages[params["name"]]
        elif op == "add":
            message = add(*values)
        elif op == "sub":
            message = add(values[0],scale(values[1],-1))
        elif op == "plain_mul":
            message = ring.mul(values[0],params["c"])
        elif op == "plain_add":
            message = add(values[0],params["c"])
        elif op == "auto":
            message = ring.auto(values[0],params["exponent"])
        elif op == "multiply":
            message = ring.mul(*values)
        elif op == "exact_divide":
            assert all(z%params["p"] == 0 for z in values[0])
            message = tuple(z//params["p"] for z in values[0])
        else:
            raise AssertionError(op)
        message = ring.reduce(message,ct.T)
        phase = add(ct.b,ring.mul(ct.a,secret))
        error = tuple(F(center(ct.T*z-Q*m,Q*ct.T),ct.T)
                      for z,m in zip(phase,message))
        assert norm(error) <= ct.bound, (ct.node,op,norm(error),ct.bound)
        assert norm(error) < F(Q,2*ct.T)
        decoded = tuple(center(nearest(F(ct.T*center(z,Q),Q)),ct.T) for z in phase)
        assert decoded == message, (ct.node,op,decoded,message)
        max_budget_ratio = max(max_budget_ratio,ct.bound/F(Q,2*ct.T))
        if ct.bound:
            max_actual_to_bound = max(max_actual_to_bound,norm(error)/ct.bound)
        if op == "exact_divide":
            old = evaluator.graph[node["parents"][0]]["ciphertext"]
            assert error == errors[old.node]
            delta = Q//ct.T-params["p"]*(Q//old.T)
            old_integer_error = add(error,scale(values[0],F(Q%old.T,old.T)))
            new_integer_error = add(error,scale(message,F(Q%ct.T,ct.T)))
            assert new_integer_error == add(old_integer_error,scale(message,-delta))
            exact_divisions.append(dict(old_T=old.T,new_T=ct.T,delta=delta))
        expected[ct.node],errors[ct.node] = message,error
        ledger.append(dict(node=ct.node,operation=op,parents=list(node["parents"]),
                           public_parameters=params,plaintext_modulus=ct.T,
                           certified_natural_error_bound=str(ct.bound),
                           decoding_threshold=str(F(Q,2*ct.T)),
                           budget_ratio=str(ct.bound/F(Q,2*ct.T)),
                           ciphertext=dict(a=list(ct.a),b=list(ct.b)),
                           post_evaluation_audit=dict(expected_plaintext=list(message),
                                                     natural_error=list(map(str,error)),
                                                     error_norm=str(norm(error)))))
    return expected,errors,dict(
        public_nodes=len(evaluator.graph),
        operations=dict(sorted(Counter(x["operation"] for x in evaluator.graph).items())),
        maximum_budget_ratio=float(max_budget_ratio),
        maximum_observed_error_to_bound=float(max_actual_to_bound),
        exact_divisions=exact_divisions,
        node_ledger=ledger,
    )


def verify_digit_identities(p,epsilon,precision):
    P = p**epsilon
    for original in range(P):
        value = (original+(2**(epsilon-precision-1) if p == 2 else 0))%P
        for current in range(epsilon,precision,-1):
            lowest = value
            for j in range(1,current):
                f = lifting_polynomial(p,j)
                lowest = sum(c*lowest**i for i,c in enumerate(f))%(p**current)
            assert (value-lowest)%p == 0
            value = ((value-lowest)//p)%(p**(current-1))
        expected = nearest(F(center(original,P),p**(epsilon-precision)))%(p**precision)
        assert value == expected
    return P


def run_fixture(config,seed):
    ring = Ring(config["m"],config["phi"])
    p,epsilon,precision = config["p"],config["epsilon"],config["r"]
    P,t = p**epsilon,p**precision
    assert gcd(p,ring.m) == 1
    # All supplied factors have degree <= 2: a quadratic is irreducible iff
    # it has no root over the prime field. No CAS factorization is trusted.
    for factor in config["factors"]:
        if len(factor) == 3:
            assert all(sum(c*x**i for i,c in enumerate(factor))%p
                       for x in range(p))
        else:
            assert len(factor) == 2
    Q = P*2**256+config["remainder"]
    rng = random.Random(seed)
    secret_in,secret_out = tuple(config["secret_in"]),tuple(config["secret_out"])
    sigma = ring.C
    assert ring.mul_norm(secret_in) <= sigma and ring.mul_norm(secret_out) <= sigma
    pack,_,crt = crt_maps(ring,config["factors"],P)
    _,unpack,_ = crt_maps(ring,config["factors"],t)
    pack_compiled = [ring.compile_linear(mat,P) for mat in pack]
    unpack_compiled = [ring.compile_linear(mat,t) for mat in unpack]
    keys,key_rows = evaluation_keys(ring,Q,secret_out,16,rng)
    digit_cases = verify_digit_identities(p,epsilon,precision)
    results=[]
    for i,message in enumerate(config["messages"]):
        message = ring.reduce(message,t)
        # A substantial nonzero input error, far larger than evaluation noise.
        amplitude = Q//config["input_error_divisor"]
        error_in = tuple(amplitude*(-1 if (i+j)%2 else 1) for j in range(ring.n))
        input_ct = encrypt(ring,Q,t,secret_in,message,error_in,rng)
        input_bound = F(amplitude)+F(Q%t,2)
        low_bound = F(P,Q)*input_bound+F(1+sigma,2)
        assert input_bound < F(Q,2*t)
        assert low_bound < F(p**(epsilon-precision),2)
        boot_error=tuple((-1)**(i+j) for j in range(ring.n))
        ba,bb = encrypt(ring,Q,P,secret_out,secret_in,boot_error,rng)
        evaluator=PublicEvaluator(ring,Q,sigma,16,keys)
        boot=evaluator.root(ba,bb,P,1+F(Q%P,P)*norm(secret_in),"encrypted_input_secret")
        output,low = public_bootstrap(evaluator,input_ct,Q,boot,pack_compiled,
                                     unpack_compiled,p,epsilon,precision)
        expected,errors,stats = audit_graph(evaluator,secret_out,
                                          {"encrypted_input_secret":secret_in})
        assert expected[output.node] == message
        low_phase=ring.reduce(add(low[1],ring.mul(low[0],secret_in)),P)
        recovered=tuple(center(nearest(F(z,p**(epsilon-precision))),t) for z in low_phase)
        assert recovered == message
        actual_low_error=ring.reduce(add(low_phase,scale(message,-p**(epsilon-precision))),P)
        assert norm(actual_low_error) <= low_bound
        assert norm(errors[output.node]) < amplitude
        stats.update(message=list(message), output=list(expected[output.node]),
                     input_error_bound=str(input_bound),
                     switched_error_bound=str(low_bound),
                     switched_error=list(actual_low_error),
                     output_error_bound=str(output.bound),
                     output_observed_error=str(norm(errors[output.node])),
                     output_bound_bits=output.bound.numerator.bit_length(),
                     ciphertext_modulus_bits=Q.bit_length())
        results.append(stats)
    # In characteristic p^e, the lifted Frobenius is tau_p, NOT z -> z^p.
    frobenius_counterexample=None
    for v in product(range(min(P,4)),repeat=ring.n):
        power_v=ring.one
        for _ in range(p):
            power_v=ring.mul(power_v,v)
        lifted=ring.reduce(ring.auto(v,p),P)
        naive=ring.reduce(power_v,P)
        if lifted != naive:
            frobenius_counterexample=dict(element=list(v),lifted=list(lifted),naive_power=list(naive))
            break
    assert frobenius_counterexample is not None
    return dict(name=config["name"],cyclotomic_index=ring.m,degree=ring.n,p=p,
                epsilon=epsilon,r=precision,P=P,t=t,Q=str(Q),Q_remainder_P=Q%P,
                extension_degree=len(config["factors"][0])-1,
                scalar_slots_per_ciphertext=len(config["factors"]),
                packed_ciphertexts=len(pack),ring_product_constant=ring.C,
                secret_operator_norm_bound=sigma,
                trace_dual=[list(x) for x in ring.trace_dual(P)],
                crt_matrix=[list(x) for x in crt],
                nonzero_evaluation_error_rows=key_rows,
                exhaustive_digit_cases=digit_cases,
                lifted_frobenius_counterexample=frobenius_counterexample,runs=results)


CONFIGURATIONS = [
    dict(name="split_phi4_p5",m=4,phi=[1,0,1],p=5,epsilon=2,r=1,
         factors=[[-7,1],[7,1]],remainder=7,
         secret_in=[1,-1],secret_out=[1,1],input_error_divisor=32,
         messages=[[2,-2],[-1,1]]),
    dict(name="extension_phi8_p3",m=8,phi=[1,0,0,0,1],p=3,epsilon=3,r=1,
         factors=[[-1,5,1],[-1,-5,1]],remainder=13,
         secret_in=[1,0,-1,1],secret_out=[1,-1,0,1],input_error_divisor=32,
         messages=[[1,-1,0,1],[-1,1,-1,0]]),
    dict(name="extension_phi8_p3_r2",m=8,phi=[1,0,0,0,1],p=3,epsilon=4,r=2,
         factors=[[-1,22,1],[-1,-22,1]],remainder=13,
         secret_in=[1,0,-1,1],secret_out=[1,-1,0,1],input_error_divisor=64,
         messages=[[4,-4,2,0],[-3,1,-4,4]]),
    dict(name="binary_coprime_phi3_p2",m=3,phi=[1,1,1],p=2,epsilon=4,r=1,
         factors=[[1,1,1]],remainder=3,
         secret_in=[1,-1],secret_out=[1,1],input_error_divisor=128,
         messages=[[1,0],[0,1]]),
]


def load_json_shards(manifest_path):
    """Verify every shard and reconstruct the original full result object."""
    manifest_path=Path(manifest_path)
    index=json.loads(manifest_path.read_text(encoding="utf-8"))
    assert index["format"] == "bfv-bootstrap-audit-index-v1"
    metadata={key:index[key] for key in
              ("status","scope","security_claim","optimized_GV_implementation")}
    result=dict(metadata,fixtures=[])
    for entry in index["parts"]:
        raw=(manifest_path.parent/entry["path"]).read_bytes()
        assert len(raw) == entry["bytes"] < 250000
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
        part=json.loads(raw)
        assert {key:value for key,value in part.items() if key != "fixtures"} == metadata
        assert len(part["fixtures"]) == 1
        fixture=part["fixtures"][0]
        assert fixture["name"] == entry["name"]
        assert len(fixture["runs"]) == entry["runs"]
        assert sum(len(run["node_ledger"]) for run in fixture["runs"]) == entry["nodes"]
        result["fixtures"].append(fixture)
    assert len(result["fixtures"]) == index["configurations"]
    assert sum(len(f["runs"]) for f in result["fixtures"]) == index["runs"]
    assert sum(len(r["node_ledger"]) for f in result["fixtures"] for r in f["runs"]) == index["audited_ciphertext_nodes"]
    canonical=(json.dumps(result,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    assert len(canonical) == index["canonical_bytes"]
    assert hashlib.sha256(canonical).hexdigest() == index["canonical_sha256"]
    return result


def write_json_shards(result,manifest_path):
    """Write compact per-configuration data plus a small, explicit index."""
    manifest_path=Path(manifest_path)
    directory=manifest_path.parent/(manifest_path.stem if manifest_path.suffix
                                    else manifest_path.name+"-parts")
    metadata={key:value for key,value in result.items() if key != "fixtures"}
    canonical=(json.dumps(result,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    entries,payloads=[],[]
    for fixture in result["fixtures"]:
        part=dict(metadata,fixtures=[fixture])
        raw=(json.dumps(part,ensure_ascii=False,separators=(",",":"))+"\n").encode("utf-8")
        assert len(raw) < 250000, (fixture["name"],len(raw))
        path=directory/(fixture["name"]+".json")
        entries.append(dict(name=fixture["name"],
                            path=path.relative_to(manifest_path.parent).as_posix(),
                            bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
                            runs=len(fixture["runs"]),
                            nodes=sum(len(r["node_ledger"]) for r in fixture["runs"])))
        payloads.append((path,raw))
    index=dict(metadata,format="bfv-bootstrap-audit-index-v1",
               canonical_serialization="UTF-8 json.dumps(ensure_ascii=False, indent=2) plus newline",
               canonical_bytes=len(canonical),canonical_sha256=hashlib.sha256(canonical).hexdigest(),
               configurations=len(entries),runs=sum(e["runs"] for e in entries),
               audited_ciphertext_nodes=sum(e["nodes"] for e in entries),parts=entries)
    directory.mkdir(parents=True,exist_ok=True)
    for path,raw in payloads:
        path.write_bytes(raw)
    manifest_path.write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    assert load_json_shards(manifest_path) == json.loads(canonical)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json",type=Path,help="optional full audit result, exact bounds as strings")
    parser.add_argument("--json-shards",type=Path,
                        help="optional index path with compact per-configuration JSON files, each <250000 bytes")
    args=parser.parse_args()
    if args.json and args.json_shards and args.json.resolve() == args.json_shards.resolve():
        parser.error("--json and --json-shards must use different output paths")
    fixtures=[run_fixture(c,20261109+i) for i,c in enumerate(CONFIGURATIONS)]
    result=dict(status="pass",scope="public BFV evaluation with independent secret-key auditing afterward",
                security_claim=False,optimized_GV_implementation=False,fixtures=fixtures)
    if args.json:
        args.json.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    if args.json_shards:
        write_json_shards(result,args.json_shards)
    for f in fixtures:
        print(json.dumps(dict(name=f["name"],status="pass",p=f["p"],P=f["P"],
                              extension_degree=f["extension_degree"],
                              packed_ciphertexts=f["packed_ciphertexts"],
                              runs=len(f["runs"]),
                              nodes=[r["public_nodes"] for r in f["runs"]],
                              max_budget_ratio=max(r["maximum_budget_ratio"] for r in f["runs"]),
                              output_bound_bits=[r["output_bound_bits"] for r in f["runs"]],
                              ciphertext_modulus_bits=f["runs"][0]["ciphertext_modulus_bits"]),
                         sort_keys=True))


if __name__ == "__main__":
    main()
