import gradio as gr
import json, os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from BabyCryLast import analyze

# Load translations
with open(os.path.join(os.path.dirname(__file__), "translations.json"), "r", encoding="utf-8") as f:
    translations = json.load(f)

DEFAULT_LANG = "en"

def get_t(lang, key):
    return translations[lang].get(key, key)

def build_ui(lang):
    t = translations[lang]
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    css = open(css_path, "r").read()

    with gr.Blocks(css=css, title="👶 BabyCry Analyzer") as app:
        # HEADER
        gr.HTML("""
        <div style='text-align:center;margin-top:30px;'>
            <h1>👶 BabyCry Analyzer</h1>
            <p style='font-size:1.1rem;color:#444;'>AI-powered detection of baby emotions & atypical cry patterns</p>
        </div>
        """)

        # NAVIGATION BAR
        with gr.Row(elem_classes="card"):
            home_btn = gr.Button("🏠 Home")
            analyze_btn = gr.Button("🎧 Analyze")
            hospitals_btn = gr.Button("🗺️ Hospitals (Soon)")
            lang_btn = gr.Dropdown(["en", "tj", "ru"], value=lang, label="🌐 Language")

        # PAGE: HOME
        with gr.Column(visible=True, elem_classes="card page") as home_page:
            gr.HTML("""
            <h2>Welcome</h2>
            <p>This system helps parents and doctors identify the baby’s emotional state 
            and early indicators of developmental conditions.</p>
            """)
            start_btn = gr.Button("🚀 Start Analysis")

        # PAGE: ANALYZE
        with gr.Column(visible=False, elem_classes="card page") as analyze_page:
            gr.HTML("<h2>🎙️ Upload or Record Baby Cry</h2>")
            audio_in = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Audio")
            result_box = gr.HTML("<div class='result-box'>Result will appear here...</div>")
            analyze_button = gr.Button("🔍 Analyze Now")

            def run_analysis(audio):
                if not audio:
                    return "<div class='result-box'>❌ No audio provided.</div>"
                res = analyze(audio)
                return f"<div class='result-box'>{res}</div>"

            analyze_button.click(run_analysis, inputs=audio_in, outputs=result_box)

        # PAGE: MAP
        with gr.Column(visible=False, elem_classes="card page") as hospitals_page:
            gr.HTML("<h2>Nearby Hospitals</h2><p>Map integration coming soon...</p>")

        # NAVIGATION LOGIC
        def switch(page):
            return (
                gr.update(visible=(page == "home")),
                gr.update(visible=(page == "analyze")),
                gr.update(visible=(page == "hospitals"))
            )

        home_btn.click(lambda: switch("home"), outputs=[home_page, analyze_page, hospitals_page])
        analyze_btn.click(lambda: switch("analyze"), outputs=[home_page, analyze_page, hospitals_page])
        hospitals_btn.click(lambda: switch("hospitals"), outputs=[home_page, analyze_page, hospitals_page])
        start_btn.click(lambda: switch("analyze"), outputs=[home_page, analyze_page, hospitals_page])

        gr.HTML("<div class='footer'>© 2025 BabyCry Analyzer | AI Health Companion</div>")

    return app

if __name__ == "__main__":
    ui = build_ui(DEFAULT_LANG)
    ui.launch()
