"""Look and feel for StudyLens AI.

Design idea: a study desk. Ruled-paper lines, a highlighter-yellow accent
(the app literally highlights the evidence it used), ink-blue surfaces.
"""

PALETTES = {
    "dark": {
        "bg": "#100F24", "panel": "#1A1838", "panel2": "#221F47",
        "line": "rgba(255,255,255,.10)", "text": "#ECEBFA", "muted": "#A3A1C8",
        "violet": "#8B73FF", "mint": "#3DDBB0", "input": "#221F47",
        "shadow": "0 14px 36px rgba(0,0,0,.45)", "rule": "rgba(139,115,255,.13)",
        "glow": "rgba(139,115,255,.20)",
    },
    "light": {
        "bg": "#F3F4FB", "panel": "#FFFFFF", "panel2": "#F0F1FA",
        "line": "rgba(27,26,58,.12)", "text": "#1B1A3A", "muted": "#5D5B82",
        "violet": "#6246EA", "mint": "#0E9F7A", "input": "#FFFFFF",
        "shadow": "0 12px 30px rgba(27,26,58,.10)", "rule": "rgba(98,70,234,.10)",
        "glow": "rgba(98,70,234,.12)",
    },
}

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700;800&family=Figtree:wght@400;500;600;700&display=swap');

:root {
  --bg:__bg__; --panel:__panel__; --panel2:__panel2__; --line:__line__;
  --text:__text__; --muted:__muted__; --violet:__violet__; --mint:__mint__;
  --input:__input__; --shadow:__shadow__; --rule:__rule__;
  --mark:#FFD93D; --mark-ink:#1B1500;
  --display:'Bricolage Grotesque','Segoe UI',system-ui,sans-serif;
  --body:'Figtree','Segoe UI',system-ui,sans-serif;
}

html, body, .stApp, [class*="st-"] { font-family: var(--body); }
.stApp, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(900px 480px at 95% -8%, __glow__, transparent 62%),
    var(--bg);
  color: var(--text);
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 1160px; padding-top: 2.2rem; padding-bottom: 5rem; }

/* text */
.stApp p, .stApp li, .stApp label, .stApp span,
[data-testid="stMarkdownContainer"] { color: var(--text); }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
  font-family: var(--display); color: var(--text); letter-spacing: -.01em; }
[data-testid="stCaptionContainer"], .stApp small { color: var(--muted) !important; }

/* sidebar */
[data-testid="stSidebar"] { background: var(--panel); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] .block-container { padding-top: 1rem; }
.brand { display:flex; align-items:center; gap:.65rem; padding:.2rem 0 .6rem 0; }
.brand-mark { width:38px; height:38px; border-radius:11px; display:grid; place-items:center;
  background: var(--mark); color: var(--mark-ink); font-size:1.25rem; }
.brand-name { font-family: var(--display); font-weight:800; font-size:1.25rem; line-height:1.1; }
.brand-sub { font-size:.75rem; color: var(--muted); }
[data-testid="stSidebarNavLink"] { border-radius: 10px; margin: 2px 0; }
[data-testid="stSidebarNavLink"][aria-current="page"] {
  background: var(--panel2); box-shadow: inset 3px 0 0 var(--mark); font-weight:700; }
[data-testid="stSidebarNavSeparator"] { color: var(--muted); }

/* inputs */
[data-baseweb="input"] > div, [data-baseweb="textarea"] > div, [data-baseweb="select"] > div,
.stTextInput input, .stTextArea textarea, .stNumberInput input {
  background: var(--input) !important; color: var(--text) !important;
  border-color: var(--line) !important; border-radius: 12px !important; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--violet) !important; }
div[data-baseweb="select"] svg { fill: var(--text); }
[data-baseweb="popover"] ul, [data-baseweb="menu"] { background: var(--panel) !important; }
[data-baseweb="popover"] li, [data-baseweb="menu"] li { color: var(--text) !important; }
[data-testid="stFileUploaderDropzone"] {
  background: var(--panel2); border: 1.5px dashed var(--violet); border-radius: 14px; }
[data-testid="stFileUploaderDropzone"] * { color: var(--text) !important; }
[data-testid="stFileUploaderFile"], [data-testid="stFileChip"] { background: transparent !important; }
[data-testid="stFileUploaderFile"] *, [data-testid="stFileChip"] * { color: var(--text) !important; }

/* buttons */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
  border-radius: 12px; border: 1px solid var(--line); background: var(--panel);
  color: var(--text); font-weight: 600; transition: border-color .15s, box-shadow .15s; }
.stButton > button:hover, .stFormSubmitButton > button:hover {
  border-color: var(--violet); box-shadow: 0 0 0 3px var(--rule); color: var(--text); }
.stButton > button:focus-visible { outline: 3px solid var(--violet); outline-offset: 2px; }
button[kind="primary"], [data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primaryFormSubmit"] {
  background: var(--mark) !important; color: var(--mark-ink) !important;
  border-color: var(--mark) !important; font-weight: 700 !important; }
