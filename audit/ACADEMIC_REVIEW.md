# FHE Textbook 中英文版逐项学术审校

审校日期：2026-11-08。对象：`wang2000star/fhe-textbook-cn`，工作分支 `chinese-edition`。

## 结论

原始英文版本确实包含会改变数学结论、算法输出或安全解释的问题。本轮已经逐章核查全部 34 个章节，并将确认的修订同步写入英文和中文。审校没有把英文原文、中英文公式一致、程序能运行或 PDF 能编译当成正确性的证明。

修订包括定义域与适用条件、模数/尺度/代表元、噪声和舍入项、密文与密钥类型、槽位变换、自举局部推导、文献归属，以及 Python 示例的实际算法。部分原证明不能通过增加一句说明修复，已改为较短的正确推导或明确引用原论文的条件性流程。原有章节和比较主题保留；被替换内容及理由逐项记录，原版本可通过下面的基线提交追溯。

**这是一轮已完成的系统学术审校及修订，不是完整密码库认证或全书形式化证明。** 仍待完成的安全参数、失败概率和自举实现问题明确列在报告末尾，不能把这些限制算成已经解决。

## 1. 来源与可复核基线

- 本仓库的 GitHub parent/source 是 [fhetextbook/fhetextbook.github.io](https://github.com/fhetextbook/fhetextbook.github.io)。审校启动时，上游 `main` 和本仓库原始英文基线都指向 [`2a901038078fe054371e53089c86caaaa1112209`](https://github.com/fhetextbook/fhetextbook.github.io/commit/2a901038078fe054371e53089c86caaaa1112209)，提交日期为 2026-07-25，标题为 “Polynomial Reduction - notation fixes”。因此，这次检查到的问题存在于所核对的上游英文快照，不能归因于克隆损坏。
- 此前中文版本/编译修订为 [`330b96f38f2d3b6982e4b30f3943ff428fd47a0c`](https://github.com/wang2000star/fhe-textbook-cn/commit/330b96f38f2d3b6982e4b30f3943ff428fd47a0c)。该提交的 34 个英文章节与上述基线相同；这次审校明确允许修改两种语言中的学术内容。
- [arXiv 2503.05136](https://arxiv.org/abs/2503.05136) 的检索版本是 v26，修订日期为 2026-06-02。它与七月 GitHub 快照日期不同，本报告没有假定两者逐字或逐公式相同。
- 原标题、原行号、标签及相关内容的审校记录见各分组 coverage JSON；[baseline-headings.json](baseline-headings.json) 固定了基线的 34 个文件和 288 个标题单元。当前行号可能随修订改变，应优先用文件、标签和问题编号定位。

## 2. 范围、方法与判定

### 覆盖范围

| 对象 | 本轮范围 | 记录位置 |
|---|---|---|
| A/B/C 基础部分 | 27 章；113 个原始标题；30 个定理框；另有 1 个新增说明段落 | [基础审校](foundations-review.md)、[覆盖记录](foundations-coverage.json) |
| D1 TFHE、D2 BFV | 2 章；77 个原始标题；全部引言、公式、例子与证明 | [TFHE/BFV 审校](tfhe-bfv-review.md)、[覆盖记录](tfhe-bfv-coverage.json) |
| D3 CKKS、D4 BGV、D5 RNS | 3 章；98 个原始标题；全部正文与推导 | [CKKS/BGV/RNS 审校](ckks-bgv-rns-review.md)、[覆盖记录](ckks-bgv-rns-coverage.json) |
| D6、前言与参考文献 | 24 个比较主题、相位约定、前言论断和文献核对 | [概要审校](summary-review.md)、[覆盖记录](summary-coverage.json) |
| D7 与示例代码 | 全部 15 个 Python 文件、实际功能与 README 命令 | [代码审校](python-review.md)、[覆盖记录](python-coverage.json) |
| 图形资源 | 19 个资源，其中 18 个在正文使用；检查图形和正文条件的关系 | [图形记录](figure-coverage.json) |

统一覆盖表见 [coverage.md](coverage.md)，机器可读版本见 [coverage.json](coverage.json)。全部发现的入口见 [findings-index.md](findings-index.md)：共 143 个稳定编号，基础 36、TFHE/BFV 33、CKKS/BGV/RNS 38、概要与文献 22、代码 14。一个根因可能出现在正文、摘要表和代码中，因此问题编号的数量不等于彼此独立的错误或漏洞数量。

### 核验过程

每个原始标题单元都实际阅读其定义、等式、推导、例子和条件，再登记覆盖记录。重点检查：对象属于哪个域或环；代表元是否一致；相位符号是否贯穿算法；整数提升是否出现模数倍数；分量舍入能否合并；误差是确定界还是概率结论；密钥、密文和明文是否混用；算法输出是否支持原文的概括。

对确定错误构造反例，或直接推导完整等式；对复杂算法查阅原论文全文和作者/机构存档。数值检查同时包含失败例和满足修正条件的正例。最后进行双语结构/公式比较、代码回归、双语编译及重点页的视觉核查。覆盖检查只防止记录遗漏，公式比较只防止译本偏离，两者都不能替代数学审查。

判定中，“已修正”表示给出的错误表达或算法已改；“补充条件”表示原结论仅在明确条件下保留；“待证/限制已明示”表示本轮没有提供完整证明或实现。高影响项会改变核心结论、输出或安全论证；中低影响项主要涉及条件、类型、定义和表达。这里没有采用生产漏洞评分。

## 3. 最重要的发现及修订

### 3.1 原公钥构造存在一个可直接攻击的推广

**FND-024。** 原 B4 将一个小随机多项式构造推广为任意 GLWE/LWE 维数。取环维数 $n=1$ 时，随机因子只有 $U\in\{-1,0,1\}$。攻击者可枚举三个候选，检查公开掩码残差是否小，再从体分量减去相应公钥倍数恢复消息。增大秘密向量维数 $k$ 不会增加这三个候选的数量。

反例脚本在 $k=32,q=2^{20},t=4$ 下检查三个随机因子和四个消息，12 次都能公开恢复。更直接地，当 $U=0$ 时，体分量本身就是带小误差的消息编码。正文已把该小节限制到有适当参数和判定 RLWE 假设的标准环公钥结构；一般 GLWE 公钥构造需另给足够的随机维数和安全归约。这个反例攻击原文的无限制推广，不证明所有 RLWE 公钥方案不安全。

**FND-021、FND-025、FND-035。** 枚举一种攻击的候选数不是攻击下界；增加样本不必增加破解难度；秘密的公开散列不能直接当作独立均匀掩码的理由。已区分 LWE、RLWE、种子展开和相关评估密钥所需的假设，但没有凭空给出安全位数。

### 3.2 BFV 正文变体和代码各有一个不同的乘法问题

**TB-017、TB-018。** 在整数中重新解释密文时，原相位一般包含 $qK$。原文的 $Q=q\Delta$、分量除以 $\Delta$ 的乘法推导遗漏了余数及舍入项。即使 $q\gg t$、输入和评估钥都无噪声，也可能解错：

$$
n=2,\quad q=8191,\quad t=17,\quad \Delta=481,\quad S=[1,1].
$$

两个输入均为 $A=[8190,8190],B=[0,2]$，消息均为零。该变体输出标准解码 $[-2,0]$，正确结果应为 $[0,0]$。现在正文明确称其为需要完整误差界的教学变体，给出完整相位恒等式和充分条件，另行说明规范 FV 的整数乘积后 $t/q$ 缩放。

**CODE-003。** Python 库的错误不同：它先把乘积模 $q\Delta$，再用 $t/q$ 缩放。由于 $t\Delta=q-r$，被丢弃的倍数缩放后不一定是 $q$ 的倍数。固定反例的消息 $[2,3]$ 与 $[1,-8]$ 在 $\mathbb Z_{17}[X]/(X^2+1)$ 中应乘得 $[-8,4]$；旧代码得到 $[8,4]$。代码已改为精确整数负循环乘积、$t/q$ 舍入和重线性化，回归同时复现旧错误及正确输出。

**TB-015、SUM-006。** 规范 BFV 解码采用

$$
M=\left[\left\lfloor\frac tq[B+AS]_q\right\rceil\right]_t.
$$

当 $r=q-t\lfloor q/t\rfloor$ 时，一个充分正确性条件为 $\|tE-rM\|_\infty<q/2$。除以 $\lfloor q/t\rfloor$ 在一致代表元和适当条件下可能有效；本轮纠正的是原文的无条件等价和代表元混用，并没有宣称所有这种解码变体都错误。

### 3.3 噪声均值为零不意味着可无限计算

**FND-028、TB-002、SUM-005、SUM-013。** 独立零均值误差的方差相加；重复使用同一个误差则按乘数平方增长。固定参数的 BFV 不会因密文模数固定而获得无限乘法能力。模数链通常限制乘法深度或层级消耗，不能直接当作全电路乘法门总数。

**FND-032、TB-005。** 分量模数切换带来的误差必须保留。例如减号相位 $b-\langle a,s\rangle$ 下：

$$
e'=\frac{q'}q e+\delta_b-\sum_i\delta_{a_i}s_i.
$$

不能把它写成仅缩小旧误差，也不能凭均值为零断言这些舍入项相消。误差为随机变量时，正确性还需要尾界和全计算的联合失败概率。

### 3.4 CKKS 的实际尺度、局部模约减和自举常数

**CBR-008、SUM-009、CODE-004。** 乘法后删除模数因子 $w_l$，实际尺度为 $\Delta_1\Delta_2/w_l$。例如 $\Delta_1=\Delta_2=100,w_l=97$，结果是 $10000/97$，不能仍当成 100。代码新增实际尺度计算并更新解码器；正文保留分量舍入误差 $\rho_B+\rho_AS$。

**CBR-014、SUM-020。** CKKS 正弦近似不是精确模运算。令 $g(x)=q_0\sin(2\pi x/q_0)/(2\pi)$，则

$$
|g(r)-r|\leq\frac{2\pi^2}{3q_0^2}|r|^3.
$$

还需增加多项式近似和同态求值误差。原 EvalExp 流程漏乘的 $q_0/(2\pi)$ 已补齐；输入归一化、稀疏槽 PartialSum、Meta-BTS 纠错符号及反正弦主值区间也逐项修正。

### 3.5 BGV 的模数切换和数位操作不能沿用错误的 BFV 类比

**CBR-020、CBR-021、CBR-031、SUM-012。** BGV 的模数切换需要保持明文剩余类或跟踪校正因子。把系数简单舍入成 $t$ 的倍数会消除所有非零明文。正文和代码明确具体同余约定及完整中心相位界。

**TB-028 至 TB-032、CBR-022 至 CBR-024。** 普通低位删除实现向下取整，不自动等于最近舍入；奇素数平衡位和二进制舍入偏移必须分别处理。模 $p^j$ 中 $p$ 不可逆，已证明可整除后的精确除法会把明文模数改为 $p^{j-1}$。自举中的内积常数还必须与加密秘密使用相同尺度。所引 CRT 槽路线还要求 $\gcd(p,2n)=1$，因此本书二幂分圆环下要求奇数 $p$；二进制位运算的局部正确性不能替代另选相容分圆环或其他完整构造。

### 3.6 TFHE 的约定、输出类型和实际实现边界

**TB-004 至 TB-011、SUM-010、SUM-018。** 公开自举钥、输出 GLWE 秘密、样本提取密钥是不同对象；普通 PBS 和 LWE 到 GGSW 的电路自举也不同。查表区间要围绕消息编码中心，并符合负循环反周期性或明确限制输入域。神经网络图中的偏置必须解释为已编码偏置。

原 D1 的减号相位对应盲旋转正指数，其主体符号和样本提取下标经检查本来正确，已保留。D6 使用加号相位，所以明确给出掩码取负的转换和相应负指数。审校没有为了形式统一而翻转正确公式。

**CODE-001、CODE-002。** 现有 TFHE mock 自举在本地读取秘密、解密、查表并重新加密，不是公开求值实现。BFV/BGV/CKKS 自举函数原为返回数字 0 的占位符，现明确抛出 `NotImplementedError`。这些功能边界已经写进双语正文和 README；本轮没有把缺失的自举实现补成完整密码库。

### 3.7 基础数学、RNS 和文献归属

**FND-005 至 FND-020。** 补正递减 gadget 的完备性条件、有限域根和分裂条件、商环求值对象、非正交基坐标、矩阵朝向、缩放舍入命题与负循环 NTT。明确 $\|AB\|_\infty\leq\|A\|_1\|B\|_\infty$，避免遗漏卷积维数。

**CBR-025 至 CBR-038、CODE-005 至 CODE-013。** 区分近似与精确 RNS 基转换，保留 carry 和模切换误差；修复错误负循环符号、不可调用的精确转换分支、超过浮点精度的整数舍入、二进制负数分解、可选参数、错误退出码及 CKKS 实例参数。原矩阵实验仅保留为数值示例。

**SUM-022。** 原 `bgv-modswitch2` 引文键链接到 BGV 2011/277，却绑定另一作者 2015/474 的条目。已纠正作者、标题、年份和编号，并补入实际核验使用的 CKKS、TFHE、RNS-BFV 原论文。

## 4. 验证与复现

反例/代数/实现检查共有 **78 组**：基础 17、TFHE/BFV 21、CKKS/BGV/RNS 12、摘要 13、代码 15。其中代码组还检查 31 种方案/操作组合，每种覆盖固定输入与固定种子的随机输入，共 62 个运行子例。这些数目描述有限检查，不表示穷举所有参数。

覆盖和构建的实际结果见 [validation.json](validation.json)。五个检查脚本均已运行通过；集成时另运行覆盖记录检查、严格双语公式比较和两种语言的编译。PDF 对重点修改页作视觉核查；没有把抽样视觉检查描述成逐页人工校对。GitHub Actions 会在每次分支更新时执行反例/回归、双语结构和公式检查，再编译并发布两种 PDF 构建产物。

本地最终集成核验：34 个中英文章节结构匹配，6,883 处规范化数学片段匹配；英文 PDF 为 216 页，中文 PDF 为 167 页。两版均未出现缺字、未定义引用或未定义引文。全页文本边界扫描未发现文字越出纸张；另抽查中英文及报告的 24 个重点页，并修正中文页脚位置。中文及报告没有横向溢出告警；英文保留 31 处长公式/段落超过文本栏宽的告警，未观察到纸张外裁切。这里的自动边界检查和重点页抽查不等同于每一页的人工排版校对。

```sh
python3 -m venv .audit-venv
.audit-venv/bin/python -m pip install -r audit/requirements.txt
.audit-venv/bin/python audit/run_checks.py
python3 scripts/check_translation.py --math
python3 scripts/build.py all
python3 audit/build_report.py
```

数学反例脚本使用标准库整数、有理数或明确的数值容差；Python 示例回归使用固定版本的 NumPy、SymPy、fastcore。图形/排版构建需要 README 中的 LaTeX 环境；审校报告还需要 Pandoc、XeLaTeX 和 CTeX。完整审校 PDF 合并本文件、五份逐项报告、发现索引与覆盖清单，完整内容不依赖外部聊天记录。

## 5. 保留的证明与实现边界

1. **完整安全参数仍待证明。** 没有对所有构造给出统一参数族、三元/高斯分布之间的归约对应、具体攻击代价和安全位数。`FND-035` 保持待证状态；改成条件性表述不等于已经完成 IND-CPA 证明。
2. **自举仍有完整性边界。** BFV/BGV 的总误差、参数选择、扩域槽与二进制变换需要完整实现和端到端分析。CKKS 的具体逼近区间、次数、尾误差和深度消耗需要按目标参数选择。局部恒等式和论文流程核对不能替代这些工作。覆盖表保留 6 个 partially_verified 单元：BFV/TFHE 概念推广、自举概览、槽变换和总结共 4 处，CKKS 的 Meta-BTS 和联合定量误差限制共 2 处。arcsin 单元在补读作者全文后已核实定义域及参数相关成本，但未重做其数值实验。其余确定问题已修正，完整算法保证未补出。
3. **示例代码仍是教学代码。** 15 个文件都已静态检查，确认问题有定向回归；没有做常数时间、旁信道、生产随机性、密钥管理或成熟 FHE 库互操作认证。原独立脚本也未对全部可能全局配置穷举。
4. **没有重新证明所有引文。** 已核对与本次核心判断有关的一手全文、公式和版本。没有把 ePrint 摘要页当作正文定理的证据；访问受限时使用可读原文存档并注明载体。其余引文不能因出现在参考文献表中就视为已逐定理验证。
5. **图片仍沿用原资源。** 19 个图形都检查了语义及正文条件，部分英文图内标注仍保留。修订用正文/图注解释尺度和条件，没有把示意图伪装成证明。

后续若要将教材示例升级为完整可用的 FHE 库，应先固定具体参数、功能和威胁模型，再分别完成安全归约、全程误差证明和真实自举实现。上述边界在当前交付中保持可见。

## 6. 主要一手全文

- [Regev：On Lattices, Learning with Errors, Random Linear Codes, and Cryptography](https://cims.nyu.edu/~regev/papers/qcrypto.pdf)，定理 1.1、引理 4.2 和公钥构造。
- [Lyubashevsky–Peikert–Regev：On Ideal Lattices and Learning with Errors over Rings](https://web.eecs.umich.edu/~cpeikert/pubs/ideal-lwe.pdf)，环假设及公钥构造条件。
- [Fan–Vercauteren：Somewhat Practical Fully Homomorphic Encryption](https://eprint.iacr.org/2012/144)，§3–4；[实际访问的原论文全文镜像](https://scispace.com/pdf/somewhat-practical-fully-homomorphic-encryption-twy4lsabil.pdf)。
- [Brakerski–Gentry–Vaikuntanathan：(Leveled) Fully Homomorphic Encryption without Bootstrapping](https://people.csail.mit.edu/vinodv/6892-Fall2013/BGV.pdf)，作者机构全文。
- [Cheon 等：Homomorphic Encryption for Arithmetic of Approximate Numbers](https://yongsoosong.github.io/files/papers/HEAAN.pdf)，原 CKKS 论文；[Bootstrapping for Approximate Homomorphic Encryption](https://yongsoosong.github.io/files/papers/HEAAN_boot.pdf)，重缩放和正弦误差。
- [Chillotti 等：TFHE: Fast Fully Homomorphic Encryption over the Torus](https://imec-publications.be/bitstreams/92b4e945-9e22-4bc6-899c-c0baa9f7b4e9/download)，机构全文；[Chillotti 博士论文](https://ilachill.github.io/papers/these_Ilaria_Chillotti_wo_acknowl.pdf)，§4–5。
- [Geelen–Vercauteren：Bootstrapping for BGV and BFV Revisited](https://imec-publications.be/bitstreams/5e8ee1f6-f7f1-4a12-983b-52a6677361fb/download)，机构接受稿，§2–3、§6；[正式 DOI](https://doi.org/10.1007/s00145-023-09454-6)。
- [Halevi–Polyakov–Shoup：An Improved RNS Variant of the BFV Homomorphic Encryption Scheme](https://www.shoup.net/papers/rns-bfv.pdf)，精确 RNS 缩放/转换。其余 RNS 及基础代数来源见相应分组报告。

各分组报告给出更细的章节、公式编号、证明边界和直接反例。报告中的推导和复现输出是本次审校结果，不冒充上游作者结论。
