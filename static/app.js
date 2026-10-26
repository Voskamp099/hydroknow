/* 氢知知识助手 · 问答页面逻辑 */

const input = document.getElementById('input');
const sendBtn = document.getElementById('sendBtn');
const result = document.getElementById('result');
const placeholder = document.getElementById('placeholder');
const chipsEl = document.getElementById('chips');
const statusEl = document.getElementById('status');

// ── 初始化 ──────────────────────────
async function init() {
  // 推荐问题
  try {
    const res = await fetch('/api/suggest');
    const data = await res.json();
    data.questions.forEach(q => {
      const chip = document.createElement('div');
      chip.className = 'chip';
      chip.textContent = q;
      chip.onclick = () => { input.value = q; ask(); };
      chipsEl.appendChild(chip);
    });
  } catch (e) { console.warn('推荐问题加载失败', e); }

  // 引擎状态
  try {
    const res = await fetch('/api/stats');
    const s = await res.json();
    statusEl.innerHTML = `<span class="dot"></span>引擎就绪 · 文档 ${s.total_docs} · 分块 ${s.total_chunks}`;
  } catch (e) {
    statusEl.innerHTML = '<span class="dot" style="background:#c44545"></span>引擎离线';
  }
}

// ── 提问 ────────────────────────────
async function ask() {
  const q = input.value.trim();
  if (!q) return;

  // 隐藏占位符
  if (placeholder) placeholder.style.display = 'none';

  // 显示 loading
  const loadingId = 'loading-' + Date.now();
  const loadingEl = document.createElement('div');
  loadingEl.id = loadingId;
  loadingEl.className = 'loading-card';
  loadingEl.innerHTML = `
    <div class="loading-dots"><span></span><span></span><span></span></div>
    <p>正在检索知识库...</p>
  `;
  result.prepend(loadingEl);

  sendBtn.disabled = true;
  input.value = '';

  try {
    const res = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q }),
    });
    const data = await res.json();

    loadingEl.remove();

    if (data.error) {
      renderError(q, data.error);
    } else {
      renderAnswer(q, data);
    }
  } catch (e) {
    loadingEl.remove();
    renderError(q, '请求失败: ' + e.message);
  }

  sendBtn.disabled = false;
  input.focus();
}

// ── 渲染答案 ────────────────────────
function renderAnswer(question, data) {
  const card = document.createElement('div');
  card.className = 'answer-card';

  // 置信度样式
  const conf = data.confidence || 0;
  let confClass = 'conf-low';
  let confLabel = '低';
  if (conf >= 0.7) { confClass = 'conf-high'; confLabel = '高'; }
  else if (conf >= 0.4) { confClass = 'conf-mid'; confLabel = '中'; }

  // 答案文本
  let html = `
    <div class="answer-header">
      <span class="q">问：<b>${escapeHtml(question)}</b></span>
      <span class="conf ${confClass}">置信度 ${confLabel} ${(conf * 100).toFixed(0)}%</span>
    </div>
    <div class="answer-body">
      <div class="answer-text">${formatAnswer(data.answer)}</div>
  `;

  // 关键信息点
  if (data.key_points && data.key_points.length > 0) {
    html += `
      <div class="key-points">
        <div class="key-points-title">关键信息</div>
        <ul>
          ${data.key_points.map(k => `<li>${escapeHtml(k)}</li>`).join('')}
        </ul>
      </div>
    `;
  }

  html += `</div>`;

  // 来源
  if (data.sources && data.sources.length > 0) {
    const grams = sourceKeywords(question);
    html += `
      <div class="sources-section">
        <div class="sources-title">📄 参考来源（${data.sources.length}，按相关度排序）</div>
        ${data.sources.map(s => `
          <div class="source-item">
            <div class="source-meta">
              <span class="source-meta-left">
                <span class="source-badge">${s.rank}</span>
                <span class="source-doc">${escapeHtml(s.doc)}</span>
              </span>
              <span class="source-score">匹配 ${(s.score * 100).toFixed(1)}%</span>
            </div>
            <div class="source-text">${highlight(escapeHtml(s.text), grams)}</div>
            <button class="source-toggle" onclick="toggleSource(this)">展开全文 ▾</button>
          </div>
        `).join('')}
      </div>
    `;
    // 渲染完成后：超过 4 行的才显示「展开全文」
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

// ── 渲染错误 ────────────────────────
function renderError(question, msg) {
  const card = document.createElement('div');
  card.className = 'answer-card';
  card.innerHTML = `
    <div class="answer-header">
      <span class="q">问：<b>${escapeHtml(question)}</b></span>
    </div>
    <div class="answer-body">
      <div class="answer-text" style="color:#c44545">${escapeHtml(msg)}</div>
    </div>
  `;
  result.prepend(card);
}

// ── 辅助 ────────────────────────────
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatAnswer(text) {
  return escapeHtml(text).replace(/\n/g, '<br>');
}

// ── 来源：命中词高亮 + 折叠 ──────────
// 从问题提取 char 2-gram（与检索算法同口径），用于在来源片段中标记命中词
function sourceKeywords(question) {
  const cleaned = question.replace(/[\s，。！？、,.!?；;：:"'“”‘’（()）【】《》]/g, '');
  if (cleaned.length < 2) return [];
  const grams = [];
  for (let i = 0; i < cleaned.length - 1; i++) grams.push(cleaned.slice(i, i + 2));
  return [...new Set(grams)].slice(0, 8);
}

// 在已转义的安全 HTML 上做高亮，跳过已包裹的 <mark> 避免嵌套
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

// 「展开全文」切换
function toggleSource(btn) {
  const text = btn.previousElementSibling;
  const expanded = text.classList.toggle('expanded');
  btn.textContent = expanded ? '收起 ▴' : '展开全文 ▾';
}

// ── 回车提交 ────────────────────────
input.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    ask();
  }
});

// 启动
init();
