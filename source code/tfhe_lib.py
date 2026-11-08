from common import round_div
import random
import numpy as np
import math

GSW_BASE = 1 << 5 # Base 32
GSW_L = 6         # to cover Q=2^30 (32^6 = 2^30

def tfhe_key_generate(K: int):
	return np.array(np.random.randint(0, 2, size=K), dtype=object)

def tfhe_encrypt(m: int, K, P, Q, s, scale):
	"""
	Returns ciphertext (vec{a}, b):
	  a <- uniform in Z_q^k
	  e <- small
	  b = -a*s + e + scale*m	(mod q)
	"""
	bound = 1
	m_scaled = scale * (m % P)
	a = np.array([random.randrange(Q) for _ in range(K)], dtype=object)
	e = random.randint(-bound, bound)
	b = (-np.dot(a, s) + m_scaled + e) % Q
	return (a, b)



def tfhe_decrypt(a, b, P, Q, s, scale, expected_dec = None):
	"""
	Decrypt:
	  v = b + a*s  (mod x^n+1, q)  ~= scale*m + e
	  m_hat = round(v/scale)
	  (optionally centered mod p if p was stored by fhe_encrypt)
	"""
	v = (np.dot(a, s) + b) % Q 
	m_hat = round_div(v, scale) % P # for the case that the result is negative 

	e_bits = None  # No reference plaintext was supplied for a diagnostic.
	if expected_dec is not None:
		e = (v - expected_dec*scale) % Q
		if e > Q // 2:
			e -= Q
		max_abs = abs(e)
		e_bits = 1 if max_abs == 0 else math.floor(math.log2(abs(max_abs))) + 1
	return m_hat, e_bits


def tfhe_encrypt_without_scaling(phase_val: int, K, Q, s):
    """
    Encrypts a specific integer phase directly (no scaling, no mod P).
    Used for Circuit Bootstrapping where target phases are raw integers 
    (m * s_i * base^j).
    
    b = -a*s + phase + e
    """
    bound = 1
    a = np.array([random.randrange(Q) for _ in range(K)], dtype=object)
    e = random.randint(-bound, bound)
    
    # Encrypt the raw phase_val directly
    b = (-np.dot(a, s) + phase_val + e) % Q
    return (a, b)



def tfhe_add_cipher_cipher(a1, b1, a2, b2, Q):
	a3 = (a1 + a2) % Q
	b3 = (b1 + b2) % Q
	return (a3, b3)

def tfhe_add_cipher_plain(a1, b1, m2, Q, scale):
	b3 = (b1 + m2 * scale) % Q
	return (a1, b3) 

def tfhe_mult_cipher_plain(a1, b1, m2, Q):
	a3 = (a1 * m2) % Q
	b3 = (b1 * m2) % Q 
	return (a3, b3)


def tfhe_mult_cipher_cipher(a1, b1, a2, b2, K, P, Q, scale, relin_key):
	 """
	 TFHE (LWE) ct x ct multiplication with relinearization.
	 """
	 # 1. Compute Tensor Product (Raw)
	 b_raw = int(b1) * int(b2)
	 a_lin_raw = (int(b1) * a2 + int(b2) * a1)
	 a_quad_raw = np.outer(a1, a2).flatten()

	 # 2. Rescale
	 b_scaled = round_div(b_raw, scale) % Q
	 a_lin_scaled = np.array([round_div(x, scale) for x in a_lin_raw], dtype=object) % Q
	 a_quad_scaled = np.array([round_div(x, scale) for x in a_quad_raw], dtype=object) % Q
	 
	 # 3. Relinearize Quadratic Term
	 # The term is + <a_quad_scaled, s_old>.
	 # We want to preserve this positive relationship.
	 # Input to keyswitch should be the coefficients themselves.
	 a_in_sw = a_quad_scaled  
	 b_in_sw = 0
	 
	 a_sw, b_sw = tfhe_keyswitch(a_in_sw, b_in_sw, relin_key)
	 
	 # 4. Combine
	 # Final = (b_scaled + b_sw) + < (a_lin + a_sw), s >
	 a_final = (a_lin_scaled + a_sw) % Q
	 b_final = (b_scaled + b_sw) % Q
	 
	 return (a_final, b_final)


def unsigned_digits_len(Q: int, base: int) -> int:
    """Smallest positive L with base**L >= Q for residues in [0,Q)."""
    Q, base = int(Q), int(base)
    if Q < 2 or base < 2:
        raise ValueError("Q and decomposition base must be at least 2")
    L, capacity = 1, base
    while capacity < Q:
        capacity *= base
        L += 1
    return L


