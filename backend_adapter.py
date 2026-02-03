import gradio as gr
import backend


def respond(
    message,
    history: list[dict[str, str]],
    system_message,
    max_tokens,
    temperature,
    top_p,
    hf_token: gr.OAuthToken,
):
    for r in backend.process_user_query(system_message, history, message, True, max_tokens, temperature, top_p, hf_token):
        yield r