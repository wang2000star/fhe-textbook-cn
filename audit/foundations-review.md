# A、B、C 基础章节逐项学术审校

## 范围、基线和结论的含义

本报告审查 `a01`–`a16`、`b01`–`b06`、`c01`–`c05`，共 27 个英文源文件及其 `zh-CN/` 对应文件。英文原版基线为提交 `2a901038078fe054371e53089c86caaaa1112209`；本轮开始前的译本/编译版本为 `330b96f38f2d3b6982e4b30f3943ff428fd47a0c`。已用 Git 比较确认这 27 个英文文件在两提交间没有差异。这是对英文原文的独立数学审查；中英文公式相同不构成正确性证据。下列确定错误已在两种语言的同一位置同步修正。A03、A10 经核查未发现需要本轮修改的确定错误，保留原文。

审查逐段阅读了定义、带标题段落、定理框、证明及主要算法推导，再用域/环条件、整数提升、类型与维数、确定性噪声界检查结论。`foundations-coverage.json` 逐条记录每个 `subsection`、`subsubsection`、`para`，另列章节整体与定理记录：共 171 条，包含 27 个章节、114 个当前标题段落和 30 个定理框；原基线有 113 个标题段落，另一个是本轮新增的密钥切换噪声说明。这样也覆盖没有小标题的正文。没有把抓取到目录等同于完成审查。一个覆盖项标记“已核查”，仅表示已检查该项陈述及所列条件，不表示已证明某个完整密码系统的安全性。

本轮发现的主要问题涉及：不成立的分解等式、未定义的商环求值、转置方向错误、缩放舍入的错误等价关系、无条件安全性断言、非整除尺度的消息溢出、遗漏卷积/舍入/截断噪声，以及不能直接实现的密钥切换表达式。尤其 B04 将一个仅有三种随机因子的标量构造推广为通用 LWE 公钥加密，是可直接攻击的安全论证错误。

`check_foundations.py` 使用 Python 标准库重现本报告的反例和有限代数检查。已运行的 17 组检查包含 1,449 个整数缩放同余样例、105 个 CRT 往返值、40 组负循环 NTT 乘法，以及公钥随机因子枚举、模数切换和密钥切换反例。这些数字描述实际运行的有限检查，不能替代后面的符号推导，更不能证明密码安全性。执行方法：

```sh
python3 audit/check_foundations.py
python3 audit/check_foundations.py --json
```

判定分为“确定错误并修正”“缺必要条件并修正”“证明缺口并补全”“术语/类型问题并修正”“条件性结论，待进一步安全证明”。严重程度衡量该问题是否改变算法输出、数学结论或安全论证，不依据排版改动大小。

## 统一的数学约定

本报告用 $R(x)=\lfloor x+1/2\rfloor$ 表示最近整数舍入，半整数向正无穷方向取整；用中心代表元解释模 $q$ 的相位。文中采用“消息在高位”的编码 $\Delta m+e\pmod q$，在没有额外说明时要求 $t\mid q$、$\Delta=q/t$。如果 $t\nmid q$，不能直接复用这一正确性证明。

整数/多项式误差均先选整数系数提升。负循环乘法在 $\mathbb Z[X]/(X^n+1)$ 中满足

$$
\|AB\|_\infty\le \|A\|_1\|B\|_\infty
\le n\|A\|_\infty\|B\|_\infty.
$$

这是逐项展开后使用三角不等式的确定性界，不需要各系数独立、均值为零或服从高斯分布。对于离散高斯误差，有限误差界描述一个事件；严格讨论解密失败概率时，还须给出尾界、样本数和联合失败概率。

本书 A06、B05、B06、C03、C05 保留递减 gadget $g_i=q/\beta^i$。其精确全长度版本采用 $q=\beta^l$；截断版本保留残差。对一般整数模数，可另行定义递增整数 gadget $1,\beta,\ldots$，但必须同步更换位分解和评估密钥权重。不能混用两种定义。

## 逐项发现与修正

### FND-001：模代表元与整数乘法群的边界

