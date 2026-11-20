/*
 * HydroKnow static snapshot demo (self-built sample corpus) — English layer.
 * English is the default (no flag). Simplified Chinese is opt-in via ?lang=zh.
 * UI labels are translated; retrieved Chinese corpus passages and source file
 * names are the actual indexed data and stay verbatim.
 */
(function () {
  if (new URLSearchParams(window.location.search).get("lang") === "zh") {
    document.documentElement.lang = "zh-CN";
    document.addEventListener("DOMContentLoaded", function () {
      if (document.getElementById("hk-demo-en")) return;
      var a = document.createElement("a");
      a.id = "hk-demo-en"; a.href = "?"; a.textContent = "EN";
      a.setAttribute("aria-label", "View in English");
      a.style.cssText = "position:fixed;right:14px;bottom:14px;z-index:2000;font:700 12px/1 system-ui,sans-serif;color:#fff;background:#0a6e4f;padding:6px 11px;border-radius:20px;text-decoration:none;box-shadow:0 4px 14px rgba(0,0,0,.35)";
      document.body.appendChild(a);
    });
    return;
  }
  if (window.__hkDemoI18nOn) return;
  window.__hkDemoI18nOn = true;
  document.documentElement.lang = "en";

  var PAIRS = [
    ["企业知识与智能服务助手 · Demo", "Corporate Knowledge & Service Assistant · Demo"],
    ["氢知 · 企业知识与智能服务助手（沐光氢能）", "HydroKnow · Corporate Knowledge & Service Assistant (sample corpus)"],
    ["RAG Demo · BM25 + TF-IDF 混合检索 · 生成于 2026-10-26 18:21", "RAG Demo · BM25 + TF-IDF hybrid retrieval · generated 2026-10-26 18:21"],
    ["答案生成为离线 stub（未调用 LLM）。接入真实模型后效果更佳。", "Answers are produced by an offline stub (no LLM call). Connecting a real model improves the result."],
    ["1. 沐光氢能成立于哪一年？", "1. What year was the company founded?"],
    ["2. 沐光氢能的主打产品是什么？", "2. What is the flagship product?"],
    ["3. 沐光氢能的核心技术能力有哪些？", "3. What are the core technical capabilities?"],
    ["4. 沐光氢能的合作方和客户有哪些？", "4. Who are the partners and customers?"],
    ["5. 沐光氢能的官网和联系方式是什么？", "5. What is the official website and contact information?"],
    ["6. 沐光氢能的应用场景有哪些？", "6. What are the application scenarios?"],
    ["根据知识库资料，关于「", "From the knowledge base, regarding "],
    ["」：", "]:"],
    ["沐光氢能成立于哪一年？", "What year was the company founded?"],
    ["沐光氢能的主打产品是什么？", "What is the flagship product?"],
    ["沐光氢能的核心技术能力有哪些？", "What are the core technical capabilities?"],
    ["沐光氢能的合作方和客户有哪些？", "Who are the partners and customers?"],
    ["沐光氢能的官网和联系方式是什么？", "What is the official website and contact information?"],
    ["沐光氢能的应用场景有哪些？", "What are the application scenarios?"],
    ["置信度", "Confidence"],
    ["检索来源", "Retrieved sources"],
    ["来源 1 · ", "Source 1 · "],
    ["来源 2 · ", "Source 2 · "],
    ["来源 3 · ", "Source 3 · "],
    ["来源 4 · ", "Source 4 · "]
  ];
  PAIRS.sort(function (a, b) { return b[0].length - a[0].length; });

  var busy = false;
  function translate(s) {
    if (!s || !/[\u4e00-\u9fff]/.test(s)) return s;
    var out = s;
    for (var i = 0; i < PAIRS.length; i++) {
      if (out.indexOf(PAIRS[i][0]) !== -1) out = out.split(PAIRS[i][0]).join(PAIRS[i][1]);
    }
    return out;
  }
  function patchTextNode(n) {
    if (!n.nodeValue || !/[\u4e00-\u9fff]/.test(n.nodeValue)) return;
    var t = translate(n.nodeValue);
    if (t !== n.nodeValue) n.nodeValue = t;
  }
  function patchTree(root) {
    if (!root) return;
    if (root.nodeType === 3) { patchTextNode(root); return; }
    if (!root.querySelectorAll) return;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    var n;
    while ((n = walker.nextNode())) patchTextNode(n);
  }
  function addSwitch() {
    if (document.getElementById("hk-demo-lang")) return;
    var a = document.createElement("a");
    a.id = "hk-demo-lang"; a.href = "?lang=zh"; a.textContent = "中文";
    a.setAttribute("aria-label", "Switch to Chinese");
    a.style.cssText = "position:fixed;left:14px;bottom:14px;z-index:2000;font:600 12px/1 system-ui,sans-serif;color:#fff;background:#0d6e4f;padding:6px 11px;border-radius:20px;text-decoration:none;box-shadow:0 4px 14px rgba(0,0,0,.35)";
    document.body.appendChild(a);
  }
  function boot() {
    document.title = translate(document.title);
    patchTree(document.body);
    addSwitch();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
