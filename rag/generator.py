"""
答案生成模块

默认为离线 stub：从检索到的片段中提取最相关句子，结构化输出。
不调用任何 LLM / 云 API。

接入真实 LLM 时，替换 generate_answer() 的实现即可，
接口签名 (question, retrieved_chunks) -> str 保持不变。
"""

import re


def _split_sentences(text):
    """中文/英文句子切分。"""
    # 按中文句号、问号、感叹号 + 英文句号切
    sentences = re.split(r"[。！？.!?\n]+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def _extract_key_sentences(question, retrieved_chunks, max_sentences=3):
    """从检索到的片段中提取与问题最相关的句子。

    策略: 取与问题字符重叠最多的句子。
    """
    # 提取问题中的关键词（2-gram）
    q_chars = set(question.replace(" ", "").lower())
    candidates = []
    for chunk, score in retrieved_chunks:
        sentences = _split_sentences(chunk["text"])
        for sent in sentences:
            s_chars = set(sent.lower())
            overlap = len(q_chars & s_chars)
            if overlap > 0:
                candidates.append((sent, overlap, score, chunk["doc"]))
    # 按重叠数排序
    candidates.sort(key=lambda x: (-x[1], -x[2]))
    # 去重
    seen = set()
    selected = []
    for sent, _, score, doc in candidates:
        if sent in seen:
            continue
        seen.add(sent)
        selected.append((sent, score, doc))
        if len(selected) >= max_sentences:
            break
    return selected


def generate_answer(question, retrieved_chunks):
    """从检索片段生成结构化答案。

    ===== 离线 STUB（不调用 LLM）=====

    接入真实 LLM 时，替换此函数体：
        context = "\\n\\n".join(c["text"] for c, _ in retrieved_chunks)
        prompt = f"基于以下资料回答问题。\\n资料:\\n{context}\\n\\n问题：{question}\\n答案："
        return your_llm_client.chat(prompt)   # OpenAI / 通义千问 / 本地 vLLM 等

    接口签名不变，其余管线无需修改。
    """
    if not retrieved_chunks:
        return {
            "answer": "未检索到相关内容。请确认知识库是否包含该信息，或尝试换个问法。",
            "key_points": [],
            "sources": [],
            "confidence": 0.0,
        }

    # 提取关键句
    key_sents = _extract_key_sentences(question, retrieved_chunks)

    # 组装答案文本
    if key_sents:
        answer_parts = [f"根据沐光氢能公开资料，关于「{question}」："]
        for sent, _, _ in key_sents:
            answer_parts.append(f"• {sent}")
        answer_text = "\n".join(answer_parts)
    else:
        # 回退：直接取最高分片段的前 200 字
        top_chunk = retrieved_chunks[0][0]
        snippet = top_chunk["text"][:200].replace("\n", " ")
        answer_text = f"根据资料检索，最相关的信息如下：\n• {snippet}"

    # 来源信息
    sources = []
    for rank, (chunk, score) in enumerate(retrieved_chunks, 1):
        sources.append({
            "rank": rank,
            "doc": chunk["doc"],
            "chunk_id": chunk["chunk_id"],
            "score": round(score, 4),
            "text": chunk["text"][:300] + ("..." if len(chunk["text"]) > 300 else ""),
        })

    # 置信度：基于最高检索分数
    confidence = round(retrieved_chunks[0][1], 4) if retrieved_chunks else 0.0

    return {
        "answer": answer_text,
        "key_points": [s[0] for s in key_sents],
        "sources": sources,
        "confidence": confidence,
    }