- **位置**：`a01-modulo.tex`，`subsec:modulo-overview`、`subsec:modulo-centered`；`a02-group.tex`，`subsec:group-ex`。
- **判断**：确定的边界/定义错误，低严重度，已双语修正。
- **原文问题**：任意整数转换到一个代表元区间时，措辞只提加减一次 $q$；整数乘法不构成群的解释将 $a^{-1}=1/a$ 当成也适用于 $a=0$。
- **核查**：例如 $101\pmod7=3$，须减去 $14q$，一次加减不够。零在整数乘法下没有逆元；非零整数的倒数仍为整数当且仅当该整数是 $\pm1$。
- **修正**：明确 $q\ge2$，取模使用加减适当的整数倍 $q$；把零与非零元素的逆元情况分开。顺带核查 A01 的加、减、乘同余和消去律：有 $ac\equiv bc\pmod q$ 时一般只能推出 $a\equiv b\pmod{q/\gcd(c,q)}$，基线该处已经正确，本轮未再次“修正”。
- **复现**：`check_modular_domains`。
- **一手/标准资料**：[Richard Earl, Rings and Modules，环与单位的定义](https://www.maths.ox.ac.uk/system/files/attachments/lectures%20rings%20and%20modules.pdf)。

### FND-002：元素阶的定义域与整除推导

- **位置**：`a04-order.tex`，`subsec:order-def`、`subsec:order-theorem`，阶性质 II 的证明。
- **判断**：定义域和证明措辞有误，中严重度，已修正。
- **原文问题**：定义只围绕有限域，后文却直接用于 $\mathbb C^\times$；证明把指数 $mn$ 是阶的倍数写成了对元素本身取倍数。
- **推导**：阶是群元素的性质。若 $a$ 的有限阶是 $k$，则 $a^{mn}=1\iff k\mid mn$，从而 $\operatorname{ord}(a^n)=k/\gcd(k,n)$。复数单位根有有限阶，但一般非零复数（例如 $2$）可以有无限阶；不能宣称所有复数元素都有所定义的有限整数阶。
- **修正**：定义扩展到群中有有限阶的元素，保留有限域为特例；证明明确使用 $k\mid mn$。费马小定理保留“素数模数”和“非零模元素”条件。
- **一手/标准资料**：[Jim Belk, Fields and Cyclotomic Polynomials](https://e.math.cornell.edu/people/belk/numbertheory/CyclotomicPolynomials.pdf)；[Keith Conrad, Finite Fields](https://kconrad.math.uconn.edu/blurbs/galoistheory/finitefields.pdf)。

### FND-003：商环求值必须同时尊重系数模数和多项式模数

- **位置**：`a05-polynomial-ring.tex`，`subsubsec:polynomial-ring-discuss` 下 `Polynomial Evaluation`；关联 `a09` 和 `a11`。
- **判断**：确定的代数错误，高严重度，已修正。
- **原文问题**：由模 $p$、模 $X^n+1$ 的多项式同余，直接推到在没有指定特征的根处取值相等；同时把 $X^n+1$ 的根称作 $n$ 次单位根。
- **推导/反例**：若整数提升满足 $f-g=Q(X)(X^n+1)+pH(X)$，在复根 $z$ 处求值得 $f(z)-g(z)=pH(z)$，一般不为零。在特征 $p$ 的目标代数中并取 $z^n+1=0$，两个项才同时消失。原小节示例中的整数多项式在 $0$ 处分别取值 $10$ 和 $0$，也说明“同余代表元”不是普通整数多项式恒等。特征不为 $2$ 时，$z^n=-1$ 给出 $z^{2n}=1$；若 $n$ 为二幂，才可进一步说这些根全部是本原 $2n$ 次单位根。
- **修正**：明确在 $\mathbb F_p$ 或其扩域求值，先约化系数；改正根的阶。未把任意复数求值伪装成有限域环同态。
- **一手/标准资料**：[Earl，商环同态与系数域](https://www.maths.ox.ac.uk/system/files/attachments/lectures%20rings%20and%20modules.pdf)；[Conrad，有限域](https://kconrad.math.uconn.edu/blurbs/galoistheory/finitefields.pdf)。

### FND-004：多项式运算的次数上界和旋转范围

- **位置**：`a05-polynomial-ring.tex`，`tab:ring-comparison`、`subsec:coeff-rotation`。
- **判断**：索引/前提错误，中严重度，已修正。
- **原式 → 修正**：输入分别有 $d_a,d_b$ 个系数，即次数至多 $d_a-1,d_b-1$ 时，加法最高索引应为 $\max(d_a,d_b)-1$，乘法最高索引应为 $d_a+d_b-2$。表中原上界各多一项。补充不存在的系数按零处理，乘积随后约减。
- **旋转核查**：原分段式描述 $0\le h<n$ 的负循环旋转；若把它用于任意整数 $h$，索引区间失效。已给这一范围，并说明 $X^n=-1$、$X^{2n}=1$ 使一般移位可模 $2n$ 处理；负移位通过 $X^{-1}=-X^{n-1}$ 定义。
- **一手/标准资料**：[Earl，多项式系数卷积及商环](https://www.maths.ox.ac.uk/system/files/attachments/lectures%20rings%20and%20modules.pdf)。

### FND-005：$\beta^l\mid q$ 不足以保证精确 gadget 分解

- **位置**：`a06-decomp.tex`，`subsec:number-decomp`、`subsec:poly-decomp`；联动 B05、C03、C05。
- **判断**：确定的等式错误，高严重度，已修正。
- **原式**：对任意 $\gamma\in\mathbb Z_q$，用 $l$ 个 $0\le\gamma_i<\beta$ 的数字断言 $\gamma=\sum_{i=1}^l\gamma_iq/\beta^i$，但只给整除或位数上界条件。
- **反例与证明**：取 $q=16,\beta=2,l=2$，权重为 $8,4$，只能得到 $0,4,8,12$，不能表示 $1$。一般令 $d=q/\beta^l\in\mathbb Z$，每个权重和均为 $d$ 的倍数。要表示全部 $q$ 个剩余类，必须 $d=1$，即 $q=\beta^l$。此时普通 radix-$\beta$ 展开给出唯一的全长度分解。
- **修正**：将精确任意剩余类的章节限定为 $q=\beta^l$；只有截断/近似版本继续允许 $\beta^l\mid q$。移位实现另要求 $q,\beta$ 是二的幂，不能把任意进制的除法称为位移。
- **复现**：`check_descending_gadget`。
- **一手来源**：[Chillotti–Gama–Georgieva–Izabachène, TFHE，Definition 3.6、Lemma 3.7 的 gadget 精度参数](https://imec-publications.be/bitstreams/92b4e945-9e22-4bc6-899c-c0baa9f7b4e9/download)。其环面定义经乘以 $q$ 后，与本报告的整数条件逐项对应；并非该论文宣称所有整数模数满足原等式。

### FND-006：截断分解必须保留环绕、残差和整数权重条件

- **位置**：`a06-decomp.tex`，`subsec:approx-decomp`、`subsec:gadget-decomposition`。
- **判断**：缺必要条件，高严重度，已修正。
- **推导**：当 $d=q/\beta^l\in\mathbb Z$ 时，将 $\gamma$ 舍入到最近的 $d$ 倍数，随后取模 $q$。因此应写 $\gamma\equiv\sum_i\gamma_i g_i+\rho\pmod q$，并选残差提升使 $|\rho|\le d/2$。例如 $q=16,d=4,\gamma=15$，最近倍数是 $16\equiv0$，残差为 $-1$，而不是把无法表示的整数 $16$ 强塞进数字向量。
- **修正**：明确上述同余和残差；如果 $\beta^l\nmid q$，递减权重未必是整数，不能直接作为本书整数环上的 gadget。另给可供一般模数使用的递增整数权重 $g_i=\beta^{i-1}$、$l=\lceil\log_\beta q\rceil$，但不静默替换后续已有约定。
- **复现**：`check_descending_gadget`。
- **一手来源**：[TFHE，Definition 3.6、Lemma 3.7 的近似分解定义与精度界](https://imec-publications.be/bitstreams/92b4e945-9e22-4bc6-899c-c0baa9f7b4e9/download)。

### FND-007：单位根计数的 $n=1$、$k=0$ 边界

- **位置**：`a07-roots-of-unity.tex`，`subsec:roots-theorem` 的定理 IV、V。
- **判断**：边界条件遗漏，低严重度，已修正。
- **原文问题**：将 $\phi(n)$ 一律解释为 $1,\ldots,n-1$ 中互素整数的个数，漏掉 $\phi(1)=1$；证明原幂阶公式只讨论 $k\ge1$，陈述却允许 $k=0$。
- **推导**：$\omega^0=1$ 的阶为 $1=n/\gcd(n,0)$，只有 $n=1$ 时为本原 $n$ 次根。用 $1\le k\le n$ 统一定义欧拉函数，或单列 $n=1$，均可消除边界错误。其余根集合分拆和本原根判据经阶的整除关系核查成立。
- **修正**：补上两处边界。没有改变 $n>1$ 的常用结论。
- **一手/标准资料**：[Belk，单位根与分圆多项式](https://e.math.cornell.edu/people/belk/numbertheory/CyclotomicPolynomials.pdf)。

### FND-008：分圆多项式整数系数的原证明不成立

- **位置**：`a08-cyclotomic-polynomial.tex`，`subsec:cyclotomic-theorem`，定理 III。
- **判断**：结论正确、原证明有实质缺口，中严重度，已补全。
- **原论证**：把乘积 $X^n-1$ 的系数为整数、首项系数为 $1$，当成每个因子的系数都是整数的充分理由。一般有理因子不能据此推出整数性，例如 $2(X-1)\cdot (X+1)/2=X^2-1$。
- **正确推导**：对 $n$ 强归纳，令 $D=\prod_{d\mid n,d<n}\Phi_d\in\mathbb Z[X]$，且 $D$ 首一。用首一多项式在 $\mathbb Z[X]$ 中长除 $X^n-1=DQ+R$，得到整数 $Q,R$。另一方面在 $\mathbb C[X]$ 中根分解已知 $X^n-1=D\Phi_n$。除法唯一性给 $R=0,Q=\Phi_n$，故 $\Phi_n\in\mathbb Z[X]$。
- **修正**：以这段归纳除法证明替换原首项系数论证；结论不变。
- **一手/标准资料**：[Belk，分圆多项式](https://e.math.cornell.edu/people/belk/numbertheory/CyclotomicPolynomials.pdf)；[Earl，首一除法与整数多项式](https://www.maths.ox.ac.uk/system/files/attachments/lectures%20rings%20and%20modules.pdf)。

### FND-009：$\Phi_{nk}(X)=\Phi_n(X^k)$ 的根映射不是双射

- **位置**：`a08-cyclotomic-polynomial.tex`，`subsec:cyclotomic-theorem`，定理 IV，条件 $k\mid n$。
- **判断**：结论在所给条件下正确，证明错误，中严重度，已补全。
- **推导**：若 $z^k$ 的阶为 $n$，设 $d=\operatorname{ord}(z)$，则 $d/\gcd(d,k)=n$。因为 $k\mid n$，可逐素数指数比较得到 $d=nk$。反向由阶公式立即成立。因此两多项式的根集合相同。原文将 $z\mapsto z^k$ 说成一一对应不成立：例如 $n=k=2$ 时 $i,-i$ 都映到 $-1$。实际每个目标根有 $k$ 个原像。
- **修正**：用阶等价、复数特征零下的单根性质和首一性推出多项式相等。没有把错误的根双射继续用作次数证明。
- **复现**：`check_cyclotomic_domains` 中 $i,-i$ 的像。
- **一手/标准资料**：[Belk，单位根的阶与分圆分解](https://e.math.cornell.edu/people/belk/numbertheory/CyclotomicPolynomials.pdf)。

### FND-010：有限域中的分圆根需要拆分域和特征条件

- **位置**：`a09-cyclotomic-polynomial-integer-ring.tex`，`sec:cyclotomic-polynomial-integer-ring`，整章与比较表。
- **判断**：缺必要条件，高严重度，已修正。
- **反例**：$\Phi_4=X^2+1$ 在 $\mathbb F_3$ 没有根，不能把其两个根写成 $\mathbb F_3$ 元素；$\Phi_3=X^2+X+1=(X-1)^2\pmod3$，其根阶为 $1$，也不能说“分圆多项式的根必为相应本原根”。
- **修正条件**：表中在 $\mathbb F_p$ 完全分解的版本要求素数 $p$、$\mu\ge2$、$\mu\mid p-1$，并将整数分圆多项式的系数约化模 $p$。若仅有 $p\nmid\mu$，应在适当有限扩域中讨论，根仍可区分；若 $p\mid\mu$，会出现重根/阶退化。明确列出这三个情形。
- **复现**：`check_cyclotomic_domains`。
- **一手/标准资料**：[Conrad, Finite Fields，有限域乘法群与扩域](https://kconrad.math.uconn.edu/blurbs/galoistheory/finitefields.pdf)。

### FND-011：投影长度、非正交投影和基坐标混淆

- **位置**：`a11-matrix.tex`，`subsec:projection`，四个投影/基段落及定理框。
- **判断**：确定的线性代数错误，中严重度，已修正。
- **原式 → 修正**：投影长度 $\|a\|\cos\theta$ → $\|a\||\cos\theta|$；前者是有符号标量分量。取 $a=-b\ne0$ 即得到负值与范数非负的矛盾。
- **非正交情形**：投影不要求所用基彼此正交。若 $Q$ 的列满秩并张成子空间，则投影矩阵为 $Q(Q^TQ)^{-1}Q^T$。若基张成全空间，投影为恒等。只有“各方向单独投影后求和”要求正交基。
- **基坐标**：原文将基向量存成矩阵 $P$ 的行，再把 $Pv$ 说成对应坐标；正确关系是 $v=P^Tc$，故 $c=(P^T)^{-1}v$。例 $P=\bigl(\begin{smallmatrix}1&0\\1&1\end{smallmatrix}\bigr),v=(1,1)^T$，正确坐标为 $(0,1)^T$，但 $Pv=(1,2)^T$。
- **修正**：给出非零方向和实标量前提，统一投影定义、正文与定理框；把线投影和子空间投影视为正交投影的两个情形。
- **复现**：`check_projection_and_modules`。
- **一手/标准资料**：[MIT 18.06SC, Projections onto Subspaces](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/00e9c8f0eafedeab21a3d079a17ed3d8_MIT18_06SCF11_Ses2.2sum.pdf)。

### FND-012：整数多项式商环是模，不是以整数为域的向量空间

- **位置**：`a11-matrix.tex`，`subsec:polynomial-ring-basis`。
- **判断**：结构类型和线性无关判据错误，中严重度，已修正。
- **推导/反例**：$\mathbb Z$ 不是域，$\mathbb Z[X]/(X^n+1)$ 是秩 $n$ 的自由 $\mathbb Z$-模。线性无关必须是 $\sum z_if_i=0\Rightarrow z_i=0$ 对全部系数成立；“任何一个元素都不能由其余元素线性表示”在一般模上不足够。例如整数模中的 $2,3$ 不能互相表示为对方的整数倍，但 $3\cdot2-2\cdot3=0$，仍相关。
- **修正**：用自由模、唯一整数线性组合和正确的零关系定义替换原表述。若系数域改为 $\mathbb F_p$、$\mathbb R$ 或 $\mathbb C$，才能按对应域使用向量空间术语。
- **复现**：`check_projection_and_modules`。
- **一手/标准资料**：[Earl，Definition 173、Examples 174–176，自由模与基](https://www.maths.ox.ac.uk/system/files/attachments/lectures%20rings%20and%20modules.pdf)。

### FND-013：求值双射不自动成为指定商环的环同构

- **位置**：`a11-matrix.tex`，`subsec:poly-vector-transformation`、`subsubsec:poly-vector-transformation-modulus`，对应总结定理。
- **判断**：缺必要条件及阶证明错误，高严重度，已修正。
- **推导**：在域中选 $n$ 个任意互异节点，对次数小于 $n$ 的代表元确实得到线性双射；要保持 $\mathbb F_t[X]/(X^n+1)$ 的乘法，还要求全部节点为模多项式的根。在节点 $0$ 上，$X^2=-1$ 的商环关系就不能被求值保持。复合模数下，“互异”还不保证拉格朗日分母可逆。
- **修正条件**：素数 $t$、$2n\mid t-1$、$n$ 为二幂；固定域中 $X^n+1$ 的 $n$ 个互异根。$g^{(t-1)/(2n)}$ 的阶用生成元最小正指数证明。由 $\omega^{2n}=1$、$\omega^n=-1$ 推阶为 $2n$ 时，明确使用二幂的每个真因子都整除 $n$；对一般 $n$ 此推论不成立。还修正把 $\operatorname{ord}(\omega)$ 错写成 $\operatorname{ord}(c)$ 的一处引用。
- **复现**：`check_evaluation_isomorphism`。
- **一手/标准资料**：[Conrad, Finite Fields](https://kconrad.math.uconn.edu/blurbs/galoistheory/finitefields.pdf)；[Earl，商环同态](https://www.maths.ox.ac.uk/system/files/attachments/lectures%20rings%20and%20modules.pdf)。

### FND-014：共轭对称空间是实代数，满射性须单独证明

- **位置**：`a11-matrix.tex`，`subsec:poly-vector-transformation-complex`、两个复数同构小节、`subsec:poly-vector-basis-transfer`。
- **判断**：标量域/边界缺失和证明缺口，中严重度，已修正。
- **核查**：映射 $\phi:\mathbb C^{n/2}\to\hat{\mathbb C}^n$ 附加逆序共轭，是实向量空间及实代数同构；通常不是复线性，因为乘 $i$ 破坏对称性。“$cv$ 对称当且仅当 $c\in\mathbb R$”要加 $v\ne0$，零向量是例外。维数 $n$ 是实维数。
- **满射证明**：对任意共轭对称目标值，用复系数拉格朗日插值获得唯一次数小于 $n$ 的多项式。节点及值都按逆序共轭配对，故系数取共轭的多项式给出相同值；唯一性迫使所有系数为实数。原文仅论证两个实多项式不会映为同一向量，不足以证明满射。
- **修正**：明确 $n=2^r,r\ge1$ 以保障 $n/2$ 整数、实标量域、非零例外、上述满射证明；基转换改为线性同构保持线性无关与张成的明确证明。
- **复现**：`check_evaluation_isomorphism` 检查实系数求值的对称性及乘 $i$ 的反例。满射性依赖书面唯一性证明，不由这一有限例子替代。
- **一手/标准资料**：[Earl，向量空间、模与线性同构](https://www.maths.ox.ac.uk/system/files/attachments/lectures%20rings%20and%20modules.pdf)；[Lyubashevsky–Peikert–Regev 的数域嵌入与共轭坐标](https://web.eecs.umich.edu/~cpeikert/pubs/ideal-lwe.pdf)。

### FND-015：Vandermonde 的节点顺序、转置和几何和例外

- **位置**：`a12-euler.tex`，`subsec:vandermonde-euler`、`subsec:vandermonde-euler-integer-ring`。
- **判断**：索引、类型和矩阵方向错误，高严重度，已修正。
- **原式 → 修正**：按本节矩阵定义，第 $j$ 行是节点 $x_j=\omega^{2j+1}$ 的幂，因此系数列向量 $a$ 的求值是 $Va$，不是 $V^Ta$。节点统一为 $j=0,\ldots,n-1$，避免从 $1$ 起却仍用 $2j+1$ 的错位。几何和为零的范围必须排除使公比为 $1$ 的情形（本推导中 $m=n$），该项恰是反对角线上得到 $n$ 的来源。
- **重要区分**：A11 的基向量按行组成的矩阵可记作 $W=V^T$。另一章节如明确采用该约定，$W^T$ 用于求值是正确的；本修正不机械地替换全书所有转置。
- **复现**：`check_vandermonde`；常数多项式系数 $(1,0,0)^T$ 在 $n=3,p=7$ 的求值是全一向量，转置乘法给不同结果。
- **一手/标准资料**：[MIT 线性代数资料的矩阵/坐标约定](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/least-squares-determinants-and-eigenvalues/projections-onto-subspaces/)；根条件见 [Conrad](https://kconrad.math.uconn.edu/blurbs/galoistheory/finitefields.pdf)。矩阵恒等式的具体推导见下一条。

### FND-016：$VV^T=nJ$ 并不要求 $n$ 为二幂

- **位置**：`a12-euler.tex`，`subsec:vandermonde-euler-integer-ring` 末尾 `Condition for μ`；复数对应段落亦复核。
- **判断**：否定性结论错误，中严重度，已修正。
- **推导**：按前一条节点顺序，

  $$
  (VV^T)_{jk}=\sum_{i=0}^{n-1}\omega^{2i(j+k+1)}.
  $$

  若 $j+k=n-1$，公比为 $1$，和为 $n$；否则公比是非平凡 $n$ 次单位根，几何和为零。因此 $VV^T=nJ$，$J$ 是逆序置换矩阵。有限域版只须素数 $p$、$2n\mid p-1$、$\omega$ 的阶为 $2n$。该条件也保证 $n$ 可逆。二幂仅用于把 $X^n+1$ 认作单个 $\Phi_{2n}$，不是此恒等式的必要条件。
- **反例**：$n=3,p=7,\omega=3$，节点为 $3,6,5$，直接得到 $VV^T=3J\pmod7$。
- **修正**：撤回“非二幂会使此性质失效”的原结论，并明确有限域条件。
- **复现**：`check_vandermonde`。
- **一手/标准资料**：[Conrad，有限域的循环乘法群](https://kconrad.math.uconn.edu/blurbs/galoistheory/finitefields.pdf)。上述几何和为本轮独立推导。

### FND-017：缩放舍入表中的“近似当且仅当”不成立

- **位置**：`a13-modulus-rescaling.tex`，`subsec:modulo-rescaling`、`tab:rescaling`、`subsec:modulo-rescaling-ex`。
- **判断**：核心等价关系错误，高严重度，已用精确命题替换。
- **正确命题**：令 $r=q'/q$。若 $a-b=hq$，则 $ra-rb=hq'$，整数平移与 $R$ 交换，故 $R(ra)-R(rb)=hq'$。这是精确的单向同余保持，并不只是“近似”。同理，将整个乘积 $ac$ 和 $bd$ 各自缩放舍入，可应用这一命题。
- **反向反例**：$q=8,q'=2,a=0,b=1$，两者都舍入为 $0$，但 $a\not\equiv b\pmod8$。不能写双向等价。
- **分别舍入的加法**：写 $\delta_x=R(rx)-rx$，则 $a+c\equiv b+d\pmod q$ 只给出舍入后和的差等于某个 $hq'$ 加 $\eta=\delta_a+\delta_c-\delta_b-\delta_d$，$|\eta|\le2$。取 $r=1/2,a=c=1,b=2,d=0$，原和相等，分别舍入后相差 $1$。分别缩放两个乘数还会引入 $r^2$，不等于只缩放乘积一次。
- **修正**：替换错误等价表及其证明，给出明确误差式；保留原 $30\to3$ 例子并解释其恰好无舍入误差不能证明逆命题。补充 LWE 相位中的加权误差 $\delta_b-\sum_i\delta_{a_i}s_i$。
- **复现**：`check_rounding_congruences`。
- **一手来源**：[Brakerski–Gentry–Vaikuntanathan，模数切换的舍入误差分析，Lemma 1、§3.3](https://eccc.weizmann.ac.il/report/2011/111/download)。该论文使用的消息同余保持规则与本书高位编码不同；本条常数和精确单向命题由上面的整数平移推导给出。

### FND-018：CRT 的两两互素、求和下标和 RNS 坐标模数

- **位置**：`a14-chinese-remainder.tex`，`sec:chinese-remainder`、`subsec:crt-application`。
- **判断**：必要条件和公式下标错误，中严重度，已修正。
- **修正**：明确所有模数 $n_i>1$ 且两两互素；将构造 $x=\sum_j a_jy_j$ 中误写的固定 $y_i$ 改为随和变化的 $y_j$；RNS 第 $i$ 坐标的加减乘应模 $n_i$，不能统一模乘积 $N$。
- **推导**：$N_i=N/n_i$，$y_i=N_i(N_i^{-1}\bmod n_i)$ 满足第 $i$ 坐标为 $1$、其余为 $0$。因此 $x=\sum a_iy_i\pmod N$ 给出唯一剩余类，且该映射是环同构。模数 $3,5,7$ 下 $100+12\equiv7\pmod{105}$，坐标为 $(1,2,0)$，不是三个坐标都模 $105$。
- **复现**：`check_crt`。
- **一手/标准资料**：[Conrad, The Chinese Remainder Theorem](https://kconrad.math.uconn.edu/blurbs/ugradnumthy/crt.pdf)。

### FND-019：Taylor 有限截断误差不保证随次数单调下降

- **位置**：`a15-taylor-series.tex`，`sec:taylor-series`，误差解释与讨论。
- **判断**：普遍性陈述错误，中严重度，已修正。
- **反例**：$f(x)=1+x-100x^2$，在 $x=0.1$ 处，零阶、一阶、二阶 Taylor 多项式的绝对误差依次为 $0.9,1,0$。增加一次阶数反而增大误差。一般也不能脱离导数界和解析收敛区域，把距离展开点远近直接解释为单调误差规律。
- **修正**：给出有限阶 Lagrange 余项界

  $$
  |f(x)-T_D(x)|\le \frac{\sup_{\xi\in I}|f^{(D+1)}(\xi)|}{(D+1)!}|x-a|^{D+1},
  $$

  并说明所需光滑性、区间与无限级数的解析收敛条件。保留原展开公式和示例。
- **复现**：`check_taylor`。
- **一手/标准资料**：[NIST DLMF §1.4$vi$，Taylor 定理与余项](https://dlmf.nist.gov/1.4.vi)。

### FND-020：FFT/NTT 的乘法目标、根条件与复杂度模型

- **位置**：`a16-ntt.tex`，全部小节，尤其 `subsec:ntt-motivation`、`subsec:ntt-forward`、`subsec:ntt-backward`。
- **判断**：算法前提和次数/向量类型缺失，中到高严重度，已修正。
- **修正**：$n$ 点、奇数次 $2n$ 单位根的变换计算的是模 $X^n+1$ 的负循环乘积。未约减的普通乘积次数可到 $2n-2$，不能直接用只有 $n$ 个值唯一恢复；若需要普通卷积应另外零填充。首段乘积末项索引由 $2n-1$ 改为 $2n-2$。
- **前提**：给二基递归 $n=2^L$；复数根为 $e^{\pi i/n}$，有限域版要求素数 $p$ 和 $2n\mid p-1$。平方后只有 $n/2$ 个互异节点；求逆向量 $y$ 与标量 $y_i$ 分开；阶的最小指数排除 $0$。普通循环 DFT 使用 $n$ 次单位根，本节的“只用奇数根”不能推广为所有 FFT 的要求。
- **核查**：分治每层 $n$ 次常数规模域运算、共 $\log_2n$ 层；$O(n\log n)$ 是域运算数，不是未指定整数位宽的位复杂度，也不处理浮点误差。
- **复现**：`check_negacyclic_ntt` 检查有限域变换、逆变换与独立系数卷积一致。
- **一手/标准资料**：[Conrad，有限域根条件](https://kconrad.math.uconn.edu/blurbs/galoistheory/finitefields.pdf)；[David Maier 的大学 FFT 课程讲义，分治结构](https://web.cecs.pdx.edu/~maier/cs584/Lectures/lect07b-11-MG.pdf)。具体负循环恒等式由本节节点求值和 A10 唯一插值推出。

### FND-021：LWE 枚举成本不是安全下界，搜索/判定等价有参数条件

- **位置**：`b01-lattice.tex`，`subsec:lattice-overview`、`subsec:lattice-scheme`、`subsec:lattice-scheme2`。
- **判断**：实质性安全论证错误，高严重度，已修正；具体参数安全性仍待证。
- **原论证问题**：从每个噪声有约 $r$ 个可能值推到攻击者必须做 $r^k$ 次尝试；说增加方程会增加攻击难度；无条件互换搜索与判定；并把 RLWE 的安全性直接视为 LWE 的结论。
- **核查**：$r^k$ 至多描述一种枚举策略的候选数，不能排除其他算法，更不是下界。更多独立样本可帮助攻击。无噪声 $k$ 条方程也只有系数矩阵可逆时才唯一恢复 $k$ 维秘密。正文一处带噪声关系写成 $s\cdot a=\sum s_ia_i+e$，也须改为 $b=\sum s_ia_i+e\pmod q$。
- **一手定理边界**：Regev Theorem 1.1 是特定噪声、模数及 $\alpha p>2\sqrt n$ 条件下，从最坏情形格问题到 LWE 的量子归约；其 Lemma 4.2 的搜索到判定转换使用素数且多项式规模模数等假设。它们不证明任意本书参数、秘密分布或 RLWE 结构安全。
- **修正**：明确 search-LWE/decision-LWE 为适当参数族的计算假设，指定均匀独立公开向量和小整数误差；把保密说明改为基于判定假设的混合论证；删除无条件抗量子和 $r^k$ 下界表达。RLWE 单列相应假设。
- **一手来源**：[Regev, On Lattices, Learning with Errors, Random Linear Codes, and Cryptography，Theorem 1.1、Lemma 4.2](https://cims.nyu.edu/~regev/papers/qcrypto.pdf)；[Lyubashevsky–Peikert–Regev, On Ideal Lattices and Learning with Errors over Rings](https://web.eecs.umich.edu/~cpeikert/pubs/ideal-lwe.pdf)。

### FND-022：解密要先最近整数舍入，噪声界要取绝对值

- **位置**：`b01-lattice.tex` 两个密码系统小节；`b02-lwe.tex` 的 Setup、`subsec:lwe-enc`、`subsec:lwe-dec`；相关 B03/B04。
- **判断**：会改变解密输出的错误，高严重度，已修正。
- **原式 → 修正**：$e<\Delta/2$ → $|e|<\Delta/2$；直接“右移” → 先按最近 $\Delta$ 倍数舍入，再除以 $\Delta$。即使 $\Delta$ 是二幂，普通向下取整的右移也不等价。例如 $\Delta=8,m=1,e=-1$，相位为 $7$，右移三位得 $0$，最近整数解码得 $1$。
- **完整解码**：对相位中心提升 $v=\operatorname{center}_q(b-a\cdot s)$，输出 $R(v/\Delta)\bmod t$。相位提取和解码是两个步骤，不能把带噪声环元素直接称为明文。使用中心代表元后的最终模 $t$ 也不可省略。
- **修正条件**：基本证明先设 $t\mid q$。误差明确为小整数（离散或舍入高斯）提升，有限界为解密成立事件；不再将连续实高斯直接当作有限整数环元素。
- **复现**：`check_decoder_and_overflow`。
- **一手来源**：[Regev，LWE 定义与加密的最近码点解码](https://cims.nyu.edu/~regev/papers/qcrypto.pdf)；[LPR，环上公钥加密的正确性噪声条件](https://web.eecs.umich.edu/~cpeikert/pubs/ideal-lwe.pdf)。

### FND-023：$t\nmid q$ 时“$q\gg t$”不足以控制任意消息溢出

- **位置**：`b02-lwe.tex`，`subsubsec:lwe-noise-bound`；`b03-rlwe.tex`，`subsec:rlwe-dec`；C01、C02 的溢出讨论。
- **判断**：正确性前提遗漏，高严重度，已修正。
- **精确推导**：令 $\Delta=\lfloor q/t\rfloor$、$r=q-\Delta t$，未约减消息 $m=m'+vt$，其中 $m'$ 取中心明文代表元。则

  $$
  \Delta m+e=\Delta m'+vq+(e-rv)\equiv\Delta m'+(e-rv)\pmod q.
  $$

  应控制有效误差 $e-rv$，而不是只看 $e$。在正文所定奇数 $t\ge3$ 的中心消息约定下，$|e-rv|<\Delta/2$ 是足够条件；可用更保守的 $|e|+r|v|<\Delta/2$。此处不需要 $t$ 为素数。
- **反例**：$q=1024,t=3,\Delta=341,m=513=171t,e=0$。相位为 $853\pmod{1024}$，中心提升为 $-171$，解码 $R(-171/341)\bmod3=2$，但应为 $0$。即使没有原始误差、$q/t$ 很大，溢出仍可破坏正确性。
- **修正**：把原无界溢出保证替换为上述条件；修复少了一层最近整数舍入的解码表达式。RLWE 按每个系数应用相同分析。
- **复现**：`check_decoder_and_overflow`。
- **一手来源**：[LPR，编码间距与总误差决定正确性的原则](https://web.eecs.umich.edu/~cpeikert/pubs/ideal-lwe.pdf)。本条 $e-rv$ 是对本书所用非整除高位编码的独立代数推导。

### FND-024：B04 的通用 GLWE 公钥安全性断言可被三次枚举攻破

- **位置**：`b04-glwe.tex`，`subsec:glwe-public-key-enc`、`Security`。
- **判断**：实质性安全论证错误，严重；已将构造范围收窄并保留反例。不是单纯“教学参数太小”的提醒。
- **原构造**：公钥 $P_1=\langle A,S\rangle+E,P_2=A$，加密 $B=P_1U+\Delta M+E_1,D=AU+E_2$，允许一般 $n,k$，而 $U$ 为一个三元系数多项式。原文由误差外形相似直接推出与 GLWE 相同的安全性。
- **反例族**：取 $n=1$，则 $U\in\{-1,0,1\}$，无论秘密向量维数 $k$ 多大，攻击者仅枚举这三个值。对每个候选 $u$，检查所有 $D_i-A_iu\pmod q$ 是否很小；正确候选留下 $E_{2,i}$。找到 $u$ 后计算 $B-P_1u=\Delta m+E_1$，无需秘密即可解码。
- **量化**：在 $|E_{2,i}|\le B_2$ 的事件上，独立均匀 $A_i$ 对一个错误候选给出每坐标至多 $(4B_2+2)/q$ 的小残差概率（候选差为 $\pm1,\pm2$，至多二对一），两个错误候选的联合上界为 $2((4B_2+2)/q)^k$。此外 $U=0$ 的概率恰为 $1/3$，此时 $B=\Delta m+E_1$ 直接暴露消息。增加 $k$ 不修复该随机性缺陷，反而更容易排除错误候选。
- **实际复现**：`check_scalar_public_key_attack` 取 $k=32,q=2^{20},t=4,B_2=2$，对全部三个 $U$ 和四个消息共 12 次加密，公钥攻击均恢复消息。这里只用有限有界样例；针对高斯噪声，需将所选尾事件的概率另计，三候选攻击结构不变。
- **最小修正**：该小节明确限定 $k=1$、足够大的二幂环维数 $n$，以及满足相应判定 RLWE 假设的参数/分布族，使用标准 RLWE 公钥结构。一般 GLWE/LWE 公钥构造须另给足够维数的随机向量/矩阵和安全归约。并加入正确性界 $\|EU+E_1-E_2S\|_\infty\le\|E\|_\infty\|U\|_1+\|E_1\|_\infty+\|E_2\|_\infty\|S\|_1<\Delta/2$。仅“大 $n$”本身不是安全证明。
- **一手来源**：[LPR，§1.2 中的 RLWE 公钥加密结构](https://web.eecs.umich.edu/~cpeikert/pubs/ideal-lwe.pdf)；[Regev，§5 使用多条公开 LWE 样本与随机子集的公钥构造](https://cims.nyu.edu/~regev/papers/qcrypto.pdf)。原高斯参数归约不能未经核对直接为本书三元秘密/随机因子背书。

### FND-025：密文种子不应定义成秘密的公开散列，维数不能单独代表安全级别

- **位置**：`b04-glwe.tex`，`subsec:glwe-enc` 及无标签 `Discussion`。
- **判断**：缺少安全条件的压缩建议，中到高严重度，已修正。
- **原文问题**：用 $H(S)$ 作为公开掩码的生成种子，会引入与秘密相关的公开辅助信息；“哈希”本身不保证展开出的全部环元素符合所需分布。以 $k,n$ 之间直观互换描述相同安全性，也没有给出参数或归约。
- **修正**：种子 $d$ 独立、公开，使用密码学 PRG/XOF，按索引域分离展开全部 $kn$ 个系数，必要时拒绝采样以达到指定均匀分布。明确加入伪随机展开假设，不公开 $H(S)$ 作为理由。安全性需联合考虑维数、模数、噪声、秘密分布和样本数，不能只比较维数乘积。
- **论证范围**：未证明一个具体 XOF 的实现安全；这是使压缩方案的假设可陈述，而不是对任意“散列种子”给安全保证。原文将对称加密中公开 $A$ 称作公钥的一处用语亦改为公开掩码。
- **一手来源**：[Regev，LWE 样本公开向量的均匀性假设](https://cims.nyu.edu/~regev/papers/qcrypto.pdf)；[LPR，环样本及分布假设](https://web.eecs.umich.edu/~cpeikert/pubs/ideal-lwe.pdf)。从理想均匀向量换到 PRG 是额外计算假设，不能由这两篇论文自动推出。

### FND-026：GLev 第一个分量通常只直接解出 $M\bmod\beta$

- **位置**：`b05-glev.tex`，`subsec:glev-enc`、无标签 `Decryption`。
- **判断**：解密范围与参数条件缺失，高严重度，已修正。
- **推导**：第 $i$ 行相位 $qM/\beta^i+E_i\pmod q$ 按最近格点解码，最多恢复 $M\pmod{\beta^i}$，且需 $\|E_i\|_\infty<q/(2\beta^i)$。第一行只能恢复 $M\pmod\beta$；例如 $q=16,\beta=4$，消息 $0$ 与 $4$ 的第一行无噪声相位都为 $0$。
- **修正**：若声明第一行足以恢复原明文，需保证所选明文代表元在模 $\beta$ 后可唯一识别，例如适当编码下 $\beta\ge t$。各行用于同态 gadget 计算，不要求全都可单独解码。明确整数权重条件和 A06 全长度条件。
- **复现**：`check_glev_and_units`。
- **一手来源**：[TFHE，gadget 精度、加密的 gadget 行与误差](https://imec-publications.be/bitstreams/92b4e945-9e22-4bc6-899c-c0baa9f7b4e9/download)。本条可恢复消息模数由该行的周期直接计算。

### FND-027：非零秘密多项式未必可逆

- **位置**：`b06-ggsw.tex`，无标签 `Decryption`。
- **判断**：环单位条件遗漏，中严重度，已修正。
- **原论证**：从 GGSW 其他行解出 $S_iM$ 后，只要 $S_i\ne0$ 就除以 $S_i$ 恢复 $M$。
- **反例**：在 $\mathbb F_5[X]/(X^2+1)$ 中，

  $$
  (X-2)(X+2)=X^2-4\equiv X^2+1\equiv0,
  $$

  两个因子都非零，却是零因子，不能求逆。此时基域为素数域仍不足以保证多项式商环为域。
- **修正**：其他行先按 B05 指定的消息模数解出乘积；只有 $S_i$ 在对应 $\mathbb Z_\beta[X]/(X^n+1)$ 中是单位时才能逆乘。最后一个 GLev 块直接恢复 $M$ 也须满足 B05 的范围/噪声条件。
- **复现**：`check_glev_and_units`。
- **一手/标准资料**：[Earl，单位、零因子和多项式商环](https://www.maths.ox.ac.uk/system/files/attachments/lectures%20rings%20and%20modules.pdf)。

### FND-028：密文相加不自动保持可解密；均值为零不推出方差相加

- **位置**：`c01-glwe-add-cipher.tex`，整章、`subsubsec:glwe-add-cipher-discuss` 的三个段落。
- **判断**：噪声正确性和统计前提遗漏，高严重度，已修正。
- **推导**：相同密钥、环、模数、尺度下，输出相位为 $\Delta(M_1+M_2)+(E_1+E_2)$。在 $t\mid q$ 时，正确解码仍需 $\|E_1+E_2\|_\infty<\Delta/2$。两个各自可解密的误差 $3,3$，取 $\Delta=8$，相加已经越界。
- **统计修正**：一般 $\operatorname{Var}(e_1+e_2)=\operatorname{Var}(e_1)+\operatorname{Var}(e_2)+2\operatorname{Cov}(e_1,e_2)$。只有独立（或至少不相关）等前提下才可省略协方差。把同一密文加给自己时误差 $2e$，方差是 $4\sigma^2$，不是 $2\sigma^2$。密文加法结果也不能默认为与新鲜误差相同的分布。
- **修正**：明示参数匹配与噪声预算，区分精确消去掩码和条件性舍入消噪；$t\nmid q$ 时引用 FND-023 的有效误差。
- **复现**：`check_addition_and_convolution_noise`。
- **一手来源**：[TFHE，噪声分析中的显式独立性假设 Assumption 3.11](https://imec-publications.be/bitstreams/92b4e945-9e22-4bc6-899c-c0baa9f7b4e9/download)。协方差公式为直接展开二阶矩所得，不依赖论文的启发式。

### FND-029：明文加法的“噪声不变”须指定消息提升

- **位置**：`c02-glwe-add-plain.tex`，整章和 `Noise Growth`。
- **判断**：正确性前提遗漏，中严重度，已修正。
- **推导**：向 $B$ 加 $\Delta\Lambda$，相对未约减消息 $M+\Lambda$ 的误差确实仍是 $E$。若 $t\mid q$，明文模 $t$ 回绕乘以 $\Delta$ 后也是 $q$ 的倍数，所以仍成立。若 $t\nmid q$，回绕带来 FND-023 的 $-(q\bmod t)v$，不能宣称最终消息代表元的有效噪声一概不变。
- **修正**：补匹配环、尺度及基本 $t\mid q$ 条件，保留原代数证明，明确该“噪声不变”是相对于哪一个消息提升。
- **一手来源**：[LPR，环上编码与误差相位](https://web.eecs.umich.edu/~cpeikert/pubs/ideal-lwe.pdf)。本条等式为直接展开。

### FND-030：明文多项式乘法遗漏误差项及卷积因子

- **位置**：`c03-glwe-mult-plain.tex`，主算法及证明。
- **判断**：正确性等式错误，高严重度，已修正。
- **原式 → 修正**：输出相位必须为 $\Delta M\Lambda+\Lambda E$，证明中一处仅写消息项，已补回 $E'=\Lambda E$。多项式系数 $X_i$ 的笔误改为 $X^i$。
- **噪声界**：$\|E'\|_\infty\le\|\Lambda\|_1\|E\|_\infty\le n\|\Lambda\|_\infty\|E\|_\infty$，还须小于 $\Delta/2$。不能把一个多项式乘法当成逐系数标量乘法而漏掉卷积求和。例 $n=4$、两个全一多项式的负循环积系数为 $(-2,0,2,4)$，系数最大绝对值已为 $4$。
- **修正**：补正确误差及范数界，指出密文运算不是“解密后再获得同噪声新密文”；NTT 可用性明确依赖 A16 的根和模数条件。
- **复现**：`check_addition_and_convolution_noise`、`check_negacyclic_ntt`。
- **一手来源**：[TFHE，外积噪声中多项式乘法和分解范数的作用](https://imec-publications.be/bitstreams/92b4e945-9e22-4bc6-899c-c0baa9f7b4e9/download)。本条上界直接来自负循环卷积的三角不等式。

### FND-031：gadget “降噪”需要额外密文、正确数字界和残差项

- **位置**：`c03-glwe-mult-plain.tex`，`subsubsec:gadget-decomposition-noise-suppression`、`subsubsec:glwe-mult-plain-discuss`。
- **判断**：算法输入和误差界错误，高严重度，已修正。
- **原文问题**：仿佛可从一个普通 GLWE 密文无代价获得全部所需尺度的密文；给未平衡数字 $0,\ldots,\beta-1$ 却用 $\beta/2$ 界；一行求和省略总误差；截断情况未说明消息残差。
- **正确条件**：须预先提供对应消息的 GLev 加密。全长度递减分解采用 $q=\beta^l$。若数字系数小于 $\beta$、每行误差范数不超过 $B_g$，则总误差界为 $nl(\beta-1)B_g$。只有定义并处理进位的平衡数字才可使用另一界；例如 radix-4 数字 $3>4/2$。
- **截断式**：若 $\Lambda\equiv\sum_i\Lambda_i g_i+\rho\pmod q$，输出相对于所需 $\Delta M\Lambda$ 的误差包含 $-\rho\Delta M$，不能漏掉。所谓“降噪”是某参数下与直接乘法界的比较，不保证每个具体样本的绝对噪声都更小。
- **修正**：明确所需 GLev 输入，补总误差、正确数字/卷积界和残差。
- **一手来源**：[TFHE，Definition 3.6、Lemma 3.7、Theorem 3.13](https://imec-publications.be/bitstreams/92b4e945-9e22-4bc6-899c-c0baa9f7b4e9/download)。

### FND-032：模数切换必须控制总误差，CLT 不能补上遗漏的条件

- **位置**：`c04-glwe-modulus-switch.tex`，`subsec:modulus-switch-lwe`、`subsubsec:modulus-switch-lwe-discuss`、RLWE/GLWE 两节。
- **判断**：影响正确性的主要证明错误，高严重度，已修正。
- **精确推导**：取 $r=\hat q/q$、$\hat a_i=R(ra_i)=ra_i+\epsilon_{a_i}$、$\hat b=R(rb)=rb+\epsilon_b$。当 $t\mid q,\hat q$ 且 $\hat\Delta=r\Delta$ 时，由整数提升 $b=\sum a_is_i+\Delta m+e+Hq$ 得

  $$
  \hat b-\sum_i\hat a_is_i
  \equiv\hat\Delta m+e_{\rm new}\pmod{\hat q},\qquad
  e_{\rm new}=re+\epsilon_b-\sum_i\epsilon_{a_i}s_i.
  $$

  因 $|\epsilon|\le1/2$，

  $$
  |e_{\rm new}|\le r|e|+\tfrac12(1+\|s\|_1).
  $$

  右侧小于 $\hat\Delta/2$ 才给出充分正确性条件。若另定义 $\hat e=R(re)$，则辅助修正 $\epsilon_{all}=\epsilon_b-\sum_i\epsilon_{a_i}s_i-\epsilon_e$，必须与 $\hat e$ 一起使用；不能单独说其“小”便推出解密。
- **原论证错误**：遗漏总误差、将上界写成等式、半整数处用严格 $<1/2$、将舍入项默认独立均匀，再用大维数和中心极限定理保证消去。舍入误差由密文和秘密相关地决定，不能无论证套独立性；增大 $k$ 也不让最坏界变小。
- **反例**：$q=16\to\hat q=4,t=2,k=4,a=(2,2,2,2),s=(1,1,1,1),b=-8,m=0,e=0$。原相位为 $0\pmod{16}$，完全无噪声；舍入后 $\hat a=(1,1,1,1),\hat b=-2$，新相位为 $-2\pmod4$，解码为 $1$，而非 $0$。
- **多项式版**：$E_{new}=rE+\epsilon_B-\sum_i\epsilon_{A_i}S_i$，充分界

  $$
  \|E_{new}\|_\infty\le r\|E\|_\infty+\tfrac12\bigl(1+\sum_i\|S_i\|_1\bigr)
  \le r\|E\|_\infty+\tfrac12(1+kn)
  $$

  用于三元秘密。RLWE 为 $k=1$。若尺度不精确成比例，还要加 $(r\Delta-\hat\Delta)M$ 和必要的消息回绕分析。
- **修正**：重写正确性条件、补遗漏的下标和误差项，撤下无依据的统计保证；解释精确缩放保持 $|e|/\Delta$，额外舍入才会消耗新预算。明文所属环纠正为 $R_t$，中间整数提升和模多项式关系明确。
- **复现**：`check_modulus_switch`。
- **一手来源**：[BGV，Lemma 1、§3.3 Lemma 4](https://eccc.weizmann.ac.il/report/2011/111/download) 的模数切换分析展示了秘密范数误差项和必要余量。其低位消息保持规则与这里的高位尺度不同，本报告没有直接挪用其常数，而是按上式独立推导。

### FND-033：模数切换数值例子原本写成 $13=14$

- **位置**：`c04-glwe-modulus-switch.tex`，无标签 `Example`。
- **判断**：确定的数值等式错误，中严重度，已修正。
- **原例核查**：$q=64\to32$、$a=(-25,12,-3,7)$、$s=(0,1,1,0)$、$b=26$、$\Delta=16,m=1,e=1$。按本报告统一舍入，输出 $(-12,6,-1,4,13)$。相位为 $13-(6-1)=8$，所以新总误差为 $0$。
- **修正**：原式缺少 $\epsilon_{all}=-1$，应写 $13=0+6-1+0+8+1-1$，而 $\hat e=R(1/2)=1$。末尾解密表达式同时保留二者，不再把辅助舍入值 $1$ 误当最终噪声。LWE 向量维数由误写的 $n$ 改为 $k$。
- **复现**：`check_modulus_switch`。
- **一手来源**：[BGV 的精确舍入误差记账原则](https://eccc.weizmann.ac.il/report/2011/111/download)；本例所有数值为独立重算。

### FND-034：密钥切换不能把未知明文秘密乘积直接从密文向量减掉

- **位置**：`c05-glwe-key-switching.tex`，`sec:glwe-key-switching`，算法框、逐步证明、`Noise and Truncation`。
- **判断**：算法类型错误和噪声条件遗漏，高严重度，已修正。
- **原问题**：算法框将密文元组直接减 $\sum_iA_iS_i$ 作为等式步骤；后者是未知秘密乘积的环元素，不是公开可计算的同类型密文。只有其在新密钥下的评估密钥加密组合可以相减。
- **正确算法**：由持有秘密的一方预先生成 $KSK_{ij}=\operatorname{GLWE}_{S'}(g_jS_i+E_{ij})$，公开计算

  $$
  c'=(0,\ldots,0,B)-\sum_{i,j}A_{ij}KSK_{ij}.
  $$

  精确分解 $A_i=\sum_jA_{ij}g_j$ 时，其相位为 $\Delta M+E'$，$E'=E-\sum_{i,j}A_{ij}E_{ij}$。原文的“约等于同一密文”改为精确的相位/误差表述。
- **界与截断**：未平衡数字给 $\|E'\|_\infty\le\|E\|_\infty+knl(\beta-1)B_{ks}$。若 $A_i\equiv\sum_jA_{ij}g_j+\rho_i\pmod q$，还须加 $\sum_i\rho_iS_i$，相应范数项为 $\sum_i\|\rho_i\|_\infty\|S_i\|_1$。不加这一项就无法证明近似分解的密钥切换正确。
- **反例**：$q=16,\beta=2,l=2,A=13,S=1$，截断数字只能表示 $12$，残差 $1$。即使输入及 KSK 无噪声，输出相位相对原消息也多 $1$；取 $\Delta=2,m=0$ 已可错误解码为 $1$。
- **修正**：仅保留公开可实现算法，补参数、误差界、残差、密钥维数可改变但环和模数须相同的范围。明确密钥切换不是噪声刷新，公开密钥形成环时的安全性另需论证。
- **复现**：`check_key_switch` 同时验证全长度误差公式和截断反例。
- **一手来源**：[TFHE，§4 Key Switching 的正确性及分解残差](https://imec-publications.be/bitstreams/92b4e945-9e22-4bc6-899c-c0baa9f7b4e9/download)。

### FND-035：尚不能据本书基础章节确认的安全性结论

- **位置**：`b01` 的 LWE/RLWE 介绍、`b04` 的种子压缩与公钥小节、`c05` 的公开密钥切换材料。
- **判断**：条件性/待证事项，不能因为未证明就判定算法已被攻破。
- **尚缺内容**：没有完整指定安全参数 $\lambda$ 随动的 $n,k,q,t,\sigma$、秘密/误差分布、样本数量和失败概率；三元秘密及三元随机因子版本与引用论文高斯分布定理的精确对应未给出；种子展开依赖所选 PRG/XOF；评估密钥是否形成循环和是否需要循环/KDM 安全假设应由完整方案确定。
- **本轮处置**：把确定错误的绝对断言改为显式假设，未捏造安全位数，也未宣称本轮给出了端到端 IND-CPA 证明。FND-024 反例只攻击原无限制的标量随机因子推广；不能据此推出满足适当假设的高维 RLWE 公钥构造不安全。
- **下一步可证目标**：固定具体参数族和分布，写出每一混合的归约对象与损失；给出随机误差尾界和全部运算/密钥样本的联合失败界；在完整密钥关系图上检查是否使用额外安全假设。完成这些后才可把此项从待证状态移除。
- **一手来源**：[Regev](https://cims.nyu.edu/~regev/papers/qcrypto.pdf)、[LPR](https://web.eecs.umich.edu/~cpeikert/pubs/ideal-lwe.pdf)、[TFHE](https://imec-publications.be/bitstreams/92b4e945-9e22-4bc6-899c-c0baa9f7b4e9/download)。这些来源提供特定形式的定理及假设，不是任意参数的安全证书。

### FND-036：矩阵不交换及不保持乘积不能写成逐输入恒不等

- **位置**：`a11-matrix.tex`，`subsec:matrix-arithmetic`，矩阵性质框。
- **判断**：全称命题和表达式类型错误，中严重度，已修正。
- **原文问题**：直接写 $AB\ne BA$、$Ax\ne xA$，以及线性变换不保持点积的“恒不等式”。但 $AI=IA$，某些矩阵本来交换；列向量 $x$ 的 $xA$ 甚至可能没有定义。$A\langle x,y\rangle$ 是矩阵的标量倍，而 $\langle Ax,Ay\rangle$ 是标量，不能作为同一个向量映射的输出比较。
- **修正**：改为“矩阵乘法一般不满足交换律，首先检查维数”，并区分线性性与乘积保持。用 $A=2I,x=y\ne0$ 展示 Hadamard 乘积不被普遍保持，同时指出 $A=I$ 就保持该乘积，所以应说恒等式不普遍成立，而非每个输入都严格不等。
- **复现**：`check_matrix_claims`。
- **一手/标准资料**：[Earl，矩阵环与非交换性](https://www.maths.ox.ac.uk/system/files/attachments/lectures%20rings%20and%20modules.pdf)。

## 未改动但实际核查的主要内容

以下核查也记录在覆盖清单，不因“没有改动”而省略。

- A01：同余等价类、加减乘的代表元独立性、逆元的互素条件、消去模数、中心区间。
- A02：群的四公理；整数加法、非零有理数乘法、模加法和单位群的例子。整数乘法零例外见 FND-001。
- A03：域的非零乘法群、有限域素数幂阶、同阶有限域同构、$\mathbb Z_p$ 与一般 $\mathbb F_{p^r}$ 的区别。未发现本轮需改的确定错误。
- A04：元素阶整除群大小、幂的阶、费马小定理的前提与逐式证明。
- A05：给定多项式约减例子的系数算术、负循环移位的符号。
- A07：复单位根显式公式、阶整除 $n$、按因子划分本原根集合。
- A08：前十个分圆多项式表和 $X^n-1=\prod_{d\mid n}\Phi_d(X)$；保留成立结论，只修错误证明。
- A10：Lagrange 基函数在节点上的 Kronecker 值、唯一性次数界，以及分母可逆所需域条件；复合模数处的反例已在基线中正确，不重复记为本轮新发现。
- A11：实向量内积、Hermitian 内积、矩阵线性运算、实共轭空间的加法和逐分量乘法；其余结构/坐标问题见各条。
- A12：勾股恒等式、$i^2=-1$、Euler 公式、实/虚部和复共轭关系；Vandermonde 的变更单列。
- A14：CRT 存在性、唯一性及幂等坐标构造；模数/索引问题已改。
- A16：从偶奇系数拆分到每层复用的递归，逆变换几何和，以及频域逐项乘法对应负循环卷积。
- B02–B04：掩码与秘密相乘后消去的符号、LWE/RLWE/GLWE 的维数和环位置、替代 GLWE 的正负号。正确性推导成立的条件已显式化，安全性单独审查。
- B05–B06：GLev 的行尺度和 GGSW 的块维数、Lev/RLev 与 GSW/RGSW 的特例关系。
- C01–C05：所有线性同态操作逐步展开的相位关系；它们的解码前提与噪声已按上述发现补齐。

## 验证边界与维护建议

本轮源码改动范围是 25 个有确定修正的英文文件及其 25 个中文对应文件，另增加本报告、覆盖清单和反例脚本；A03/A10 未改。本报告不把编译成功、双语公式一致或有限数值检查标成“学术上全书无误”。结构与公式同步应另运行仓库的 `scripts/check_translation.py --math`；编译与排版由全书集成记录报告，避免在这里声称未经本报告作者独立执行的最终 PDF 结果。

后续维护应保留发现 ID。修改一个条件时，同时查看覆盖清单中的下游章节。例如从 $q=\beta^l$ 改回一般模数，必须更新 A06 分解、B05 的 GLev 权重、C03 的消息残差、C05 的 KSK 及其噪声界；不能只让公式检查脚本“再次相等”。同样，更换明文编码、舍入规则、秘密分布或 NTT 根顺序都会改变本报告证明中所用的前提。
