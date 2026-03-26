/* ═══════════════════════════════════════════════════════════════
   THRIFTEY — Frontend Application
   SPA with engine-powered pages, i18n, community forum
   ═══════════════════════════════════════════════════════════════ */

const API = 'http://127.0.0.1:8001';
let TOKEN = null;
let CURRENT_PAGE = 'dashboard';
let DASH_DATA = null;

/* ═══════════════════════════════════════════════════════════
   i18n — Regional Language Support (EN / Hindi / Tamil)
   ═══════════════════════════════════════════════════════════ */
const TRANSLATIONS = {
  en: {
    login_subtitle: "Financial Intelligence for Small Business",
    email: "Email", password: "Password", sign_in: "Sign In",
    demo_accounts: "Demo accounts",
    nav_dashboard: "Dashboard", nav_obligations: "Obligations",
    nav_whatif: "What-If Simulator", nav_health: "Health Score",
    nav_gst: "GST Reminders", nav_email: "Email Drafts",
    nav_community: "Community", logout: "Logout",
    days_to_zero: "Days to Zero", cash_balance: "Cash Balance",
    cash_runway: "Cash runway countdown", available_funds: "Available funds",
    active_obligations: "Active Obligations", unpaid_month: "Unpaid this month",
    expected_receivables: "Expected Receivables", next_30_days: "In next 30 days",
    top_obligations: "Top Priority Obligations",
    runway_chart: "6-Month Cash Runway",
    all_obligations: "All Obligations — Prioritized",
    sorted_priority: "Ranked by engine priority score. Priority bar = weighted urgency + penalty + relationship + flexibility.",
    whatif_title: "What-If Scenario Builder",
    whatif_desc: "Change a financial variable and instantly see how it impacts your cash runway.",
    current_cash: "Current Cash", current_runway: "Current Runway",
    variable: "Variable", new_cash: "New Cash Balance (₹)",
    run_sim: "Run Simulation",
    health_title: "Financial Health Score",
    score_breakdown: "Score Breakdown",
    gst_title: "Upcoming GST Filing Deadlines",
    gst_desc: "Stay ahead of GSTR-1 and GSTR-3B filings. Late penalty: ₹50/day.",
    email_title: "Context-Aware Email Drafts",
    email_desc: "Auto-generated negotiation emails tailored to each counterparty relationship.",
    community_title: "Community Forum",
    community_desc: "Connect with fellow small business owners. Share tips, ask questions, and learn together.",
    post_btn: "Post to Community",
    all: "All", cash_flow: "Cash Flow", gst_cat: "GST",
    suppliers: "Suppliers", general: "General",
    due: "Due", rank: "Rank", priority: "Priority",
    payable: "Payable", cannot_pay: "Cannot Pay", partial: "Partial",
    days: "days", replies: "Replies", by: "by", reply: "Reply",
    days_remaining: "days remaining", overdue: "Overdue",
    send_reply: "Send Reply", view_full: "View Full Email ▼",
    new_runway: "New Runway", impact: "Impact",
  },
  hi: {
    login_subtitle: "छोटे व्यवसायों के लिए वित्तीय बुद्धिमत्ता",
    email: "ईमेल", password: "पासवर्ड", sign_in: "लॉग इन करें",
    demo_accounts: "डेमो खाते",
    nav_dashboard: "डैशबोर्ड", nav_obligations: "दायित्व",
    nav_whatif: "क्या-अगर सिम्युलेटर", nav_health: "स्वास्थ्य स्कोर",
    nav_gst: "GST अनुस्मारक", nav_email: "ईमेल ड्राफ्ट",
    nav_community: "समुदाय", logout: "लॉगआउट",
    days_to_zero: "शून्य तक के दिन", cash_balance: "नकद शेष",
    cash_runway: "नकद रनवे उल्टी गिनती", available_funds: "उपलब्ध धनराशि",
    active_obligations: "सक्रिय दायित्व", unpaid_month: "इस महीने अवैतनिक",
    expected_receivables: "अपेक्षित प्राप्य", next_30_days: "अगले 30 दिनों में",
    top_obligations: "शीर्ष प्राथमिकता दायित्व",
    runway_chart: "6-महीने का नकद रनवे",
    all_obligations: "सभी दायित्व — प्राथमिकता अनुसार",
    sorted_priority: "इंजन प्राथमिकता स्कोर द्वारा रैंक।",
    whatif_title: "क्या-अगर सिम्युलेटर",
    whatif_desc: "एक वित्तीय चर बदलें और तुरंत देखें कि यह आपके नकद रनवे को कैसे प्रभावित करता है।",
    current_cash: "वर्तमान नकद", current_runway: "वर्तमान रनवे",
    variable: "चर", new_cash: "नया नकद शेष (₹)", run_sim: "सिम्युलेशन चलाएं",
    health_title: "वित्तीय स्वास्थ्य स्कोर", score_breakdown: "स्कोर विश्लेषण",
    gst_title: "आगामी GST फाइलिंग तिथियां",
    gst_desc: "GSTR-1 और GSTR-3B फाइलिंग से आगे रहें। देरी जुर्माना: ₹50/दिन।",
    email_title: "संदर्भ-आधारित ईमेल ड्राफ्ट",
    email_desc: "प्रत्येक प्रतिपक्ष संबंध के अनुरूप स्वचालित बातचीत ईमेल।",
    community_title: "समुदाय मंच",
    community_desc: "साथी छोटे व्यवसाय मालिकों से जुड़ें। सुझाव साझा करें और सीखें।",
    post_btn: "समुदाय में पोस्ट करें",
    all: "सभी", cash_flow: "नकद प्रवाह", gst_cat: "GST",
    suppliers: "आपूर्तिकर्ता", general: "सामान्य",
    due: "देय", rank: "रैंक", priority: "प्राथमिकता",
    payable: "भुगतान योग्य", cannot_pay: "भुगतान नहीं कर सकते", partial: "आंशिक",
    days: "दिन", replies: "उत्तर", by: "द्वारा", reply: "उत्तर",
    days_remaining: "दिन शेष", overdue: "अतिदेय",
    send_reply: "उत्तर भेजें", view_full: "पूरा ईमेल देखें ▼",
    new_runway: "नया रनवे", impact: "प्रभाव",
  },
  ta: {
    login_subtitle: "சிறு வணிகங்களுக்கான நிதி நுண்ணறிவு",
    email: "மின்னஞ்சல்", password: "கடவுச்சொல்", sign_in: "உள்நுழை",
    demo_accounts: "டெமோ கணக்குகள்",
    nav_dashboard: "டாஷ்போர்டு", nav_obligations: "கடமைகள்",
    nav_whatif: "என்ன-ஆனால் சிமுலேட்டர்", nav_health: "சுகாதார மதிப்பெண்",
    nav_gst: "GST நினைவூட்டல்", nav_email: "மின்னஞ்சல் வரைவுகள்",
    nav_community: "சமூகம்", logout: "வெளியேறு",
    days_to_zero: "பூஜ்ஜியத்திற்கு நாட்கள்", cash_balance: "பண இருப்பு",
    cash_runway: "பண ரன்வே கவுண்ட்டவுன்", available_funds: "கிடைக்கும் நிதி",
    active_obligations: "செயல்படும் கடமைகள்", unpaid_month: "இம்மாதம் செலுத்தப்படாதவை",
    expected_receivables: "எதிர்பார்க்கப்படும் பெறுதல்கள்", next_30_days: "அடுத்த 30 நாட்களில்",
    top_obligations: "முன்னுரிமை கடமைகள்",
    runway_chart: "6-மாத பண ரன்வே",
    all_obligations: "அனைத்து கடமைகள் — முன்னுரிமை",
    sorted_priority: "இயந்திர முன்னுரிமை மதிப்பெண் படி தரவரிசை।",
    whatif_title: "என்ன-ஆனால் சிமுலேட்டர்",
    whatif_desc: "ஒரு நிதி மாறியை மாற்றி உங்கள் பண ரன்வேயை எவ்வாறு பாதிக்கிறது என்பதைப் பாருங்கள்.",
    current_cash: "தற்போதைய பணம்", current_runway: "தற்போதைய ரன்வே",
    variable: "மாறி", new_cash: "புதிய பண இருப்பு (₹)", run_sim: "சிமுலேஷன் இயக்கு",
    health_title: "நிதி சுகாதார மதிப்பெண்", score_breakdown: "மதிப்பெண் பகுப்பாய்வு",
    gst_title: "வரவிருக்கும் GST தாக்கல் தேதிகள்",
    gst_desc: "GSTR-1 மற்றும் GSTR-3B தாக்கல்களுக்கு முன்னதாக இருங்கள்.",
    email_title: "சூழல்-அறிவு மின்னஞ்சல் வரைவுகள்",
    email_desc: "ஒவ்வொரு எதிர்தரப்பு உறவுக்கும் தானியங்கி ஈமெயில்.",
    community_title: "சமூக மன்றம்",
    community_desc: "சக சிறு வணிக உரிமையாளர்களுடன் இணையுங்கள்.",
    post_btn: "சமூகத்தில் பதிவிடு",
    all: "அனைத்தும்", cash_flow: "பண ஓட்டம்", gst_cat: "GST",
    suppliers: "சப்ளையர்கள்", general: "பொது",
    due: "நிலுவை", rank: "தரவரிசை", priority: "முன்னுரிமை",
    payable: "செலுத்தக்கூடியது", cannot_pay: "செலுத்த இயலாது", partial: "பகுதி",
    days: "நாட்கள்", replies: "பதில்கள்", by: "மூலம்", reply: "பதில்",
    days_remaining: "நாட்கள் உள்ளன", overdue: "தாமதம்",
    send_reply: "பதில் அனுப்பு", view_full: "முழு ஈமெயில் ▼",
    new_runway: "புதிய ரன்வே", impact: "தாக்கம்",
  }
};

