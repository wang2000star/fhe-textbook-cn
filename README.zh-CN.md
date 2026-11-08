# 全同态加密入门教材：中文版本

本仓库为 Ronny Ko 的 **The Beginner's Textbook for Fully Homomorphic Encryption** 增加可独立编译的中文版本。中文稿覆盖原书全部 34 个章节文件，包括数学基础、格密码与 LWE/RLWE/GLWE、通用同态运算，以及 TFHE、BFV、CKKS、BGV 和 RNS。

**当前为完整中文初译，尚未完成逐式学术审校。** 公式、章节结构、交叉引用及参考文献与英文源码对应；图中已经嵌入的英文、专名、算法标识和参考文献原题保留。翻译基线、术语与待核对的原文问题见 [TRANSLATION.md](TRANSLATION.md)。

原书：[arXiv 论文](https://arxiv.org/abs/2503.05136) · [英文动态网站](https://fhetextbook.github.io) · [英文说明与 Python 示例](README.md)

## 中英文入口

| 版本 | LaTeX 主文件 | 正文章节 | 默认 PDF 输出 |
| --- | --- | --- | --- |
| 中文 | `00-main-zh.tex` | `zh-CN/` 下的 34 个 `.tex` 文件 | `build/zh/00-main-zh.pdf` |
| 英文 | `00-main.tex` | 根目录下的 `a01-*.tex` 至 `d07-*.tex` | `build/en/00-main.pdf` |

两种版本共用 `figures/` 图片、`z-bibfile.bib` 文献库及 `source code/` 教学代码。修改中文正文时，编辑 `zh-CN/` 中对应文件；中文入口负责封面、前言、目录、章节标题和中文排版设置。

中文版本使用 **XeLaTeX + CTeX + Fandol 字体**，通过 `latexmk` 自动执行必要的重编译及参考文献处理。Fandol 随 TeX Live 提供，不依赖操作系统中的宋体等专有字体。英文版本沿用 pdfLaTeX 编译入口。

## 本地编译

需要 Python 3、`latexmk` 和完整的 LaTeX 依赖。推荐安装 **TeX Live 2025 完整版**，以覆盖原书使用的数学、算法、表格、绘图和字体宏包，并与 CI 的固定工具链保持一致。本地也已用 TeX Live 2022 完成两版编译。确保 `python`（或 `python3`）、`latexmk`、`xelatex`、`pdflatex`、`bibtex` 可从终端调用。

本次验证的 TeX Live 2026 `latest` 镜像在中文稿的粗体公式处报告 `Extended mathchar used as mathchar (65306)`；该宏包组合尚不属于本项目支持的构建环境。遇到此错误时，请使用 TeX Live 2025 或下文的固定容器，不必修改数学公式。排查记录见 [TRANSLATION.md](TRANSLATION.md#构建兼容性记录)。

在仓库根目录执行：

```bash
# 中文版本
python scripts/build.py zh

# 英文版本
python scripts/build.py en

# 两个版本
python scripts/build.py all
```

Linux 或仅提供 `python3` 命令的环境，将上述 `python` 改为 `python3`。脚本默认构建中文版本，因此 `python scripts/build.py` 也可使用。构建中文版本（包括 `all`）之前，会自动检查中文章节的覆盖及结构。

可用 `--output-dir` 改变构建输出目录，例如：

```bash
python scripts/build.py all --output-dir output
```

此时输出分别位于 `output/zh/` 和 `output/en/`。

### Make 命令

安装了 Make 的环境还可执行：

```bash
make zh       # 构建中文 PDF
make en       # 构建英文 PDF
make all      # 构建两种版本
make check    # 仅检查翻译文件结构
make clean    # 删除 build/ 中的编译产物
```

Make 默认使用 `python3`；如需指定 Python 命令，可执行 `make zh PYTHON=python`。

### Debian / Ubuntu 的依赖

最直接的安装方式是：

```bash
sudo apt-get update
sudo apt-get install python3 texlive-full
```

如果采用分包安装，可使用以下依赖组合：

```bash
sudo apt-get install \
  python3 latexmk \
  texlive-latex-base texlive-latex-recommended texlive-latex-extra \
  texlive-fonts-recommended texlive-fonts-extra \
  texlive-xetex texlive-lang-chinese texlive-lang-korean \
  texlive-science texlive-plain-generic
```

其中，`texlive-lang-chinese` 提供中文支持与 Fandol 字体；英文源码使用的 `kotex` 需要韩文支持；`esvect` 及其字体由相关 TeX Live 字体包提供，`texlive-fonts-extra` 的安装体积较大。若出现 `File ...sty not found` 或字体缺失，应补齐相应 TeX Live 包后重新编译。

Windows 可安装 TeX Live 并运行同样的 Python 命令；macOS 可使用完整 MacTeX。这里的 Python 构建脚本不依赖 Bash 或 Make。

### 固定版本的容器构建

安装了 Docker 的 Linux/macOS 环境可在仓库根目录执行以下命令，使用与 CI 相同的 TeX Live 2025 快照编译两版 PDF：

```bash
python3 scripts/check_translation.py --math
docker run --rm -v "$PWD:/work" -w /work \
  ghcr.io/xu-cheng/texlive-historic-alpine:2025 \
  /bin/bash -eo pipefail -c '
    mkdir -p build/en build/zh
    latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build/en 00-main.tex
    latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=build/zh 00-main-zh.tex
  '
```

首次运行需要下载镜像。容器输出仍位于宿主机的 `build/en/` 和 `build/zh/`。发行版的 `texlive-full` 包版本由发行版决定；需要复现 CI 环境时，优先使用上述快照。

## Overleaf

1. 将仓库源码完整上传为一个 Overleaf 项目，保留 `zh-CN/`、`figures/` 等目录。
2. 在项目设置中，将 **Main document** 设为 `00-main-zh.tex`。
3. 将 **Compiler** 设为 **XeLaTeX**，使用项目设置中可选的 **TeX Live 2025** 环境，然后重新编译。

切回英文版时，将主文件设为 `00-main.tex`，编译器设为 pdfLaTeX。中文入口应从仓库根目录编译，不要直接编译单个章节文件。

## GitHub Actions

工作流 [Textbook PDFs](.github/workflows/pdf.yml) 在 `main` 或 `chinese-edition` 分支推送、面向 `main` 的 Pull Request 时执行结构和公式一致性检查，再编译中英文 PDF。工作流进入默认分支后，也可通过 `workflow_dispatch` 手动运行。

编译步骤使用 `xu-cheng/texlive-action@v3` 并指定 `texlive_version: '2025'`，对应官方 `texlive-historic-alpine:2025` 快照。

构建成功后，可在对应 Actions 运行的 **Artifacts** 区域下载：

| Artifact 名称 | 内容 |
| --- | --- |
| `fhe-textbook-zh` | 中文 PDF |
| `fhe-textbook-en` | 英文 PDF |

该 PDF 工作流只上传构建产物。现有英文网站由独立的 [English website](.github/workflows/main.yml) 工作流构建，其自动发布仅在 `main` 分支推送时触发。

## 校订与维护

修订译文时，优先保持公式、标签、引用键、算法变量和图片路径与对应英文文件一致。术语约定和已发现的原文问题记录在 [TRANSLATION.md](TRANSLATION.md)。提交前运行：

```bash
python scripts/check_translation.py
python scripts/build.py zh
```

结构检查通过并不等于数学证明、译文语义或最终页面排版已经正确。修改长公式、表格、标题或字体后，还应打开生成的 PDF，检查相关页面的换行、溢出、交叉引用和字体显示。
