# 前言、方案比较及参考文献审校

范围：原始英文基线 `2a901038078fe054371e53089c86caaaa1112209` 的前言、D6 全部 24 张表、相关引用。所有已确认修订同步应用于中文。表格被重新组织以明确条件，原来的 24 个比较主题均保留；没有将概要表当作完整安全证明。

“高”指影响正确性、算法或核心安全论断；“中”指适用条件、类型或定义域缺失。条目间可能关联同一个根因，不应把条目数当作独立漏洞数。


## SUM-001　前言将近似计算和计算完整性泛化为 FHE 自身保证

**级别：高；状态：已修正。** 位置：00-main.tex / 00-main-zh.tex，前言第 1—4 段。

**原问题。** 原文无条件说解密结果与明文计算相同，并把执行完整性与 FHE 机密性合并描述。

**核验依据。** CKKS 的表示与运算含编码、舍入及求值误差；BFV/BGV 的精确结果属于指定有限明文环。求值者也可以返回 Enc(0) 而不执行指定电路，FHE 机密性本身不排除此行为。

**修订。** 补充噪声与失败概率条件、有限环/近似语义、除法的可逆性或输入区间，以及验证计算需要额外协议。

**来源或复现。** CKKS 原论文；BGV 原论文的正确性/安全性定义；返回错误密文的直接协议反例。

## SUM-002　安全基础与密文表示遗漏环层和评估密钥假设

**级别：中；状态：已修正。** 位置：D6：Hard Problem Basis、Unit Data Type、Ciphertext。

**原问题。** 把 TFHE 完整结构概括为仅 LWE 向量，把其余方案概括为多项式，易将用户接口与内部密文类型混淆。

**核验依据。** TFHE 的盲旋转和电路自举使用 GLWE/GGSW；循环公开加密秘密密钥的信息还涉及相应安全假设。不同秘密密钥/误差分布和参数不能由同一个名称自动获得等强安全性。

**修订。** 分别列出标量接口和环内部结构，说明维数、模数、分布与评估密钥相关假设。

**来源或复现。** Chillotti 博士论文第 3—5 章；Geelen–Vercauteren §3。

## SUM-003　明文素数条件与 CKKS 定义域混淆

**级别：中；状态：已修正。** 位置：D6：Plaintext、Ciphertext、Scaling Factor。

**原问题。** 把 BFV/BGV 的 t 为素数列为通用要求，并对 CKKS 沿用没有定义的 q≫t。

**核验依据。** BFV/BGV 允许更一般的明文模数；常见完整标量批编码另要求素数 t≡1 mod 2n。CKKS 的语义域是复数槽，整数编码进入有限密文环，并不存在同样的明文模数 t。

**修订。** 区分方案、批编码与本书参数选择；CKKS 使用相位大小与精度预算条件。

**来源或复现。** Geelen–Vercauteren §2.2–2.4；CKKS 原论文 §3。

## SUM-004　三元密钥采样集被写成模 3 运算环

**级别：中；状态：已修正。** 位置：D6：Secret Key。

**原问题。** 将三元系数秘密写成 Z3[X]/(X^n+1)，未说明它只是小整数采样再嵌入 Rq。

**核验依据。** 系数 1+1 在整数/大模数环中为 2，在中心化模 3 环中为 −1；两种运算并不相同。

**修订。** 明确 S∈R，系数可采自 {−1,0,1}，再嵌入 Rq；二元/三元只是选择之一。

**来源或复现。** 直接代数；各方案的密钥分布定义。

## SUM-005　同态结果沿用相同 σ，自举或模切换被说成消除/重置噪声

**级别：高；状态：已修正。** 位置：D6：Noise、Addition、Bootstrapping Goal、Noise Management。

**原问题。** 多张表对新鲜密文及运算后密文使用相同 σ，并将“均值仍为零”“重置”“持续增长”当作无条件结论。

**核验依据。** 独立 e1,e2∈{−1,1} 均值为零，但 Var(e1+e2)=2；同一样本加自身的方差为 4。固定 q=32、Δ=4，误差 1 的零明文重复相加五次即误解为 1。模切换还降低模数并产生舍入误差。

**修订。** 改为完整相位误差与概率预算；自举输出仍含新噪声；CKKS 既有数值误差通常不会被清除，误差也不是对所有电路单调递增。

**来源或复现。** check_summary.py；Chillotti 第 3—5 章误差分析；BGV §3；CKKS 自举 §2–3。

## SUM-006　BFV 解密把除以 floor(q/t) 当作一般规范式，并无条件去掉 mod q

**级别：高；状态：已修正。** 位置：D6：Decryption Formula；与 D2 对应。

