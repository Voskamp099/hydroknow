#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业知识与智能服务助手 — Flask Web 应用

一键启动:
  python app.py

然后浏览器打开 http://127.0.0.1:5000

API:
  GET  /             — 聊天界面
  POST /api/ask      — 问答接口 {"question": "..."} -> {"answer", "sources", ...}
  GET  /api/stats    — 引擎统计
  GET  /api/suggest  — 推荐问题列表
"""

import os
import datetime

from flask import Flask, request, jsonify, render_template
from rag import RAGEngine

# ── 配置 ──────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")

app = Flask(__name__, template_folder="templates", static_folder="static")

# 启动时加载 RAG 引擎（只加载一次）
engine = RAGEngine(data_dir=DATA_DIR, top_k=4)
engine.load()

# 推荐问题
SUGGESTED_QUESTIONS = [
    "沐光氢能成立于哪一年？",
    "沐光氢能的主打产品是什么？",
    "沐光氢能的核心技术能力有哪些？",
    "沐光氢能的合作方和客户有哪些？",
    "沐光氢能的官网和联系方式是什么？",
    "沐光氢能的应用场景有哪些？",
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "请输入问题"}), 400

    result = engine.ask(question)
    result["timestamp"] = datetime.datetime.now().strftime("%H:%M:%S")
    return jsonify(result)


@app.route("/api/stats")
def api_stats():
    return jsonify(engine.stats())


@app.route("/api/suggest")
def api_suggest():
    return jsonify({"questions": SUGGESTED_QUESTIONS})


if __name__ == "__main__":
    print(f"\n{'='*50}")
    print("  企业知识与智能服务助手")
    print("  浏览器打开: http://127.0.0.1:5000")
    print(f"{'='*50}\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
