from common import *



def fhe_encrypt(m: Polynomial, N, Q_BASE, s, scale):
	"""
	Returns ciphertext (a, b):
	  a <- uniform in R_q
	  e <- small
	  b = -a*s + e + scale*m   (mod x^n+1, q)
	"""
	Q = math.prod(Q_BASE)
	m_scaled = round_polynomial(Polynomial(np.array([c * scale for c in m.coef], dtype=object)))

	a = sample_uniform_poly(N, Q)
	e = sample_small_poly(N, bound=1)

	b = poly_add(poly_add(-poly_mult(a, s, N, Q), e, N, Q),
				 m_scaled, N, Q)

	a = poly_mod(a, N, Q)
	b = poly_mod(b, N, Q)
	return (a, b)



def fhe_decrypt(a: Polynomial, b: Polynomial, N, Q_BASE, s, scale, expected_dec: Polynomial = None) -> Polynomial:
	"""
	Decrypt:
	  v = b + a*s  (mod x^n+1, q)  ~= scale*m + e
	  m_hat = v/scale (approximate coefficients; no integer rounding)
	  (optionally centered mod p if p was stored by fhe_encrypt)
	"""
	Q = math.prod(Q_BASE)
	v = poly_add(b, poly_mult(a, s, N, Q), N, Q)
	m_hat = [c / scale for c in v.coef]

	max_abs = None  # No reference plaintext was supplied for a diagnostic.
	if expected_dec is not None:
		e = poly_sub(m_hat, expected_dec, N, Q)
		max_abs = float(np.max(np.abs(e.coef))) if len(e.coef) else 0.0
	return Polynomial(np.array(m_hat, dtype=object)), max_abs

def fhe_add_cipher_cipher(a1, b1, a2, b2, N, Q_BASE):
	Q = math.prod(Q_BASE)
	a3 = poly_add(a1, a2, N, Q)
	b3 = poly_add(b1, b2, N, Q)
	return (a3, b3)

def fhe_add_cipher_plain(a1, b1, p2, N, Q_BASE, scale):
	Q = math.prod(Q_BASE)
	p2_scaled = round_polynomial(Polynomial(np.array([c * scale for c in p2.coef], dtype=object)))
	b3 = poly_add(b1, p2_scaled, N, Q)
	return (a1, b3) 

def fhe_mult_cipher_plain(a1, b1, p2, N, Q_BASE, scale):
   """Multiply and rescale, mutating Q_BASE. Track scale**2 / dropped prime."""
   if len(Q_BASE) < 2:
       raise ValueError("CKKS rescaling requires at least two modulus factors")
   # 1. Scale the plaintext (Delta * m)
   # Use integer rounding to keep it in the ring
   p2_scaled = round_polynomial(Polynomial(np.array([c * scale for c in p2.coef], dtype=object)))
   
   # 2. Multiply ciphertext by the SCALED plaintext
   Q = math.prod(Q_BASE) 
   a3 = poly_mult(a1, p2_scaled, N, Q)
   b3 = poly_mult(b1, p2_scaled, N, Q)

   # 3. Rescale (Divide by the last prime q_last)
   q_last = Q_BASE.pop() 
   
   # 4. Modulo switching for the result (Divide coefficients by q_last)
   a3_rescaled = Polynomial(np.array([round_div(c, q_last) for c in a3.coef], dtype=object))
   b3_rescaled = Polynomial(np.array([round_div(c, q_last) for c in b3.coef], dtype=object))
   
   return (a3_rescaled, b3_rescaled)


def fhe_rotate(a1, b1, N, Q_BASE, rotation_offset, galois_rotation_key):
	Q = math.prod(Q_BASE)
	# 1) Automorphism on ciphertext components
	a_rot = poly_mod(poly_rotate(a1, Q, N, rotation_offset), N, Q)
	b_rot = poly_mod(poly_rotate(b1, Q, N, rotation_offset), N, Q)

	# 2) Key-switch from s_rot -> s (cache by (offset,N,Q,s)) by gadget decomposition
	a_out, b_out = fhe_keyswitch(a_rot, b_rot, galois_rotation_key)
	return (a_out, b_out)


def fhe_conjugate(a1, b1, N, Q_BASE, conjugate_key):
	Q = math.prod(Q_BASE)

	a_conj = poly_conjugate(a1, N, Q)
	b_conj = poly_conjugate(b1, N, Q)

	a_out, b_out = fhe_keyswitch(a_conj, b_conj, conjugate_key)
	return (a_out, b_out)


def fhe_mult_cipher_cipher(a1, b1, a2, b2, N, Q_BASE, scale, relin_key):
	"""
	CKKS ct×ct with gadget decomposition relinearization.
	Mutates Q_BASE. The output scale is scale**2 / the removed prime.
	"""
	if len(Q_BASE) < 2:
		raise ValueError("CKKS rescaling requires at least two modulus factors")
	Q = math.prod(Q_BASE)

	# Ensure inputs are centered in R_Q
	a1 = poly_mod(a1, N, Q); b1 = poly_mod(b1, N, Q)
	a2 = poly_mod(a2, N, Q); b2 = poly_mod(b2, N, Q)

	# ---- Tensor product modulo the current ciphertext modulus ----
	d0_raw = poly_mult(b1, b2, N, Q)  # b1*b2
	d1_raw = poly_add(
		poly_mult(b1, a2, N, Q),
		poly_mult(a1, b2, N, Q),
		N, Q
	)  # b1*a2 + a1*b2
	d2_raw = poly_mult(a1, a2, N, Q)  # a1*a2

	# ---- CKKS rescale: divide each component by the removed prime ----
	q_last = Q_BASE.pop()
	Q = Q // q_last
	d0 = Polynomial(np.array([round_div(c, q_last) for c in d0_raw.coef], dtype=object)) 
	d1 = Polynomial(np.array([round_div(c, q_last) for c in d1_raw.coef], dtype=object)) 
	d2 = Polynomial(np.array([round_div(c, q_last) for c in d2_raw.coef], dtype=object)) 

	# ---- Relinearize the s^2 term using the gadget-decomp keyswitch ----
	# Under s^2, (a_old=d2, b_old=0) has phase = d2*s^2
	a_old = poly_mod(d2, N, Q)
	b_old = poly_zero(N)
	a_sw, b_sw = fhe_keyswitch(a_old, b_old, relin_key)

	# Combine into 2-term ciphertext under s
	a3 = poly_add(d1, a_sw, N, Q)
	b3 = poly_add(d0, b_sw, N, Q)
	return (a3, b3)



def fhe_bootstrapping(a1, b1, N, Q):
	raise NotImplementedError("CKKS bootstrapping is not implemented in this educational demo")

def ckks_rescaled_scale(scale_left, scale_right, dropped_modulus):
    """Return the actual output scale; nearby primes are not exactly equal to scale."""
    if scale_left <= 0 or scale_right <= 0 or dropped_modulus <= 0:
        raise ValueError("scales and the dropped modulus must be positive")
    return scale_left * scale_right / dropped_modulus
