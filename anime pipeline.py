import json
from transformers import pipeline

SYSTEM_PROMPT = 'You write cookie recipes using ONLY the ingredients listed. You do not need to use all the listed ingredients.'
USER_PROMPT = 'eggs, yogurt, flour, salt, brown sugar, ketchup, powdered sugar, fish paste'

def query_model(system_prompt, context, chat_history, use_local_model, user_message, max_tokens, temperature, top_p):

    pipe_liquid = pipeline(task='text-generation', model='LiquidAI/LFM2.5-1.2B-Thinking')

    chat = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': USER_PROMPT}
    ]

    messages = [{"role": "system", "content": system_prompt + context}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    response3 = pipe_liquid(chat, do_sample=False, max_tokens=max_tokens)

    ## print(json.dumps(response3, indent=2))
    ## print(response3[0]['generated_text'][-1]['content'].split('</think>')[-1].strip())


    if use_local_model == True:
        print(response3[0]['generated_text'][-1]['content'].split('</think>')[-1].strip())
    elif use_local_model == False:
        response = ""
        for chunk in pipe_liquid.chat_completion(
                chat,
                max_tokens=max_tokens,
                stream=True,
                temperature=temperature,
                top_p=top_p,
        ):
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                response += token
                yield response