**原问题。** 原式混用无符号与中心化代表元，且忽略 q 不被 t 整除时的余数。

**核验依据。** 令 q=31,t=8,Δ=3,m=0,e=−1。旧式使用相位 30，round(30/3) mod 8=2；规范式 round(8·30/31) mod 8=0。除以 Δ 在一致中心代表元及相应界内可以成立，不应声称它总是错误。

**修订。** 采用 round((t/q)[B+AS]q) mod t；令 r=q−tΔ，给出充分条件 ||tE−rM||∞<q/2。

**来源或复现。** check_summary.py；FV2012 §3–4；Geelen–Vercauteren §2.2。

## SUM-007　BGV 正确性界漏绝对值、明文项与中心化范围

**级别：高；状态：已修正。** 位置：D6：Decryption Formula。

**原问题。** 只要求 tE<q。

**核验依据。** q=11,t=5,m=1,e=2 满足 10<11，却有 [m+te]q=0，解密为 0≠1。

**修订。** 使用整个中心相位的充分界 ||M+tE||∞<q/2，并区分模数回绕的影响。

**来源或复现。** check_summary.py；BGV 相位恒等式。

## SUM-008　模数链乘积上界和 BGV 同余条件错误

**级别：中；状态：已修正。** 位置：D6：Ciphertext Modulus。

**原问题。** 定义 qi 时乘积上界误写为 l；所有 wi 同余并不保证链中 qi 同余。

**核验依据。** 因子 7、17、37 均模 5 余 2，但 q0=7 模 5 余 2，而 q1=119 模 5 余 4。

**修订。** 改为 qi=∏j=0..i wj；简单 BGV 约定取每个 wj≡1 mod t，更一般链须跟踪校正因子。

**来源或复现。** check_summary.py；BGV/HElib 的 residue-preserving modulus-switch 条件。

## SUM-009　CKKS 把近似尺度匹配当精确等式，并漏舍入误差

**级别：高；状态：已修正。** 位置：D6：Scaling、Decrypt、AddPlain、MultPlain、MultCipher。

**原问题。** 用 wl≈Δ 推成除以 wl 等价于除以 Δ，输出尺度恒为 Δ；某些表将未取整的实多项式直接当环元素。

**核验依据。** Δ=100、wl=97 时，输出尺度为 10000/97≈103.0928，不是 100。分量舍入带来 ρB+ρAS，绝对值界取决于秘密系数范数。

**修订。** 跟踪 Δout=Δ1Δ2/wl；使用整数编码，并把编码、乘法、重线性化、重缩放误差计入预算。

**来源或复现。** check_summary.py / check_python.py；CKKS 原论文及自举论文的 rescale lemma。

## SUM-010　LWE→GSW 转换误称普通可编程自举

**级别：高；状态：已修正。** 位置：D6：Ciphertext-to-Ciphertext Multiplication，TFHE 行。

**原问题。** 将 LWE 密文转换成 GSW/GGSW 表示直接标为 Programmable Bootstrapping。

**核验依据。** 普通 PBS 的输出仍是标量 LWE；电路自举还组合私有函数密钥切换等步骤，并有独立参数/噪声分析。

**修订。** 明确 circuit bootstrapping，并保留外积所需的类型和误差条件。

**来源或复现。** Chillotti 博士论文 §5.2、Algorithm 12；TFHE 原论文。

## SUM-011　BFV 模数提升被解释成保持原相位的小噪声加密

**级别：高；状态：已修正。** 位置：D6：Ciphertext-to-Ciphertext Multiplication，BFV 行。

**原问题。** 将相同 (A,B) 从 q 解释到 Q 后直接写成同一 Enc(ΔM)，遗漏 qK。

**核验依据。** q=17,Δ=4,a=8,b=13,s=1：原模数下相位为 4，大模数 Q=68 下相位为 21=4+17。

**修订。** 摘要改为规范 FV 的整数负循环乘积、t/q 缩放舍入和重线性化；正文 1/Δ 教学变体与规范算法分开，须保留额外误差项。

**来源或复现。** check_summary.py；FV2012 §4 直接讨论两种缩放的区别。

## SUM-012　BGV 模切换不能舍入到 t 的倍数

**级别：高；状态：已修正。** 位置：D6：Ciphertext-to-Ciphertext Multiplication，BGV 行。

**原问题。** 写成除以 Δ=t，然后舍入到最接近的 t 倍数。

**核验依据。** 任何输出若成为 t 的倍数，其明文剩余类都是 0；明文 1 的标量例子已足以推翻该规则。

**修订。** 使用 q′/q 和剩余类校正；明确适用的 q′≡q mod t 或校正因子条件。

**来源或复现。** check_summary.py；BGV 原论文 modulus reduction；D4/D5 的精确公式。

