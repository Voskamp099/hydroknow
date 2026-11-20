/*
 * HydroKnow Flask chat app — English presentation layer.
 * English is the default (no flag). Simplified Chinese is opt-in via ?lang=zh.
 * Only UI chrome is translated; retrieved corpus passages and source file names
 * are real data and stay verbatim.
 */
(function () {
  if (new URLSearchParams(window.location.search).get("lang") === "zh") {
    document.documentElement.lang = "zh-CN";
    document.addEventListener("DOMContentLoaded", function () {
      if (document.getElementById("hk-app-en")) return;
      var a = document.createElement("a");
      a.id = "hk-app-en"; a.href = "?"; a.textContent = "EN";
      a.setAttribute("aria-label", "View in English");
      a.style.cssText = "position:fixed;right:14px;bottom:14px;z-index:2000;font:700 12px/1 system-ui,sans-serif;color:#fff;background:#0a6e4f;padding:6px 11px;border-radius:20px;text-decoration:none;box-shadow:0 4px 14px rgba(0,0,0,.35)";
      document.body.appendChild(a);
    });
    return;
  }
  if (window.__hkAppI18nOn) return;
  window.__hkAppI18nOn = true;
  document.documentElement.lang = "en";
  document.documentElement.classList.add("lang-en");

  var PAIRS = [
    ["氢知 HydroKnow · 沐光氢能企业知识智能服务助手", "HydroKnow · Corporate Knowledge & Service Assistant"],
    ["我是小知 · 沐光氢能企业知识智能服务助手 · RAG 检索增强 · 离线运行", "Corporate knowledge assistant · RAG retrieval · runs offline"],
    ["问点什么吧，比如：沐光氢能的主打产品是什么？", "Ask me anything, e.g. What is the flagship product?"],
    ["输入问题，小知会从沐光氢能的企业资料中检索答案，并附上原文来源。", "Enter a question; the assistant retrieves answers from the company materials and cites the original sources."],
    ["沐光氢能成立于哪一年？", "What year was the company founded?"],
    ["沐光氢能的主打产品是什么？", "What is the flagship product?"],
    ["沐光氢能的核心技术能力有哪些？", "What are the core technical capabilities?"],
    ["沐光氢能的合作方和客户有哪些？", "Who are the partners and customers?"],
    ["沐光氢能的官网和联系方式是什么？", "Official website and contact information?"],
    ["沐光氢能的应用场景有哪些？", "What are the application scenarios?"],
    ["提问", "Ask"],
    ["引擎就绪 · 文档 ", "Engine ready · documents "],
    [" · 分块 ", " · chunks "],
    ["引擎离线", "Engine offline"],
    ["正在检索知识库", "Searching the knowledge base"],
    ["请求失败", "Request failed"],
    ["问：", "Q:"],
    ["置信度", "Confidence"],
    ["关键信息点", "Key points"],
    ["关键信息", "Key points"],
    ["参考来源（", "Sources ("],
    ["按相关度排序）", ", sorted by relevance)"],
    ["匹配 ", "Match "],
    ["展开全文", "Expand"],
    ["收起", "Collapse"],
    ["来源：命中词高亮 + 折叠", "Sources: keyword highlighting + collapsible"]
  ];
  PAIRS.sort(function (a, b) { return b[0].length - a[0].length; });

  var busy = false;
  var CONF = { "低": "low", "中": "medium", "高": "high" };
  function translate(s) {
    if (!s || !/[\u4e00-\u9fff]/.test(s)) return s;
    var out = s.replace(/置信度\s*([低中高])\s*(\d+%)/g, function (_, lvl, pct) {
      return "Confidence " + CONF[lvl] + " " + pct;
    });
    for (var i = 0; i < PAIRS.length; i++) {
      var k = PAIRS[i][0];
      if (out.indexOf(k) !== -1) out = out.split(k).join(PAIRS[i][1]);
    }
    return out;
  }
  function patchTextNode(n) {
    if (!n.nodeValue || !/[\u4e00-\u9fff]/.test(n.nodeValue)) return;
    // The logo's standalone Chinese brand mark is redundant next to "HydroKnow".
    if (n.nodeValue.trim() === "氢知") { n.nodeValue = ""; return; }
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
  function addSwitch() {
    if (document.getElementById("hk-lang-switch")) return;
    var a = document.createElement("a");
    a.id = "hk-lang-switch"; a.href = "?lang=zh"; a.textContent = "中文";
    a.setAttribute("aria-label", "Switch to Chinese");
    a.style.cssText = "position:fixed;left:14px;bottom:14px;z-index:2000;font:600 12px/1 system-ui,sans-serif;color:#fff;background:#0d9070;padding:6px 11px;border-radius:20px;text-decoration:none;box-shadow:0 4px 14px rgba(0,0,0,.35)";
    document.body.appendChild(a);
  }
  function patchAll() {
    if (busy) return; busy = true;
    try {
      document.title = translate(document.title);
      patchTree(document.body); patchAttrs(document.body); addSwitch();
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
