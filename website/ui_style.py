# -*- coding: utf-8 -*-
# ======================================================================
# Premium CSS + Animated Splash + Refined Layout
# ======================================================================

PREMIUM_CSS = r"""
:root {
  --bg: #080d18;
  --panel: #0f1730;
  --card: #121a36;
  --muted: #9aa3b5;
  --acc1: #7c5cff;
  --acc2: #14d3c3;
  --acc3: #ff7ac3;
  --ring: rgba(124,92,255,0.35);
}

.gradio-container {
  font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background:
    radial-gradient(1200px 700px at 15% 10%, rgba(124,92,255,0.20), transparent 40%),
    radial-gradient(1100px 600px at 85% 18%, rgba(20,211,195,0.18), transparent 40%),
    linear-gradient(180deg, #080d18, #0a0f1c 60%, #0a0e19);
  color: #e6e9ef;
}

/* Splash overlay */
#splash {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  background: radial-gradient(900px 600px at 50% 35%, rgba(124,92,255,0.16), transparent 50%),
              linear-gradient(180deg, #090e1b, #0a0f1c);
  z-index: 9999;
  animation: fadeOut 1.2s ease 1.6s forwards;
}
@keyframes fadeOut { to { opacity: 0; visibility: hidden; } }
.logo-hero {
  font-weight: 900;
  font-size: 62px;
  letter-spacing: 0.6px;
  background: linear-gradient(135deg, #f4f4ff 0%, #bfb6ff 30%, #7c5cff 65%, #14d3c3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 50px rgba(124,92,255,0.45);
  animation: floatUp 1.2s ease-out;
}
@keyframes floatUp {
  0% { transform: translateY(40px); opacity: 0; }
  100% { transform: translateY(0); opacity: 1; }
}

/* General container */
.container-narrow { max-width: 1180px; margin: 0 auto; }

/* Header / Hero */
.hero {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: linear-gradient(90deg, rgba(124,92,255,0.08), rgba(20,211,195,0.08));
  border: 1px solid rgba(255,255,255,0.06);
  padding: 24px 20px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}
#app-title {
  margin: 0;
  font-weight: 900;
  font-size: 2.5rem;
  letter-spacing: 0.25px;
  background: linear-gradient(120deg, #ffffff, #cfd6ff 40%, #b2a1ff 70%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 4px 25px rgba(124,92,255,0.35);
}
.tagline {
  color: var(--muted);
  margin-top: 8px;
  font-size: 1.08rem;
  letter-spacing: 0.1px;
}

/* Language switch styling */
.lang-switch {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  margin-top: 20px !important;
}

.lang-switch label {
  display: block !important;
  text-align: center !important;
  font-weight: 600 !important;
  color: var(--muted);
  margin-bottom: 10px !important;
  font-size: 1rem;
}

.lang-switch input[type="radio"] + span {
  padding: 6px 12px;
  border-radius: 8px;
  transition: background 0.25s;
}

.lang-switch input[type="radio"]:checked + span {
  background: linear-gradient(135deg, var(--acc1), var(--acc2));
  color: white;
}


/* Cards */
.card {
  background: var(--card);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 18px;
  box-shadow: 0 10px 36px rgba(0,0,0,0.35);
  transition: transform .25s ease, box-shadow .25s ease;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 44px rgba(0,0,0,0.45);
}
.section-title {
  margin: 0 0 10px 0;
  font-weight: 800;
  font-size: 1.15rem;
  letter-spacing: .25px;
}

/* Buttons */
.primary-btn button {
  background: linear-gradient(135deg, var(--acc1), var(--acc2));
  border: 0;
  color: white;
  font-weight: 700;
  border-radius: 12px;
  font-size: 1rem;
  padding: 10px 18px;
  transition: transform .15s ease, filter .15s ease;
}
.primary-btn button:hover {
  filter: brightness(1.08);
  transform: translateY(-2px);
}

/* Results */
.result-box {
  white-space: pre-wrap;
  border-left: 4px solid var(--acc2);
  background: rgba(20,211,195,0.08);
  padding: 18px 20px;
  border-radius: 14px;
  font-size: 1.05rem;
  line-height: 1.55;
  color: #e6e9ef;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  transition: transform .25s ease;
  animation: fadeIn 0.6s ease-out;
}
.result-box:hover { transform: translateY(-2px); }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Tabs */
.tabs > div[role="tablist"] button {
  border-radius: 12px !important;
  padding: 8px 14px;
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 0.1px;
  color: #e6e9ef;
}

/* Footer */
.footer {
  margin: 25px auto 10px auto;
  text-align: center;
  color: #cbd3e6;
  opacity: 0.75;
  font-size: 0.95rem;
  border-top: 1px solid rgba(255,255,255,0.06);
  padding-top: 12px;
  letter-spacing: 0.1px;
}
footer { display: none !important; }
"""

SPLASH_HTML = """
<div id="splash">
  <div class="logo-hero">KudakAI</div>
</div>
<script>
setTimeout(() => {
  const s = document.getElementById('splash');
  if (s) s.style.display = 'none';
}, 3200);
</script>
"""
