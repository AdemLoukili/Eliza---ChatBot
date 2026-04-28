/* ── PAGE SWITCHING ── */
function launchApp() {
  document.getElementById('landing-page').style.display = 'none';
  document.getElementById('app-page').style.display = 'block';
  loadSchools();
}
function backToLanding() {
  document.getElementById('app-page').style.display = 'none';
  document.getElementById('landing-page').style.display = 'block';
}

/* ── REVEAL ON SCROLL ── */
const revObs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.1 });
document.querySelectorAll('.reveal').forEach(el => revObs.observe(el));

/* ── LANDING DEMO ── */
const lpConvos = [
  { user: "Quels sont les horaires du campus ?", bot: "EPITECH Lyon est ouvert lun-ven 8h30-21h et sam 9h-17h. 📅" },
  { user: "Comment y aller en transport ?", bot: "Métro B → Jean Macé, puis T2 Centre Berthelot ou T1 Quai Claude Bernard. 🚇" },
  { user: "Où manger près du campus ?", bot: "RU Bourse du Travail, kebabs quai de Saône, et plusieurs restos dans le quartier. 🍽️" }
];
let lpIdx = 0;
function nextLpDemo() {
  const chat = document.getElementById('lp-chat-demo');
  if (lpIdx >= lpConvos.length) {
    lpIdx = 0;
    chat.innerHTML = '<div class="lp-cm bot"><div class="lp-cm-who">IONISBot</div>Bienvenue ! 👋 Je suis ton assistant pour le campus EPITECH Lyon.</div>';
    return;
  }
  const c = lpConvos[lpIdx++];
  const u = document.createElement('div');
  u.className = 'lp-cm user';
  u.innerHTML = `<div class="lp-cm-who">Toi</div>${c.user}`;
  chat.appendChild(u);
  const t = document.createElement('div');
  t.className = 'lp-cm bot';
  t.innerHTML = '<div class="lp-cm-who">IONISBot</div><div class="lp-dots"><span></span><span></span><span></span></div>';
  chat.appendChild(t);
  chat.scrollTop = chat.scrollHeight;
  setTimeout(() => { t.innerHTML = `<div class="lp-cm-who">IONISBot</div>${c.bot}`; chat.scrollTop = chat.scrollHeight; }, 1200);
}

/* ── CHATBOT ── */
let SCHOOLS = {}, selectedSchool = '', selectedCampus = '', history = [], loading = false;

async function loadSchools() {
  try {
    const r = await fetch('/schools');
    SCHOOLS = await r.json();
    renderSchoolTabs();
  } catch {
    document.getElementById('select-screen').innerHTML =
      '<p style="color:var(--muted);margin-top:40px">❌ Impossible de charger les données. Vérifie que Flask tourne sur le port 8000.</p>';
  }
}

function renderSchoolTabs() {
  const tabs = document.getElementById('school-tabs');
  tabs.innerHTML = '';
  Object.keys(SCHOOLS).forEach(school => {
    const btn = document.createElement('button');
    btn.className = 'school-tab'; btn.textContent = school;
    btn.onclick = () => selectSchool(school);
    tabs.appendChild(btn);
  });
}

function selectSchool(school) {
  selectedSchool = school;
  document.querySelectorAll('.school-tab').forEach(b => b.classList.toggle('active', b.textContent === school));
  const desc = document.getElementById('school-desc');
  desc.textContent = `${SCHOOLS[school].domaine} — ${SCHOOLS[school].description}`;
  desc.classList.add('visible');
  renderCampusGrid(SCHOOLS[school].campus);
}

function renderCampusGrid(campusList) {
  const grid = document.getElementById('campus-grid');
  grid.innerHTML = '';
  campusList.forEach(city => {
    const btn = document.createElement('button');
    btn.className = 'c-btn';
    btn.innerHTML = `<span class="city">${city}</span>`;
    btn.onclick = () => startChat(city);
    grid.appendChild(btn);
  });
}

function startChat(campus) {
  selectedCampus = campus;
  document.getElementById('select-screen').style.display = 'none';
  document.getElementById('chat-screen').style.display = 'flex';
  document.getElementById('quick-row').style.display = 'flex';
  document.getElementById('input-zone').style.display = 'block';
  document.getElementById('campus-tag').style.display = 'flex';
  document.getElementById('tag-school').textContent = selectedSchool;
  document.getElementById('tag-campus').textContent = campus;
  addMsg('bot', `Bienvenue sur IONISBot ! 👋\n\nJe suis ton assistant pour le campus **${selectedSchool} — ${campus}**.\n\nPose-moi tes questions sur les horaires, les transports, la restauration, les formations, l'admission ou la vie étudiante.`);
  document.getElementById('user-input').focus();
}

function resetSelection() {
  selectedSchool = ''; selectedCampus = ''; history = [];
  document.getElementById('chat-screen').style.display = 'none';
  document.getElementById('chat-screen').innerHTML = '';
  document.getElementById('quick-row').style.display = 'none';
  document.getElementById('input-zone').style.display = 'none';
  document.getElementById('campus-tag').style.display = 'none';
  document.getElementById('select-screen').style.display = 'flex';
  document.querySelectorAll('.school-tab').forEach(b => b.classList.remove('active'));
  document.getElementById('school-desc').classList.remove('visible');
  document.getElementById('campus-grid').innerHTML = '';
}

function addMsg(role, text) {
  const chat = document.getElementById('chat-screen');
  const wrap = document.createElement('div'); wrap.className = `msg ${role}`;
  const who = document.createElement('div'); who.className = 'msg-who';
  who.textContent = role === 'user' ? 'TOI' : `IONISBOT · ${selectedSchool.toUpperCase()} ${selectedCampus.toUpperCase()}`;
  const bubble = document.createElement('div'); bubble.className = 'bubble';
  bubble.textContent = text;
  wrap.appendChild(who); wrap.appendChild(bubble);
  chat.appendChild(wrap); chat.scrollTop = chat.scrollHeight;
  return wrap;
}

function addTyping() {
  const chat = document.getElementById('chat-screen');
  const wrap = document.createElement('div'); wrap.className = 'msg bot typing'; wrap.id = 'typing';
  const who = document.createElement('div'); who.className = 'msg-who'; who.textContent = 'IONISBOT';
  const bubble = document.createElement('div'); bubble.className = 'bubble';
  bubble.innerHTML = '<div class="d"></div><div class="d"></div><div class="d"></div>';
  wrap.appendChild(who); wrap.appendChild(bubble);
  chat.appendChild(wrap); chat.scrollTop = chat.scrollHeight;
}

function removeTyping() { const t = document.getElementById('typing'); if (t) t.remove(); }

const input = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
input.addEventListener('input', () => { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 120) + 'px'; });
input.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } });

async function send() {
  const msg = input.value.trim();
  if (!msg || loading) return;
  loading = true; sendBtn.disabled = true;
  input.value = ''; input.style.height = 'auto';
  addMsg('user', msg); history.push({ role: 'user', content: msg }); addTyping();
  try {
    const r = await fetch('/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, history: history.slice(-10), school: selectedSchool, campus: selectedCampus })
    });
    const d = await r.json();
    removeTyping(); addMsg('bot', d.reply);
    history.push({ role: 'assistant', content: d.reply });
  } catch {
    removeTyping();
    addMsg('bot', '❌ Impossible de joindre le serveur. Vérifie que python app.py tourne sur le port 8000.');
  }
  loading = false; sendBtn.disabled = false; input.focus();
}

function quick(text) { input.value = text; send(); }