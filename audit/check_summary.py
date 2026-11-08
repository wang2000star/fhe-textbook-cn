#!/usr/bin/env python3
"""Small exact counterexamples for preface/D6 review claims; standard library only."""
from fractions import Fraction
from itertools import product
import math
import unittest


def nearest(x):
    x = Fraction(x)
    return (x.numerator * 2 + x.denominator) // (2 * x.denominator)


def centered(x, q):
    return (x + q // 2) % q - q // 2


class SummaryCounterexamples(unittest.TestCase):
    def test_zero_mean_does_not_imply_constant_noise(self):
        values = [-1, 1]
        sums = [a+b for a,b in product(values,repeat=2)]
        self.assertEqual(sum(sums),0)
        self.assertEqual(Fraction(sum(x*x for x in sums),len(sums)),2)
        self.assertEqual(Fraction(sum((2*x)**2 for x in values),len(values)),4)

    def test_finite_noise_budget(self):
        q,t,delta = 32,8,4
        # Encrypt zero with phase error 1, then add the same ciphertext five times.
        self.assertEqual(nearest(Fraction(1,delta)) % t,0)
        self.assertEqual(nearest(Fraction(5,delta)) % t,1)
        self.assertLess(1,delta/2)
        self.assertGreater(5,delta/2)

    def test_bfv_unsigned_division_by_floor_scale(self):
        q,t,delta,m,e=31,8,3,0,-1
        phase=(delta*m+e)%q
        self.assertEqual(nearest(Fraction(phase,delta))%t,2)
        self.assertEqual(nearest(Fraction(t*phase,q))%t,m)
        self.assertLess(abs(e),delta/2)

    def test_bgv_condition_requires_entire_centered_phase(self):
        q,t,m,e=11,5,1,2
        self.assertLess(t*e,q)  # Original one-sided condition passes.
        self.assertEqual(centered(m+t*e,q)%t,0)
        self.assertNotEqual(centered(m+t*e,q)%t,m)

    def test_equal_factor_residues_do_not_give_equal_chain_residues(self):
        factors=[7,17,37]
        self.assertEqual([w%5 for w in factors],[2,2,2])
        self.assertNotEqual(factors[0]%5,(factors[0]*factors[1])%5)

    def test_ckks_actual_rescale_factor(self):
        delta,w=100,97
        self.assertEqual(Fraction(delta*delta,w),Fraction(10000,97))
        self.assertNotEqual(Fraction(delta*delta,w),delta)
        # Component rounding can be nonzero even with zero encryption noise.
        self.assertNotEqual(Fraction(nearest(Fraction(1,2)),1),Fraction(1,2))

    def test_bfv_lift_exposes_q_multiple(self):
        q,delta,a,b,s=17,4,8,13,1
        self.assertEqual((b+a*s)%q,delta)
        self.assertEqual((b+a*s)%(q*delta),delta+q)
        self.assertNotEqual((b+a*s)%(q*delta),delta)

    def test_bgv_rounding_to_multiple_of_t_destroys_message(self):
        t,q,qp,c=5,31,16,1
        bad=t*nearest(Fraction(c,t*t))
        candidates=range(c-3*t,c+3*t+1,t)
        good=min(candidates,key=lambda v:abs(Fraction(v)-Fraction(qp*c,q)))
        self.assertEqual(bad%t,0)
        self.assertEqual(good%t,c)

    def test_moddrop_needs_no_wrap_condition(self):
        q,qp,t,m,e=77,11,5,3,2
        self.assertEqual(q%qp,0)
        self.assertEqual(centered(m+t*e,q)%t,m)
        self.assertEqual(centered(m+t*e,qp)%t,2)

    def test_automorphism_has_two_scalar_orbits(self):
        n=8
        positive=[pow(5,j,2*n) for j in range(n//2)]
        negative=[(-x)%(2*n) for x in positive]
        self.assertTrue(set(positive).isdisjoint(negative))
        self.assertEqual(set(positive+negative),set(range(1,2*n,2)))
        self.assertEqual(pow(5,n//2,2*n),1)

    def test_tfhe_blind_rotation_sign_must_match_phase(self):
        modulus,a,b,s=16,1,3,1
        phase=(b+a*s)%modulus
        self.assertEqual((-b-a*s)%modulus,(-phase)%modulus)
        self.assertNotEqual((-b+a*s)%modulus,(-phase)%modulus)

    def test_sine_is_approximate_modular_reduction(self):
        q,r,k=64,16,3
        got=q*math.sin(2*math.pi*(r+k*q)/q)/(2*math.pi)
        bound=(2*math.pi)**2*abs(r)**3/(6*q*q)
        self.assertGreater(abs(got-r),5)
        self.assertLessEqual(abs(got-r),bound)
        self.assertAlmostEqual(got,q/(2*math.pi))

    def test_integer_digit_division_changes_plaintext_modulus(self):
        # In Z/9Z, 3 has no inverse; exact division 3x/3 is interpreted in Z/3Z.
        self.assertNotEqual(math.gcd(3,9),1)
        self.assertEqual((6//3)%3,((6+9)//3)%3)
        self.assertNotEqual((6//3)%9,((6+9)//3)%9)


if __name__=='__main__':
    unittest.main(verbosity=2)
