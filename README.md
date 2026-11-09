# 全同态加密入门教材 · 中文版

本仓库在保留英文源码的基础上，提供对应的 **34 个章节中文译本**和独立中文 PDF 编译入口。

- [逐项学术审校报告](audit/ACADEMIC_REVIEW.md)：原英文基线、问题依据、反例、双语修订与验证边界
- [续审报告](audit/FOLLOWUP_REVIEW.md)：安全归约、扩域槽与公开 BFV 自举、CKKS 定量误差及真实 OpenFHE 复现
- [中文编译与阅读说明](README.zh-CN.md)
- [翻译范围、术语及维护记录](TRANSLATION.md)
- 中文入口：`00-main-zh.tex`；中文正文：`zh-CN/`
- 快速编译：`python3 scripts/build.py zh`（需要 XeLaTeX 和 latexmk）
- 英文入口仍为 `00-main.tex`；同时编译两版：`python3 scripts/build.py all`
- GitHub Actions 的 **Textbook PDFs** 工作流提供两版 PDF 下载。

---

# The Beginner's Textbook for Fully Homomorphic Encryption

#### ArXiv's PDF Link: [https://arxiv.org/abs/2503.05136](https://arxiv.org/abs/2503.05136)

#### Dynamic Website Version: [https://fhetextbook.github.io](https://fhetextbook.github.io)

-  Please post any bugs or errors regarding the draft to the Issues board or create a pull request.

## Python FHE Demo Library Quickstart

We implemented this library for educational purposes. Because it is written in pure Python and does not use an RNS-optimized backend, computations are relatively slow. For this reason, the default parameters are intentionally small—for example, the ring dimension / polynomial modulus degree ($N$) and ciphertext modulus ($Q$) are set to small values (e.g., $N=4$, $Q = 2^{30}$).

In the source code, the global variable `N` denotes the polynomial modulus degree (i.e., computations are performed modulo $x^N + 1$). The variable `Q` denotes the ciphertext modulus (or modulus chain, depending on the scheme configuration) for BFV and TFHE. For CKKS and BGV (when using a modulus chain), `Q_BIT` and `Q_LEVEL` control the per-prime bit-size and the number of levels in the modulus chain.

You may adjust these globals for algebra experiments, but each change requires a new correctness and security analysis. Increasing the ciphertext modulus alone may weaken RLWE security at fixed dimension. Noise bounds, the modulus chain, encoding scale, and NTT-prime conditions must be considered together. The toy dimensions and Python/NumPy random samplers in these demos are not production cryptographic parameters or cryptographic randomness.


### Implemented operations and simulations

The four `*_example.py` runners demonstrate encryption, addition, multiplication and key switching; the ring examples also demonstrate encoding and rotations, and CKKS includes conjugation. The TFHE multiplication runner uses a tensor-product construction with relinearization; it does not benchmark standard TFHE PBS.

| Component | Actual capability |
| --- | --- |
| `tfhe_mock_pbs` and `tfhe_circuit_bootstrap` | Local functional simulation: decrypt, apply a LUT, re-encrypt. The `mock_bk` dictionary contains the **plaintext secret key** and must not be published as an evaluation key. |
| BFV / CKKS / BGV `fhe_bootstrapping` | Unimplemented; raises `NotImplementedError`. |
| `bfv.py`, `bfv_rotation_only.py`, `ckks.py` | Earlier plaintext encoding/rotation experiments, without ciphertext encryption. |
| `rns.py`, `bgv.py`, `bfv_j_matrix_inverse_proof.py` | Standalone algebra experiments; their printouts are not generic correctness proofs. |

Decryption helpers return `(message, diagnostic)`. The diagnostic is `None` when an expected plaintext was not supplied. CKKS multiplication mutates the modulus-factor list; the caller must use the actual output scale `scale_left * scale_right / dropped_prime` (see `ckks_rescaled_scale` and the updated example). The CKKS example checks an absolute error tolerance per real/imaginary component, not a percentage error.

