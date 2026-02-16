# -*- coding: utf-8 -*-
import os, sys, io, base64
import gradio as gr
import numpy as np
import librosa, matplotlib.pyplot as plt
import librosa.display

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT)

# Internal imports
from BabyCryLast import analyze as core_analyze
from website.ui_translations import TRANSLATIONS, DEFAULT_TRANSLATIONS, localize_result
from website.ui_style import PREMIUM_CSS, SPLASH_HTML
from website.ai_assistant import ask_gpt


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------
def _fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=140)
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode("ascii")
    plt.close(fig)
    return f"data:image/png;base64,{data}"


def _render_viz(audio_path: str, label_text: str):
    """
    Visualization block that makes sense to a parent:
    1. Cry duration and energy curve
    2. Emotional intensity profile
    3. Calmness vs. distress radar
    """
    y, sr = librosa.load(audio_path, sr=16000, mono=True)
    dur = len(y) / sr

    # ------------------------------------------------------------
    # 1. Cry Energy Curve
    # ------------------------------------------------------------
    hop_length = 512
    energy = np.array([
        np.sum(np.abs(y[i:i+hop_length]**2))
        for i in range(0, len(y), hop_length)
    ])
    times = np.linspace(0, dur, len(energy))
    fig, ax = plt.subplots(figsize=(7, 2))
    ax.plot(times, energy, color="#14d3c3", linewidth=1.8)
    ax.fill_between(times, energy, color="#14d3c3", alpha=0.25)
    ax.set_title("Cry Energy Over Time", fontsize=11, color="white")
    ax.set_xlabel("Time (s)", color="#cbd3e6")
    ax.set_ylabel("Energy", color="#cbd3e6")
    ax.tick_params(colors="#cbd3e6")
    ax.set_facecolor("#0e1730")
    fig.patch.set_facecolor("#0e1730")
    energy_html = (
        f"<img src='{_fig_to_b64(fig)}' "
        f"style='width:100%;border-radius:12px;margin-top:6px;'>"
        f"<p style='font-size:13px;opacity:0.75;'>"
        f"This graph shows how strong and intense the cry was over time. "
        f"Sudden peaks usually mean bursts of distress or pain.</p>"
    )

    # ------------------------------------------------------------
    # 2. Emotional Intensity Profile (bar chart)
    # ------------------------------------------------------------
    emotions = ["hunger", "pain", "tiredness", "discomfort", "loneliness"]
    np.random.seed(abs(hash(label_text)) % (10**6))
    values = np.clip(np.abs(np.random.randn(len(emotions))) * 0.8, 0.2, 1.0)
    fig, ax = plt.subplots(figsize=(6, 2))
    bars = ax.bar(emotions, values, color="#14d3c3", alpha=0.9)
    for i, v in enumerate(values):
        ax.text(i, v + 0.02, f"{int(v*100)}%", ha="center", color="white", fontsize=9)
    ax.set_ylim(0, 1.2)
    ax.set_title("Emotional Intensity Profile", fontsize=11, color="white")
    ax.tick_params(axis="x", colors="#cbd3e6")
    ax.tick_params(axis="y", colors="#cbd3e6")
    ax.set_facecolor("#0e1730")
    fig.patch.set_facecolor("#0e1730")
    bar_html = (
        f"<img src='{_fig_to_b64(fig)}' "
        f"style='width:100%;border-radius:12px;margin-top:6px;'>"
        f"<p style='font-size:13px;opacity:0.75;'>"
        f"This bar chart shows which emotional cues were most dominant. "
        f"High 'pain' or 'discomfort' levels often match intense crying.</p>"
    )
    # ------------------------------------------------------------
    # 2. Cry Stability Analysis (replaces Emotional Intensity Profile)
    # ------------------------------------------------------------
    frame_len = 2048
    hop = 512
    energy = np.array([
        np.sum(np.abs(y[i:i+frame_len]**2))
        for i in range(0, len(y), hop)
    ])
    zcr = librosa.feature.zero_crossing_rate(y, frame_length=frame_len, hop_length=hop)[0]
    
    # Normalize both curves for comparison
    energy_norm = energy / np.max(energy + 1e-8)
    zcr_norm = zcr / np.max(zcr + 1e-8)
    
    fig, ax = plt.subplots(figsize=(7, 2))
    ax.plot(energy_norm, color="#14d3c3", linewidth=1.8, alpha=0.9, label="Cry Energy")
    ax.plot(zcr_norm, color="#e57373", linewidth=1.2, alpha=0.9, label="Pitch Variability (ZCR)")
    ax.fill_between(range(len(energy_norm)), energy_norm, color="#14d3c3", alpha=0.25)
    ax.fill_between(range(len(zcr_norm)), zcr_norm, color="#e57373", alpha=0.15)
    ax.legend(fontsize=8, loc="upper right", facecolor="#0e1730", labelcolor="white")
    ax.set_title("Cry Stability Analysis", fontsize=11, color="white")
    ax.set_xlabel("Time (frames)", color="#cbd3e6")
    ax.set_ylabel("Relative Intensity", color="#cbd3e6")
    ax.tick_params(colors="#cbd3e6")
    ax.set_facecolor("#0e1730")
    fig.patch.set_facecolor("#0e1730")
    
    bar_html = (
        f"<img src='{_fig_to_b64(fig)}' "
        f"style='width:100%;border-radius:12px;margin-top:6px;'>"
        f"<p style='font-size:13px;opacity:0.75;'>"
        f"This analysis compares <b>energy</b> and <b>pitch stability</b> of the baby’s cry. "
        f"Smooth, regular lines often mean calm or sleepy crying, while sharp irregular peaks "
        f"signal discomfort, belly pain, or sudden distress.</p>"
    )

    

    return energy_html + bar_html  


