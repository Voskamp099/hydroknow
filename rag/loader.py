"""
文档加载与分块模块

职责:
  1. 读取 data/ 下的 PDF 文件，抽取纯文本
  2. 清洗乱码段落（pdfminer 对图片化 PDF 会产出替换字符）
  3. 按段落智能分块，保留语义边界
"""

import os
import re
from pdfminer.high_level import extract_text

# ── 分块参数 ──────────────────────────────────────────────
CHUNK_TARGET = 400      # 目标块长度（字符）
CHUNK_MIN = 80          # 最小块长度；短于此则合并到前一块
CHUNK_MAX = 600         # 单块上限，超出则强制切
# 乱码判定：替换字符占比超过此阈值则丢弃
GARBAGE_RATIO = 0.3


def _is_garbage(text):
    """判断一段文本是否为乱码（替换字符占比过高）。"""
    if not text or len(text.strip()) < 5:
        return True
    bad = sum(1 for c in text if c in "\ufffd\u0000" or ord(c) < 9)
    return bad / len(text) > GARBAGE_RATIO


def _clean_text(text):
    """清洗 pdfminer 抽出的文本：去多余空白、过滤乱码行。"""
    lines = []
    for line in text.replace("\r", "\n").split("\n"):
        line = line.strip()
        if not line:
            continue
        if _is_garbage(line):
            continue
        # 去掉连续重复的页码标记（如 "Page 1-1"）
        if re.match(r"^(Page\s*)?\d+[-–]\d+$", line):
            continue
        lines.append(line)
    return "\n".join(lines)


def load_pdfs(data_dir):
    """读取 data_dir 下所有 PDF，返回 [(filename, cleaned_text), ...]。"""
    records = []
    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"数据目录不存在: {data_dir}")
    for name in sorted(os.listdir(data_dir)):
        if not name.lower().endswith(".pdf"):
            continue
        path = os.path.join(data_dir, name)
        try:
            raw = extract_text(path)
        except Exception as e:
            print(f"  [warn] 抽取失败 {name}: {e}")
            raw = ""
        cleaned = _clean_text(raw)
        records.append((name, cleaned))
        print(f"  [load] {name}: {len(raw)} -> {len(cleaned)} chars (清洗后)")
    return records


def split_into_chunks(records):
    """将文档按段落分块。

    策略:
      - 逐段落累积，到达 CHUNK_TARGET 时输出一个块
      - 单段超 CHUNK_MAX 时按目标长度切
      - 尾部短块合并到前一块

    返回 [{"doc", "chunk_id", "text"}, ...]
    """
    chunks = []
    for doc_name, text in records:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        buf = ""
        cid = 0
        for p in paragraphs:
            # 累积到目标长度
            if buf and len(buf) + len(p) > CHUNK_TARGET:
                chunks.append({"doc": doc_name, "chunk_id": cid, "text": buf})
                cid += 1
                buf = p
            else:
                buf = f"{buf}\n{p}".strip() if buf else p
            # 超长强制切
            while len(buf) > CHUNK_MAX:
                cut = buf[:CHUNK_TARGET]
                chunks.append({"doc": doc_name, "chunk_id": cid, "text": cut})
                cid += 1
                buf = buf[CHUNK_TARGET:].strip()
        # 尾部
        if buf:
            if len(buf) < CHUNK_MIN and chunks and chunks[-1]["doc"] == doc_name:
                # 合并到前一块
                chunks[-1]["text"] = f"{chunks[-1]['text']}\n{buf}".strip()
            else:
                chunks.append({"doc": doc_name, "chunk_id": cid, "text": buf})
    return chunks
