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

当前版本完成全部 34 个章节的中文初译，并对上述英文基线进行了逐项学术审校。审校发现的数学、算法、文献及演示代码问题已在中英文稿中同步修订。**逐项审校不等于形式化验证或密码学安全认证。** 具体范围、问题依据、修订、反例和未验证边界见 [学术审校主报告](audit/ACADEMIC_REVIEW.md)，各组详细记录与覆盖清单位于 `audit/`。

英文稿也包含本次勘误，因此当前英文稿和最初上游基线已不再逐字相同。原始内容仍可通过 Git 基线提交查阅；中文和英文当前修订稿之间继续进行结构、引用及数学片段对应检查。

针对首轮遗留问题的[续审](audit/FOLLOWUP_REVIEW.md)进一步补充了实际分布下的条件性安全归约、公开种子模型、同密钥环仿射消息与独立密钥图的区分、一般扩域槽变换及 BFV 逐节点误差预算。CKKS 部分新增含首轮重缩放误差的 Meta-BTS 递推、复扰动下的联合误差界，以及固定 OpenFHE 版本的实际自举复现。首轮报告中把精确除法的坐标漂移重复计入噪声的表述也已更正；未取得的原论文完整证明、具体安全参数与生产实现范围继续单独记录。

## 保留与调整的内容

- 以原书章节结构为基础，保留稳定标签与交叉引用。已确认错误的公式、定义域、噪声界和推导按审校记录同步修正中英文，不能为了逐字对齐继续保留已知错误。
- 保留作者姓名、机构名称等专名；可辨识的算法名称和代码标识，例如 `FastBConvEx`、`Decomp`、`GLWE`，不改成中文标识。
- 共用 `figures/` 中的原始图片。图片文件内部已经嵌入的英文文字仍为英文，中文图注在对应 `.tex` 文件中提供。
- 共用 `z-bibfile.bib`。本次更正 BGV 的错误文献指向，并补充 CKKS、TFHE、HPS 的原始论文出处；既有稳定引用键尽可能保留。
- 教学 Python 源码仍位于 `source code/`，函数及命令行标识使用英文。本次学术审校还修正了确认的算术、尺度、基转换、分解和测试缺陷，详见 `audit/python-review.md`。
- 中文入口使用 XeLaTeX、CTeX 与 Fandol 字体，并将正文输入路径改为 `zh-CN/`。纯排版笔误可在中文稿中修正；例如 A-12 的虚数小节标题后多余的字母 `n` 已去除。
- D6 的 24 个比较主题已统一梳理相位约定、明文域、噪声与尺度条件；原先仅加译者提醒的“无限乘法”问题，现已在英文与中文中正式纠正。

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

## 从初译线索到逐项审校

初译时列出的 14 条疑点已纳入本次完整审校，不再以未处理清单重复保留。审校记录区分确定错误、缺少条件、表述澄清和仍未重新验证的边界。每个问题有稳定编号，读者可以从主报告进入对应组的详细原文位置、推导或反例。

- [基础数学、LWE/RLWE/GLWE 与通用运算](audit/foundations-review.md)
- [TFHE 与 BFV](audit/tfhe-bfv-review.md)
- [CKKS、BGV 与 RNS](audit/ckks-bgv-rns-review.md)
- [前言、24 张方案比较表与引用](audit/summary-review.md)
- [Python 实现与教材语义](audit/python-review.md)

今后若发现新问题，应新增稳定编号并记录独立依据；只有依据充分时才改写技术结论，不能把编译成功或有限参数测试当成一般证明。

## 构建兼容性记录

两版全文已在本地 TeX Live 2022 编译。首次远端构建使用的 `ghcr.io/xu-cheng/texlive-full:latest` 为 TeX Live 2026；中文稿在 A-4 的 `\bm{\textsf{ord}_{\mathbb{F}}(a)}` 处报告 `Extended mathchar used as mathchar (65306)`。章节结构和公式比对在该次 CI 中通过，英文 PDF 也已编译完成。

隔离实验中，TeX Live 2026 所对应的 bm v1.2g 配合旧版 xeCJK 3.9.1 可以编译完整 A-4，因此不能将问题仅归因于 bm。新版 xeCJK 包装标准文本字体命令后的数学边界处理是待进一步确认的兼容性因素；本次没有在完整的新环境中证明其具体内部根因，也没有加入依赖宏包内部接口的补丁。

PDF 工作流改用 [TeX Live Action v3](https://github.com/xu-cheng/texlive-action/tree/v3) 的 `texlive_version: '2025'`，固定到官方 TeX Live 2025 历史快照。这一工具链兼容性变更本身没有改动正文公式；后续学术勘误另行记录。以后升级工具链时，应先完成两版全文编译和中文页面抽查，再更新这一版本约束。

## 更新与校验流程

1. 记录新的英文基线提交，比较英文主文件、章节文件及文献库的变化。
2. 更新 `zh-CN/` 中的对应章节，并同步 `00-main-zh.tex` 的前言、章节入口或标题变更。
3. 保留稳定的标签及引用键。英文新增或移除章节时，同时调整中文入口和对应文件，避免旧章节意外回退到英文正文。
4. 运行 `python scripts/check_translation.py` 检查中文章节的覆盖与结构；Linux 环境可使用 `python3`。也可执行 `make check`。增加 `--math` 参数可对规范化后的数学片段作额外比对，任何差异都应人工复核；该比对允许正文说明文字的翻译和同一段落内公式出现顺序的调整。
5. 运行 `python scripts/build.py all` 构建两个版本，检查编译日志和 PDF。涉及中文字体、长标题、表格或长公式时，重点检查相应页面的实际布局。
6. 在提交说明中区分翻译修订、排版修订与技术勘误，必要时更新本文件的术语表及待核对问题。

结构校验用于发现遗漏章节、失配的引用或其他源文件结构问题，不能证明翻译语义、公式推导、密码学安全性或版面质量正确。编译与结构校验应与人工审读配合使用。

本轮 PDF 集成同时将演示代码链接指向已审校分支，并调整中文页脚间距，使页码完整处于页面内。