def unsigned_gadget_decompose(x, base, L):
	"""
	Decomposes integer x into STANDARD base-B digits (Unsigned).
	x = sum(d_i * base^i) where d_i in [0, base-1]
	"""
	if base < 2 or L < 1 or x < 0:
		raise ValueError("unsigned decomposition requires x >= 0, base >= 2, L >= 1")
	digits = []
	val = int(x)
	
	for _ in range(L):
		# Standard modulo gives range [0, base-1]
		d = val % base
		digits.append(d)
		
		# Standard integer division
		val = (val - d) // base
		
	if val != 0:
		raise ValueError("decomposition length is too short for an exact representation")
	return digits


def tfhe_keyswitch_keygen(s_old: np.array, s_new: np.array, K: int, Q: int, base: int = 1 << 10, bound: int = 1):
	"""
	Generates LWE Key Switching Key (KSK) from s_old (k-dim) to s_new (K-dim).
	
	Structure:
	  KSK is a list of size len(s_old).
	  Each element KSK[i] is a list of size L (levels).
	  KSK[i][j] is an LWE encryption of (s_old[i] * base^j) under s_new.
	"""
	k_old = len(s_old)
	L = unsigned_digits_len(Q, base) # from common.py
	
	ksk = []
	
	for i in range(k_old):
		ksk_i = []
		base_pow = 1
		
		for j in range(L):
			# Message to encrypt: s_old[i] * base^j
			# This is a scalar value added to the phase.
			msg = (int(s_old[i]) * base_pow) % Q
			
			# Encrypt msg under s_new
			# LWE sample: b = -<A, s_new> + e + msg (plus-phase convention)
			A = np.array([random.randrange(Q) for _ in range(K)], dtype=object)
			e = random.randint(-bound, bound)
			b = (-np.dot(A, s_new) + e + msg) % Q

			ksk_i.append((A, b))
			base_pow *= base
			
		ksk.append(ksk_i)
		
	return {"base": base, "L": L, "K": K, "Q": Q, "ksk": ksk}



def tfhe_keyswitch(a: np.array, b: int, ksk_bundle):
	"""
	Switches LWE ciphertext (a, b) from s_old to s_new.
	
	Decryption logic:
	  Phase = b + <a, s_old>
			= b + sum(a_i * s_old[i])
			= b + sum( sum(d_{i,j} * base^j) * s_old[i] )
			= b + sum( sum(d_{i,j} * (base^j * s_old[i])) )
			
	  We replace (base^j * s_old[i]) with its encryption KSK[i][j].
	"""
	base = int(ksk_bundle["base"])
	L	= int(ksk_bundle["L"])
	K	= int(ksk_bundle["K"]) # Dimension of s_new
	Q	= int(ksk_bundle["Q"])
	ksk  = ksk_bundle["ksk"]	# dim: n_old x L
	
	k_old = len(a)
	
	# Initialize result (a', b')
	# Starting with (0, b)
	a_new = np.zeros(K, dtype=object)
	b_new = b
	
	# Iterate over elements of old 'a' vector
	for i in range(k_old):
		# Decompose coefficient a[i]
		digits = unsigned_gadget_decompose(int(a[i]) % Q, base, L)
		
		for j in range(L):
			d = digits[j]
			if d == 0:
				continue
				
			# Retrieve key switching key parts
			A_ksk, b_ksk = ksk[i][j]
			
			# Add d * KSK to the (0,b) accumulator for the plus-phase convention.
			
			term_a = (d * A_ksk) % Q
			term_b = (d * b_ksk) % Q
			
			a_new = (a_new + term_a) % Q
			b_new = (b_new + term_b) % Q
			
	return (a_new, b_new)


def tfhe_circuit_bootstrap(ct_lwe, bk, K, P, Q, scale):
    """LOCAL SIMULATION of LWE-to-GSW conversion; requires a plaintext secret.

    This is not TFHE's circuit-bootstrapping algorithm. Each row is obtained
    by secret-key decryption and re-encryption through tfhe_mock_pbs.
    The plus-phase convention requires row phases m*s_i*base^j, followed
    by the body row m*base^j. Never distribute this mock key to an evaluator.
    """
    if bk.get('type') != 'mock_bk':
        raise ValueError("this function only accepts a local mock_bk")
    base = GSW_BASE
    L = unsigned_digits_len(Q, base)
    gsw_ct = []
    for i in range(K + 1):
        secret_factor = int(bk['s'][i]) if i < K else 1
        block = []
        for j in range(L):
            multiplier = secret_factor * base**j
            block.append(tfhe_mock_pbs(
                ct_lwe, lambda x, multiplier=multiplier: x * multiplier,
                K, P, Q, scale, bk['s']))
        gsw_ct.append(block)
    return gsw_ct


