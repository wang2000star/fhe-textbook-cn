# CKKS、BGV 与 RNS 章节学术审校

审校日期：2026-11-08。范围：英文 `d03-ckks.tex`、`d04-bgv.tex`、`d05-rns.tex` 的全部活动正文、公式、表格和算法，以及对应的 `zh-CN/` 译文。这里把英文原书作为待审对象，没有把译文与英文一致视为数学正确性的证据。

## 结论与修改范围

本次逐段阅读并审查了 **98 个标题单元**：CKKS 51 个、BGV 21 个、RNS 26 个；另外审查了 3 个章首导言，共 101 个阅读单元。完整覆盖记录见 `audit/ckks-bgv-rns-coverage.json`。标题提取用于核对覆盖是否完整，每条判断和关联发现均来自实际阅读及数学核查，不是自动生成的“已审阅”标记。

确认的主要问题包括：CKKS 把近似尺度写成精确尺度、把分量舍入与相位舍入混为一谈、用随机加密/解密恒等式解释自举、漏掉 EvalExp 最后一个尺度常数、把多项式求值成本说成随次数指数增长；BGV 忽略中心化相位界、把固定噪声整除因子解释成不断平方、用普通向下取整删除有符号溢出项、没有在精确除法后降低明文模数；RNS 混淆近似与精确基转换、丢弃辅助剩余类后继续使用、错误复用 BFV 解密器计算不可逆的模数切换，以及给出没有完整正确性条件的自举替代流程。

所有确认且可明确修复的问题均已同步修改英文与中文。对于错误贯穿整个推导的小节，保留原标题和标签，改为较短但有明确输入、输出和条件的推导；没有保留已知不成立的中间等式。原来正确的核心结构也已明确保留：典范嵌入、张量乘积、环自同构、CRT 重构、满足范围界的冗余模数纠正等。

**本报告不是密码安全证明，也不是对所有实现参数的认证。** 对缺少具体参数的自举，本次只能修正算法和必要/充分条件，不能代替输入范围、失败概率、精度和剩余层级的完整实例化分析。尚未充分核验的细节单列在文末，没有用新公式掩盖缺口。

## 一手资料及实际核查范围