button[kind="primary"] *, [data-testid="stBaseButton-primary"] *,
[data-testid="stBaseButton-primaryFormSubmit"] * { color: var(--mark-ink) !important; }
[data-testid="stPageLink"] a { border-radius: 10px; font-weight: 600; }
[data-testid="stPageLink"] a:hover { background: var(--panel2); }

/* tabs */
.stTabs [role="tablist"] { gap: 4px; border-bottom: 1px solid var(--line); }
.stTabs [role="tab"] { border-radius: 10px 10px 0 0; padding: 8px 16px; background: transparent; }
.stTabs [role="tab"][aria-selected="true"] { box-shadow: inset 0 -3px 0 var(--mark); font-weight: 700; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* containers, metrics, expanders, alerts */
[class*="st-key-tile_"] { background: var(--panel); border: 1px solid var(--line);
  border-radius: 18px; padding: 1.1rem 1.3rem; height: 100%; }
[class*="st-key-tile_"]:hover { border-color: var(--violet); }
[data-testid="stMetric"] { background: var(--panel); border: 1px solid var(--line);
  border-radius: 14px; padding: .8rem 1rem; }
[data-testid="stMetricValue"] { font-family: var(--display); font-weight: 800; }
[data-testid="stExpander"] { background: var(--panel); border: 1px solid var(--line); border-radius: 14px; }
[data-testid="stExpander"] details { border: none !important; background: transparent !important; }
[data-testid="stAlert"] { background: var(--panel) !important; border: 1px solid var(--line);
  border-radius: 14px; }
[data-testid="stAlert"] * { color: var(--text) !important; }
[data-testid="stSlider"] * { color: var(--text); }

/* page header */
.page-head { display:flex; align-items:center; gap:1rem; margin: 0 0 1.4rem 0; padding-bottom: 1rem;
  border-bottom: 1px solid var(--line); }
.page-icon { width:52px; height:52px; border-radius:14px; display:grid; place-items:center;
  font-size:1.6rem; background: var(--panel2); border: 1px solid var(--line); flex:none; }
.page-head h1 { margin:0; font-size:2rem; line-height:1.1; }
.page-head p { margin:.25rem 0 0 0; color: var(--muted); max-width: 62ch; }

/* hero: ruled notebook paper */
.hero { display:grid; grid-template-columns: 1.15fr 1fr; gap: 2rem; align-items:center;
  padding: 2.6rem 2.6rem; border-radius: 26px; border: 1px solid var(--line);
  background:
    repeating-linear-gradient(to bottom, transparent 0 35px, var(--rule) 35px 36px),
    linear-gradient(90deg, transparent 0 58px, rgba(255,90,90,.35) 58px 59px, transparent 59px),
    var(--panel);
  box-shadow: var(--shadow); margin-bottom: 1.6rem; }
.hero h1 { font-size: clamp(2rem, 4.2vw, 3.3rem); line-height: 1.04; margin: 0 0 1rem 0;
  font-weight: 800; padding-left: 1.4rem; }
.hero .lead { font-size: 1.12rem; line-height: 1.55; color: var(--muted); max-width: 46ch;
  padding-left: 1.4rem; margin: 0 0 1.1rem 0; }
.hero .sources { padding-left: 1.4rem; display:flex; flex-wrap:wrap; gap:.5rem; }
.pill { display:inline-block; padding:.28rem .8rem; border-radius:999px; font-size:.84rem;
  font-weight:600; border:1px solid var(--line); background: var(--panel2); color: var(--text); }

/* the evidence demo card: the one memorable element */
.demo { background: var(--bg); border:1px solid var(--line); border-radius:18px; padding:1.1rem 1.2rem;
  box-shadow: var(--shadow); animation: bob 6s ease-in-out infinite; }
.demo .q { font-weight:700; margin-bottom:.7rem; }
.demo .meta { font-size:.8rem; color: var(--muted); margin-bottom:.35rem; }
.demo .quote { font-size:.95rem; line-height:1.6; padding:.7rem .85rem; border-radius:12px;
  background: var(--panel2); border-left: 4px solid var(--mark); }
.demo .ans { margin-top:.8rem; font-size:.95rem; line-height:1.55; }
.demo .tag { display:inline-block; font-size:.74rem; font-weight:700; padding:2px 9px;
  border-radius:999px; background: var(--mint); color:#04271e; margin-left:6px; }
mark { background: var(--mark); color: var(--mark-ink); padding: 0 3px; border-radius: 4px; }
@keyframes bob { 0%,100% { transform: translateY(0) } 50% { transform: translateY(-8px) } }

/* steps + feature copy */
.step { display:flex; gap:.9rem; align-items:flex-start; padding:.2rem 0; }
.step .n { flex:none; width:34px; height:34px; border-radius:50%; display:grid; place-items:center;
  font-family: var(--display); font-weight:800; background: var(--mark); color: var(--mark-ink); }
.step b { display:block; font-size:1.02rem; }
.step span { color: var(--muted); font-size:.92rem; }
.tile-title { font-family: var(--display); font-weight:800; font-size:1.25rem; margin:0 0 .25rem 0; }
.tile-text { color: var(--muted); font-size:.95rem; line-height:1.5; margin:0 0 .4rem 0; }

/* answers + evidence */
.answer { border-left: 6px solid var(--mark); background: var(--panel); border-radius: 14px;
  padding: 1.1rem 1.3rem; font-size: 1.06rem; line-height:1.65; box-shadow: var(--shadow); }
.answer.nf { border-left-color: #E08A00; }
.ev { background: var(--panel); border:1px solid var(--line); border-radius:16px;
  padding: 1rem 1.2rem; margin: .6rem 0 .3rem 0; line-height:1.6; }
.badge { display:inline-block; padding:2px 10px; border-radius:999px; font-size:.78rem;
  font-weight:700; color:#fff; margin-left:8px; }
.empty { text-align:center; padding: 2.6rem 1.5rem; border:1.5px dashed var(--line);
  border-radius: 20px; background: var(--panel); }
.empty .big { font-size:2.4rem; }
.empty h3 { margin:.4rem 0 .3rem 0; }
.empty p { color: var(--muted); max-width: 48ch; margin: 0 auto; }
.status { font-size:.85rem; color: var(--muted); }
.status b { color: var(--text); }

/* floating study guide */
.fab-wrap { position: fixed; right: 26px; bottom: 26px; z-index: 9999; }
.fab { width:56px; height:56px; border-radius:50%; display:grid; place-items:center; font-size:1.5rem;
  cursor:pointer; background: var(--mark); color: var(--mark-ink);
  box-shadow: 0 10px 26px rgba(0,0,0,.35); animation: bob 4s ease-in-out infinite; }
.fab-card { position:absolute; right:0; bottom:72px; width:280px; padding:14px 16px; border-radius:16px;
  background: var(--panel); color: var(--text); border:1px solid var(--line); box-shadow: var(--shadow);
  opacity:0; transform: translateY(10px); pointer-events:none; transition: all .22s ease;
  font-size:.9rem; line-height:1.55; }
.fab-wrap:hover .fab-card, .fab-wrap:focus-within .fab-card { opacity:1; transform:none; pointer-events:auto; }
.fab-card b { color: var(--violet); }

@media (max-width: 860px) {
  .hero { grid-template-columns: 1fr; padding: 1.6rem 1.2rem; }
  .fab-wrap { display:none; }
}
@media (prefers-reduced-motion: reduce) { .demo, .fab { animation: none; } }
</style>
"""


def theme_css(dark=True):
    p = PALETTES["dark" if dark else "light"]
    css = _CSS
    for key, value in p.items():
        css = css.replace(f"__{key}__", value)
    return css


def page_header(icon, title, subtitle):
    return (
        f'<div class="page-head"><div class="page-icon">{icon}</div>'
        f'<div><h1>{title}</h1><p>{subtitle}</p></div></div>'
    )


def empty_state(icon, title, text):
    return f'<div class="empty"><div class="big">{icon}</div><h3>{title}</h3><p>{text}</p></div>'


BRAND_HTML = """
<div class="brand">
  <div class="brand-mark">🔎</div>
  <div><div class="brand-name">StudyLens AI</div><div class="brand-sub">Answers you can check</div></div>
</div>
"""

HERO_HTML = """
<div class="hero">
  <div>
    <h1>Know exactly where every answer comes from.</h1>
    <p class="lead">Upload your textbooks and notes, then ask questions in plain language.
    StudyLens answers and highlights the page it used, so you can check it before you trust it.</p>
    <div class="sources">
      <span class="pill">📄 PDFs</span><span class="pill">🌐 Websites</span>
      <span class="pill">🎥 YouTube lectures</span><span class="pill">📝 Your own notes</span>
    </div>
  </div>
  <div class="demo" aria-label="Example of an answer with evidence">
    <div class="q">What is overfitting?</div>
    <div class="meta">Example · lecture-notes.pdf · Page 14 <span class="tag">Strong match</span></div>
    <div class="quote">A model that learns the training data too closely, including its noise,
      <mark>performs poorly on new data</mark> it has not seen before.</div>
    <div class="ans"><b>Answer:</b> Overfitting is when a model memorises its training examples,
    so it does well on them but badly on new data.</div>
  </div>
</div>
"""

FLOATING_HELP_HTML = """
<div class="fab-wrap" tabindex="0">
  <div class="fab-card">
    <b>Quick study guide</b><br>
    1. Add PDFs in the sidebar<br>
    2. Ask a question on <b>Ask</b><br>
    3. Check the highlighted evidence<br>
    4. Turn it into notes, quizzes, flashcards<br>
    5. Paste a link on <b>Web &amp; video</b>
  </div>
  <div class="fab" aria-label="Help">💡</div>
</div>
"""
