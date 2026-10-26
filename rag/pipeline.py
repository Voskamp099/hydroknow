"""
RAG 管线串联模块

RAGEngine 封装: 加载 PDF -> 分块 -> 建索引 -> 检索 -> 生成答案
启动时加载一次，后续查询复用索引。
"""

import os
import json

from .loader import load_documents, split_into_chunks
from .retriever import HybridRetriever, DEFAULT_TOP_K
from .generator import generate_answer


class RAGEngine:
    """企业知识 RAG 引擎"""

    def __init__(self, data_dir=None, top_k=DEFAULT_TOP_K):
        """初始化引擎：加载 PDF、分块、建索引。

        Args:
            data_dir: PDF 数据目录（默认: 同级 ../data/）
            top_k: 检索返回的片段数
        """
        if data_dir is None:
            here = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(here, "..", "data")

        self.data_dir = os.path.abspath(data_dir)
        self.top_k = top_k
        self.chunks = []
        self.retriever = None
        self._loaded = False

    def load(self):
        """加载 PDF 并构建索引（启动时调用一次）。"""
        print(f"[RAG] 加载资料: {self.data_dir}")
        records = load_documents(self.data_dir)
        total_chars = sum(len(t) for _, t in records)
        print(f"[RAG] 共 {len(records)} 个文档, {total_chars} 字符")

        print("[RAG] 分块中 ...")
        self.chunks = split_into_chunks(records)
        print(f"[RAG] 生成 {len(self.chunks)} 个文本块")

        print("[RAG] 构建混合检索索引 (BM25 + TF-IDF) ...")
        self.retriever = HybridRetriever(self.chunks, top_k=self.top_k)
        self._loaded = True
        print(f"[RAG] 就绪 — 共 {len(self.chunks)} 块, top_k={self.top_k}")

    def ask(self, question):
        """问答接口。

        Args:
            question: 用户问题（字符串）

        Returns:
            dict: {answer, key_points, sources, confidence}
        """
        if not self._loaded:
            self.load()
        retrieved = self.retriever.retrieve(question)
        result = generate_answer(question, retrieved)
        result["question"] = question
        return result

    def ask_batch(self, questions):
        """批量问答。"""
        return [self.ask(q) for q in questions]

    def stats(self):
        """返回引擎统计信息。"""
        return {
            "total_docs": len({c["doc"] for c in self.chunks}),
            "total_chunks": len(self.chunks),
            "top_k": self.top_k,
            "data_dir": self.data_dir,
            "loaded": self._loaded,
        }
