
def process_user_query(system_message, history, user_message, use_local_model, max_tokens, temperature, top_p, hf_token):
    genre_list = detect_genres(user_message)
    recommendations = get_recommendations()