let CURRENT_LANG = 'en';

function t(key) {
  return (TRANSLATIONS[CURRENT_LANG] && TRANSLATIONS[CURRENT_LANG][key]) || TRANSLATIONS.en[key] || key;
}

function setLanguage(lang) {
  CURRENT_LANG = lang;
  // Update language toggle buttons
  document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelector(`.lang-btn[onclick="setLanguage('${lang}')"]`).classList.add('active');
  // Update all data-i18n elements
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    el.textContent = t(key);
  });
  // Update topbar title
  const titles = { dashboard: 'nav_dashboard', obligations: 'nav_obligations', whatif: 'nav_whatif',
                   health: 'nav_health', gst: 'nav_gst', email: 'nav_email', community: 'nav_community' };
  document.querySelector('.topbar-title').textContent = t(titles[CURRENT_PAGE] || 'nav_dashboard');
}


/* ═══════════════════════════════════════════════════════════
   Utility Functions
   ═══════════════════════════════════════════════════════════ */

function fmt(n) { return '₹' + Number(n).toLocaleString('en-IN'); }
function fmtDate(s) { return new Date(s).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }); }
function fmtTime(s) { return new Date(s).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }); }
function urgencyBadge(u) {
  if (u >= 0.85) return `<span class="badge badge-danger">${t('overdue')}</span>`;
  if (u >= 0.7) return '<span class="badge badge-warning">High</span>';
  if (u >= 0.4) return '<span class="badge badge-info">Medium</span>';
  return '<span class="badge badge-success">Low</span>';
}
function priorityBar(score) {
  const filled = Math.round(score * 10);
  return '<div class="priority-bar">' +
    Array.from({ length: 10 }, (_, i) =>
      `<div class="priority-segment ${i < filled ? (score >= 0.7 ? 'danger-fill' : 'filled') : ''}"></div>`
    ).join('') + '</div>';
}
function canPayBadge(status) {
  if (status === 'payable') return `<span class="badge badge-success">${t('payable')}</span>`;
  if (status === 'partial') return `<span class="badge badge-warning">${t('partial')}</span>`;
  return `<span class="badge badge-danger">${t('cannot_pay')}</span>`;
}

