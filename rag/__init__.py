"""
RAG 引擎包 —— 企业知识与智能服务助手

模块:
  loader     — PDF 加载、文本清洗、智能分块
  retriever  — BM25 + TF-IDF 混合检索
  generator  — 答案生成（可插拔 LLM 接口）
"""

from .pipeline import RAGEngine

__all__ = ["RAGEngine"]
