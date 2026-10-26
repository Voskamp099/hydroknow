"""
文档加载与分块模块

职责:
  1. 读取 data/ 下的 PDF 文件，抽取纯文本
  2. 清洗乱码段落（pdfminer 对图片化 PDF 会产出替换字符）
  3. 按段落智能分块，保留语义边界
"""

import os
import re

try:                       # PDF 支持是可选的
    import fitz            # PyMuPDF
except ImportError:        # pragma: no cover - 没有 PyMuPDF 时仍可用文本语料
    fitz = None

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


def _repair_pua_digits(text):
    """修复 PDF 字体把数字映射到 Unicode 私有区（PUA）的乱码。

    现象: "成立于 2010 年" 抽出为 "成立于  年"。
    原因: 该 PDF 嵌入字体把数字 0-9 编码到了连续的 PUA 字符 (U+F6B1..U+F6BA)。
    解法: 将这 10 个连续 PUA 字符映射回 '0'..'9'，其他 PUA 直接删除。
    验证: 成立于  →  "2010" 年。
    """
    # 数字 0-9: PUA 偏移 \uf6b1..\uf6ba
    digit_map = {0xf6b1 + i: str(i) for i in range(10)}
    out_chars = []
    for ch in text:
        cp = ord(ch)
        if cp in digit_map:
            out_chars.append(digit_map[cp])
        elif 0xE000 <= cp <= 0xF8FF:
            # 其他 PUA 字符（乱码）直接丢弃
            continue
        else:
            out_chars.append(ch)
    return "".join(out_chars)


def _clean_text(text):
    """清洗 pdfminer 抽出的文本：修复 PUA 数字乱码、去多余空白、过滤乱码行。"""
    text = _repair_pua_digits(text)
    lines = []
    for line in text.replace("\r", "\n").split("\n"):
        line = line.strip()
        # 去掉 Markdown 标题标记，保留标题文字
        line = re.sub(r"^#{1,6}\s*", "", line)
        if not line:
            continue
        if _is_garbage(line):
            continue
        # 去掉连续重复的页码标记（如 "Page 1-1"）
        if re.match(r"^(Page\s*)?\d+[-–]\d+$", line):
            continue
        lines.append(line)
    return "\n".join(lines)


TEXT_SUFFIXES = (".md", ".markdown", ".txt")


def _read_pdf(path):
    """抽取 PDF 文本。缺少 PyMuPDF 时返回空串并提示。"""
    if fitz is None:
        print("  [warn] 未安装 PyMuPDF，跳过 PDF: " + os.path.basename(path))
        return ""
    raw = ""
    try:
        doc = fitz.open(path)
        for page in doc:
            raw += page.get_text()
        doc.close()
    except Exception as e:
        print(f"  [warn] 抽取失败 {os.path.basename(path)}: {e}")
    return raw


def _read_markdown(path):
    """读取 Markdown：把标题并入它下面的正文，避免标题单独成句被当成答案要点。"""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    out = []
    pending = ""
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        heading = re.match(r"^#{1,6}\s*(.+)$", line)
        if heading:
            pending = heading.group(1).strip() + "："
            continue
        if pending:
            out.append(pending + line)
            pending = ""
        else:
            out.append(line)
    if pending:
        out.append(pending)
    return "\n".join(out)


def load_documents(data_dir):
    """读取 data_dir 下的文档，返回 [(filename, cleaned_text), ...]。

    支持三类来源：PDF（需要 PyMuPDF）、Markdown 和纯文本。文本文件直接读取，
    不经过 PDF 抽取的乱码清洗；PDF 抽取使用 PyMuPDF 而非 pdfminer，
    因为 pdfminer 遇到字体无 ToUnicode 映射时会把数字替换成 U+FFFD 不可逆丢失。
    """
    records = []
    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"数据目录不存在: {data_dir}")
    for name in sorted(os.listdir(data_dir)):
        path = os.path.join(data_dir, name)
        if not os.path.isfile(path):
            continue
        lower = name.lower()
        if lower.endswith(".pdf"):
            raw = _read_pdf(path)
        elif lower.endswith((".md", ".markdown")):
            try:
                raw = _read_markdown(path)
            except Exception as e:
                print(f"  [warn] 读取失败 {name}: {e}")
                continue
        elif lower.endswith(".txt"):
            try:
                with open(path, encoding="utf-8") as fh:
                    raw = fh.read()
            except Exception as e:
                print(f"  [warn] 读取失败 {name}: {e}")
                continue
        else:
            continue
        cleaned = _clean_text(raw)
        records.append((name, cleaned))
        print(f"  [load] {name}: {len(raw)} -> {len(cleaned)} chars (清洗后)")
    return records


# 旧名保留为别名，避免外部调用方失效
load_pdfs = load_documents


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