async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (TOKEN) headers['Authorization'] = `Bearer ${TOKEN}`;
  const res = await fetch(`${API}${path}`, { ...options, headers });
  if (res.status === 401) { logout(); throw new Error('Session expired'); }
  if (!res.ok) { const err = await res.json().catch(() => ({})); throw new Error(err.message || res.statusText); }
  return res.json();
}

/* ═══════════════════════════════════════════════════════════
   Auth — Login / Logout
   ═══════════════════════════════════════════════════════════ */

document.getElementById('login-form').addEventListener('submit', async e => {
  e.preventDefault();
  const btn = document.getElementById('login-btn');
  const errEl = document.getElementById('login-error');
  btn.disabled = true;
  btn.innerHTML = '<span class="loading-spinner"></span> Signing in…';
  errEl.textContent = '';

  try {
    const body = new URLSearchParams();
    body.append('username', document.getElementById('login-email').value);
    body.append('password', document.getElementById('login-password').value);

    const res = await fetch(`${API}/auth/login`, {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Login failed');
    TOKEN = data.access_token;
    document.querySelector('.login-wrapper').style.display = 'none';
    document.querySelector('.app-layout').classList.add('active');
    const today = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric' });
    document.querySelector('.topbar-date').textContent = today;
    navigate('dashboard');
  } catch (err) {
    errEl.textContent = err.message;
  } finally {
    btn.disabled = false;
    btn.innerHTML = '🔐 <span data-i18n="sign_in">' + t('sign_in') + '</span>';
  }
});

function logout() {
  TOKEN = null; DASH_DATA = null;
  document.querySelector('.login-wrapper').style.display = 'flex';
  document.querySelector('.app-layout').classList.remove('active');
}
document.getElementById('logout-btn').addEventListener('click', logout);


/* ═══════════════════════════════════════════════════════════
   Navigation
   ═══════════════════════════════════════════════════════════ */

const PAGE_TITLES = {
  dashboard: 'nav_dashboard', obligations: 'nav_obligations', whatif: 'nav_whatif',
  health: 'nav_health', gst: 'nav_gst', email: 'nav_email', community: 'nav_community',
};
const PAGE_LOADERS = {
  dashboard: loadDashboard, obligations: loadObligations, whatif: loadWhatIf,
  health: loadHealth, gst: loadGST, email: loadEmail, community: loadCommunity,
};

document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', e => {
    e.preventDefault();
    navigate(item.dataset.page);
  });
});

