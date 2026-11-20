/*
 * HydroKnow static demo (self-built sample corpus) — English presentation layer.
 * English is the default (no flag). Simplified Chinese is opt-in via ?lang=zh.
 * Only UI chrome is translated; retrieved Chinese corpus passages and source
 * file names are the actual indexed data and stay verbatim.
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
    ["氢知", "HydroKnow"],
    ["氢知 HydroKnow · 沐光氢能企业知识智能服务助手", "HydroKnow · Corporate Knowledge & Service Assistant"],
    ["氢知 HydroKnow · 纯前端 RAG", "HydroKnow · fully client-side RAG"],
    ["沐光氢能企业知识智能服务助手 · RAG 检索增强 · 纯前端离线运行", "Corporate knowledge assistant · RAG retrieval · runs fully offline in-browser"],
    ["企业知识与智能服务助手 · 自建样例语料原型", "Corporate knowledge & service assistant · self-built sample corpus prototype"],
    ["知识库：仓库内自建的虚构样例语料 · BM25 + TF-IDF 混合检索 · 全部计算在浏览器本地完成", "Knowledge base: a fictional sample corpus built in-repo · BM25 + TF-IDF hybrid retrieval · all computation runs locally in the browser"],
    ["混合检索（与 HybridRetriever", "Hybrid retrieval (mirrors HybridRetriever"],
    ["分词（与 retriever", "Tokenization (mirrors retriever"],
    ["答案生成（与 generator", "Answer generation (mirrors generator"],
    ["引擎就绪 · 文档 ", "Engine ready · documents "],
    [" · 分块 ", " · chunks "],
    [" · 纯前端计算", " · computed client-side"],
    ["提问", "Ask"],
    ["问：", "Q:"],
    ["我是小知，问点什么吧，比如：沐光氢能的主打产品是什么？", "Ask me anything, e.g. What is the flagship product?"],
    ["输入问题，小知会从沐光氢能的企业资料中检索答案，并附上原文来源。", "Enter a question; the assistant retrieves answers from the company materials and cites the original sources."],
    ["沐光氢能成立于哪一年？", "What year was the company founded?"],
    ["沐光氢能的主打产品是什么？", "What is the flagship product?"],
    ["沐光氢能的核心技术能力有哪些？", "What are the core technical capabilities?"],
    ["沐光氢能的合作方和客户有哪些？", "Who are the partners and customers?"],
    ["沐光氢能的官网和联系方式是什么？", "What is the official website and contact information?"],
    ["沐光氢能的应用场景有哪些？", "What are the application scenarios?"],
    ["根据知识库资料，关于「", "From the knowledge base, regarding "],
    ["根据资料检索，最相关的信息如下：", "The most relevant information found in the materials:"],
    ["未检索到相关内容。请确认知识库是否包含该信息，或尝试换个问法。", "No relevant content was found. Check whether the knowledge base covers it, or try rephrasing."],
    ["置信度", "Confidence"],
    ["关键信息", "Key points"],
    ["参考来源（", "Sources ("],
    ["，按相关度排序）", ", sorted by relevance)"],
    ["匹配 ", "Match "],
    ["展开全文 ▾", "Expand ▾"],
    ["收起 ▴", "Collapse ▴"],
    ["来源：命中词高亮 + 折叠", "Sources: keyword highlighting + collapsible"],
    ["答案生成", "Answer generation"]
  ];
  // Longest-first so short keys (低/中/高) never corrupt longer phrases.
  PAIRS.sort(function (a, b) { return b[0].length - a[0].length; });

  var busy = false;
  // Single-character confidence labels (低/中/高) must not corrupt corpus text
  // such as 高新技术 or 中试线: translate them only inside the explicit
  // "置信度 X N%" fragment, never as standalone corpus characters.
  var CONF = { "低": "low", "中": "medium", "高": "high" };
  function translate(s) {
    if (!s || !/[\u4e00-\u9fff]/.test(s)) return s;
    var out = s;
    // Handle the dynamically composed confidence string first.
    out = out.replace(/置信度\s*([低中高])\s*(\d+%)/g, function (_, lvl, pct) {
      return "Confidence " + CONF[lvl] + " " + pct;
    });
    for (var i = 0; i < PAIRS.length; i++) {
      var k = PAIRS[i][0];
      if (k in CONF) continue;
      if (out.indexOf(k) !== -1) out = out.split(k).join(PAIRS[i][1]);
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
  function patchAttrs(root) {
    if (!root || !root.querySelectorAll) return;
    var els = root.querySelectorAll("[placeholder],[title],[aria-label]");
    for (var i = 0; i < els.length; i++) {
      ["placeholder", "title", "aria-label"].forEach(function (at) {
        var v = els[i].getAttribute(at);
        if (v && /[\u4e00-\u9fff]/.test(v)) els[i].setAttribute(at, translate(v));
      });
    }
  }
  function patchAll() {
    if (busy) return; busy = true;
    try {
      document.title = translate(document.title);
      patchTree(document.body);
      patchAttrs(document.body);
      addSwitch();
    } finally { busy = false; }
  }
  function boot() {
    patchAll();
    var obs = new MutationObserver(function (muts) {
      if (busy) return;
      for (var i = 0; i < muts.length; i++) {
        var m = muts[i];
        if (m.type === "childList") {
          for (var j = 0; j < m.addedNodes.length; j++) patchTree(m.addedNodes[j]);
          patchAttrs(document.body);
        } else if (m.type === "characterData") patchTextNode(m.target);
        else if (m.type === "attributes") patchAttrs(m.target.parentNode || document.body);
      }
    });
    obs.observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
