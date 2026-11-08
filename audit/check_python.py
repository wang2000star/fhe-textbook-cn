#!/usr/bin/env python3
"""Regression checks for confirmed academic/code discrepancies (numpy, sympy, fastcore).

These checks establish the stated finite examples and arithmetic invariants, not
cryptographic security or general correctness of arbitrary parameter sets.
"""
from pathlib import Path
import ast
import contextlib
import importlib
import io
import math
import random
import subprocess
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'source code'))
import numpy as np
from numpy.polynomial import Polynomial
import common as common
import bfv_lib as bfv
import bgv_lib as bgv
import ckks_lib as ckks
import tfhe_lib as tfhe


def poly(values):
    return Polynomial(np.array(values, dtype=object))


def coefficients(p, n):
    return list(p.coef) + [0] * (n - len(p.coef))


def load_experiment_functions(filename, n=2):
    """Load only declarations, avoiding the old scripts' random top-level demos."""
    path = ROOT / 'source code' / filename
    tree = ast.parse(path.read_text())
    declarations = [node for node in tree.body
                    if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef))]
    namespace = {'__name__': 'audit_legacy', 'N': n}
    exec(compile(ast.Module(body=declarations, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


class AcademicCodeChecks(unittest.TestCase):
    def setUp(self):
        random.seed(4189)
        np.random.seed(4189)

    def test_optional_decryption_diagnostics(self):
        z = poly([0, 0])
        calls = [
            lambda: bfv.fhe_decrypt(z, z, 2, 5, 1024, z, 204),
            lambda: bgv.fhe_decrypt(z, z, 2, 5, [1024], z, 5),
            lambda: ckks.fhe_decrypt(z, z, 2, [1024], z, 32),
            lambda: tfhe.tfhe_decrypt(np.array([0]), 0, 8, 1024, np.array([0]), 128),
        ]
        for call in calls:
            with self.subTest(call=call):
                _, diagnostic = call()
                self.assertIsNone(diagnostic)

    def test_unimplemented_bootstrapping_is_explicit(self):
        for module, args in [(bfv, (None, None, 2, 5, 1024)),
                             (bgv, (None, None, 2, 1024)),
                             (ckks, (None, None, 2, 1024))]:
            with self.subTest(module=module.__name__), self.assertRaises(NotImplementedError):
                module.fhe_bootstrapping(*args)

    def test_exact_signed_decomposition(self):
        for q in [17, 32, 97]:
            for base in [2, 3, 4, 16]:
                length = common.digits_len(q, base)
                for value in range(-q // 2, q // 2 + 1):
                    ds = common.gadget_decompose_poly(poly([value, 0]), 2, q, base, length)
                    recovered = sum(int(d.coef[0]) * base**i for i, d in enumerate(ds))
                    self.assertEqual(recovered, common.centered_mod(value, q))
        with self.assertRaises(ValueError):
            common.gadget_decompose_poly(poly([7, 0]), 2, 97, 2, 1)
        with self.assertRaises(ValueError):
            common.digits_len(17, 1)

    def test_integer_ring_products_and_ntt(self):
        # X^(N-1)*X = -1; X^(2N) = +1, including the legacy sign-precedence bug.
        for n in [2, 4, 8]:
            x = poly([0, 1])
            xn1 = poly([0] * (n - 1) + [1])
            self.assertEqual(coefficients(common.poly_mult_integer(xn1, x, n), n), [-1] + [0]*(n-1))
            for q in [97, 65537, 1024]:
                for _ in range(8):
                    a, b = [random.randint(-30, 30) for _ in range(n)], [random.randint(-30, 30) for _ in range(n)]
                    # Coefficient oracle directly from the negacyclic convolution identity.
                    expected = [sum(a[i] * b[(k-i) % n] * (1 if i <= k else -1)
                                    for i in range(n)) for k in range(n)]
                    expected = [common.centered_mod(v, q) for v in expected]
                    self.assertEqual(coefficients(common.poly_mult(poly(a), poly(b), n, q), n), expected)
        for filename in ['bfv.py', 'bfv_rotation_only.py', 'ckks.py']:
            ns = load_experiment_functions(filename)
            result = ns['reduce_polynomial'](poly([0, 0, 0, 0, 1]), 2, 97)
            self.assertEqual(int(result.coef[0]), 1, filename)
        for filename in ['bgv.py', 'rns.py']:
            ns = load_experiment_functions(filename)
            source = np.array([0, 0, 1], dtype=object)
            self.assertEqual(list(ns['poly_reduce'](source, 97)), [-1, 0], filename)
            self.assertEqual(list(source), [0, 0, 1])

    def test_bfv_nondivisible_modulus_counterexample(self):
        n, p, q = 2, 17, 8191
        scale, secret = q // p, poly([1, -1])
        a1, b1, a2, b2 = map(poly, [[2715, 3314], [3124, 844], [4710, 5559], [-1597, 3494]])
        self.assertEqual(list(bfv.fhe_decrypt(a1, b1, n, p, q, secret, scale)[0].coef), [2, 3])
        self.assertEqual(list(bfv.fhe_decrypt(a2, b2, n, p, q, secret, scale)[0].coef), [1, -8])
        key = common.fhe_keyswitch_keygen(common.poly_mult(secret, secret, n, q), secret,
                                         n, q, base=16, bound=0)
        fixed = bfv.fhe_mult_cipher_cipher(a1, b1, a2, b2, n, p, q, scale, key)
        self.assertEqual(list(bfv.fhe_decrypt(*fixed, n, p, q, secret, scale)[0].coef), [-8, 4])
        # Reproduce the old lossy intermediate-modulus algorithm independently.
        a1,b1,a2,b2 = [common.poly_mod(v,n,q) for v in [a1,b1,a2,b2]]
        d0 = common.poly_rescale_P_over_Q(common.poly_mult(b1, b2, n, q*scale), p, q, n)
        d1 = common.poly_rescale_P_over_Q(common.poly_add(common.poly_mult(a1, b2, n, q*scale),
                        common.poly_mult(a2, b1, n, q*scale), n, q*scale), p, q, n)
        d2 = common.poly_rescale_P_over_Q(common.poly_mult(a1, a2, n, q*scale), p, q, n)
        phase_old = common.poly_add(d0, common.poly_add(common.poly_mult(d1, secret, n, q),
                        common.poly_mult(d2, common.poly_mult(secret, secret, n, q), n, q), n, q), n, q)
        old_message = [common.centered_mod(common.round_div(p*int(v), q), p) for v in phase_old.coef]
        self.assertEqual(old_message, [8, 4])

    def test_bfv_standard_decoder_not_division_by_floor_scale(self):
        # A negative phase's unsigned representative exposes /floor(q/t) dependence.
        q, t, delta = 31, 8, 3
        # Valid negative noise, unsigned representative: original textbook formula fails.
        self.assertEqual(common.round_div(30, delta) % t, 2)
        self.assertEqual(common.round_div(t*30, q) % t, 0)
        self.assertEqual(common.round_div(t*(-1), q) % t, 0)

    def test_ckks_tracks_actual_output_scale(self):
        n, base, scale = 2, [1009, 97], 100
        z, body = poly([0, 0]), poly([100, 0])
        out = ckks.fhe_mult_cipher_plain(z, body, poly([1, 0]), n, base, scale)
        actual_scale = ckks.ckks_rescaled_scale(scale, scale, 97)
        self.assertAlmostEqual(actual_scale, 10000/97)
        decoded, _ = ckks.fhe_decrypt(*out, n, base, z, actual_scale)
        wrong, _ = ckks.fhe_decrypt(*out, n, base, z, scale)
        self.assertLess(abs(float(decoded.coef[0]) - 1), 0.001)
        self.assertGreater(abs(float(wrong.coef[0]) - 1), 0.02)
        with self.assertRaises(ValueError):
            ckks.fhe_mult_cipher_plain(z, body, poly([1, 0]), n, [97], scale)

    def test_bgv_switch_with_residue_and_error_conditions(self):
        n, t, old_q, new_q = 2, 5, 451, 41  # all congruent to 1 modulo t
        secret = poly([1, -1])
        for message in [-2, -1, 0, 1, 2]:
            for error in [-1, 0, 1]:
                a = poly([26, -17])
                b = common.poly_mod(poly([message+t*error, 0])-common.poly_mult(a, secret, n, old_q),n,old_q)
                result = [bgv.bgv_mod_switch_poly(v, n, t, old_q, new_q) for v in [a,b]]
                decoded,_ = bgv.fhe_decrypt(*result,n,t,[new_q],secret,t)
                self.assertEqual(list(decoded.coef),[message,0])
        with self.assertRaises(ValueError):
            bgv.bgv_mod_switch_poly(poly([1,0]), n, t, old_q, 43)

    def test_rns_exact_extension_drop_switch_and_carry(self):
        ns = load_experiment_functions('rns.py')
        self.assertEqual(list(ns['mod_inverse'](np.array([2,3],dtype=object),7)),[-3,-2])
        source_base, target_base, auxiliary = [5, 7], [11, 13], 17
        values = np.arange(-17, 18, dtype=object)
        residues = [ns['centered_mod'](values, q) for q in source_base]
        extended = ns['ModRaiseRNS'](residues, source_base, source_base+target_base)
        self.assertEqual(list(ns['rns_recover'](extended, source_base+target_base)), list(values))
        self.assertEqual(list(ns['ModDropRNS'](extended, source_base+target_base,[7])[0]),list(residues[1]))
        augmented = residues + [ns['centered_mod'](values,auxiliary)]
        converted = ns['FastBConvEx'](augmented, source_base, auxiliary, target_base)
        self.assertEqual(list(ns['rns_recover'](converted,target_base)),list(values))
        all_base, kept = [11,13,5,7], [11,13]
        values = np.array([-2499,-246,0,245,2499],dtype=object)
        residues = [ns['centered_mod'](values,q) for q in all_base]
        switched = ns['ModSwitchRNS'](residues,all_base,kept)
        expected = [common.centered_mod(common.round_div(int(v),35),143) for v in values]
        self.assertEqual(list(ns['rns_recover'](switched,kept)),expected)
        with self.assertRaises(ValueError):
            ns['FastBConvEx'](augmented,source_base,3,target_base)

    def test_large_integer_modswitch_avoids_float_rounding(self):
        ns = load_experiment_functions('bgv.py')
        # Halfway-adjacent > 2**53: floating point loses the deciding unit.
        q, qnew, t = 2**61-1, 2**59+1, 3
        while q % t != qnew % t or math.gcd(q,t) != 1:
            qnew += 1
        values = np.array([q//3, -(q//3)],dtype=object)
        self.assertNotEqual(common.round_div(int(values[0])*qnew,q),
                            round(float(values[0])*(float(qnew)/float(q))))
        got = ns['ModSwitchBGV'](values,t,q,qnew)
        rounded = np.array([common.round_div(int(v)*qnew,q) for v in values],dtype=object)
        correction = ns['centered_mod']((qnew*values-q*rounded)*pow(q,-1,t),t)
        expected = ns['centered_mod'](rounded+correction,qnew)
        self.assertEqual(list(got),list(expected))
        self.assertEqual(list(values),[q//3,-(q//3)])

    def test_tfhe_wraparound_and_mock_boundary(self):
        k,p,q = 2,256,2**30
        scale,secret = q//p,np.array([1,0],dtype=object)
        ct1 = tfhe.tfhe_encrypt(255,k,p,q,secret,scale)
        ct2 = tfhe.tfhe_encrypt(255,k,p,q,secret,scale)
        key = tfhe.tfhe_keyswitch_keygen(np.outer(secret,secret).flatten(),secret,k,q,bound=0)
        out = tfhe.tfhe_mult_cipher_cipher(*ct1,*ct2,k,p,q,scale,key)
        self.assertEqual(tfhe.tfhe_decrypt(*out,p,q,secret,scale)[0],1)
        self.assertEqual(tfhe.tfhe_decrypt(*tfhe.tfhe_add_cipher_cipher(*ct1,*ct2,q),p,q,secret,scale)[0],254)
        mock_key = tfhe.tfhe_bootstrap_keygen(secret)
        self.assertEqual(mock_key['type'],'mock_bk')
        self.assertTrue(np.array_equal(mock_key['s'],secret))
        mock_out = tfhe.tfhe_mult_cipher_cipher_circuit_bootstrapping(*ct1,*ct2,k,p,q,scale,mock_key)
        self.assertEqual(tfhe.tfhe_decrypt(*mock_out,p,q,secret,scale)[0],1)

    def test_all_documented_example_operations(self):
        operations = ['encode','encrypt','add_cipher_plain','add_cipher_cipher',
                      'mult_cipher_plain','mult_cipher_cipher','keyswitch','rotate']
        for scheme in ['bfv','bgv','ckks','tfhe']:
            module = importlib.import_module(scheme+'_example')
            module.args = types.SimpleNamespace(encrypt=True)
            for operation in operations+(['conjugate'] if scheme=='ckks' else []):
                if scheme=='tfhe' and operation in ['encode','rotate']:
                    continue
                for randomized in [False, True]:
                    with self.subTest(scheme=scheme,operation=operation,randomized=randomized):
                        random.seed(601); np.random.seed(601)
                        with contextlib.redirect_stdout(io.StringIO()):
                            module.main(0,operation!='encode',operation,randomized)

    def test_cli_flags_and_failure_exit_status(self):
        for script, flag in [('bfv_example.py','--encode'),('ckks_example.py','--conjugate')]:
            run = subprocess.run([sys.executable,str(ROOT/'source code'/script),flag],
                                 text=True,capture_output=True,timeout=30)
            self.assertEqual(run.returncode,0,run.stderr+run.stdout[-1000:])
        module = importlib.import_module('tfhe_example')
        old_decrypt = module.tfhe_decrypt
        try:
            module.tfhe_decrypt = lambda *args: (-1,0)
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as failure:
                module.main(0,True,'encrypt',False)
            self.assertEqual(failure.exception.code,1)
        finally:
            module.tfhe_decrypt = old_decrypt

    def test_legacy_ckks_encoder_uses_instance_parameters(self):
        ns = load_experiment_functions('ckks.py', n=8)
        ns.update(M=16, scale=10000, is_homogeneous_rotation=True)
        with contextlib.redirect_stdout(io.StringIO()):
            encoder = ns['CKKSEncoder'](4, 100)
            values = np.array([1+2j,3-4j],dtype=object)
            decoded = encoder.decode(encoder.encode(values))[:2]
        self.assertEqual(encoder.M,8)
        self.assertLess(max(abs(a-b) for a,b in zip(values,decoded)),0.02)

    def test_positive_power_of_two(self):
        self.assertEqual(common.get_ntt_root(1, 1000000007), 1)
        self.assertEqual(list(common.poly_mult(poly([3]), poly([4]), 1, 1000000007).coef), [12])
        for value in [-8,-1,0,3,2**70+1]:
            self.assertFalse(common.is_power_of_2(value))
        for value in [1,2,4,2**70]:
            self.assertTrue(common.is_power_of_2(value))


if __name__ == '__main__':
    unittest.main(verbosity=2)
