#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业知识与智能服务助手 — CLI 模式

批量跑预设问题，终端打印答案 + 生成静态 demo.html。

用法:
  python run_cli.py
  python run_cli.py --question "沐光氢能成立于哪一年？"
"""

import os
import sys
import html
import json
import argparse
import datetime

# 确保能 import rag 包
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from rag import RAGEngine

DATA_DIR = os.path.join(HERE, "data")
DEMO_HTML = os.path.join(HERE, "demo.html")

PRESET_QUESTIONS = [
    "沐光氢能成立于哪一年？",
    "沐光氢能的主打产品是什么？",
    "沐光氢能的核心技术能力有哪些？",
    "沐光氢能的合作方和客户有哪些？",
    "沐光氢能的官网和联系方式是什么？",
    "沐光氢能的应用场景有哪些？",
]


def run_batch(engine, questions):
    """批量跑问题，返回结果列表。"""
    results = []
    for i, q in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"Q{i}: {q}")
        print(f"{'-'*60}")
        r = engine.ask(q)
        print(r["answer"])
        if r["sources"]:
            print(f"\n  来源:")
            for s in r["sources"]:
                print(f"    [{s['rank']}] {s['doc']} (score={s['score']})")
        results.append(r)
    return results


def render_demo_html(results):
    """生成静态 demo.html（用于离线展示 / 提交附件）。"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cards = []
    for i, r in enumerate(results, 1):
        sources_html = ""
        for s in r.get("sources", []):
            snippet = html.escape(s["text"])
            sources_html += (
                f'<div class="source-card">'
                f'<div class="source-meta">'
                f'<span>来源 {s["rank"]} · {html.escape(s["doc"])}</span>'
                f'<span class="source-score">{s["score"]*100:.1f}%</span>'
                f'</div>'
                f'<div class="source-text">{snippet}</div>'
                f'</div>\n'
            )
        answer_html = html.escape(r["answer"]).replace("\n", "<br>")
        cards.append(
            f'<div class="qa-card">'
            f'<div class="qa-q">{i}. {html.escape(r["question"])}</div>'
            f'<div class="qa-a">{answer_html}</div>'
            f'<div class="qa-confidence">置信度 {r["confidence"]}</div>'
            f'<div class="qa-sources-title">检索来源</div>'
            f'{sources_html}'
            f'</div>\n'
        )

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>企业知识与智能服务助手 · Demo</title>
<style>
  :root {{ --bg:#0f1117; --card:#252836; --border:#2d3142; --ink:#e4e6ef;
          --muted:#8b90a0; --accent:#0a6e4f; --accent-light:#0d9070; }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:var(--bg); color:var(--ink);
         font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
         line-height:1.6; font-size:14px; }}
  header {{ background:var(--accent); padding:28px 24px; }}
  header h1 {{ font-size:20px; color:#fff; }}
  header p {{ font-size:13px; color:rgba(255,255,255,0.85); margin-top:4px; }}
  main {{ max-width:800px; margin:24px auto; padding:0 16px 48px; }}
  .qa-card {{ background:var(--card); border:1px solid var(--border);
              border-radius:12px; padding:18px 20px; margin-bottom:20px; }}
  .qa-q {{ font-weight:700; font-size:16px; margin-bottom:12px; }}
  .qa-a {{ white-space:pre-wrap; background:rgba(255,255,255,0.03);
          border-radius:8px; padding:12px 14px; }}
  .qa-confidence {{ display:inline-block; font-size:11px; color:var(--muted);
                   margin-top:8px; padding:2px 8px; background:rgba(255,255,255,0.05);
                   border-radius:4px; }}
  .qa-sources-title {{ margin:16px 0 8px; font-size:12px; color:var(--muted);
                       font-weight:600; }}
  .source-card {{ border-left:3px solid var(--accent); background:rgba(255,255,255,0.03);
                  border-radius:6px; padding:10px 12px; margin-bottom:10px; }}
  .source-meta {{ display:flex; justify-content:space-between; font-size:11px;
                  color:var(--muted); margin-bottom:6px; }}
  .source-score {{ color:var(--accent-light); font-weight:600; }}
  .source-text {{ font-size:12px; white-space:pre-wrap; max-height:120px; overflow-y:auto; }}
  footer {{ text-align:center; color:var(--muted); font-size:12px; padding:18px; }}
</style>
</head>
<body>
<header>
  <h1>氢知 · 企业知识与智能服务助手（沐光氢能）</h1>
  <p>RAG Demo · BM25 + TF-IDF 混合检索 · 生成于 {now}</p>
</header>
<main>
{"".join(cards)}
</main>
<footer>答案生成为离线 stub（未调用 LLM）。接入真实模型后效果更佳。</footer>
</body>
</html>"""
    with open(DEMO_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"\n[demo] 已生成 {DEMO_HTML}")


def main():
    ap = argparse.ArgumentParser(description="企业知识助手 CLI")
    ap.add_argument("--question", "-q", type=str, help="单个问题")
    ap.add_argument("--data", type=str, default=DATA_DIR, help="PDF 数据目录")
    args = ap.parse_args()

    engine = RAGEngine(data_dir=args.data, top_k=4)
    engine.load()

    print(f"\n{'='*60}")
    print(f"  企业知识与智能服务助手 · CLI 模式")
    print(f"  文档: {engine.stats()['total_docs']} | 分块: {engine.stats()['total_chunks']}")
    print(f"{'='*60}")

    if args.question:
        questions = [args.question]
    else:
        questions = PRESET_QUESTIONS

    results = run_batch(engine, questions)

    # 生成 demo.html
    render_demo_html(results)

    # 存 JSON
    json_path = os.path.join(HERE, "cli_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[json] 已保存 {json_path}")
    print(f"\n[done] 完成。Web 模式请运行: python app.py")


if __name__ == "__main__":
    main()