function navigate(page) {
  CURRENT_PAGE = page;
  document.querySelectorAll('.nav-item').forEach(n => n.classList.toggle('active', n.dataset.page === page));
  document.querySelectorAll('.page-view').forEach(p => { p.style.display = 'none'; p.classList.remove('active'); });
  const el = document.getElementById('page-' + page);
  if (el) { el.style.display = 'block'; el.classList.add('active'); }
  document.querySelector('.topbar-title').textContent = t(PAGE_TITLES[page] || 'nav_dashboard');
  if (PAGE_LOADERS[page]) PAGE_LOADERS[page]();
}


/* ═══════════════════════════════════════════════════════════
   DASHBOARD
   ═══════════════════════════════════════════════════════════ */

async function loadDashboard() {
  try {
    DASH_DATA = await api('/dashboard/summary');
    const d = DASH_DATA;

    document.querySelector('.sidebar-business').textContent = d.business_name;
    document.getElementById('stat-dtz').textContent = d.days_to_zero === -1 ? '∞' : d.days_to_zero;
    document.getElementById('stat-cash').textContent = fmt(d.cash_balance);
    document.getElementById('stat-obligations').textContent = d.obligations.length;
    document.getElementById('stat-receivables').textContent = fmt(d.total_receivables);

    // Top obligations
    const oblList = document.getElementById('dash-obligations-list');
    oblList.innerHTML = d.obligations.slice(0, 5).map(ob => `
      <div class="list-item">
        <div class="list-item-left">
          <div class="list-item-name">${ob.counterparty}</div>
          <div class="list-item-sub">${ob.counterparty_type} · ${t('due')} ${fmtDate(ob.due_date)}</div>
          ${priorityBar(ob.priority_score)}
        </div>
        <div class="list-item-right">
          <div class="list-item-amount">${fmt(ob.amount)}</div>
          <div class="list-item-date">${canPayBadge(ob.can_pay)}</div>
        </div>
      </div>
    `).join('');

    // Receivables
    const recList = document.getElementById('dash-receivables-list');
    recList.innerHTML = d.receivables.map(r => `
      <div class="list-item">
        <div class="list-item-left">
          <div class="list-item-name">${r.counterparty}</div>
          <div class="list-item-sub">${t('due')} ${fmtDate(r.expected_date)} · ${(r.confidence * 100).toFixed(0)}% confidence</div>
        </div>
        <div class="list-item-right">
          <div class="list-item-amount" style="color:var(--success)">${fmt(r.amount)}</div>
        </div>
      </div>
    `).join('');

    // Runway chart
    const chart = document.getElementById('runway-chart');
    const maxVal = Math.max(...d.runway_chart.map(r => r.actual || r.projected || 0), 1);
    chart.innerHTML = d.runway_chart.map(r => {
      const val = r.actual || r.projected || 0;
      const pct = Math.max(5, (val / maxVal) * 100);
      const type = r.actual ? 'actual' : 'projected';
      return `<div class="runway-bar-col">
        <div class="runway-bar-value">${fmt(val)}</div>
        <div class="runway-bar ${type}" style="height:${pct}%"></div>
        <div class="runway-bar-label">${r.month}</div>
      </div>`;
    }).join('');

  } catch (err) { console.error('Dashboard error:', err); }
}


