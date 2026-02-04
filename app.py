import gradio as gr
from pathlib import Path
import backend
from constants import SYSTEM_PROMPT

theme_css = Path("static/css/theme.css").read_text() if Path("static/css/theme.css").exists() else ""
main_css = Path("static/css/gradiomain.css").read_text()
CSS = theme_css + "\n\n" + main_css

# Load static directory
gr.set_static_paths(paths=[Path.cwd().absolute()/"static"])

# Adapter function between frontend and backend. Returns a generator yielding backend results.
def respond(
    message,
    history: list[dict[str, str]],
    system_message,
    use_local_model,
    max_tokens,
    temperature,
    top_p,
    hf_token: gr.OAuthToken,
):
    for r in backend.process_user_query(system_message, history, message, use_local_model, max_tokens, temperature, top_p, hf_token.token):
        yield r

with gr.Blocks() as homepage:
    gr.Markdown(
        """
        # Anime Recommendation Chatbot
        An AI designed to give recommendations of the best anime options based on your preferences! Has knowledge of a full database of anime!
        """,
        elem_classes=["page-header"]
    )

    with gr.Sidebar():
        gr.LoginButton()

    # System message textbox
    system_msg = gr.Textbox(
        value="You are a friendly Chatbot.",
        label="System message",
        elem_classes=["system-msg"]
    )

    # Drop down section (Advanced Settings)
    with gr.Accordion("Advanced Settings", open=False):
        max_tokens_slider = gr.Slider(
            minimum=1,
            maximum=2048,
            value=512,
            step=1,
            label="Max new tokens",
            elem_classes=["custom-slider"]
        )
        temperature_slider = gr.Slider(
            minimum=0.1,
            maximum=2.0,
            value=0.7,
            step=0.1,
            label="Temperature",
            elem_classes=["custom-slider"]
        )
        top_p_slider = gr.Slider(
            minimum=0.1,
            maximum=1.0,
            value=0.95,
            step=0.05,
            label="Top-p (nucleus sampling)",
            elem_classes=["custom-slider"]
        )
        use_local_model = gr.Checkbox(
            label="Use Local Model?",
            value=False,
            elem_classes=["toggle-button"]
        )

    # Main chatbot interface
    chatbot = gr.ChatInterface(
        respond,
        additional_inputs=[
            system_msg,
            use_local_model,
            max_tokens_slider,
            temperature_slider,
            top_p_slider
        ],
    )
    chatbot.chatbot.elem_classes = ["custom-chatbot"]

if __name__ == "__main__":
    homepage.launch(css=CSS)