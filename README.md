# 氢知 HydroKnow · 沐光氢能企业知识智能服务助手

[English](README.en.md) · [简体中文](README.md)

> 企业知识与智能服务助手
> 基于 RAG（检索增强生成）的企业智能客服系统（助手人格：小知）

**在线 Demo（长期稳定 · GitHub Pages）**：https://voskamp099.github.io/hydroknow/

> > 更新 Demo：改完内容后运行 `bash publish.sh`（重新构建 + 自动推送，约 1-3 分钟生效）

## 简介

为北京沐光氢能科技有限公司构建的智能 AI 客服助手「小知」，解决"市场销售、品牌营销人员不足"的企业痛点。系统基于公司公开资料（宣传册、产品单页），通过 RAG 技术实现知识检索与问答，能协助市场和品牌部开展工作。

## 功能

- **知识库构建**：自动加载企业 PDF 资料，清洗文本，智能分块
- **混合检索**：BM25 + TF-IDF 双路检索，加权融合，中文无需分词器
- **智能问答**：从检索片段提取关键信息，结构化输出答案 + 来源 + 置信度
- **Web 聊天界面**：实时交互问答，展示检索来源与匹配度
- **CLI 批量演示**：预设问题批量跑，生成静态 demo.html
- **LLM 可插拔**：默认离线 stub，接口清晰，一行替换接入真实模型

## 项目结构

```
./
├── app.py                 # Flask Web 应用（一键启动聊天界面）
├── build_static.py        # 纯前端静态 Demo 构建脚本（生成 dist/index.html）
├── dist/
│   └── index.html         # 自包含静态 Demo（语料+检索全内嵌，可任意静态托管）
├── run.py                 # CLI 入口（兼容旧路径）
├── run_cli.py             # CLI 完整实现（批量问答 + 生成 demo.html）
├── rag/                   # RAG 核心引擎
│   ├── __init__.py        # 包入口，导出 RAGEngine
│   ├── loader.py          # PDF 加载 + 文本清洗 + 智能分块
│   ├── retriever.py       # BM25 + TF-IDF 混合检索
│   ├── generator.py       # 答案生成（可插拔 LLM stub）
│   └── pipeline.py        # 管线串联（RAGEngine）
├── templates/
│   └── index.html         # 聊天界面
├── static/
│   ├── style.css          # 深色主题样式
│   └── app.js             # 前端交互逻辑
├── data/                  # 企业 PDF 资料（自包含）
│   ├── 00_企业资料说明.pdf
│   ├── 01 沐光氢能2025产品单页.pdf
│   └── 02 沐光氢能2025宣传册.pdf
├── requirements.txt       # Python 依赖
├── demo.html              # CLI 生成的静态演示页
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

依赖：Flask, pdfminer.six, scikit-learn, numpy（均为常用库，无外部 API）。

### 2. Web 模式（推荐）

```bash
python app.py
```

浏览器打开 `http://127.0.0.1:5000`，在聊天框输入问题或点击左侧推荐问题。

### 3. CLI 模式

```bash
# 批量跑预设问题
python run.py

# 单个问题
python run.py --question "沐光氢能成立于哪一年？"
```

终端打印答案，同时生成 `demo.html`（静态展示页）和 `cli_results.json`（机器可读结果）。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 聊天界面 |
| POST | `/api/ask` | 问答接口，body: `{"question": "..."}` |
| GET | `/api/stats` | 引擎统计（文档数、分块数等） |
| GET | `/api/suggest` | 推荐问题列表 |

### 问答接口示例

```bash
curl -X POST http://127.0.0.1:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "沐光氢能成立于哪一年？"}'
```

返回：
```json
{
  "answer": "根据沐光氢能公开资料，关于「沐光氢能成立于哪一年？」：\n• 成立于2010年",
  "key_points": ["成立于2010年"],
  "sources": [
    {"rank": 1, "doc": "00_企业资料说明.pdf", "score": 0.82, "text": "..."}
  ],
  "confidence": 0.82,
  "question": "沐光氢能成立于哪一年？"
}
```

## 技术架构

```
用户问题
    │
    ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  PDF 加载   │────▶│  文本分块    │────▶│  混合检索     │
│  (pdfminer) │     │  (~400字/块) │     │  BM25+TF-IDF  │
└─────────────┘     └──────────────┘     └───────┬───────┘
                                                 │ top-k 片段
                                                 ▼
                                        ┌───────────────┐
                                        │  答案生成     │
                                        │  (可插拔 LLM) │
                                        └───────┬───────┘
                                                 │
                                                 ▼
                                    答案 + 关键信息 + 来源 + 置信度
```

### 检索策略

- **BM25**：关键词精确匹配，char bigram 分词（中文无需分词器）
- **TF-IDF**：char n-gram (1,2) + 余弦相似度，补充语义模糊匹配
- **融合**：`score = 0.6 × BM25_norm + 0.4 × TF-IDF_norm`，归一化后加权

## 接入真实 LLM

当前答案生成为**离线 stub**（不调用任何 API），从检索片段提取关键句并结构化输出。

接入真实 LLM（如通义千问、DeepSeek、本地 vLLM 等），只需修改 `rag/generator.py` 中的 `generate_answer()` 函数：

```python
def generate_answer(question, retrieved_chunks):
    context = "\n\n".join(c["text"] for c, _ in retrieved_chunks)
    prompt = f"基于以下资料回答问题。\n资料:\n{context}\n\n问题：{question}\n答案："
    answer_text = your_llm_client.chat(prompt)  # 替换为你的 LLM 调用

    return {
        "answer": answer_text,
        "key_points": [...],
        "sources": [...],
        "confidence": ...,
    }
```

接口签名不变，Web / CLI 管线无需修改。

## 数据说明

- 来源：沐光氢能公开发布的 3 份 PDF（企业资料说明 + 产品单页 + 2025 宣传册）
- 敏感性：企业公开资料，可用于比赛展示
- 已知限制：产品单页 PDF 为图片化设计稿，pdfminer 文本抽取为乱码（已自动清洗过滤）；主要有效信息来自企业资料说明和宣传册

## 限制声明

1. **LLM 为 stub**：当前答案生成不调用 LLM，输出为检索片段的结构化提取。接入真实模型后效果显著提升。
2. **知识库较薄**：仅 3 份公开 PDF，信息量有限。实际部署建议扩充 FAQ 库、产品手册、技术文档等。
3. **检索为词法匹配**：BM25 + TF-IDF 为词法级匹配，无语义理解。接入 embedding 模型（如 BGE/M3E）可提升语义检索能力。
4. **无持久化**：每次启动重新加载 PDF 并建索引（约 2-3 秒）。生产环境建议预建向量库。
