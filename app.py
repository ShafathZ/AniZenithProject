import gradio as gr
from pathlib import Path
import backend
from constants import *

theme_css = Path("static/css/theme.css").read_text() if Path("static/css/theme.css").exists() else ""
main_css = Path("static/css/gradiomain.css").read_text()
CSS = theme_css + "\n\n" + main_css

# Load static directory
gr.set_static_paths(paths=[Path.cwd().absolute()/"static"])

# Adapter function between frontend and backend. Returns a generator yielding backend results.
def respond(
    message,
    history: list[dict[str, str]],
    use_local_model,
    hf_token: gr.OAuthToken,
):
    for r in backend.process_user_query(SYSTEM_PROMPT, history, message, use_local_model, MAX_TOKENS, TEMPERATURE, TOP_P, hf_token.token):
        yield r

with gr.Blocks() as homepage:
    gr.Markdown(
        """
        # Ani<span style="font-size: 2rem;">ℤ</span>enith
        An AI designed to give recommendations of the best anime options based on your preferences! Has knowledge of a full database of anime!
        """,
        elem_classes=["page-header"]
    )

    with gr.Sidebar():
        gr.LoginButton()

    local_model = gr.Checkbox(
        label="Use Local Model?",
        value=False,
        elem_classes=["toggle-button"]
    )

    # Main chatbot interface
    chatbot = gr.ChatInterface(
        respond,
        additional_inputs=[
            local_model,
        ],
    )
    chatbot.chatbot.elem_classes = ["custom-chatbot"]

if __name__ == "__main__":
    homepage.launch(css=CSS)