The academic review added deterministic counterexamples and regression checks. After installing the dependencies below, run:

```bash
python3 audit/check_summary.py
python3 audit/check_python.py
```

The complete audit commands and scope are in [the review report](audit/ACADEMIC_REVIEW.md). Tests demonstrate the checked finite cases; they do not certify cryptographic security or unlimited circuit depth.

The [follow-up review](audit/FOLLOWUP_REVIEW.md) adds explicit conditional security reductions, a public BFV bootstrap with a separate secret-key auditor, and a pinned OpenFHE iterative-CKKS experiment. These are separate audit artifacts: the demo library's bootstrapping capabilities remain as listed above. Run all standard-library and Python checks with `python3 audit/run_checks.py`; the optional C++ experiment has its own build instructions in [the OpenFHE report](audit/openfhe-review.md).

### Installation




```
cd 'source code'
pip3 install numpy fastcore sympy
```


### TFHE Library
```
usage: tfhe_example.py [-h] [--encrypt] [--add-cipher-cipher] 
                    [--add-cipher-plain] [--mult-cipher-cipher] [--mult-cipher-plain] \
                    [--keyswitch] [--random] [--all]

options:
  -h, --help            show this help message and exit
  --random              A bulk of random tests
  --encrypt             Encrytion/decryption test
  --add-cipher-cipher   Cipher-cipher addition test
  --add-cipher-plain    Cipher-plain addition test
  --mult-cipher-cipher  Cipher-cipher multiplication test
  --mult-cipher-plain   Cipher-plain multiplication test
  --keyswitch           Key switch test
  --all                 All test
```
| Test Operations | Command |
|---|---|
| Encrypt | `python3 tfhe_example.py --encrypt` |
| Add Cipher-Cipher | `python3 tfhe_example.py --add-cipher-cipher` |
| Add Cipher-Plain | `python3 tfhe_example.py --add-cipher-plain` |
| Multiply Cipher-Plain | `python3 tfhe_example.py --mult-cipher-plain` |
| Multiply Cipher-Cipher | `python3 tfhe_example.py --mult-cipher-cipher` |
| Key Switching | `python3 tfhe_example.py --keyswitch` |
| Random 1000 'Encrypt' Tests | `python3 tfhe_example.py --random --encrypt` |
| Random 1000 Any Tests | `python3 tfhe_example.py --all` |


### BFV Library
```
usage: bfv_example.py [-h] [--encode] [--encrypt] [--add-cipher-cipher] 
                    [--add-cipher-plain] [--mult-cipher-cipher] [--mult-cipher-plain] \
                    [--rotate] [--keyswitch] [--random] [--all]

options:
  -h, --help            show this help message and exit
  --encode              Encoding test
  --random              A bulk of random tests
  --encrypt             Encrytion/decryption test
  --add-cipher-cipher   Cipher-cipher addition test
  --add-cipher-plain    Cipher-plain addition test
  --mult-cipher-cipher  Cipher-cipher multiplication test
  --mult-cipher-plain   Cipher-plain multiplication test
  --rotate              Rotation test
  --keyswitch           Key switch test
  --all                 All test
```
| Test Operations | Command |
|---|---|
| Encode | `python3 bfv_example.py --encode` |
| Encrypt | `python3 bfv_example.py --encrypt` |
| Add Cipher-Cipher | `python3 bfv_example.py --add-cipher-cipher` |
| Add Cipher-Plain | `python3 bfv_example.py --add-cipher-plain` |
| Multiply Cipher-Plain | `python3 bfv_example.py --mult-cipher-plain` |
| Multiply Cipher-Cipher | `python3 bfv_example.py --mult-cipher-cipher` |
| Key Switching | `python3 bfv_example.py --keyswitch` |
| Rotate | `python3 bfv_example.py --rotate` |
| Random 1000 'Encrypt' Tests | `python3 bfv_example.py --random --encrypt` |
| Random 1000 'Rotate' Tests | `python3 bfv_example.py --random --rotate` |
| Random 1000 Any Tests | `python3 bfv_example.py --all` |