# ----------------------------------------------------------------------
# Build Gradio App
# ----------------------------------------------------------------------
def build_app():
    MAP_HTML_PATH = os.path.join(os.path.dirname(__file__), "ui_map.html")
    with open(MAP_HTML_PATH, "r", encoding="utf-8") as f:
        MAP_HTML = f.read()

    with gr.Blocks(css=PREMIUM_CSS, theme=gr.themes.Soft()) as app:
        gr.HTML(SPLASH_HTML)
        lang_state = gr.State("en")

        with gr.Column(elem_classes="container-narrow"):
            with gr.Row(elem_classes="hero"):
                with gr.Column(scale=12):
                    title = gr.Markdown("", elem_id="app-title")
                    tagline = gr.Markdown("", elem_classes="tagline")
                    lang_radio = gr.Radio(
                        choices=["en", "tj", "ru"],
                        value="en",
                        label="🌐 Language",
                        interactive=True,
                        elem_classes="lang-switch",
                    )

            tabs_labels = DEFAULT_TRANSLATIONS["en"]["tab_labels"]

            with gr.Tabs(elem_classes="tabs"):
                # ------------------------------------------------------------
                # Analyzer
                # ------------------------------------------------------------
                with gr.TabItem(f"{tabs_labels['analyze']}"):
                    last_result = gr.State("")
                    with gr.Row():
                        with gr.Column(scale=6, elem_classes="card"):
                            analyzer_header = gr.Markdown("", elem_classes="section-title")
                            audio = gr.Audio(sources=["microphone", "upload"], type="filepath", label="")
                            analyze_btn = gr.Button("", elem_classes="primary-btn")
                        with gr.Column(scale=6, elem_classes="card"):
                            result_header = gr.Markdown("", elem_classes="section-title")
                            result = gr.HTML("<div class='result-box'></div>")
                            chat_context_btn = gr.Button("💬 Chat about this analysis", visible=False)

                # ------------------------------------------------------------
                # Hospitals
                # ------------------------------------------------------------
                with gr.TabItem(f"{tabs_labels['hospitals']}"):
                    with gr.Column(elem_classes="card"):
                        hospitals_header = gr.Markdown("", elem_classes="section-title")
                        map_hint = gr.Markdown("")
                        gr.HTML(MAP_HTML)

                # ------------------------------------------------------------
                # KudakAI Assistant
                # ------------------------------------------------------------
                with gr.TabItem("💬 Ask KudakAI"):
                    with gr.Column(elem_classes="card"):
                        chat_header = gr.Markdown("### 💬 Chat with KudakAI")
                        chat_history = gr.State([])
                        chat_box = gr.Chatbot(label="KudakAI", height=500, type="messages")
                        chat_input = gr.Textbox(
                            label="Your message",
                            placeholder="Type something (e.g. My baby keeps crying at night...)",
                            lines=2,
                        )
                        send_btn = gr.Button("Send", elem_classes="primary-btn")

                        def do_chat(user_text, history):
                            if not user_text.strip():
                                return history, history
                            history = history + [{"role": "user", "content": user_text}]
                            convo = "\n".join(f"{m['role']}: {m['content']}" for m in history[-6:])
                            try:
                                answer = ask_gpt(convo)
                                history.append({"role": "assistant", "content": answer})
                                return history, history
                            except Exception as e:
                                history.append({"role": "assistant", "content": f"⚠️ Error: {e}"})
                                return history, history

                        send_btn.click(do_chat, inputs=[chat_input, chat_history], outputs=[chat_box, chat_history])
                        chat_input.submit(do_chat, inputs=[chat_input, chat_history], outputs=[chat_box, chat_history])

            # ------------------------------------------------------------
            # Footer
            # ------------------------------------------------------------
            footer = gr.HTML(f"<div class='footer'>{DEFAULT_TRANSLATIONS['en']['footer']}</div>")

            # ------------------------------------------------------------
            # Logic
            # ------------------------------------------------------------
            def apply_lang(lang_choice: str):
                d = TRANSLATIONS.get(lang_choice, DEFAULT_TRANSLATIONS["en"])
                return (
                    d["app_title"], d["app_tagline"], d["analyzer_header"],
                    d["upload_label"], d["analyze_btn"], d["result_label"],
                    d["hospitals_header"], d["map_hint"],
                    d["about_header"], d["about_md"], d["footer"], lang_choice
                )

            def do_analyze(path, lang_choice):
                raw = core_analyze(path)

                # Support explainable model output (dict)
                if isinstance(raw, dict):
                    label = raw.get("label", "")
                    reasoning = raw.get("reasoning", "")
                    localized = f"<b>Detected:</b> {label}<br><b>Why:</b> {reasoning}"
                    text = label
                else:
                    text = " ".join(str(x) for x in raw) if isinstance(raw, (list, tuple)) else str(raw)
                    localized = localize_result(text, lang_choice)

                # Add visualization
                try:
                    viz_html = _render_viz(path, text)
                except Exception:
                    viz_html = ""

                # Calm medical summary for atypical cries
                if any(k in localized.lower() for k in ["atypical", "атипич", "ғайримуқаррар"]):
                    med_prompt = (
                        f"You are KudakGPT. Answer in {lang_choice}. "
                        f"Give 3 calm bullet points about unusual baby cries "
                        f"and recommend contacting a pediatrician if symptoms persist."
                    )
                    try:
                        summary = ask_gpt(med_prompt)
                        localized += f"<br><br><b>Medical Info:</b><br>{summary}"
                    except Exception:
                        pass

                html = f"<div class='result-box'>{localized}</div><div>{viz_html}</div>"
                return html, localized, gr.update(visible=True)

            analyze_btn.click(do_analyze, inputs=[audio, lang_state], outputs=[result, last_result, chat_context_btn])

            # ------------------------------------------------------------
            # Language setup
            # ------------------------------------------------------------
            (
                t_title, t_tag, t_ahead, t_ulab, t_btn, t_rhead,
                t_hhead, t_hint, t_abhead, t_abmd, t_foot, _
            ) = apply_lang("en")

            title.value = t_title
            tagline.value = t_tag
            analyzer_header.value = t_ahead
            audio.label = t_ulab
            analyze_btn.value = t_btn
            result_header.value = t_rhead
            hospitals_header.value = t_hhead
            map_hint.value = t_hint
            footer.value = f"<div class='footer'>{t_foot}</div>"

            lang_radio.change(
                apply_lang,
                inputs=[lang_radio],
                outputs=[
                    title, tagline,
                    analyzer_header, audio, analyze_btn, result_header,
                    hospitals_header, map_hint,
                    footer, lang_state,
                ],
            )
            lang_radio.label = f"🌐 {DEFAULT_TRANSLATIONS['en']['lang_label']}"

    return app


# ----------------------------------------------------------------------
# Launch
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = build_app()
    app.launch(share="True")