/* ═══════════════════════════════════════════════════════════
   OBLIGATIONS
   ═══════════════════════════════════════════════════════════ */

async function loadObligations() {
  try {
    const obligations = await api('/obligations/');
    const conflicts = await api('/obligations/conflicts');

    const banner = document.getElementById('conflict-banner');
    if (conflicts.conflict) {
      banner.style.display = 'flex';
      banner.innerHTML = `
        <div class="icon">⚠️</div>
        <div>
          <div class="title">${t('cash_balance')}: ${fmt(conflicts.cash_balance)} · Total Due: ${fmt(conflicts.total_due_this_week)}</div>
          <div class="desc">Shortfall of ${fmt(conflicts.shortfall)}. ${conflicts.obligations.length} obligations this week — ${conflicts.obligations.filter(o => o.can_pay === 'payable').length} payable, ${conflicts.obligations.filter(o => o.can_pay !== 'payable').length} at risk.</div>
        </div>`;
    } else { banner.style.display = 'none'; }

    document.getElementById('obligations-list').innerHTML = obligations.map(ob => `
      <div class="list-item">
        <div class="list-item-left" style="flex:1">
          <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap">
            <div class="list-item-name">#${ob.rank} ${ob.counterparty}</div>
            ${urgencyBadge(ob.urgency)}
            ${canPayBadge(ob.can_pay)}
          </div>
          <div class="list-item-sub">${ob.counterparty_type} · ${t('due')} ${fmtDate(ob.due_date)} · ${t('priority')}: ${(ob.priority_score * 100).toFixed(0)}%</div>
          ${priorityBar(ob.priority_score)}
        </div>
        <div class="list-item-right">
          <div class="list-item-amount">${fmt(ob.amount)}</div>
        </div>
      </div>
    `).join('');
  } catch (err) { console.error('Obligations error:', err); }
}


/* ═══════════════════════════════════════════════════════════
   WHAT-IF SIMULATOR
   ═══════════════════════════════════════════════════════════ */

async function loadWhatIf() {
  if (DASH_DATA) {
    document.getElementById('whatif-current-cash').textContent = fmt(DASH_DATA.cash_balance);
    document.getElementById('whatif-current-dtz').textContent = DASH_DATA.days_to_zero === -1 ? '∞' : DASH_DATA.days_to_zero + ' ' + t('days');
  }
}

document.getElementById('whatif-variable').addEventListener('change', function() {
  const label = document.getElementById('whatif-value-label');
  label.textContent = this.value === 'cash_balance' ? t('new_cash') : 'New Amount (₹)';
});