|编号|一手资料与可读全文|本次实际核查内容|
|---|---|---|
|P1|Cheon–Kim–Kim–Song, *Homomorphic Encryption for Arithmetic of Approximate Numbers*, ASIACRYPT 2017，ePrint 2016/421；[作者全文](https://yongsoosong.github.io/files/papers/HEAAN.pdf)|全文可读。核查 §3.2 编码、§3.3–3.4 运算/误差及引理 1–3、附录相关证明；没有逐项重做安全归约和实验。|
|P2|Cheon 等，*Bootstrapping for Approximate Homomorphic Encryption*, ePrint 2018/153；[作者全文](https://yongsoosong.github.io/files/papers/HEAAN_boot.pdf)|全文可读。核查复指数近似、自举线性变换，以及 §5.1、§5.2 的稀疏打包与 PartialSum。|
|P3|Cheon 等，*A Full RNS Variant of Approximate Homomorphic Encryption*, ePrint 2018/931；[作者全文](https://yongsoosong.github.io/files/papers/RNS.pdf)|全文可读。核查 §3.2 ModUp/ModDown 的输入、输出、误差与算法 1、2，以及相应附录正确性关系。|
|P4|Brakerski–Gentry–Vaikuntanathan, *(Leveled) Fully Homomorphic Encryption without Bootstrapping*, ePrint 2011/277；[作者课程全文](https://people.csail.mit.edu/vinodv/6892-Fall2013/BGV.pdf)|全文可读。核查 §3.3 Definition 9、Lemma 5：同余保持的缩放以及带余量的中心化相位界。|
|P5|Geelen–Vercauteren, *Bootstrapping for BGV and BFV Revisited*, ePrint 2022/1363；[作者机构接受稿](https://imec-publications.be/bitstreams/5e8ee1f6-f7f1-4a12-983b-52a6677361fb/download)|全文可读。核查 §2.2–2.3、§3.2–3.4，特别是式 (8)–(12)，以及 §6 的平衡数位、舍入定义、脚注 10 和 Halevi/Shoup 算法。|
|P6|Bajard–Eynard–Hasan–Zucca, *A Full RNS Variant of FV-like Somewhat Homomorphic Encryption Schemes*, SAC 2016，ePrint 2016/510；[作者全文](https://webusers.imj-prg.fr/~jean-claude.bajard/MesPublis/SAC2016.pdf)|全文可读。核查 §3 的冗余模数解密、Theorem 1/Algorithm 1，§4.2 Small Montgomery、Algorithm 2/Lemma 4，§4.3 approximate flooring、Lemma 5，§4.4 精确基转换、Lemma 6，以及 §4.5 的 RNS gadget。|
|P7|Halevi–Polyakov–Shoup, *An Improved RNS Variant of the BFV Homomorphic Encryption Scheme*, ePrint 2018/117；[作者全文](https://www.shoup.net/papers/rns-bfv.pdf)|网页工具可读取完整 PDF。核查 §2.2–2.4 的基转换及简单/复杂缩放、§4.5 的乘法；注意浮点商近似与舍入边界，不把 HPS 与 BEHZ 当成同一个算法。|

补充核验已取得 arcsin 改进的完整作者稿（[ePrint 2020/552](https://eprint.iacr.org/2020/552)；[SNU 作者实验室目录第140项](https://ccl.snu.ac.kr/publication/intl-journal) → [作者提供的全文](https://drive.google.com/file/d/1Leyad-pmhT69ugUpdA3K04aetgoocIV5/view)）。已读 §4、§5.1–5.2，核对定义域、式(4)、Table 7 的近似次数和误差预算，未重跑其 SEAL 数值实验。Meta-BTS（[ePrint 2022/1167](https://eprint.iacr.org/2022/1167.pdf)）仍未取得完整 PDF；已定向核对 §1.1、定义 2.1/2.2、§3.2.1 Algorithm 1 与相邻说明、Theorem 3.1/3.2、§4.1 Corollary 4.2 的原论文正文缓存，并取得完整的[作者 CCS 2022 讲稿](https://wony0404.github.io/files/META-BTS_Wonhee_Cho_CCS.pptx)。独立条件定理已证明，但不声称逐段核对了原论文全稿；来源 SHA、访问边界和完整推导见 [CKKS 补核](ckks-followup.md)。BASALISC、HElib 资料的原引用保留，但本次对应数学结论主要由 P3–P6 全文及独立推导支持。

## 发现清单：CKKS

### CBR-001　原生明文语义、环的概念及整数编码

- **位置**：`d03-ckks.tex` 导言；`subsec:ckks-encoding-decoding`。
- **原陈述**：CKKS 针对实数、其他方案只能处理整数；复数编码“不在环上”；CKKS 多项式系数为实数，而其他方案为整数。
- **判断**：概念混淆。CKKS 原生支持复数近似算术，实数是特例；精确有限明文方案仍可通过编码/电路实现定点或浮点计算。复数是域，当然也是环。逆典范嵌入先得到实系数多项式，随后缩放舍入成整数多项式，实际 RLWE 密文位于整数商环。
- **修正**：区分实代数、整数环和密文环，明确近似误差的来源及原生语义；删除“复数不是环”等表述。没有把是否适用某任务表述为方案的绝对能力边界。
- **依据**：[P1，§3.2–3.3](https://yongsoosong.github.io/files/papers/HEAAN.pdf)。**状态：已修正。**

### CBR-002　典范嵌入、矩阵朝向与槽位数

- **位置**：`subsec:ckks-encoding-decoding`、`subsec:ckks-rotation`、`subsec:ckks-encoding-contemplate`、`subsubsec:ckks-bootstrapping-coefftoslot-details`。
- **原陈述**：旋转说明把编码矩阵写成 $n^{-1}I_n^R\widehat W$，并把复数/有限域上的矩阵视为同一个数值矩阵；部分自举推导混用矩阵乘多项式系数和同态槽位变换。
- **判断与推导**：按本书定义，主编码式 $n^{-1}\widehat W I_n^R$ 本身正确，不能把两因子随意换位。选取 $\zeta_j=\omega^{5^j}$，令 $U_{jk}=\zeta_j^k$。对实系数向量 $t$，有 $z=Ut$，并且
  $$t=\frac1n(\overline U^{,T}z+U^T\overline z).$$
  这来自全部 $n$ 个根的正交性，而不是把 $n/2$ 个复数槽位误当成 $n$ 个独立复数槽位。矩阵常数在有限明文环与复数域中分别解释。
- **修正**：保持正确的主编码式；修正反序矩阵顺序、矩阵符号、CoeffToSlot 的维数和共轭项；用 $U=(U_0\ U_1)$ 明确两半系数的变换。
- **验证**：脚本在 $n=4,8,16$ 验证往返编码、实系数性与旋转。依据：[P1 §3.2](https://yongsoosong.github.io/files/papers/HEAAN.pdf)、[P2](https://yongsoosong.github.io/files/papers/HEAAN_boot.pdf)。**状态：已修正。**

### CBR-003　四维编码例子的具体计算错误

- **位置**：`subsubsec:ckks-encoding-ex`。
- **原陈述**：$0.825\sqrt2\approx1.1657$；展开式一处漏掉共轭根；$\cos(3\pi/4)$ 的展开符号错误；解码根行与实际给出的数值结果不一致。
- **判断**：直接数值错误及抄写错误。正确值为 $0.825\sqrt2=1.1667261889578033\ldots$。正确编码整数仍是 $(2355,1195,1485,2933)$，因此原例子的最终整数其实与它前面的错误小数不一致。
- **修正**：改为 1.1667，补齐根/符号，使用根序 $1,5,-1,-5\pmod8$ 的解码矩阵，并说明应从精确根式计算整数编码，而不是累积显示小数的截断误差。
- **验证**：`canonical_embedding_and_example` 重算全部整数、解码误差和根序。依据：[P1 §3.2 的定义](https://yongsoosong.github.io/files/papers/HEAAN.pdf)及独立复数计算。**状态：已修正。**

### CBR-004　CKKS 解密不会舍掉一般噪声；系数界不等于槽位精度

- **位置**：`subsec:ckks-enc-dec`；段落 `CKKS's Approximation Property`。
- **原陈述**：将相位除以尺度后，舍入到 $1/\Delta$ 的倍数可消除噪声；只要 $e_i<\Delta/2$ 即有固定精度。
- **判断与推导**：原始相位是 $P+E_0=\Delta M+E$，输出槽位误差为 $E(\zeta_j)/\Delta$，而非消失。系数界只给出
  $$|\widehat v_j-v_j|\le\|E\|_{\mathrm{can},\infty}/\Delta\le n\|E\|_\infty/\Delta.$$
  若最近整数编码误差每系数至多 $1/2$，保守槽位编码误差是 $n/(2\Delta)$。更紧的随机/典范范数分析可以采用，但不能省掉范数转换。
- **修正**：区分原始相位、缩放和槽位解码；引入完整中心化界 $\|\Delta M+E\|_\infty<q/2$；删除把 CKKS 噪声当作可精确舍掉的说法。
- **依据**：[P1 §3.2–3.4](https://yongsoosong.github.io/files/papers/HEAAN.pdf)。**状态：已修正。**

### CBR-005　乘法相位必须保留全部交叉误差

- **位置**：`subsubsec:ckks-mult-cipher-relation`、`subsubsec:ckks-mult-cipher-summary`。
- **原陈述**：在合成密文推导中使用“解密再加密”的等价写法，并忽略一般 CKKS 不能消除的误差项。
- **判断**：张量乘积的基本三项正确，但精确关系必须是
  $$D_0+D_1S+D_2S^2\equiv\Delta^2M_1M_2+Delta M_1E_2+Delta M_2E_1+E_1E_2\pmod q.$$
  重线性化还增加求值密钥误差，且不负责把尺度从 $\Delta^2$ 恢复为 $\Delta$。
- **修正**：直接给出相位恒等式，以 $(D_1,D_0)$ 对应本书 $(A,B)$ 顺序；保留重线性化前后误差，消除随机密文分布相等的暗示。
- **依据**：[P1 乘法与重线性化](https://yongsoosong.github.io/files/papers/HEAAN.pdf)。**状态：已修正。**

### CBR-006　同一组 gadget 数位不能同时使用两套权重

- **位置**：`subsubsec:relinearization-gadget-decomposition`、`subsec:ckks-key-switching`。
- **原陈述**：沿用前文下降权重 $q/\beta^i$ 的分解，却配用 $\beta^{i-1}$ 的求值密钥；对一般 CKKS/RNS 模数也没有给出整数与精确重构条件。
- **判断**：权重和数位不匹配即不再重构原多项式。对于任意模数，$q/\beta^i$ 还可能不是整数，例如 $q=97,\beta=8$。不能因为“都是 gadget”就交换它们。
- **修正**：本节显式选择 $g_i=\beta^{i-1}$、$l=\lceil\log_\beta q\rceil$，使用无符号代表元的精确基数分解；明确与前文下降权重约定不同。关键是同步生成 $g_iS$ 或 $g_iS^2$ 的求值密钥。
- **验证**：脚本穷举 $q=97$ 的全部输入。依据：[P1](https://yongsoosong.github.io/files/papers/HEAAN.pdf)、[P6 §4.1、§4.5](https://webusers.imj-prg.fr/~jean-claude.bajard/MesPublis/SAC2016.pdf)及整数重构恒等式。**状态：已修正。**

### CBR-007　扩展模数重线性化的舍入推导不成立

- **位置**：`subsubsec:relinearization-modulus-switch`。
- **原陈述**：将分量舍入分配到加法、乘秘密多项式内部，并把扩大参数 $g$ 说成会消除全部误差；求值密钥采样域也与扩展模数混杂。
- **判断与反例**：$\operatorname{rnd}(2/5)+\operatorname{rnd}(2/5)=0$，而 $\operatorname{rnd}(4/5)=1$。乘以秘密也不与舍入交换。正确输出相位为
  $$D_2S^2+D_2E'/g+R_B+R_AS\pmod q,$$
  其中每个 $R_A,R_B$ 系数至多 $1/2$。相应系数误差界包含 $(1+\|S\|_1)/2$，它不会因为增大 $g$ 自动消失。
- **修正**：均匀采样 $A'\in R_{gq}$，明确 $g$ 的参数地位、固定的 $D_2$ 整数提升和模 $gq$ 约减，保留完整舍入误差及扩展模数安全参数的影响。
- **依据**：[P1 的 key switching/multiplication 误差分析](https://yongsoosong.github.io/files/papers/HEAAN.pdf)、[P3 附录正确性](https://yongsoosong.github.io/files/papers/RNS.pdf)。**状态：已修正。**

### CBR-008　实际重缩放尺度、舍入误差与 RNS 安全参数

- **位置**：`subsubsec:ckks-mult-cipher-rescale`、其 Initial Scaling Factor/Noise Growth 段落、`subsec:ckks-mult-plain`。
- **原陈述**：用 $w_l\approx\Delta$ 替换成精确除以 $\Delta$，输出仍标作精确尺度 $\Delta$；尺度自身也被舍入；RNS 好像缩小了密码参数。
- **判断**：重缩放除数是实际 $w_l=q_l/q_{l-1}$。输入尺度 $\Delta_1,\Delta_2$ 相乘后再重缩放，输出尺度是
  $$\Delta_{out}=\Delta_1\Delta_2/w_l.$$
  $\Delta=16,w_l=17$ 时结果为 $256/17\ne16$。相位误差为旧误差除以 $w_l$ 再加 $R_B+R_AS$；若人为把尺度改标为 16，会引入依赖消息大小的误差。
- **修正**：显式跟踪实际尺度与误差；明文乘法可使用尺度 1 的精确整数常量，不是每次都必须消耗一层。RNS 只改变表示，不能用每个小素数的比特数替代总模数和秘密分布的安全分析。
- **依据**：[P1 rescaling 引理](https://yongsoosong.github.io/files/papers/HEAAN.pdf)、[P3](https://yongsoosong.github.io/files/papers/RNS.pdf)。**状态：已修正。**

### CBR-009　乘法层级与噪声的无条件论断

- **位置**：`subsubsec:bfv-bootstrapping-ckks-comparison`；以及“乘法层级”“噪声增长”“交换顺序”段落。
- **原陈述**：固定模数 BFV 可以无限次乘法；CKKS 每次乘法必然消耗一层且噪声必然增大；重线性化和重缩放可无条件交换。
- **判断**：固定模数仍受噪声预算限制；层级是缩放安排的资源，不是所有乘法操作本身的普遍计数。零乘数、不同尺度常量等足以否定所有输入上“噪声必增”的说法。若先缩放三分量密文，舍入误差要按秘密向量 $(1,S,S^2)$ 分析，而且后续求值密钥必须适用于新模数。
- **修正**：改为带模数、尺度、消息和噪声条件的描述；明确交换次序会改变误差和成本。
- **依据**：[P1](https://yongsoosong.github.io/files/papers/HEAAN.pdf)、[P4](https://people.csail.mit.edu/vinodv/6892-Fall2013/BGV.pdf)。**状态：已修正。**

### CBR-010　ModDrop 的相位条件及用途

- **位置**：`subsec:ckks-moddrop`、`subsubsec:ckks-moddrop-vs-modswitch`。
- **原陈述**：裸约减后默认保持消息和噪声，推导漏掉分量模约减经 $S$ 传播的项；用途被局限在计算末尾。
- **判断**：若 $q'\mid q$，新的相位确与原相位模 $q'$ 同余，但要把它解释为同一整数相位，必须有 $\|\Delta M+E\|_\infty<q'/2$。超过范围时，回绕可以改变解码值。它还可用于对齐层级。
- **修正**：用模同余证明取代错误的整数等式，补足完整相位界和尺度不变条件，说明层级对齐用途。
- **依据**：[P1](https://yongsoosong.github.io/files/papers/HEAAN.pdf)、[P3 ModUp/ModDown 的表示区分](https://yongsoosong.github.io/files/papers/RNS.pdf)。**状态：已修正。**

### CBR-011　旋转方向、共轭根序和旋转后的秘密密钥

- **位置**：`subsec:ckks-rotation`、`subsubsec:ckks-rotation-ex`、`subsec:ckks-conjugation`。
- **原陈述**：第一半左移、共轭半右移；BFV 用户只能选 $n/2$ 个槽位；共轭时改用与编码不一致的奇数根序；例子在只做自同构后暗示可直接使用原密钥解密。
- **判断**：采用 $J(j)=5^j,J_*(j)=-5^j$，乘 $5^h$ 后两半都映到下标 $j+h$，方向一致。共轭是 $X\mapsto X^{-1}$，槽位变成各自的复共轭，不需要更换根序。自同构后的秘密为 $S(X^{5^h})$，须切回原密钥。
- **修正**：统一两半左移与 $n/2$ 独立复槽；完全分裂 BFV 有 $n$ 个可独立选槽位；修正例子的初始向量标记、环记号和密钥切换缺步。
- **验证**：小参数编码/自同构往返。依据：[P1 的 slot permutation](https://yongsoosong.github.io/files/papers/HEAAN.pdf)、[P2](https://yongsoosong.github.io/files/papers/HEAAN_boot.pdf)。**状态：已修正。**

### CBR-012　稀疏打包逆命题的证明缺口

- **位置**：`subsec:ckks-sparse-packing`、无独立 label 的 Forward Proof 小节。
- **原陈述**：由整体编码是同构，直接把一个方向的子空间结论反推为另一个方向。
- **判断**：整体同构本身不保证两个指定子空间互为像。原文的正向根指数计算可成立；还需证明重复槽空间与 $\mathbb R[Y]/(Y^{n'}+1)$ 的实维数都为 $n'$，并利用单射得出满射到该子空间。
- **修正**：补充 $n'\ge2$、$n'\mid n$ 和维数论证；保留正向证明。该结论是消息编码的性质，不能自动应用于自举提升后的全部噪声相位。
- **依据**：[P2 §5.1–5.2](https://yongsoosong.github.io/files/papers/HEAAN_boot.pdf)及线性代数。**状态：已补全。**

### CBR-013　CKKS 自举不能用 Enc/Dec 恒等消去说明

- **位置**：`subsec:ckks-bootstrapping`、`subsubsec:ckks-bootstrapping-high-level`、`subsubsec:ckks-bootstrapping-high-level-correctness` 及五个 para。
- **原陈述**：模数提升后先解密再重新编码/加密，通过 $Enc\circ Dec$ 或 $Dec\circ Enc$ 消掉操作来得到无需密钥的算法；还把非线性 EvalExp 混在线性变换中。
- **判断**：随机带噪加密不满足密文级 $Enc(Dec(ct))=ct$，CKKS 一般也不精确恢复原数。实际基础自举直接操作提升后的密文，秘密只出现在正确性分析及求值密钥中。线性实槽变换与非线性模约减电路必须分开。
- **修正**：保留 $T=\Delta M+E+q_0K$ 的相位解释，以公开旋转/共轭/重线性化密钥支持实际电路；明确两密文系数分半、非线性多项式求值、输出误差和剩余模数。删除把一个“编码的函数多项式”与密文相乘当作函数求值的表述。
- **依据**：[P2 的完整自举构造](https://yongsoosong.github.io/files/papers/HEAAN_boot.pdf)。**状态：已重写错误推导。**

### CBR-014　EvalExp 的复杂度、输入归一化与漏乘常数

- **位置**：`subsubsec:ckks-bootstrapping-evalexp-details`。
- **原陈述**：一般多项式求值成本随次数指数增长；$q_0$ 变大直接迫使次数变大；把 $\theta$ 与 $\theta/2^r$ 的界混淆；最后仅乘 $-i/2$ 却声称得到 $q_0\sin(2\pi x/q_0)/(2\pi)$。
- **判断与反例**：Horner 求 $d$ 次多项式只需 $d$ 次乘法，平行幂构造能以多项式工作量获得对数深度。决定近似的是归一化区间 $\theta=2\pi x/q_0$，不是 $q_0$ 单独的绝对大小。重复平方需要传播初始近似误差。最后一步确实漏乘 $q_0/(2\pi)$；例如 $q_0=100,x=1$，未缩放正弦为 0.06279，目标近似余数为 0.99934。
- **修正**：纠正成本与角度界；要求 $k_{max}$ 约束完整 $|x|/q_0$；最后乘编码常数 $-iq_0/(4\pi)$，并把指数/共轭操作写成近似而非精确等式。
- **依据**：[P2 的复指数方法](https://yongsoosong.github.io/files/papers/HEAAN_boot.pdf)、[P5 §6 关于次数/深度](https://imec-publications.be/bitstreams/5e8ee1f6-f7f1-4a12-983b-52a6677361fb/download)及脚本反例。**状态：已修正。**

### CBR-015　稀疏自举漏掉 PartialSum；系数计数和复制轮数错误

- **位置**：`subsubsec:ckks-bootstrapping-time-reduction`。
- **原陈述**：消息稀疏便可在 ModRaise 后忽略其他系数；非零系数数量写成 $n/n'$；复制槽位的次数/移位量不一致，并断言固定减半的收益。
- **判断**：即使 $M$ 只含 $X^{dj}$ 的适当子环项，$E+q_0K$ 通常不稀疏。P2 §5.2 在提升后加入 PartialSum：令 $d=n/n'$，逐次相加旋转量 $(n'/2)2^j$，共 $\log_2d$ 轮。它是子群迹，消去次数不被 $d$ 整除的项，并将保留项乘以 $d$。
- **修正**：补入该步骤及尺度/周期归一化；正确非零系数数目为 $n'$；对初始零填充块，采用负向倍增复制的移位和轮数；把实际开销收益留给具体变换分析。
- **验证**：脚本在 $n=8,16,32$、$n'=2,4$ 上验证全部系数位置的迹恒等式。依据：[P2 §5.2](https://yongsoosong.github.io/files/papers/HEAAN_boot.pdf)。**状态：已修正。**

### CBR-016　Meta-BTS 纠错符号和尺度对齐错误

- **位置**：`subsubsec:ckks-bootstrapping-noise-reduction` 的 Meta-BTS para。
- **原陈述**：令误差密文为原密文减自举结果，之后又从自举结果减去该误差；用一次 rescale 代替层级对齐；未经归一化便声称误差总会指数减小，并给出无条件“最好”评价。
- **判断**：若 $c_1$ 表示 $m+\eta$，错误方向的差为 $-\eta$，再相减得到 $m+2\eta$。正确的示意纠错是提取 $c_1-c$，适当归一化并自举该小误差，再从 $c_1$ 相减。ModDrop 与 rescale 的尺度效果不同。
- **修正**：撤销没有比较范围的最优性断言，并把示意流程补为条件定理。取实际因子 $a_j$、$P_1=1$、$P_{j+1}=a_jP_j$，基础尺度 $\Delta$、误差界 $\varepsilon$、重缩放归一化界 $\rho$。输入/输出尺度为 $P_k\Delta$，所有派生输入满足基础自举的内部允许条件，且 $a_j(\rho+\varepsilon)\le B$、$\|z_0\|_\infty+\rho\sum_{j<k}P_j^{-1}\le B$ 时，可在适当模数容量下得到新增误差界 $\varepsilon/P_k$。第一次重缩放与前次自举误差逐路径抵消，不假设独立性。
- **新增反例**：$a=256,\varepsilon=1/256,\rho=1/65536$ 时，放大残差界为 $257/256>1$，故“8 位基础精度”本身不保证下一调用有效。实际 RNS 因子 65537 错用名义 65536 时，一个合法参数例的残差由约 $-0.75$ 变成 $-1.25$；真实因子必须进入尺度和输入预算。
- **依据与状态**：独立证明和精确分数检查见 [CKKS 补核 §§3–6](ckks-followup.md)。[原论文](https://eprint.iacr.org/2022/1167.pdf)正文缓存及[完整作者讲稿](https://wony0404.github.io/files/META-BTS_Wonhee_Cho_CCS.pptx)支持方法结构。**教材所写条件定理已经证明；原论文完整定量主张与证明的逐段核验仍保留部分核验**，不把完整 PDF 尚不可得的问题与条件性代数推导混为一项。

### CBR-017　arcsin 的主值区间与固定“三层”论断

- **位置**：同上，arcsin para 和 Limitation in Noise Handling para。
- **原陈述**：$\arcsin(\sin x)$ 可直接作为直线消除全部类型三误差，代价固定为三层；反复纠错带来无条件指数收敛。
- **判断**：精确复合只在主区间 $[-\pi/2,\pi/2]$ 上等于 $x$；例如 $x=\pi$ 时返回 0。周期延拓在不同区间交替斜率。实际电路还要近似各函数，深度取决于近似次数、分解和尺度安排，不能从函数恒等式得出固定三层的普遍结论。
- **修正**：补充定义域和局部余数解释，撤销无条件深度/指数改善保证。进一步给出完整联合误差预算：在复邻域中取内层导数界 $L_s$，令 $E_s=L_sE_C+\epsilon_s+H_s$；外层使用实区间近似界 $\epsilon_a$ 与复圆盘导数界 $L_a$，得到 $E_R\le(\epsilon_a+L_aE_s+H_a)/(2\pi)$。最终尺度恢复与线性变换必须计入 $\|L\|_\infty E_R+E_L$。因此没有把实数 Remez 近似界直接扩展到复噪声。
- **一手全文核验**：作者提供的 EUROCRYPT 2021 版本 pp.643–644 §5.1 式(4) 要求 $0<\epsilon<1/4$，在 $\bigcup_k[k-\epsilon,k+\epsilon]$ 上使用 $\operatorname{normod}(t)=\arcsin(\sin(2\pi t))/(2\pi)$。p.645 Table 7 的反正弦多项式次数随参数为 15、9、7、5、5，正文仅称额外深度消耗。§4 与 §5.2 的误差平台讨论针对固定参数和实现，不能泛化成所有方法的不可突破下界。
- **依据与状态**：主值定义、独立反例及[作者全文](https://drive.google.com/file/d/1Leyad-pmhT69ugUpdA3K04aetgoocIV5/view)相互核对；联合误差模型的证明、Taylor 尾界、复扰动正反例和失败概率边界见 [CKKS 补核 §§7–8](ckks-followup.md)。明确上界不等于普遍正误差下限，旧误差不会被该纠错恢复。**已修正并完成教材所写条件、成本和联合误差论断核查**，对应原部分核验单元 `d03-ckks-051` 改为 corrected。未重新实现论文的 SEAL 数值实验，也未认证具体生产参数。

## 发现清单：BGV

### CBR-018　BGV 打包的素数条件与整数代表元

- **位置**：`d04-bgv.tex` 导言、`subsec:bgv-encoding-decoding`。
- **原陈述**：直接把明文多项式视作密文域中的同一元素；把素数 $t\equiv1\pmod{2n}$ 的完全分裂批处理条件泛化为 BGV 的一般定义；用高/低二进制位描述任意素数明文模数。
- **判断**：明文环到整数代表元的选取不是环的包含映射。若本节要得到 $n$ 个标量槽位，确实可取素数 $t\equiv1\pmod{2n}$，但更一般的 BGV 可使用素数幂明文及扩张环槽位。任意奇素数的倍数不是字面二进制位移。
- **修正**：声明本节完全分裂的特例，先选整数代表元再在密文环中加密；将位图解释限定为直观数位图像，未将其作为证明。
- **依据**：[P4](https://people.csail.mit.edu/vinodv/6892-Fall2013/BGV.pdf)、[P5 §2.2、§3.4](https://imec-publications.be/bitstreams/5e8ee1f6-f7f1-4a12-983b-52a6677361fb/download)。**状态：已修正。**

### CBR-019　BGV 解密需要完整的中心化相位界

- **位置**：`subsec:bgv-enc-dec`、`subsec:bgv-moddrop`。
- **原陈述**：使用 $m_i+te_i<q$ 等单边界即可解密；被消除的 $E$ 本身是 $t$ 的倍数；ModDrop 后默认仍能解密。
- **判断**：必须先恢复中心化整数相位，再对 $t$ 取模。一个清楚的充分条件是 $\|M+tE\|_\infty<q_l/2$。$q_l$ 通常与 $t$ 互素，所以发生模 $q_l$ 回绕后再模 $t$，不保持原明文。消掉的是 $tE$，不是要求 $E$ 自身被 $t$ 整除。
- **修正**：补充绝对值和总相位界；明确相位的模约减顺序；对裸 ModDrop 加入更小模数的界；加法和明文乘法的框保留，但通过相位记号约定避免声称计算后误差仍是新鲜分布。
- **依据**：[P4 §3.3 Lemma 5](https://people.csail.mit.edu/vinodv/6892-Fall2013/BGV.pdf)、[P5 §2.2](https://imec-publications.be/bitstreams/5e8ee1f6-f7f1-4a12-983b-52a6677361fb/download)。**状态：已修正。**

### CBR-020　模数切换必须保持明文同余，并留出纠正误差的空间

- **位置**：`subsec:bgv-modulus-switch`、`subsubsec:bgv-moddrop-vs-modswitch`。
- **原陈述**：最终模 $t$ 的结果在复杂展开中被直接宣布等于 $M$；缺少舍入与同余纠正后的严格不回绕界；把便利的 $q_l\equiv\widehat q\equiv1\pmod t$ 当成所有 BGV 的必要条件。
- **判断与推导**：设 $\rho=\widehat q/q_l$，先得到同余保持代表元 $\widetilde A,\widetilde B$，令 $\delta_A=\widetilde A-\rho A$、$\delta_B=\widetilde B-\rho B$。若 $AS+B=M+tE+Kq_l$，则
  $$Y=\widetilde AS+\widetilde B-K\widehat q=\rho(M+tE)+\delta_AS+\delta_B.$$
  同余条件给 $Y\equiv M\pmod t$，但仍需 $\|Y\|_\infty<\widehat q/2$，才能认定它就是新中心化相位。原文的“先最近舍入再中心化纠正”可给出保守界 $\|\delta_A\|_\infty,\|\delta_B\|_\infty\le(t+1)/2$。
- **修正**：写出上述完整证明和充分界
  $$\rho\|M+tE\|_\infty+\frac{t+1}{2}(1+\|S\|_1)<\widehat q/2.$$
  与 P4 定义的“在正确模 $t$ 剩余类中选最近点”相比，这个两步版本界稍松，但其正确性现在可检查；没有冒称它是最优舍入规则。
- **验证**：小参数穷举 13,377 个满足该充分条件的标量情形，及额外 91 个单素数 RNS 步骤。依据：[P4 §3.3 Definition 9/Lemma 5](https://people.csail.mit.edu/vinodv/6892-Fall2013/BGV.pdf)。**状态：已修正。**

### CBR-021　固定的 $t$、乘法误差与 BGV 求值密钥

- **位置**：`subsec:bgv-mult-cipher`、Optional Rescaling para、`subsec:bgv-key-switching`、`subsec:bgv-rotation`。
- **原陈述**：每次乘法让噪声尺度依次成为 $t^2,t^4,\ldots$，再靠重缩放回到 $t$；只要模数比足够大于 $t$，结果噪声就小于两个输入；直接复用一般 RLev 密钥而未要求误差被 $t$ 整除。
- **判断**：精确展开为
  $$(M_1+tE_1)(M_2+tE_2)=M_1M_2+t(M_1E_2+M_2E_1+tE_1E_2).$$
  方案的整除因子一直是 $t$。误差大小取决于消息、卷积、两个误差及密钥切换，不由 $w>t$ 单独决定。若求值密钥只加普通 $E_i$，会改变最终模 $t$ 剩余类。
- **修正**：显式给出 $g_iS^2+tE_i$、$g_iS+tE_i$ 的求值密钥和累计误差；模数切换使用实际比例与同余纠正；交换重线性化/缩放次序附带秘密平方和新模数条件。
- **依据**：[P4 运算和 Scale 分析](https://people.csail.mit.edu/vinodv/6892-Fall2013/BGV.pdf)、[P5 §2.2](https://imec-publications.be/bitstreams/5e8ee1f6-f7f1-4a12-983b-52a6677361fb/download)。**状态：已修正。**

### CBR-022　自举溢出项 $K'$ 的界不是无条件 $n+1$

- **位置**：`subsec:bgv-bootstrapping`；Discussion 的 Choice of epsilon para。
- **原陈述**：乘 $p^{\varepsilon-1}$ 后，一律有 $\|K'\|_\infty\le n+1$，于是选足够大的数位间隔便会成功。
- **判断与推导**：P5 式 (8)–(11) 规定，先令 $A'=[p^{\varepsilon-r}A]_q$、$B'=[p^{\varepsilon-r}B]_q$，则
  $$u=B'+A'S=p^{\varepsilon-r}M+p^\varepsilon E+qK'.$$
  三角不等式给
  $$\|K'\|_\infty\le\|(B'+A'S)/q\|_\infty+p^{\varepsilon-r}\|M\|_\infty/q+p^\varepsilon\|E\|_\infty/q.$$
  后两项不能仅因秘密三元就删除。尤其增大 $\varepsilon$ 同时增大噪声项，不能只看数位间隔。
- **修正**：写出完整界与必要的恢复条件 $\|K'\|_\infty<p^{\varepsilon-r}/2$；要求给出确定性参数界或明确概率模型/失败率，未套用未经论证的独立均匀假设。
- **依据**：[P5 §3.2–3.3，式 (8)、(10)、(11)](https://imec-publications.be/bitstreams/5e8ee1f6-f7f1-4a12-983b-52a6677361fb/download)。**状态：已修正；具体实例失败率需另算。**

### CBR-023　负数数位提取与精确除法后的明文模数

- **位置**：`subsec:bgv-bootstrapping` 的 digit extraction；Handling the Divisions by p para。
- **原陈述**：将 $K'$ 连续向下取整，最终得到 $\lfloor K'/p^{\varepsilon-1}\rfloor=0$；乘 $p^{-1}\bmod Q$ 就能一般地除以明文 $p$，而明文模数不必同步变更。
- **判断与反例**：$K'=-1$ 时，无论正分母多大，普通 floor 都是 $-1$。P5 使用平衡数位与最近整数舍入；二进制另需偏移。另一方面，$p$ 在 $\mathbb Z_{p^j}$ 中不可逆。只有前一步先得到可整除相位 $pT+p^jF$，在 $\gcd(p,Q)=1$ 时乘密文模数下的逆元才得到
  $$T+p^{j-1}F\pmod Q,$$
  此时明文模数应为 $p^{j-1}$。
- **修正**：保留“数位提取”的正确目的，但以平衡舍入定义输出；精确除法显式降低明文模数。脚本例子 $p=3,Q=101,j=3,T=2,F=1$ 得相位 11，它模 9 是 2，模 27 却不是 2。
- **依据**：[P5 §6、脚注 10、Algorithm 1](https://imec-publications.be/bitstreams/5e8ee1f6-f7f1-4a12-983b-52a6677361fb/download)。**状态：已修正。**

### CBR-024　BGV 自举的原 ModRaise 推导没有建立完整正确性

- **位置**：`subsec:bgv-bootstrapping`；Reason for Modulus Switch、Generalization、Comparing Bootstrapping 小节。
- **原陈述**：乘数预处理产生 $(A',B')$ 后，下一步又提升旧的 $(\widehat A,\widehat B)$，却赋予其新相位；同时声明需要同态解密但实际步骤缺失；直接复用 CKKS 复矩阵；断言输出噪声系数必然增大。
- **判断**：这不是一个可由现有式子直接证明的算法。提升旧分量的符号错误可以确定，但仅改一个帽子仍不足以建立全流程。P5 明确给出公开预处理、同态内积、适当明文环上的线性变换、精确数位提取和逆变换。一般槽位是扩张环，不必一系数对应一个现有标量槽。还必须满足 P5 §2.3 的 $\gcd(p,\mu)=1$；对本书 $\mu=2n$ 的二次幂环，这要求 $p$ 为奇数。论文的二进制数位规则不能在该分歧环中自动创造 CRT 槽。
- **修正**：采用 P5 已核查的通用流程；用工作明文模数 $p^\varepsilon$ 的自举密钥加密 $S$，同态计算 $B'+A'S$。把完全分裂 $p\equiv1\pmod{2n}$ 作为单密文标量槽说明的条件；一般情况明确多密文/扩张槽的需求。推广 $t=p^r$ 时统一使用 $p^{\varepsilon-r}$。
- **依据**：[P5 §3.2–3.4](https://imec-publications.be/bitstreams/5e8ee1f6-f7f1-4a12-983b-52a6677361fb/download)。**状态：原错误链已替换；没有为其他 lift 型 BGV 自举变体编造证明。**

## 发现清单：RNS

### CBR-025　FastBConv 的共同 CRT 提升及误差界的证明

- **位置**：`d05-rns.tex` 导言、`subsec:rns-fastbconv`。
- **原陈述**：中心化整数的端点写成对所有奇偶模数通用的 $q/2-1$；从 CRT 和 $T$ 的界直接得出 $uq$ 的同样界，漏掉 $x$；目标向量长度在 $k,l$ 间混用。
- **判断**：算法核心正确，原来较松的 $|u|\le k/2+1$ 并非需要推翻的错误结论，但其证明缺项。对于两两互素奇模数、中心化余数，$T=\sum_i[x_iz_i]_{q_i}(q/q_i)=x+uq$。因为 $|T|<kq/2$、$|x|<q/2$，得到 $|u|<(k+1)/2$，故 $|u|\le\lfloor k/2\rfloor$。
- **修正**：明确奇模数与中心区间，采用完整三角不等式；输出是同一个 $T$ 在全部目标模数下的剩余类，统一维数为 $l$。区分“近似基转换”与 CRT 正确性。
- **验证**：基 $(5,7,11)$ 的全部 385 个代表元；例如 $x=-192$ 时 $T=193=x+385$。依据：[P3 §3.2](https://yongsoosong.github.io/files/papers/RNS.pdf)、[P6](https://webusers.imj-prg.fr/~jean-claude.bajard/MesPublis/SAC2016.pdf)。**状态：证明与记号已修正。**

### CBR-026　SmallMont 不能丢掉辅助剩余类，且需要量化条件

- **位置**：`subsec:rns-smallmont`、`subsubsec:rns-smallmont-fastbconv`。
- **原陈述**：先将 $T$ 模 $b$ 约减，再用该结果计算模 $b_\alpha$ 的纠正；用“$v$ 增长比 $b_\alpha$ 慢”证明最终误差仅为 $\{-q,0,q\}$，没有给出门槛。
- **判断**：因 $b$ 与 $b_\alpha$ 互素，$[[T]_b]_{b_\alpha}$ 通常不同于原 $[T]_{b_\alpha}$。对于预处理 $[b_\alpha x]_q$，令其共同 CRT 提升为 $T=b_\alpha x+(v+u)q$，正确的纠正是 $a=[Tq^{-1}]_{b_\alpha}$。结果为
  $$\frac{T-qa}{b_\alpha}=x+q\frac{v+u-a}{b_\alpha}.$$
  中心化条件给 $|v|<(b_\alpha+1)/2$、$|a|<b_\alpha/2$，若 $b_\alpha>U_k+1/2$，整数商的绝对值小于 2，因此属于 $\{-1,0,1\}$。
- **修正**：保留独立辅助剩余类；给出上述中心化变体的充分条件。明确这不是逐字复制 BEHZ 的无符号版参数界；也不是精确基转换。
- **验证**：$q=385,b=323,b_\alpha=13,x=-192$ 时，正确辅助纠正为 6，错误嵌套约减给 -4；$x=-187$ 的有效 SmallMont 输出是 198，证明输出仍可相差一个 $q$。依据：[P6 §4.2 Algorithm 2/Lemma 4](https://webusers.imj-prg.fr/~jean-claude.bajard/MesPublis/SAC2016.pdf)及上述独立推导。**状态：已修正。**

### CBR-027　ModRaise 的分量误差不等于相位误差

- **位置**：`subsec:rns-modraise`。
- **原陈述**：把基扩展描述为直接保持数值的模数提升，并将各系数的一个 $q$ 倍数当作整个密文的同等小噪声。
- **判断**：CRT 扩展选择一个整数提升，并非自然的环包含。若分量分别变化 $qU_A,qU_B$，相位变化是 $q(U_B+U_AS)$；还需加上原整数相位本来含有的 $qK$。因此即便每分量误差系数有界，也不能省去秘密卷积。
- **修正**：写明输出代表 $x+uq\pmod{qb}$，相位界为 $qU_k(1+\|S\|_1)$ 的保守形式；这些是有结构的表示倍数，不是独立新鲜 RLWE 样本。
- **依据**：[P3 §3.2 Algorithm 1](https://yongsoosong.github.io/files/papers/RNS.pdf)。**状态：已修正。**

### CBR-028　裸 ModDrop 不能一般地保持 BFV 明文

- **位置**：`subsec:rns-moddrop`、`subsubsec:rns-dec-ckks-bgv`。
- **原陈述**：删除 RNS 因子不增加误差，所以保持明文；CKKS/BGV 解密可一律先降到单个最小模数。
- **反例**：BFV 取 $q=105,t=7$，无噪声消息 $m=1$ 的相位为 15。降到 $q'=35$ 后相位仍为 15，且仍在中心区间内，但标准 BFV 解码为 $\operatorname{rnd}(7\cdot15/35)=3$。原因是尺度变化，不是分量约减不精确。CKKS/BGV 虽不采用这个 BFV 尺度，仍需完整相位装得进目标模数。
- **修正**：区分精确剩余类约减与正确明文语义；CKKS/BGV 需要更强的小模数相位界；否则 CRT 重构或方案正确的缩放/切换，不得强行删除因子。
- **依据**：[P1](https://yongsoosong.github.io/files/papers/HEAAN.pdf)、[P6 标准 BFV 解码](https://webusers.imj-prg.fr/~jean-claude.bajard/MesPublis/SAC2016.pdf)及脚本反例。**状态：已修正。**

### CBR-029　RNS ModSwitch 的误差应相对于理想舍入定义

- **位置**：`subsec:rns-modswitch`、无 label 的三原语比较小节。
- **原陈述**：误差约为某个转换值除以 $b$，用模糊上界解释；比较小节又把这个近似操作写成精确缩放。
- **判断与推导**：令 $r=[x]_b$，快速转换给 $r+ub$，则
  $$b^{-1}(x-r-ub)=\operatorname{rnd}(x/b)-u\pmod q.$$
  额外误差恰为 $-u$。只删除一个奇模数时 $u=0$，分量舍入精确；多个因子时仍有转换误差。算法定义不需要 $b\ll q$，但密文解释需要相位界。
- **修正**：把目标、误差和条件分开，统一下标；明确相位扰动还包括秘密多项式，BGV 必须另用同余保持规则。
- **验证**：单因子和双因子共 520 个情形。依据：[P3 §3.2 Algorithm 2](https://yongsoosong.github.io/files/papers/RNS.pdf)。**状态：已修正。**

### CBR-030　BFV RNS 解密的尺度、符号和半区间纠正门槛

- **位置**：`subsubsec:rns-dec-bfv`。
- **原陈述**：本章突然采用 $B=AS+\Delta M+E$ 的相反符号；把除以 $\lfloor q/t\rfloor$ 当成乘 $t/q$；把中心化余数恒等式写为 floor；任取互素 $\gamma$，只要求残差小于 $\gamma$ 即可消去。
- **判断与推导**：按本书统一符号取 $x=[B+AS]_q$，目标为 $m_0=\operatorname{rnd}(tx/q)$。令 $\delta=tx/q-m_0$，$v=[t\gamma x]_q$，快速 CRT 和为 $v+uq$。则纠正前
  $$y\equiv-q^{-1}(v+uq)\equiv\gamma m_0+\eta\pmod{\gamma t},\qquad\eta=\operatorname{rnd}(\gamma\delta)-u.$$
  要把 $y_\gamma$ 解释为 $\eta$，需要 $|\eta|<\gamma/2$，不是 $\gamma$。充分条件是 $\gamma|\delta|+1/2+U_k<\gamma/2$。
- **修正**：给出正确尺度和三步冗余纠正，明确边界余量。$q=385,t=3,\gamma=13,x=-189$ 时 $\eta=-7$，虽有 $|\eta|<13$，解码仍错误：输出 1，而正确舍入为 -1。
- **依据**：[P6 §3.4 Theorem 1/Algorithm 1](https://webusers.imj-prg.fr/~jean-claude.bajard/MesPublis/SAC2016.pdf)、[P7 §2.3–2.4](https://www.shoup.net/papers/rns-bfv.pdf)及脚本穷举。**状态：已修正。**

### CBR-031　BGV RNS 切换不能把目标模数当成 BFV 明文模数

- **位置**：`subsec:rns-modswitch-bgv`。
- **原陈述**：将 BFV 解密器设为 $q=q_l,t=\widehat q$，即可计算 BGV 切换中的舍入。
- **判断**：常用模数链有 $\widehat q\mid q_l$，BFV 例程所需的 $q_l^{-1}\bmod\widehat q$ 不存在，例如 105 模 35。即使互素，CBR-030 的舍入余量也不保证对任意密文系数成立。
- **修正与推导**：对常用一步 $q=Qw$、$w\equiv1\pmod t$、$\gcd(w,Qt)=1$，直接令
  $$d=t[t^{-1}a]_w,\quad a'=(a-d)/w,\quad a_i'=[w^{-1}(a_i-d)]_{q_i}.$$
  这里 $d\equiv a\pmod w$ 且 $d\equiv0\pmod t$，故商为整数并保持模 $t$ 同余；误差至多 $t/2$。完整相位条件为 $\|M+tE\|_\infty/w+(t/2)(1+\|S\|_1)<Q/2$。多因子 $w$ 的中心化剩余类仍需精确恢复。
- **依据**：[P4 Definition 9/Lemma 5](https://people.csail.mit.edu/vinodv/6892-Fall2013/BGV.pdf)的同余保持原则，以及上述完整整数推导。**状态：错误复用已替换为明确特例，不宣称覆盖所有链策略。**

### CBR-032　FastBConvEx 是有范围条件的精确算法，不是 SmallMont

- **位置**：`subsec:rns-fastbconvex`、Necessity of Centered Residue Representation para。
- **原陈述**：把“输入远小于模数”当作条件说明；省略同一 CRT 和的约束；把中心化表示说成唯一可能的实现；相关尾段又把该算法当成仍需 SmallMont 的有噪声转换。
- **判断与推导**：原算法核心是正确的 Shenoy–Kumaresan 型纠正。令 $[x]_b=x+\mu b$，两次快速转换都使用共同 $T=x+(\mu+u)b$。当 $|\mu+u|<b_\alpha/2$ 时，$\gamma=[(T-x_\alpha)b^{-1}]_{b_\alpha}=\mu+u$，所以 $T-\gamma b=x$，误差完全消除。原来较保守的模数大小要求可满足此条件，不必把它误判为错误算法。
- **修正**：以 $b_\alpha>2(\lambda+U_l)$ 等量化充分界说明范围；中心化用于恢复带符号整数，无符号实现若显式恢复符号也可行；超出范围时可能错一个 $bb_\alpha$ 倍数。
- **验证**：595 个满足界限的值全部精确，另保留超界失败例。依据：[P6 §4.4 Lemma 6，式 (12)、(13)](https://webusers.imj-prg.fr/~jean-claude.bajard/MesPublis/SAC2016.pdf)。**状态：证明、条件和分类已澄清。**

### CBR-033　RNS gadget 的整数提升与 $(A,B)$ 分量顺序

- **位置**：`subsec:rns-decompmult`、`subsubsec:rns-application-key-switching`、`subsubsec:rns-rotation`、`subsubsec:rns-application-basic`。
- **原陈述**：把各个 RNS 剩余类直接称为 gadget 数位，却没有说明作为 $R_q$ 乘数时如何在其他坐标表示；重线性化把 $(D_0,D_1)$ 当作本书的 $(A,B)$；输入/输出秘密记号混用；把标量的 RNS 逐点乘法与多项式乘法混在一起。
- **判断与推导**：可选择 $g_i=(q/q_i)[(q/q_i)^{-1}]_{q_i}$、$A_i=[A]_{q_i}$，此时 $A\equiv\sum_iA_ig_i\pmod q$。但 $A_i$ 必须先选小整数代表元，再把同一整数约减到每个目标模数。求值密钥满足 $b_i+a_iS'=g_iS+E_i$ 时，新增误差恰为 $\sum_iA_iE_i$。把其他坐标填零会改变乘数及误差。BEHZ 可采用另一种把逆元放入数位的等价约定，不能混配。
- **修正**：明确提升与误差，统一 $(D_1,D_0)$、$S'$ 和 BGV 的 $tE_i$。RNS 逐点操作只针对标量剩余类，多项式仍是负循环卷积；NTT 后才可逐点相乘。旋转的自同构本身不增加近似误差，随后的密钥切换才增加误差。
- **验证**：穷举 CRT gadget 重构，并用 $(1+X)^2=1+2X+X^2$ 反驳直接逐系数相乘。依据：[P6 §4.5 Lemma 7/8](https://webusers.imj-prg.fr/~jean-claude.bajard/MesPublis/SAC2016.pdf)。**状态：已修正。**

### CBR-034　BFV RNS 乘法缺失辅助范围、近似缩放与秘密相关误差

- **位置**：`subsubsec:rns-cipher-mult-bfv`。
- **原陈述**：$b>\Delta$ 就足够装下乘积；一个 $b_\alpha$ 既作为 SmallMont 临时模数被删除，又用作最后精确转换的冗余模数；ModSwitch 的输出被当成精确舍入；分量舍入被合成相位的一次舍入替代；所有剩余项都比消息小，因此正确。
- **判断**：这是多个独立缺口。真实范围取决于 $t$、环维数、卷积和提升后的分量界，不能只比较明文尺度。BEHZ §4.2 明确区分临时 $\widetilde m$ 与保留的 $m_{sk}$。本书中心化 ModSwitch 给
  $$Z_j=\operatorname{rnd}(tD_j/q)-u_j=tD_j/q+\rho_j,$$
  故最终相位包含 $\rho_0+\rho_1S+\rho_2S^2$。即使消息为零，误差仍可能非零，所以“相对消息很小”不是正确性条件。
- **修正**：给出保留 $b_\alpha$、使用独立 $\widetilde m$ 的流程，要求每个 $tD_j$ 位于辅助整数范围内，并另行满足 FastBConvEx 的纠正界。随后用标准 $t/q$ 解码的绝对误差条件表述正确性。修正缺帽分量、使用 $Z_2$ 而非旧 $D_2$ 的重线性化输入及 $(A,B)$ 顺序。
- **验证**：$q=17,t=3,b=7,n=8$ 已有 $b>\Delta$，但合法系数形成的卷积远超 $qb/2$。该反例否定原充分条件，不声称这是安全参数。P6 的实际紧参数分析应与其范数约定一起使用；本书新给出的保守条件不是论文最佳参数表。
- **依据**：[P6 §4.2–4.5，式 (8)–(17)](https://webusers.imj-prg.fr/~jean-claude.bajard/MesPublis/SAC2016.pdf)、[P7 §2.2–2.4、§4.5](https://www.shoup.net/papers/rns-bfv.pdf)。**状态：已修正；具体性能/安全实例未认证。**

### CBR-035　素数幂可以是一个 RNS 模数；原 BFV RNS 自举替代流程未证明

- **位置**：`subsubsec:rns-bfv-bootstrapping`。
- **原陈述**：RNS 因子必须互素，所以不能模切换到 $p^\varepsilon$，因此必须采用所列九步替代流程；其中预处理之后分量名仍写作未缩放的量，自举误差没有完整界。
- **判断**：CRT 要求不同基模数互素，不要求每个模数都是素数。$p^\varepsilon$ 可以作为一个模数，也可以只作为同态电路的明文模数，与工作密文 RNS 基独立。禁止把 $p,p,\ldots,p$ 作为彼此独立的 CRT 坐标，不等于禁止素数幂。原文没有给出九步替代流程的完整正确性论证，BEHZ/HPS 的乘法正确性也不能自动补足它。
- **修正**：采用已核查 P5 式 (9) 的公开预处理
  $$c_i'=[\operatorname{rnd}(p^\varepsilon c_i/q)]_{p^\varepsilon},$$
  然后按工作明文模数 $p^\varepsilon$ 同态计算内积、线性变换、舍入数位提取及逆变换。公开系数可由 CRT 精确重构，或采用有明确精度保证的缩放算法。系数到槽位路线仍需 $\gcd(p,\mu)=1$；本书二次幂环要求奇数 $p$，其他相容分圆环才可直接使用论文的二进制槽方案。若相位采用理想尺度 $q/p^r$，误差为 $(p^\varepsilon/q)E+R_B+R_AS$；实际 floor 尺度的差须计入 $E$。
- **依据**：[P5 §3.2 式 (9)、§3.3 式 (12)、§3.4](https://imec-publications.be/bitstreams/5e8ee1f6-f7f1-4a12-983b-52a6677361fb/download)。**状态：错误的禁用理由已纠正；未证明的替代链已撤下，未声称所有变体都不可能成立。**

### CBR-036　RNS CKKS 自举流程与完整溢出界

- **位置**：`subsubsec:rns-ckks-bootstrapping`、`subsubsec:rns-cipher-mult-ckks`。
- **原陈述**：在 CKKS 的 ModRaise 后插入显式同态秘密内积和最终 reinterpretation；把 SmallMont 每分量的 $\{-1,0,1\}$ 界当作整条相位的同样界；周期性会精确消除所有溢出。
- **判断**：基础 CKKS 自举直接操作提升后的密文；RNS 表示不应添加另一套无证明流程。相位为
  $$\Delta M+E+q_0(K+U_B+U_AS).$$
  多项式近似必须覆盖总溢出所定义的输入区间，有限次数多项式不因目标函数周期就成为精确模约减。RNS 乘法的尺度仍为实际 $\Delta_1\Delta_2/w$。
- **修正**：与 D3 的正确流程一致，补充稀疏 PartialSum、完整相位倍数和所有误差预算；澄清混合密钥切换可以使用自己的辅助基，并非宣称 CKKS 实现中永远不用基扩展。
- **依据**：[P2](https://yongsoosong.github.io/files/papers/HEAAN_boot.pdf)、[P3](https://yongsoosong.github.io/files/papers/RNS.pdf)。**状态：已修正。**

### CBR-037　RNS BGV 自举不能重复除法，也不能把任意基转换叫 ModRaise

- **位置**：`subsubsec:rns-bgv-bootstrapping`、`subsubsec:rns-cipher-mult-bgv`。
- **原陈述**：数位提取已经在各轮除以 $p$，末尾还要再乘 $p^{-(\varepsilon-1)}$；从与原链互素的 $\widehat q$ 到 $q_L$ 直接调用只定义在 $q\to qb$ 上的 ModRaise；混用 EvalExp 与整数数位提取。
- **判断**：重复除法会把消息额外缩小；$\widehat q\nmid q_L$ 时，不能把该转换描述为保留原基坐标的扩展。一般转换可能可实现，但需另定义选择整数代表元和误差的算法。
- **修正**：跟随 D4 已修正的 P5 同态内积流程，工作密文模数与明文模数分离。每次精确除法仅做一次并更新 $p^j\to p^{j-1}$；不加额外总除法。特殊模数可以用公开重构和有效同余保持模切换得到。
- **依据**：[P5 §3.2–3.4、§6](https://imec-publications.be/bitstreams/5e8ee1f6-f7f1-4a12-983b-52a6677361fb/download)、[P3 对 ModUp 的精确定义](https://yongsoosong.github.io/files/papers/RNS.pdf)。**状态：已修正。**

### CBR-038　RNS 噪声分类、适用范围与原语命名混淆

- **位置**：`subsubsec:rns-noise`、导言，以及三种模数操作的比较。
- **原陈述**：FastBConvEx 产生的噪声总要配合 SmallMont 降低；各种 RNS 操作的扰动都直接作为同类噪声加入；TFHE 不使用 RNS 被说成方案的绝对属性。
- **判断**：FastBConvEx 在界内是精确的，SmallMont 则仍允许 $\pm q$ 偏差。ModDrop 是精确剩余类约减但可改变解码语义；ModSwitch 是舍入加可量化转换偏差。扰动是否被后续模约减消掉，需要看具体算法。对分量扰动，正确相位项统一是 $\delta_B+\delta_AS$，高阶密文还包含秘密幂。
- **修正**：分别说明表示倍数、缩放误差和精确转换；用完整相位界统一解释，删除“必须总配合”的错误要求。常见机器字 TFHE 实现不需要本章大整数 RNS 分解，仅作为实现范围说明；也删除固定比特数的普遍安全暗示。
- **依据**：[P3](https://yongsoosong.github.io/files/papers/RNS.pdf)、[P6](https://webusers.imj-prg.fr/~jean-claude.bajard/MesPublis/SAC2016.pdf)、[P7](https://www.shoup.net/papers/rns-bfv.pdf)。**状态：已修正。**

## 已核查且保留的内容

不能因为本报告集中列问题，就推断章节中所有内容原来都错。以下核心内容经过实际核对，保留其成立部分：

- CKKS 原主编码矩阵顺序 $n^{-1}\widehat W I_n^R$、共轭对称向量的实系数性、二次幂环的根结构。
- 四维编码例子的最终整数及旋转后的主要数值结果；被修改的是前面的错误小数、符号和缺失步骤。
- 密文逐分量加法、加明文只作用于 $B$ 分量、张量乘积三项和相位展开；补充同尺度/同密钥/相位界及噪声约定。
- $X\mapsto X^{5^h}$、$X\mapsto X^{-1}$ 的环自同构原理，及稀疏打包正向根指数计算。
- BGV 的相位 $M+tE$ 和模 $t$ 解密思想；相同明文模数下的加法、明文乘法基本公式。
- CRT 的标量加法和乘法、FastBConv 的共同提升形式、冗余模数精确纠正的核心算法；所补的是范围、表示约定和误差传播。
- RNS 只是表示方式，能够承载同一方案的环运算；没有把所有方案重新定义为同一尺度管理方法。

## 可重复验证与证据边界

运行：

```bash
python audit/check_ckks_bgv_rns.py
python audit/check_ckks_bgv_rns.py --json
python audit/check_meta_bts.py --json
python scripts/check_translation.py --math
```

反例脚本仅使用 Python 标准库，包含 12 组、合计 16,368 个案例。它检验有限域/整数等式、CRT 提升和界、中心化舍入、BGV 同余保持、四维复数编码、槽位旋转和稀疏迹。测试不是随机跑到“未失败”，而是在固定小范围上穷举，或针对明确错误给出稳定的反例；每组对应本报告的发现 ID。

后续 `check_meta_bts.py` 增加 8 组、13,970 个检查实例，涵盖实际尺度、递归残差、完全相关/自适应误差、输入余量、模数条件、复多项式导数及联合误差预算。6 组为精确有理数检查，2 组为明确标注的浮点一致性检查；它们不是完整 CKKS 实现或安全参数证明。完整推导和证据访问边界另存于 `ckks-followup.md`。

翻译校验用于确认英文与中文的标签、引用、环境、图路径、标题数量和归一化数学片段一致，不证明数学正确。额外词法检查也确认本次六个文件没有孤立 `\item`、错配环境或数学环境之外的裸下标/上标。完整双语编译由主审校流程统一运行，编译和版式结果记录在总报告中，避免在此记录其他章节仍变化时的过时页数。

## 明确保留的审查限制

1. **具体安全参数和失败概率**：没有为书中未实例化的 $n,q,Q,t,\Delta$、秘密分布和误差分布提供安全等级认证。新给出的确定性界通常是保守充分条件，不能代替原论文的更紧分析或具体库的参数选择。
2. **复杂自举的完整实现**：核查了 P2、P5 的算法结构与关键正确性等式，并修正了原文错误；没有实现或形式化验证完整 CKKS/BGV/BFV 自举。线性变换分解、数位提取多项式的实际电路、每层噪声与尺度安排仍需具体实现来实例化。
3. **改进自举的定量保证**：arcsin 已补读作者全文并核查定义域与参数相关成本，但没有重做其 SEAL 实验。Meta-BTS 的指定定理正文缓存及完整作者讲稿已读，完整论文仍未取得并逐段审阅，故仅其原论文全稿核验部分继续保留 `d03-ckks-050` 的 partially_verified 状态。教材新增的条件递推和联合误差模型均已独立证明；`d03-ckks-051` 已改为 corrected。具体生产参数下的内部允许条件与失败概率仍需实例化，不能将固定配置的实验平台视为所有方法普遍不可突破的下界。
4. **HPS 浮点实现**：已阅读其基转换/缩放定义和精度讨论，没有认证任意浮点格式、编译器或硬件实现。靠近舍入边界的量不能无条件声称精确；本报告没有拿摘要替代全文，也没有把 BEHZ 的误差界移植成 HPS 的性能结论。
5. **例子脚本与图像**：章节中链接的 `source code/` 程序由总审校任务另行审查；本报告的覆盖标记只确认本章节如何引用它们及其数学语义，不声称它们是生产可用密码库。原图像的标注和排版由总审校检查，本次没有悄悄修改图像来掩盖公式差异。
6. **未证明的其他变体**：本书原 RNS BFV/BGV 自举替代链没有足够证据支持，本次已改为有来源的通用流程。结论是原文不能按现有说明证明，而不是声称任何经过补全的类似变体都不可能正确。

## 基线与同步记录

本轮源书审校基线为仓库提交 `2a901038078fe054371e53089c86caaaa1112209`。每个英文基线文件及修订文件的 SHA-256、阅读单元原始行号和标签记录在 coverage JSON。`330b96f…` 是前次译本阶段的提交标记，不作为本次数学正确性的基准。

修订同步涉及六个正文文件和本报告、覆盖记录、反例脚本；未由本分任务提交或推送 Git。参考文献新增与跨章总结由主审校统一整合。对原文错误的更正不会被“译文必须忠实保留原错误”的旧工作方式阻止；现在中英文都指向相同、经本次审校的版本。