def tfhe_mock_pbs(ct_in, lut_func, K, P, Q, scale, s):
    """
    INSECURE CLIENT-SIDE SIMULATION: decrypt, apply a LUT, and re-encrypt.
    In a real library, this uses Blind Rotate + Sample Extract.
    Here, we decrypt, apply LUT, and re-encrypt to allow the
    higher-level 'Cipher-Cipher' logic to be tested.
    """
    # 1. Decrypt to get the underlying message m
    a, b = ct_in
    phase = (b + np.dot(a, s)) % Q
    m_noisy = round_div(phase, scale) % P
    
    # 2. Apply LUT to get the new TARGET PHASE
    # Note: We do NOT mod P here. The result is a raw phase in Z_Q.
    target_phase = lut_func(m_noisy) % Q
    
    # 3. Re-encrypt the raw phase directly (Bypassing tfhe_encrypt scaling)
    return tfhe_encrypt_without_scaling(target_phase, K, Q, s)


# ==========================================
#        Main Multiplication Wrapper
# ==========================================

def tfhe_mult_cipher_cipher_circuit_bootstrapping(a1, b1, a2, b2, K, P, Q, scale, bk):
    """
    INSECURE CLIENT-SIDE SIMULATION of multiplication via circuit bootstrapping.
    ct1: LWE(m1)
    ct2: LWE(m2)
    Returns: LWE(m1 * m2)
    
    Method:
    1. Convert ct2 -> GSW(m2) using Circuit Bootstrap.
    2. Compute ct1 * GSW(m2) using External Product.
    """

    L = unsigned_digits_len(Q, GSW_BASE)

    ct1 = (a1, b1)
    ct2 = (a2, b2)

    # 1. Simulated circuit bootstrap (requires the plaintext secret).
    # Note: We pass 'bk' which contains the secret key 's' for our mock PBS.
    gsw_m2 = tfhe_circuit_bootstrap(ct2, bk, K, P, Q, scale)
    
    # 2. External Product: LWE(m1) * GSW(m2) -> LWE(m1 * m2)
    # Formula: sum( <Decomp(ct1_i), GSW_row_i> )
    res_ct = tfhe_external_product(ct1, gsw_m2, K, Q, base=GSW_BASE, L=L)
    
    return res_ct



def tfhe_external_product(ct_lwe, ct_gsw, K, Q, base=GSW_BASE, L=None):
    """
    Computes LWE * GSW -> LWE.
    Formula: sum( < Decomp(ct_i), GSW_i > )
    """
    if L is None:
        L = unsigned_digits_len(Q, base)
    a, b = ct_lwe
    # Combine a and b into a single vector for iteration: (a_0, ... a_{k-1}, b)
    # This matches the user notation: ct = (ct_0, ... ct_k)
    full_ct = np.concatenate([a, [b]])
    
    # Initialize result accumulator (0, 0)
    res_a = np.zeros(K, dtype=object)
    res_b = 0
    
    # Iterate through each component of the LWE ciphertext
    # ct_gsw is a list of 'Lev' blocks. ct_gsw[i] corresponds to full_ct[i].
    for i in range(len(full_ct)):
        # Decompose the scalar component full_ct[i]
        digits = unsigned_gadget_decompose(int(full_ct[i]) % Q, base, L)
        
        # Access the i-th block of the GSW ciphertext
        # This block is a list of L ciphertexts (Lev_0, ... Lev_{L-1})
        lev_block = ct_gsw[i]
        
        for j in range(L):
            d = digits[j]
            if d == 0: continue
            
            # The j-th element of the Lev block is an LWE ciphertext
            lev_a, lev_b = lev_block[j]
            
            # Add d * Lev_j to result
            term_a = (d * lev_a) % Q
            term_b = (d * lev_b) % Q
            
            res_a = (res_a + term_a) % Q
            res_b = (res_b + term_b) % Q
            
    return (res_a, res_b)



def tfhe_bootstrap_keygen(s: np.array):
    """
    Packages a secret for a LOCAL SIMULATION, not a publishable bootstrapping key.
    
    In a FULL TFHE implementation, this would generate RGSW encryptions 
    of the secret key bits (for Blind Rotation).
    
    In this FUNCTIONAL PROTOTYPE (Mock PBS), this packages the secret key 's'
    to allow the tfhe_mock_pbs function to simulate the bootstrapping noise 
    refresh and LUT application.
    """
    bk = {
        's': s,
        'type': 'mock_bk',
        'info': 'Contains secret key for functional PBS simulation'
    }
    return bk



