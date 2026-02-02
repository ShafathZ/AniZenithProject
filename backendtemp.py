from huggingface_hub import InferenceClient
import gradio as gr


def respond(
    message,
    history: list[dict[str, str]],
    system_message,
    max_tokens,
    temperature,
    top_p,
    hf_token: gr.OAuthToken,
):
    client = InferenceClient(
        token=hf_token.token,
        model="openai/gpt-oss-20b"
    )

    messages = [{"role": "system", "content": system_message}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    for chunk in client.chat_completion(
        messages,
        max_tokens=max_tokens,
        stream=True,
        temperature=temperature,
        top_p=top_p,
    ):
        if chunk.choices and chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            response += token
            yield response

# 1) respond(message,
#     history: list[dict[str, str]],
#     use_local_model: bool,
#     hf_token: gr.OAuthToken)

# 2) process_user_query(user_message, history, system_message, use_local_model, max_tokens, temperature, top_p, hf_token)
#   2.1) detect_genres(user_message) -> List[str]
#   2.2) get_recommendations(genres: List[str], limit: int) -> str (json-like)
#   2.3) query_model(system_prompt, context, chat_history, use_local_model, max_tokens, temperature, top_p) -> (Streamable)str
#       2.3.1) InferenceClient or pipline: client.chat_completion(messages, max_tokens, temperature, top_p) -> (Streamable)str
# 3) Frontend: Collect(str)