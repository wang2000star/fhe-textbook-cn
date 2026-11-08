# 中文译本说明与维护记录

## 版本与范围

中文初译对应的英文基线为：

```text
2a901038078fe054371e53089c86caaaa1112209
```

基线提交：[Polynomial Reduction - notation fixes](https://github.com/wang2000star/fhe-textbook-cn/commit/2a901038078fe054371e53089c86caaaa1112209)。

中文主文件为 `00-main-zh.tex`，正文位于 `zh-CN/`，与英文版的 34 个章节文件逐一对应：

| 部分 | 文件 | 内容 |
| --- | --- | --- |
| A | `a01-*.tex` 至 `a16-*.tex`，共 16 个 | 模运算、群与域、多项式环、单位根、分圆多项式、插值、矩阵、CRT、FFT/NTT 等基础 |
| B | `b01-*.tex` 至 `b06-*.tex`，共 6 个 | 格密码、LWE、RLWE、GLWE、GLev、GGSW |
| C | `c01-*.tex` 至 `c05-*.tex`，共 5 个 | 通用同态加法、明文乘法、模数切换与密钥切换 |
| D | `d01-*.tex` 至 `d07-*.tex`，共 7 个 | TFHE、BFV、CKKS、BGV、RNS、方案比较与 Python 示例入口 |

当前版本完成了全部正文的中文初译，包括主文件中的前言、标题以及章节中的解释、证明文字、图注和表格文字。**这不表示已经完成逐式学术审校，也不表示原书的所有技术陈述已被独立证明。** 对原文的明显条件缺失、术语疑点或上下文矛盾，应结合上下文及所引原始文献进一步核对。

## 保留与调整的内容

- 保留原书的结构、公式、数学符号、标签、交叉引用、引用键和参考文献。
- 保留作者姓名、机构名称等专名；可辨识的算法名称和代码标识，例如 `FastBConvEx`、`Decomp`、`GLWE`，不改成中文标识。
- 共用 `figures/` 中的原始图片。图片文件内部已经嵌入的英文文字仍为英文，中文图注在对应 `.tex` 文件中提供。
- 共用 `z-bibfile.bib`。参考文献的作者、原题、出版信息与链接保持原样，便于查证和检索。
- 教学 Python 源码仍位于 `source code/`；本次译本支持没有将函数名、命令行参数或示例程序接口翻译为中文。
- 中文入口使用 XeLaTeX、CTeX 与 Fandol 字体，并将正文输入路径改为 `zh-CN/`。纯排版笔误可在中文稿中修正；例如 A-12 的虚数小节标题后多余的字母 `n` 已去除。
- 涉及技术含义的修订应明确标注。D-6 对 BFV“无限乘法”的表述增加了译者说明，提醒读者同态运算仍受噪声预算约束，持续计算需要合适的自举及参数条件。

## 术语约定

| 英文 | 中文 |
| --- | --- |
| fully homomorphic encryption, FHE | 全同态加密 |
| plaintext / ciphertext | 明文 / 密文 |
| secret key / public key | 秘密密钥 / 公钥 |
| random public mask | 公开随机掩码 |
| lattice | 格 |
| Learning with Errors, LWE | 带误差学习 |
| Ring Learning with Errors, RLWE | 环带误差学习 |
| Generalized LWE, GLWE | 广义带误差学习 |
| modulus / modulo reduction | 模数 / 模约减 |
| centered residue representation | 中心化剩余表示 |
| scaling factor | 尺度因子 |
| modulus switching | 模数切换 |
| rescaling | 重缩放 |
| key switching | 密钥切换 |
| relinearization | 重线性化 |
| bootstrapping | 自举 |
| blind rotation | 盲旋转 |
| sample extraction | 样本提取 |
| lookup table, LUT | 查找表（或查表） |
| decomposition / gadget decomposition | 分解 / Gadget 分解 |
| root of unity / primitive root of unity | 单位根 / 本原单位根 |
| cyclotomic polynomial | 分圆多项式 |
| coefficient / evaluation / interpolation | 系数 / 求值 / 插值 |
| point-value representation | 点值表示 |
| Hadamard product | Hadamard 积（逐元素乘积） |
| Hermitian product | Hermitian 内积 |
| Chinese Remainder Theorem, CRT | 中国剩余定理 |
| Residue Number System, RNS | 剩余数系统 |
| Number-Theoretic Transform, NTT | 数论变换 |

同一个英文词在不同上下文中可能有不同含义。例如，`public mask` 是对称 LWE/GLWE 密文的公开随机分量，不应与公钥加密方案中可复用的加密公钥混为一谈。关于缩放、取模与舍入的文字，应始终以对应公式中的运算为准。

## 原文中需要进一步核对的问题

以下记录定位于英文基线及对应中文章节。它们是校审线索，不是已经完成的勘误证明；除明确的译者说明外，中文稿没有将整套推导替换为新推导。

| 位置 | 待核对问题 |
| --- | --- |
| A-6，`a06-decomp.tex`，数的分解 | 仅给出 `β^ℓ \| q`，不足以保证任意 `γ ∈ Z_q` 都能按文中等式精确表示。例如 `q=8, β=2, ℓ=1` 时，右侧只能表示 0 或 4，不能表示 1。精确表示还需要对 `γ` 的可表示性作限制；若要覆盖全部剩余类，通常需要足够的分解位数。原文的近似分解讨论也应与此统一。 |
| A-9，`a09-cyclotomic-polynomial-integer-ring.tex` | 将复数上单位根与分圆多项式的乘积表达直接迁移到 `Z_p` 时，需要说明根是否全部存在于该域中，以及是否需要扩域。例如 `Φ_4(x)=x²+1` 在 `F_3` 中没有根，不能在 `F_3` 内按两个一次因子的乘积表示。后文选择模数的条件应与本节衔接。 |
| B-1，`b01-lattice.tex`，安全性直观解释 | 噪声取值的暴力枚举空间呈指数增长，只能作为直观解释，不能代替 LWE/RLWE 的安全性分析，也不排除其他攻击算法。搜索问题与判定问题之间的归约需要相应的参数、分布及代数条件。 |
| B-2，`b02-lwe.tex`，解密后的缩放解释 | 描述“缩放明文后加入噪声”的一句原文使用 `right-shifting`，与同段先前的加密左移描述及所引图示方向不一致，需核对是否为 `left-shifting` 的笔误。 |
| D-1，`d01-tfhe.tex`，噪声增长 | 噪声均值仍为零，并不能说明噪声方差、尾界或失败概率不随运算增加。相关“噪声不增长”的结论需结合方差和正确性界重新检查。 |
| D-1，`d01-tfhe.tex`，自举密钥术语 | 有一处将加密 GLWE 查找表所使用的秘密密钥称为 `bootstrapping key`。应区分底层秘密密钥与由加密秘密密钥信息组成、供自举计算使用的自举密钥。 |
| D-1，`d01-tfhe.tex`，环面表示 | “采用环面浮点表示后无需缩放”的描述较为简化。需要区分数学上的环面表示、明文离散编码、查表区间、噪声容限与有限精度实现，不能直接理解为不再需要编码尺度。 |
| D-2 与 D-6，`d02-bfv.tex`、`d06-scheme-summary.tex` | BFV 可以持续进行乘法的说法必须同时说明噪声约束、参数预算以及必要的自举条件，不能理解为固定参数下无需自举即可无限次正确相乘。D-6 已增加相应译者说明。 |
| D-2，`d02-bfv.tex`，重线性化中的密钥项 | 原文将 `S²` 对应的密钥项称为 `square root of S`，而公式是平方，不是平方根。应以公式及上下文为依据校订这一用词。 |
| D-2，`d02-bfv.tex`，自举中的尺度序列 | 原文一处写为 `p^ε - 1`、`p^ε - 2`，而后文又使用 `p^{ε-1}`。需核对减一、减二应位于指数中还是指数外，并与每步的尺度变化统一。 |
| D-3，`d03-ckks.tex`，多项式求值开销 | 原文存在将多项式求值开销描述为随次数“指数增长”的说法。需要区分多项式次数、乘法次数、乘法深度、参数增长及同态求值总成本，不能笼统等同。 |
| D-3 与 D-5，`d03-ckks.tex`、`d05-rns.tex`，CKKS 自举 | 两章对自举流程及“同态解密”的叙述存在差异，需核对讨论的是哪种具体自举实现，以及模数提升、系数与槽转换、模约减等步骤之间的关系。 |
| D-4，`d04-bgv.tex`，BGV 重缩放讨论 | 比较不同方案时，有一段称噪声尺度因子发生变化，而前文又描述 `Δ` 保持不变。需要核对其中“尺度因子”分别指明文尺度、噪声系数还是其他参数。 |
| D-5，`d05-rns.tex`，`FastBConvEx` 与 `SmallMont` | 原文先描述 `FastBConvEx` 为精确转换，随后又讨论结合 `SmallMont` 降低转换噪声，可能存在将 `FastBConv` 写成 `FastBConvEx` 的名称混用，需结合公式和引用确认。 |

修订这些问题时，应记录涉及的英文段落、公式、所依据的文献，以及中文稿采取的处理方式。不要仅替换一个结论而保留与之矛盾的后续推导。

## 构建兼容性记录

两版全文已在本地 TeX Live 2022 编译。首次远端构建使用的 `ghcr.io/xu-cheng/texlive-full:latest` 为 TeX Live 2026；中文稿在 A-4 的 `\bm{\textsf{ord}_{\mathbb{F}}(a)}` 处报告 `Extended mathchar used as mathchar (65306)`。章节结构和公式比对在该次 CI 中通过，英文 PDF 也已编译完成。

隔离实验中，TeX Live 2026 所对应的 bm v1.2g 配合旧版 xeCJK 3.9.1 可以编译完整 A-4，因此不能将问题仅归因于 bm。新版 xeCJK 包装标准文本字体命令后的数学边界处理是待进一步确认的兼容性因素；本次没有在完整的新环境中证明其具体内部根因，也没有加入依赖宏包内部接口的补丁。

PDF 工作流改用 [TeX Live Action v3](https://github.com/xu-cheng/texlive-action/tree/v3) 的 `texlive_version: '2025'`，固定到官方 TeX Live 2025 历史快照。正文公式保持原样。以后升级工具链时，应先完成两版全文编译和中文页面抽查，再更新这一版本约束。

## 更新与校验流程

1. 记录新的英文基线提交，比较英文主文件、章节文件及文献库的变化。
2. 更新 `zh-CN/` 中的对应章节，并同步 `00-main-zh.tex` 的前言、章节入口或标题变更。
3. 保留稳定的标签及引用键。英文新增或移除章节时，同时调整中文入口和对应文件，避免旧章节意外回退到英文正文。
4. 运行 `python scripts/check_translation.py` 检查中文章节的覆盖与结构；Linux 环境可使用 `python3`。也可执行 `make check`。增加 `--math` 参数可对规范化后的数学片段作额外比对，任何差异都应人工复核；该比对允许正文说明文字的翻译和同一段落内公式出现顺序的调整。
5. 运行 `python scripts/build.py all` 构建两个版本，检查编译日志和 PDF。涉及中文字体、长标题、表格或长公式时，重点检查相应页面的实际布局。
6. 在提交说明中区分翻译修订、排版修订与技术勘误，必要时更新本文件的术语表及待核对问题。

结构校验用于发现遗漏章节、失配的引用或其他源文件结构问题，不能证明翻译语义、公式推导、密码学安全性或版面质量正确。编译与结构校验应与人工审读配合使用。