document.getElementById('whatif-run-btn').addEventListener('click', async () => {
  const variable = document.getElementById('whatif-variable').value;
  const value = document.getElementById('whatif-new-value').value;
  if (!value) return;

  const btn = document.getElementById('whatif-run-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="loading-spinner"></span>';

  try {
    const result = await api('/whatif/', {
      method: 'POST',
      body: JSON.stringify({ variable, new_value: parseFloat(value) }),
    });

    const deltaClass = result.delta_days > 0 ? 'delta-positive' : result.delta_days < 0 ? 'delta-negative' : 'delta-neutral';
    const deltaSign = result.delta_days > 0 ? '+' : '';

    // Build trajectory mini-chart
    let trajectoryHtml = '';
    if (result.trajectory_chart && result.trajectory_chart.length > 0) {
      const maxB = Math.max(...result.trajectory_chart.map(t => t.balance), 1);
      trajectoryHtml = `<div class="glass card-body" style="margin-top:0.75rem">
        <div class="card-title">📉 Cash Trajectory (30 ${t('days')})</div>
        <div class="runway-bars" style="height:150px">
          ${result.trajectory_chart.filter((_, i) => i % 3 === 0).map(pt => {
            const pct = Math.max(3, (pt.balance / maxB) * 100);
            return `<div class="runway-bar-col">
              <div class="runway-bar-value">${fmt(pt.balance)}</div>
              <div class="runway-bar projected" style="height:${pct}%"></div>
              <div class="runway-bar-label">D${pt.day}</div>
            </div>`;
          }).join('')}
        </div>
      </div>`;
    }

    document.getElementById('whatif-results').innerHTML = `
      <div class="stats-grid">
        <div class="stat-card glass">
          <div class="stat-label">${t('new_runway')}</div>
          <div class="stat-value">${result.new_runway_days >= 999 ? '∞' : result.new_runway_days} ${t('days')}</div>
        </div>
        <div class="stat-card glass">
          <div class="stat-label">${t('impact')}</div>
          <div class="stat-value"><span class="delta-badge ${deltaClass}">${deltaSign}${result.delta_days} ${t('days')}</span></div>
        </div>
      </div>
      <div class="glass card-body" style="margin-top:0.75rem">
        <div class="card-title">📝 ${t('impact')} Summary</div>
        <p style="color:var(--text-secondary); font-size:0.85rem; line-height:1.6">${result.impact_summary}</p>
        ${result.affected_obligations.length > 0 ? `
          <div style="margin-top:1rem">
            <div class="stat-label" style="margin-bottom:0.5rem">Affected Obligations</div>
            ${result.affected_obligations.map(a => `
              <div class="list-item">
                <div class="list-item-left">
                  <div class="list-item-name">${a.counterparty}</div>
                  <div class="list-item-sub">${t('due')} ${fmtDate(a.due_date)}</div>
                </div>
                <div class="list-item-right"><div class="list-item-amount" style="color:var(--danger)">${fmt(a.amount)}</div></div>
              </div>`).join('')}
          </div>` : ''}
      </div>
      ${trajectoryHtml}`;
  } catch (err) { console.error('What-if error:', err); }
  finally {
    btn.disabled = false;
    btn.innerHTML = '⚡ <span data-i18n="run_sim">' + t('run_sim') + '</span>';
  }
});


/* ═══════════════════════════════════════════════════════════
   HEALTH SCORE
   ═══════════════════════════════════════════════════════════ */

async function loadHealth() {
  try {
    const data = await api('/health-score/');
    const score = data.score;
    const circ = 2 * Math.PI * 85;
    const offset = circ * (1 - score / 100);

    document.getElementById('health-gauge').innerHTML = `
      <svg class="gauge-ring" viewBox="0 0 200 200">
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#D97706"/>
            <stop offset="100%" style="stop-color:#4ade80"/>
          </linearGradient>
        </defs>
        <circle class="gauge-bg" cx="100" cy="100" r="85"/>
        <circle class="gauge-fill" cx="100" cy="100" r="85"
                stroke-dasharray="${circ}" stroke-dashoffset="${offset}"/>
      </svg>
      <div class="gauge-center">
        <div class="gauge-score">${score}</div>
        <div class="gauge-level">${data.level}</div>
      </div>`;

    // Factors
    const factorMap = { payment_score: t('payable'), gst_score: 'GST', runway_score: t('current_runway'), receivables_score: t('expected_receivables') };
    const maxMap = { payment_score: 40, gst_score: 20, runway_score: 20, receivables_score: 20 };
    const factorsEl = document.getElementById('health-factors');
    factorsEl.innerHTML = Object.entries(data.factors).map(([key, val]) => {
      const max = maxMap[key] || 20;
      const pct = Math.min(100, (val / max) * 100);
      const cls = pct >= 70 ? 'success' : pct >= 40 ? '' : 'danger';
      return `<div class="factor-row">
        <div class="factor-label">${factorMap[key] || key}</div>
        <div class="factor-bar"><div class="progress-track"><div class="progress-fill ${cls}" style="width:${pct}%"></div></div></div>
        <div class="factor-value">${val.toFixed(1)}/${max}</div>
      </div>`;
    }).join('');

    // Gamification
    const gam = data.gamification;
    let metaHtml = '';
    if (gam) {
      metaHtml += `<div class="next-unlock" style="margin-top:1rem">
        <strong>${gam.level_name}</strong> (Level ${gam.level_number}) · Next: ${gam.next_level_threshold}
        <br><span style="font-size:0.72rem">${gam.motivational_message}</span>
      </div>`;
      if (gam.badges) {
        metaHtml += '<div style="margin-top:0.75rem">';
        gam.badges.forEach(b => {
          metaHtml += `<div class="badge-unlock" style="opacity:${b.unlocked ? 1 : 0.35}">
            <div class="emoji">${b.icon}</div>
            <div class="text">${b.name}<br><span style="font-size:0.65rem;color:var(--text-muted)">${b.description}</span></div>
          </div>`;
        });
        metaHtml += '</div>';
      }
    }
    if (data.improvement_tips && data.improvement_tips.length) {
      metaHtml += '<div style="margin-top:1rem"><div class="stat-label" style="margin-bottom:0.5rem">💡 Tips</div>';
      data.improvement_tips.forEach(tip => {
        metaHtml += `<div style="font-size:0.78rem; color:var(--text-secondary); margin-bottom:0.3rem">• ${tip}</div>`;
      });
      metaHtml += '</div>';
    }
    document.getElementById('health-meta').innerHTML = metaHtml;
  } catch (err) { console.error('Health error:', err); }
}


/* ═══════════════════════════════════════════════════════════
   GST REMINDERS
   ═══════════════════════════════════════════════════════════ */

async function loadGST() {
  try {
    const reminders = await api('/gst/reminders');
    document.getElementById('gst-list').innerHTML = reminders.map(r => {
      const urgent = r.days_remaining <= 5;
      return `<div class="glass gst-card fade-in">
        <div class="gst-icon ${urgent ? 'urgent' : ''}">${r.is_overdue ? '🔴' : urgent ? '🟡' : '🟢'}</div>
        <div style="flex:1">
          <div class="list-item-name">${r.form_name}</div>
          <div class="list-item-sub">${r.notes || ''}</div>
          ${r.penalty_info ? `<div class="list-item-sub" style="color:var(--danger)">${r.penalty_info}</div>` : ''}
        </div>
        <div style="text-align:right">
          <div class="list-item-amount">${fmtDate(r.deadline_date)}</div>
          <div class="list-item-date">${r.is_overdue ? `<span class="badge badge-danger">${t('overdue')}</span>` : `${r.days_remaining} ${t('days_remaining')}`}</div>
        </div>
      </div>`;
    }).join('');
  } catch (err) { console.error('GST error:', err); }
}


/* ═══════════════════════════════════════════════════════════
   EMAIL DRAFTS
   ═══════════════════════════════════════════════════════════ */

async function loadEmail() {
  try {
    const data = await api('/email/drafts');
    if (!data.drafts || !data.drafts.length) {
      document.getElementById('email-list').innerHTML = '<div class="empty-state"><div class="emoji">✉️</div><div class="msg">No email drafts available</div></div>';
      return;
    }
    document.getElementById('email-list').innerHTML = data.drafts.map((d, i) => `
      <div class="glass draft-card fade-in" style="animation-delay:${i * 0.05}s">
        <div class="draft-header">
          <div>
            <div class="draft-to">${d.counterparty}</div>
            <div class="draft-subject">${d.subject_preview}</div>
          </div>
          <div style="text-align:right">
            <div class="list-item-amount">${fmt(d.amount)}</div>
            <div class="list-item-date">${t('due')} ${fmtDate(d.due_date)}</div>
          </div>
        </div>
        <div class="draft-body">${d.body_preview.replace(/\n/g, '<br>')}</div>
        <button class="btn-ghost btn-sm" style="margin-top:0.5rem" onclick="loadFullDraft(${d.id}, this)">${t('view_full')}</button>
        <div class="draft-full" id="draft-full-${d.id}"></div>
      </div>`).join('');
  } catch (err) { console.error('Email error:', err); }
}

async function loadFullDraft(id, btn) {
  try {
    const el = document.getElementById('draft-full-' + id);
    if (el.classList.contains('visible')) { el.classList.remove('visible'); return; }
    const data = await api('/email/draft', { method: 'POST', body: JSON.stringify({ obligation_id: id }) });
    el.innerHTML = `<div class="draft-body" style="margin-top:0.5rem">${data.draft_body.replace(/\n/g, '<br>')}</div>`;
    el.classList.add('visible');
  } catch (err) { console.error('Draft error:', err); }
}


/* ═══════════════════════════════════════════════════════════
   COMMUNITY FORUM
   ═══════════════════════════════════════════════════════════ */

let CURRENT_CATEGORY = null;

async function loadCommunity() {
  try {
    document.getElementById('community-list-view').style.display = 'block';
    document.getElementById('community-detail-view').style.display = 'none';

    let url = '/community/posts';
    if (CURRENT_CATEGORY) url += `?category=${CURRENT_CATEGORY}`;
    const posts = await api(url);

    const postsEl = document.getElementById('community-posts');
    if (!posts.length) {
      postsEl.innerHTML = '<div class="empty-state"><div class="emoji">👥</div><div class="msg">No posts yet. Be the first to share!</div></div>';
      return;
    }
    postsEl.innerHTML = posts.map((p, i) => {
      const catIcons = { cash_flow: '💰', gst: '🧾', suppliers: '🤝', general: '💬' };
      return `<div class="glass post-card fade-in" style="animation-delay:${i * 0.04}s" onclick="viewPost(${p.id})">
        <div style="display:flex; justify-content:space-between; align-items:flex-start">
          <div class="post-title">${catIcons[p.category] || '💬'} ${p.title}</div>
          ${p.is_own ? '<span class="badge badge-info">You</span>' : ''}
        </div>
        <div class="post-preview">${p.content.substring(0, 150)}${p.content.length > 150 ? '...' : ''}</div>
        <div class="post-meta">
          <span>${t('by')} <strong>${p.business_name}</strong></span>
          <span>${p.created_at ? fmtTime(p.created_at) : ''}</span>
          <span>💬 ${p.reply_count} ${t('replies')}</span>
        </div>
      </div>`;
    }).join('');
  } catch (err) { console.error('Community error:', err); }
}

function filterPosts(category, btn) {
  CURRENT_CATEGORY = category;
  document.querySelectorAll('.category-pill').forEach(p => p.classList.remove('active'));
  if (btn) btn.classList.add('active');
  loadCommunity();
}

async function createPost() {
  const title = document.getElementById('new-post-title').value.trim();
  const content = document.getElementById('new-post-content').value.trim();
  const category = document.getElementById('new-post-category').value;
  if (!title || !content) return;

  try {
    await api('/community/posts', {
      method: 'POST',
      body: JSON.stringify({ title, content, category }),
    });
    document.getElementById('new-post-title').value = '';
    document.getElementById('new-post-content').value = '';
    loadCommunity();
  } catch (err) { console.error('Create post error:', err); }
}

async function viewPost(postId) {
  try {
    document.getElementById('community-list-view').style.display = 'none';
    document.getElementById('community-detail-view').style.display = 'block';

    const post = await api(`/community/posts/${postId}`);
    const catIcons = { cash_flow: '💰', gst: '🧾', suppliers: '🤝', general: '💬' };

    let html = `
      <div class="post-detail-back" onclick="loadCommunity()">← Back to Forum</div>
      <div class="glass card-body" style="margin-bottom:1rem">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem">
          <div class="post-title" style="font-size:1.1rem">${catIcons[post.category] || '💬'} ${post.title}</div>
          ${post.is_own ? '<span class="badge badge-info">You</span>' : ''}
        </div>
        <p style="color:var(--text-secondary); font-size:0.85rem; line-height:1.6">${post.content}</p>
        <div class="post-meta" style="margin-top:0.75rem">
          <span>${t('by')} <strong>${post.business_name}</strong></span>
          <span>${post.created_at ? fmtTime(post.created_at) : ''}</span>
        </div>
      </div>

      <div style="margin-bottom:0.75rem">
        <div class="stat-label">💬 ${post.replies ? post.replies.length : 0} ${t('replies')}</div>
      </div>`;

    if (post.replies && post.replies.length) {
      post.replies.forEach(r => {
        html += `<div class="glass reply-card fade-in">
          <div class="reply-author">${r.business_name} ${r.is_own ? '(You)' : ''}</div>
          <div class="reply-content">${r.content}</div>
          <div class="reply-time">${r.created_at ? fmtTime(r.created_at) : ''}</div>
        </div>`;
      });
    }

    html += `
      <div class="new-reply-form" style="margin-top:1rem">
        <textarea id="reply-text-${postId}" placeholder="Write a reply..."></textarea>
        <button class="btn-ghost" onclick="replyToPost(${postId})">${t('send_reply')}</button>
      </div>`;

    document.getElementById('community-detail-content').innerHTML = html;
  } catch (err) { console.error('View post error:', err); }
}

async function replyToPost(postId) {
  const textarea = document.getElementById('reply-text-' + postId);
  const content = textarea.value.trim();
  if (!content) return;

  try {
    await api(`/community/posts/${postId}/reply`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
    viewPost(postId); // Reload
  } catch (err) { console.error('Reply error:', err); }
}
