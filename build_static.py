#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
氢知 HydroKnow · 静态 Demo 构建脚本

把 RAG 语料（15 个文本块）内嵌进一个纯前端 HTML，
检索算法（BM25 char-bigram + TF-IDF char 1-2gram 混合）在浏览器里等价复刻，
无需任何后端即可交互问答 —— 用于公网部署演示。

用法:
  python build_static.py          # 生成 dist/index.html
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rag import RAGEngine  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
DIST = os.path.join(HERE, "dist")


def build():
    # 1. 加载引擎导出语料块
    engine = RAGEngine(data_dir=DATA_DIR, top_k=4)
    engine.load()
    chunks = [
        {"doc": c["doc"], "chunk_id": c["chunk_id"], "text": c["text"]}
        for c in engine.chunks
    ]

    # 2. 生成静态页
    html = HTML_TEMPLATE.replace("__CHUNKS_JSON__", json.dumps(chunks, ensure_ascii=False))
    html = html.replace("__SUGGEST_JSON__", json.dumps(SUGGESTED, ensure_ascii=False))

    os.makedirs(DIST, exist_ok=True)
    out = os.path.join(DIST, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] {out}  ({len(html)//1024} KB, {len(chunks)} chunks embedded)")


SUGGESTED = [
    "沐光氢能成立于哪一年？",
    "沐光氢能的主打产品是什么？",
    "沐光氢能的核心技术能力有哪些？",
    "沐光氢能的合作方和客户有哪些？",
    "沐光氢能的官网和联系方式是什么？",
    "沐光氢能的应用场景有哪些？",
]

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>氢知 HydroKnow · 沐光氢能企业知识智能服务助手</title>
<style>
:root {
  --bg: #0f1117; --surface: #171922; --card: #1c1f2b; --border: #2d3142;
  --ink: #e4e6ef; --muted: #8b90a0; --accent: #0a8e6f; --accent-light: #0da884;
  --accent-glow: rgba(10,142,111,0.15); --radius: 12px;
  --font: -apple-system, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--ink); font-family: var(--font); font-size: 15px; line-height: 1.6; min-height: 100vh; }
.qa-page { max-width: 760px; margin: 0 auto; padding: 48px 24px 80px; }
.qa-header { text-align: center; margin-bottom: 40px; }
.qa-logo { display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 8px; }
.qa-logo-icon { font-size: 28px; }
.qa-logo h1 { font-size: 24px; font-weight: 700; }
.qa-logo h1 .en { color: var(--accent-light); font-size: 16px; font-weight: 600; margin-left: 8px; }
.qa-subtitle { font-size: 13px; color: var(--muted); margin-bottom: 28px; }
.qa-search-box { display: flex; border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; transition: border-color .2s; background: var(--surface); }
.qa-search-box:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }
.qa-search-box input { flex: 1; background: transparent; border: none; padding: 14px 18px; color: var(--ink); font-size: 15px; font-family: var(--font); outline: none; }
.qa-search-box input::placeholder { color: var(--muted); }
.qa-search-box button { background: var(--accent); color: #fff; border: none; padding: 0 28px; font-size: 15px; font-weight: 600; font-family: var(--font); cursor: pointer; transition: background .2s; }
.qa-search-box button:hover { background: var(--accent-light); }
.qa-chips { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-top: 16px; }
.chip { padding: 6px 14px; background: var(--card); border: 1px solid var(--border); border-radius: 20px; font-size: 13px; color: var(--muted); cursor: pointer; transition: all .2s; }
.chip:hover { border-color: var(--accent); color: var(--ink); background: var(--accent-glow); }
.qa-status { margin-top: 14px; font-size: 12px; color: var(--muted); }
.qa-status .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--accent); margin-right: 6px; vertical-align: middle; }
.qa-result { min-height: 300px; }
.qa-placeholder { text-align: center; padding: 60px 20px; color: var(--muted); }
.placeholder-icon { font-size: 40px; margin-bottom: 12px; }
.answer-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; margin-bottom: 20px; animation: fadeIn .3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.answer-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 18px; border-bottom: 1px solid var(--border); background: var(--surface); gap: 12px; }
.answer-header .q { font-size: 13px; color: var(--muted); text-align: left; }
.answer-header .q b { color: var(--ink); }
.answer-header .conf { font-size: 12px; padding: 3px 10px; border-radius: 6px; font-weight: 600; white-space: nowrap; }
.conf-high { background: rgba(10,142,111,.2); color: var(--accent-light); }
.conf-mid { background: rgba(204,170,50,.2); color: #ccaa32; }
.conf-low { background: rgba(196,69,69,.2); color: #c44545; }
.answer-body { padding: 18px; }
.answer-body .answer-text { font-size: 15px; line-height: 1.75; margin-bottom: 16px; }
.key-points { margin-bottom: 16px; }
.key-points-title { font-size: 13px; font-weight: 600; color: var(--muted); margin-bottom: 8px; }
.key-points ul { list-style: none; padding: 0; }
.key-points li { padding: 4px 0 4px 16px; position: relative; font-size: 14px; }
.key-points li::before { content: "▸"; position: absolute; left: 0; color: var(--accent); }
.sources-section { border-top: 1px solid var(--border); padding: 16px 18px; }
.sources-title { font-size: 12px; color: var(--muted); margin-bottom: 12px; letter-spacing: .5px; }
.source-item { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent); border-radius: 8px; padding: 12px 14px; margin-bottom: 10px; transition: border-color .2s; }
.source-item:hover { border-color: var(--accent); }
.source-item:last-child { margin-bottom: 0; }
.source-meta { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
.source-meta-left { display: flex; align-items: center; min-width: 0; }
.source-badge { flex-shrink: 0; width: 20px; height: 20px; border-radius: 6px; background: var(--accent); color: #fff; font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; margin-right: 8px; }
.source-doc { font-size: 12px; color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.source-score { font-size: 11px; color: var(--accent-light); font-weight: 600; white-space: nowrap; }
.source-text { font-size: 12.5px; color: var(--ink); line-height: 1.7; white-space: pre-wrap; max-height: 96px; overflow: hidden; position: relative; }
.source-text.expanded { max-height: none; }
.source-text:not(.expanded)::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 28px; background: linear-gradient(transparent, var(--surface)); pointer-events: none; }
.source-toggle { display: none; margin-top: 8px; font-size: 11px; color: var(--accent-light); background: none; border: none; cursor: pointer; padding: 0; font-family: var(--font); }
.source-toggle.show { display: inline-block; }
.source-toggle:hover { text-decoration: underline; }
mark { background: rgba(10,142,111,.35); color: #c9f7ea; padding: 0 1px; border-radius: 2px; }
.footer-note { text-align: center; font-size: 11px; color: var(--muted); margin-top: 40px; line-height: 1.8; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
</head>
<body>
<div class="qa-page">
  <header class="qa-header">
    <div class="qa-logo">
      <span class="qa-logo-icon">H₂</span>
      <h1>氢知 <span class="en">HydroKnow</span></h1>
    </div>
    <p class="qa-subtitle">沐光氢能企业知识智能服务助手 · RAG 检索增强 · 纯前端离线运行</p>
    <div class="qa-search-box">
      <input type="text" id="input" placeholder="我是小知，问点什么吧，比如：沐光氢能的主打产品是什么？" autocomplete="off" autofocus>
      <button id="sendBtn" onclick="ask()">提问</button>
    </div>
    <div class="qa-chips" id="chips"></div>
    <div class="qa-status" id="status"></div>
  </header>

  <main class="qa-result" id="result">
    <div class="qa-placeholder" id="placeholder">
      <div class="placeholder-icon">💬</div>
      <p>输入问题，小知会从沐光氢能的企业资料中检索答案，并附上原文来源。</p>
    </div>
  </main>

  <div class="footer-note">
    企业知识与智能服务助手 · 自建样例语料原型<br>
    知识库：仓库内自建的虚构样例语料 · BM25 + TF-IDF 混合检索 · 全部计算在浏览器本地完成
  </div>
</div>

<script>
// ══════════════════════════════════════════════════════════
// 氢知 HydroKnow · 纯前端 RAG（与 Python 版 rag/ 逐行等价）
// ══════════════════════════════════════════════════════════
const CHUNKS = __CHUNKS_JSON__;
const SUGGEST = __SUGGEST_JSON__;
const BM25_WEIGHT = 0.6, TFIDF_WEIGHT = 0.4, TOP_K = 4;
const K1 = 1.5, B = 0.75;

// ── char bigram 分词（与 retriever.py BM25Okapi._tokenize 一致）──
function tokenize(text) {
  text = text.toLowerCase().trim();
  if (text.length < 2) return text ? [text] : [];
  const out = [];
  for (let i = 0; i < text.length - 1; i++) out.push(text.slice(i, i + 2));
  return out;
}

// ── char 1-2gram（与 TfidfVectorizer(analyzer='char', ngram_range=(1,2)) 近似）──
function ngrams(text) {
  text = text.toLowerCase();
  const out = [];
  for (let i = 0; i < text.length; i++) {
    out.push(text.slice(i, i + 1));
    if (i < text.length - 1) out.push(text.slice(i, i + 2));
  }
  return out;
}

// ── BM25 索引 ─────────────────────────────────────────────
const tokenized = CHUNKS.map(c => tokenize(c.text));
const docLen = tokenized.map(t => t.length);
const avgdl = docLen.reduce((a, b) => a + b, 0) / docLen.length;
const tf = tokenized.map(tokens => {
  const f = {};
  for (const t of tokens) f[t] = (f[t] || 0) + 1;
  return f;
});
const df = {};
for (const f of tf) for (const t in f) df[t] = (df[t] || 0) + 1;
const N = CHUNKS.length;
const idf = {};
for (const t in df) idf[t] = Math.log((N - df[t] + 0.5) / (df[t] + 0.5) + 1);

function bm25Scores(query) {
  const qTokens = tokenize(query);
  const scores = new Array(N).fill(0);
  for (let i = 0; i < N; i++) {
    if (docLen[i] === 0) continue;
    let s = 0;
    for (const qt of qTokens) {
      if (!(qt in idf)) continue;
      const tfi = tf[i][qt] || 0;
      if (tfi === 0) continue;
      const denom = tfi + K1 * (1 - B + B * docLen[i] / avgdl);
      s += idf[qt] * tfi * (K1 + 1) / denom;
    }
    scores[i] = s;
  }
  return scores;
}

// ── TF-IDF 余弦相似度（l2 归一化，smooth idf）─────────────
const docVecs = CHUNKS.map(c => {
  const grams = ngrams(c.text);
  const v = {};
  for (const g of grams) v[g] = (v[g] || 0) + 1;
  // smooth idf: ln((1+N)/(1+df)) + 1
  for (const g in v) v[g] *= (Math.log((1 + N) / (1 + (df[g] || 0))) + 1);
  // l2 normalize
  let norm = 0;
  for (const g in v) norm += v[g] * v[g];
  norm = Math.sqrt(norm) || 1;
  for (const g in v) v[g] /= norm;
  return v;
});

function tfidfScores(query) {
  const grams = ngrams(query);
  const qv = {};
  for (const g of grams) qv[g] = (qv[g] || 0) + 1;
  for (const g in qv) qv[g] *= (Math.log((1 + N) / (1 + (df[g] || 0))) + 1);
  let norm = 0;
  for (const g in qv) norm += qv[g] * qv[g];
  norm = Math.sqrt(norm) || 1;
  for (const g in qv) qv[g] /= norm;

  const scores = new Array(N).fill(0);
  for (let i = 0; i < N; i++) {
    let dot = 0;
    for (const g in qv) if (docVecs[i][g]) dot += qv[g] * docVecs[i][g];
    scores[i] = dot;
  }
  return scores;
}

// ── 混合检索（与 HybridRetriever.retrieve 一致）──────────
function retrieve(question) {
  const bm = bm25Scores(question);
  const bmMax = Math.max(...bm);
  const bmNorm = bmMax > 0 ? bm.map(s => s / bmMax) : bm;
  const tf_ = tfidfScores(question);
  const tfMax = Math.max(...tf_);
  const tfNorm = tfMax > 0 ? tf_.map(s => s / tfMax) : tf_;

  const hybrid = bmNorm.map((s, i) => BM25_WEIGHT * s + TFIDF_WEIGHT * tfNorm[i]);
  const order = hybrid.map((s, i) => [s, i]).sort((a, b) => b[0] - a[0]);
  const results = [];
  for (const [score, idx] of order.slice(0, TOP_K)) {
    if (score <= 0) continue;
    results.push({ chunk: CHUNKS[idx], score });
  }
  return results;
}

// ── 答案生成（与 generator.py stub 逐行等价）─────────────
function splitSentences(text) {
  const parts = text.split(/[。！？.!?\n]+/);
  return parts.map(s => s.trim()).filter(s => s.length > 10);
}

function extractKeySentences(question, retrieved, maxSents) {
  maxSents = maxSents || 3;
  const qChars = new Set(question.replace(/\s/g, '').toLowerCase());
  const candidates = [];
  for (const { chunk, score } of retrieved) {
    for (const sent of splitSentences(chunk.text)) {
      const sChars = new Set(sent.toLowerCase());
      let overlap = 0;
      for (const c of qChars) if (sChars.has(c)) overlap++;
      if (overlap > 0) candidates.push({ sent, overlap, score, doc: chunk.doc });
    }
  }
  candidates.sort((a, b) => b.overlap - a.overlap || b.score - a.score);
  const seen = new Set(), selected = [];
  for (const c of candidates) {
    if (seen.has(c.sent)) continue;
    seen.add(c.sent);
    selected.push(c);
    if (selected.length >= maxSents) break;
  }
  return selected;
}

function generateAnswer(question, retrieved) {
  if (!retrieved.length) {
    return { answer: '未检索到相关内容。请确认知识库是否包含该信息，或尝试换个问法。', key_points: [], sources: [], confidence: 0 };
  }
  const keySents = extractKeySentences(question, retrieved);
  let answerText;
  if (keySents.length) {
    answerText = '根据知识库资料，关于「' + question + '」：\n' + keySents.map(s => '• ' + s.sent).join('\n');
  } else {
    answerText = '根据资料检索，最相关的信息如下：\n• ' + retrieved[0].chunk.text.slice(0, 200).replace(/\n/g, ' ');
  }
  const sources = retrieved.map((r, i) => ({
    rank: i + 1, doc: r.chunk.doc, chunk_id: r.chunk.chunk_id, score: r.score,
    text: r.chunk.text.slice(0, 300) + (r.chunk.text.length > 300 ? '...' : '')
  }));
  return { answer: answerText, key_points: keySents.map(s => s.sent), sources, confidence: retrieved[0].score };
}

// ── UI 逻辑（与 Flask 版 app.js 一致）────────────────────
const input = document.getElementById('input');
const sendBtn = document.getElementById('sendBtn');
const result = document.getElementById('result');
const placeholder = document.getElementById('placeholder');
const chipsEl = document.getElementById('chips');
const statusEl = document.getElementById('status');

function init() {
  SUGGEST.forEach(q => {
    const chip = document.createElement('div');
    chip.className = 'chip';
    chip.textContent = q;
    chip.onclick = () => { input.value = q; ask(); };
    chipsEl.appendChild(chip);
  });
  const docs = new Set(CHUNKS.map(c => c.doc));
  statusEl.innerHTML = '<span class="dot"></span>引擎就绪 · 文档 ' + docs.size + ' · 分块 ' + CHUNKS.length + ' · 纯前端计算';
}

function ask() {
  const q = input.value.trim();
  if (!q) return;
  if (placeholder) placeholder.style.display = 'none';

  const t0 = performance.now();
  const retrieved = retrieve(q);
  const data = generateAnswer(q, retrieved);
  const ms = (performance.now() - t0).toFixed(1);

  renderAnswer(q, data, ms);
  input.value = '';
  input.focus();
}

function renderAnswer(question, data, ms) {
  const conf = data.confidence || 0;
  let confClass = 'conf-low', confLabel = '低';
  if (conf >= 0.7) { confClass = 'conf-high'; confLabel = '高'; }
  else if (conf >= 0.4) { confClass = 'conf-mid'; confLabel = '中'; }

  const card = document.createElement('div');
  card.className = 'answer-card';
  let html = '<div class="answer-header">' +
    '<span class="q">问：<b>' + esc(question) + '</b></span>' +
    '<span class="conf ' + confClass + '">置信度 ' + confLabel + ' ' + Math.round(conf * 100) + '% · ' + ms + 'ms</span>' +
    '</div><div class="answer-body"><div class="answer-text">' + esc(data.answer).replace(/\n/g, '<br>') + '</div>';
  if (data.key_points.length) {
    html += '<div class="key-points"><div class="key-points-title">关键信息</div><ul>' +
      data.key_points.map(k => '<li>' + esc(k) + '</li>').join('') + '</ul></div>';
  }
  html += '</div>';
  if (data.sources.length) {
    const grams = sourceKeywords(question);
    html += '<div class="sources-section"><div class="sources-title">📄 参考来源（' + data.sources.length + '，按相关度排序）</div>' +
      data.sources.map(s =>
        '<div class="source-item"><div class="source-meta">' +
        '<span class="source-meta-left"><span class="source-badge">' + s.rank + '</span><span class="source-doc">' + esc(s.doc) + '</span></span>' +
        '<span class="source-score">匹配 ' + (s.score * 100).toFixed(1) + '%</span></div>' +
        '<div class="source-text">' + highlight(esc(s.text), grams) + '</div>' +
        '<button class="source-toggle" onclick="toggleSource(this)">展开全文 ▾</button></div>'
      ).join('') + '</div>';
    requestAnimationFrame(() => {
      card.querySelectorAll('.source-item').forEach(item => {
        const text = item.querySelector('.source-text');
        const btn = item.querySelector('.source-toggle');
        if (text.scrollHeight > text.clientHeight + 4) btn.classList.add('show');
      });
    });
  }
  card.innerHTML = html;
  result.prepend(card);
}

function esc(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }

// ── 来源：命中词高亮 + 折叠（与 Flask 版 app.js 一致）──
function sourceKeywords(question) {
  const cleaned = question.replace(/[\s，。！？、,.!?；;：:"'“”‘’（()）【】《》]/g, '');
  if (cleaned.length < 2) return [];
  const grams = [];
  for (let i = 0; i < cleaned.length - 1; i++) grams.push(cleaned.slice(i, i + 2));
  return [...new Set(grams)].slice(0, 8);
}
function highlight(textHtml, grams) {
  let out = textHtml;
  for (const g of grams) {
    const parts = out.split(/(<mark>[\s\S]*?<\/mark>)/g);
    out = parts.map(p => {
      if (/^<mark>/.test(p)) return p;
      return p.split(g).join('<mark>' + g + '</mark>');
    }).join('');
  }
  return out;
}
function toggleSource(btn) {
  const text = btn.previousElementSibling;
  const expanded = text.classList.toggle('expanded');
  btn.textContent = expanded ? '收起 ▴' : '展开全文 ▾';
}

input.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(); }
});

init();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
