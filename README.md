# 氢知 HydroKnow · 企业知识与智能服务助手

[English](README.en.md) · [简体中文](README.md)

> 基于 RAG（检索增强生成）的本地知识问答助手（助手人格：小知）

**在线 Demo（长期稳定 · GitHub Pages）**：https://voskamp099.github.io/hydroknow/

> > 更新 Demo：改完内容后运行 `bash publish.sh`（重新构建 + 自动推送，约 1-3 分钟生效）

## 简介

一个可以完全离线运行的企业知识问答助手。系统加载 `data/` 里的资料，抽取文本、智能分块，用 BM25 与 TF-IDF 混合检索找出最相关的片段，再从片段中组织出带来源和置信度的答案。

仓库里的 `data/` 是**自建的虚构样例语料**（一家虚构的氢能公司「沐光氢能」），用来演示完整的检索与生成链路。换成自己的资料即可变成自己的知识助手：把 PDF、Markdown 或纯文本放进 `data/`，重跑一次即可。

本仓库不包含任何第三方资料。样例语料、示例问答和检索结果都由自建内容生成。

## 功能

- **知识库构建**：自动加载 PDF / Markdown / 纯文本资料，清洗文本，智能分块
- **混合检索**：BM25 + TF-IDF 双路检索，加权融合，中文无需分词器
- **智能问答**：从检索片段提取关键信息，结构化输出答案 + 来源 + 置信度
- **Web 聊天界面**：实时交互问答，展示检索来源与匹配度
- **CLI 批量演示**：预设问题批量跑，生成静态 demo.html
- **LLM 可插拔**：默认离线 stub，接口清晰，一行替换接入真实模型

## 项目结构

```
.
├── app.py                 # Flask Web 应用（一键启动聊天界面）
├── build_static.py        # 纯前端静态 Demo 构建脚本（生成 dist/index.html）
├── data/                  # 知识库目录：PDF / Markdown / 纯文本均可
│   ├── 00_公司资料说明.md
│   ├── 01_燃料电池产品单页.md
│   └── 02_解决方案手册.md
├── dist/
│   └── index.html         # 自包含静态 Demo（语料+检索全内嵌，可任意静态托管）
├── run.py                 # CLI 入口（兼容旧路径）
├── run_cli.py             # CLI 完整实现（批量问答 + 生成 demo.html）
├── rag/                   # RAG 核心引擎
│   ├── __init__.py        # 包入口，导出 RAGEngine
│   ├── loader.py          # 资料加载（PDF / 文本）+ 文本清洗 + 智能分块
│   ├── retriever.py       # BM25 + TF-IDF 混合检索
│   ├── generator.py       # 答案生成（可插拔 LLM stub）
│   └── pipeline.py        # 管线串联（RAGEngine）
├── templates/
│   └── index.html         # 聊天界面
├── static/
│   ├── style.css          # 深色主题样式
│   └── app.js             # 前端交互逻辑
└── requirements.txt
```

## 运行

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python app.py            # Web 界面 → http://127.0.0.1:5000
python run_cli.py        # CLI 批量问答 + 生成 demo.html
python build_static.py   # 生成自包含静态 Demo → dist/index.html
```

PDF 语料需要 PyMuPDF；只用 Markdown 或纯文本时可以不装它。

## 换成自己的资料

1. 把资料放进 `data/`（支持 `.pdf`、`.md`、`.txt`）。
2. 改 `run_cli.py` 和 `app.py` 里的 `SUGGESTED` / `SUGGESTED_QUESTIONS`，换成自己领域的推荐问题。
3. 重跑 `python run_cli.py` 和 `python build_static.py`，再 `bash publish.sh` 发布。

## 发布到 GitHub Pages

`publish.sh` 会重新构建静态 Demo 并推送到 `gh-pages` 分支。解释器默认用 `python3`，需要指定时用 `PYTHON=/path/to/python3 bash publish.sh`。

## 设计说明

- **为什么要混合检索**：BM25 负责长尾词与专有名词，TF-IDF 负责整体语义分布；中文不分词时用字符 n-gram 近似，两者加权融合比单一路线稳。
- **为什么不直接调 LLM**：默认走离线 stub，保证任何环境都能跑通、可复现；接真实模型时只要替换 `rag/generator.py` 里的 `generate_answer()`，接口签名保持 `generate_answer(question, retrieved_chunks) -> str`。
- **PDF 为什么要用 PyMuPDF**：pdfminer 遇到字体没有 ToUnicode 映射时，会把数字直接替换成 U+FFFD，不可逆丢失；PyMuPDF 保留为私有区字符，再由 `_repair_pua_digits` 还原。