### CKKS Library
```
usage: ckks_example.py [-h] [--encode] [--encrypt] [--add-cipher-cipher] 
                    [--add-cipher-plain] [--mult-cipher-cipher] [--mult-cipher-plain] \
                    [--rotate] [--conjugate] [--keyswitch] [--random] [--all]

options:
  -h, --help            show this help message and exit
  --encode              Encoding test
  --random              A bulk of random tests
  --encrypt             Encrytion/decryption test
  --add-cipher-cipher   Cipher-cipher addition test
  --add-cipher-plain    Cipher-plain addition test
  --mult-cipher-cipher  Cipher-cipher multiplication test
  --mult-cipher-plain   Cipher-plain multiplication test
  --rotate              Rotation test
  --conjugate           Conjugation test
  --keyswitch           Key switch test
  --all                 All test
```
| Test Operations | Command |
|---|---|
| Encode | `python3 ckks_example.py --encode` |
| Encrypt | `python3 ckks_example.py --encrypt` |
| Add Cipher-Cipher | `python3 ckks_example.py --add-cipher-cipher` |
| Add Cipher-Plain | `python3 ckks_example.py --add-cipher-plain` |
| Multiply Cipher-Plain | `python3 ckks_example.py --mult-cipher-plain` |
| Multiply Cipher-Cipher | `python3 ckks_example.py --mult-cipher-cipher` |
| Key Switching | `python3 ckks_example.py --keyswitch` |
| Rotate | `python3 ckks_example.py --rotate` |
| Conjugate | `python3 ckks_example.py --conjugate` |
| Random 1000 'Encrypt' Tests | `python3 ckks_example.py --random --encrypt` |
| Random 1000 'Rotate' Tests | `python3 ckks_example.py --random --rotate` |
| Random 1000 Any Tests | `python3 ckks_example.py --all` |



### BGV Library
```
usage: bgv_example.py [-h] [--encode] [--encrypt] [--add-cipher-cipher]
                    [--add-cipher-plain] [--mult-cipher-cipher] [--mult-cipher-plain] \
                    [--rotate] [--keyswitch] [--random] [--all]

options:
  -h, --help            show this help message and exit
  --encode              Encoding test
  --random              A bulk of random tests
  --encrypt             Encrytion/decryption test
  --add-cipher-cipher   Cipher-cipher addition test
  --add-cipher-plain    Cipher-plain addition test
  --mult-cipher-cipher  Cipher-cipher multiplication test
  --mult-cipher-plain   Cipher-plain multiplication test
  --rotate              Rotation test
  --keyswitch           Key switch test
  --all                 All test
```
| Test Operations | Command |
|---|---|
| Encode | `python3 bgv_example.py --encode` |
| Encrypt | `python3 bgv_example.py --encrypt` |
| Add Cipher-Cipher | `python3 bgv_example.py --add-cipher-cipher` |
| Add Cipher-Plain | `python3 bgv_example.py --add-cipher-plain` |
| Multiply Cipher-Plain | `python3 bgv_example.py --mult-cipher-plain` |
| Multiply Cipher-Cipher | `python3 bgv_example.py --mult-cipher-cipher` |
| Key Switching | `python3 bgv_example.py --keyswitch` |
| Rotate | `python3 bgv_example.py --rotate` |
| Random 1000 'Encrypt' Tests | `python3 bgv_example.py --random --encrypt` |
| Random 1000 'Rotate' Tests | `python3 bgv_example.py --random --rotate` |
| Random 1000 Any Tests | `python3 bgv_example.py --all` |

## Community Implementations
- For interested readers, a BFV-RNS implementation in SystemVerilog is available at [https://github.com/alibillalhammoud/FHEforEEs](https://github.com/alibillalhammoud/FHEforEEs).