## SUM-013　“无自举无限乘法”与链长度等于总乘法次数

**级别：高；状态：已修正。** 位置：D6：Maximum Possible Multiplications。

**原问题。** BFV 被标成 Unlimited；TFHE 的“无自举”行却引用 PBS；CKKS/BGV 将链长度当总乘法次数。

**核验依据。** 噪声预算受固定参数约束；一个很宽但深度很小的电路可含大量并行乘法门，链长通常约束层级消耗或深度，不是门总数。

**修订。** 重写为各方案的有限计算预算；把自举及其有效参数条件单独说明。

**来源或复现。** BGV 原论文摘要及 leveled FHE 定义；FV2012 噪声界；check_summary.py。

## SUM-014　密钥切换摘要缺少密文类型、误差和分解余量

**级别：中；状态：已修正。** 位置：D6：Key Switching。

**原问题。** 标量 B 直接加到密文的记法未解释，评估密钥缩放和新的 σ 也未区分。

**核验依据。** 若 A=Σdigi，且 Ki 在新密钥下相位为 giS+εi，则 (0,B)+ΣdiKi 的相位是 B+AS+Σdiεi；近似分解还要另计残差。

**修订。** 用这一相位恒等式明确每项类型和新噪声，BGV 的评估密钥误差必须带 t 因子。

**来源或复现。** 直接相位推导；C5 与各方案密钥切换定义。

## SUM-015　ModDrop 被无条件解释成保持同一明文

**级别：高；状态：已修正。** 位置：D6：Modulus Drop。

**原问题。** 合并 CKKS/BGV 的相位公式，未约束减小模数后的回绕。

**核验依据。** q=77,q′=11,t=5,m=3,e=2：原中心相位 13 解得 3，模数丢弃后相位 2 解得 2。

**修订。** 分别说明 CKKS 尺度保持与 BGV 明文保持的无回绕条件。

**来源或复现。** check_summary.py；模数约减的直接计算。

## SUM-016　TFHE 标量被说成完全不需要编码

**级别：中；状态：已修正。** 位置：D6：Encoding and Decoding。

**原问题。** 将没有 SIMD 变换混同于没有消息编码。

**核验依据。** 标量仍需嵌入环面并保留解码间距；PBS LUT 还需输入区间、填充和误差裕量。

**修订。** 明确标量编码、批编码、CKKS 典范嵌入是不同层次。

**来源或复现。** Chillotti 第 3 章、第 5 章；Marc Joye 环面综述。

## SUM-017　5^h 自同构不是贯穿 n 个标量槽的单个旋转

**级别：高；状态：已修正。** 位置：D6：Input Slot Rotation；关联 D2/D4。

**原问题。** 把 CKKS 的 n/2 复数槽与 BFV/BGV 的 n 个标量槽使用同一个整圈旋转解释。

**核验依据。** n=8 时，5 的幂模 16 只有 {1,5,9,13}；其相反数构成另一条不相交轨道。

**修订。** 说明两行各自循环和密钥切换；一般排列或跨行矩阵运算需要额外自同构/掩码。

**来源或复现。** check_summary.py；Geelen–Vercauteren §2.4 的超立方体与旋转。

## SUM-018　TFHE 自举摘要的符号、索引、输出和提取密钥不一致

**级别：高；状态：已修正。** 位置：D6：Bootstrapping Details，TFHE 行。

**原问题。** 前表使用 b+a·s，却套用适合 b−a·s 的旋转符号；还混用 ai 与 s(i−1)，把一般 LUT 输出写成 m，并把提取密钥当输入密钥。

**核验依据。** 加号相位下必须合成 X^(−b−Σaisi)；例如 a=1,b=3,s=1 时，−b+a·s≠−(b+a·s)。模切换误差还含所有公开系数舍入项。

**修订。** D6 统一加号相位，明确与 D1 减号约定的转换；注明输出尺度、f(m)、GLWE 派生提取密钥及可选密钥切换；以 F(j)=coeff_0(VX^(−j)) 表达 LUT 的反周期和输入域条件，而不是普通多项式求值。

**来源或复现。** check_summary.py；Chillotti §4.1.2–4.1.3、§5.1。

## SUM-019　BFV 自举的内积常数、线性变换和数位操作不严谨

**级别：高；状态：已修正。** 位置：D6：Bootstrapping Details，BFV 行。

**原问题。** 同态内积使用加密的 Δ′S 却直接加未编码 B；把 CoeffToSlot 当普通单次多项式乘法；结束处无理由把 Δ′ 换为 Δ。

**核验依据。** 若秘密项采用新尺度 Δ′，公开常数也需以 Δ′B 编码。槽变换是由自同构和明文乘法组成的线性映射，扩域槽数由 ord(2n)(p) 决定。精确除 p 涉及明文模数或尺度变化。

**修订。** 将错误的逐步等式替换为带适用条件的规范流程概要，引用 Geelen–Vercauteren 的完整推导，不宣称任意参数都能自举。CRT 槽路线要求 gcd(p,2n)=1；本书二幂分圆环下 p 为奇数，二进制数位偏移恒等式不能直接赋予该环完整二进制自举。

**来源或复现。** Geelen–Vercauteren §3.2 Eq.(9)、§3.3–3.4、§6；正文 D2 同步修正。

## SUM-020　CKKS 正弦近似被写成精确模约减

**级别：高；状态：已修正。** 位置：D6：Bootstrapping Details，CKKS 行。

**原问题。** 对 ΔM+E+Kq0 求近似正弦后，原文直接给出精确 ΔM+E。

**核验依据。** g(x)=q0 sin(2πx/q0)/(2π)，在 r=q0/4 时 g(r)=q0/(2π)≠r；误差界为 (2π)^2|r|^3/(6q0^2)，另有多项式近似和同态运算误差。

**修订。** 改为 EvalMod 的有界域近似，区分线性槽变换与非线性模约减，保留残差 ε。

**来源或复现。** check_summary.py；Cheon 等，Bootstrapping for Approximate HE，§3.1。

## SUM-021　BGV 自举精确除法与明文模数变化被省略

**级别：高；状态：已修正。** 位置：D6：Bootstrapping Details，BGV 行。

**原问题。** 把一次 ModRaise 当作已经完成同态解密，普通 floor 处理负数位，并将除 p 简写为在同一明文环取逆。

**核验依据。** p 在 Z/(p^j) 中不可逆；若已证明输入可整除 p，精确除法后的明文模数应降为 p^(j−1)。例如 6 与 15 在模 9 下相同，除 3 后在模 9 下不同，在模 3 下才相同。

**修订。** 改为同态内积、槽变换、平衡数位提取及明确除法不变量的概要；移除不受支持的无条件等式。

**来源或复现。** check_summary.py；Geelen–Vercauteren §2.2、§3.2–3.4、§6；D4。

## SUM-022　BGV 引文键误指向另一位作者的同名论文

**级别：高；状态：已修正。** 位置：z-bibfile.bib：bgv-modswitch2。

**原问题。** 正文链接为 2011/277，但 BibTeX 键绑定 Masahiro Yagisawa 的 2015/474。

**核验依据。** 2011/277 的作者是 Zvika Brakerski、Craig Gentry、Vinod Vaikuntanathan，题名含 (Leveled)；两篇并非同一论文。

**修订。** 更正作者、标题、年份、ePrint 编号和 URL，保留引用键以维持交叉引用。

**来源或复现。** 已读取 BGV2011 作者公开全文和 ePrint 元数据。

## 可读的一手全文与访问边界

- Brakerski、Gentry、Vaikuntanathan，* (Leveled) Fully Homomorphic Encryption without Bootstrapping*，2011/277：[作者机构存档](https://people.csail.mit.edu/vinodv/6892-Fall2013/BGV.pdf)。
- Cheon 等，*Bootstrapping for Approximate Homomorphic Encryption*，EUROCRYPT 2018：[作者全文](https://yongsoosong.github.io/files/papers/HEAAN_boot.pdf)。本组核对 §2–3 的重缩放与正弦误差。
- Geelen、Vercauteren，*Bootstrapping for BGV and BFV Revisited*：[机构接受稿](https://imec-publications.be/bitstreams/5e8ee1f6-f7f1-4a12-983b-52a6677361fb/download)，[正式 DOI](https://doi.org/10.1007/s00145-023-09454-6)。核对 §2、§3、§6；接受稿不宣称等同于出版后所有修订。
- Chillotti，博士论文 *Towards efficient and secure Fully Homomorphic Encryption and cloud computing*，2018：[作者全文](https://ilachill.github.io/papers/these_Ilaria_Chillotti_wo_acknowl.pdf)。核对 §4.1、§5.1–5.2。
- Fan、Vercauteren，*Somewhat Practical Fully Homomorphic Encryption*：[规范记录](https://eprint.iacr.org/2012/144)，[全文镜像](https://scispace.com/pdf/somewhat-practical-fully-homomorphic-encryption-twy4lsabil.pdf)。直接 ePrint PDF 访问被服务器拒绝；仅在核到完整镜像后才引用 §3–4 的具体推导。

本组直接推导的有限反例见 `check_summary.py`，由标准库有理数运算和有限穷举复现。复杂自举的完整性能和安全参数没有重新实现或认证。
