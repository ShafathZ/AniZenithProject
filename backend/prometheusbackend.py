from prometheus_client import Counter, Histogram, Gauge

# ----- Counters -----
# Total user messages received (Sum the conversation user messages)
USER_MESSAGES = Counter(
    "chatbot_user_messages_total",
    "Total number of user messages received",
    ["user_id", "model"]
)

# Total bot messages sent (Sum the conversation bot messages + 1 for response)
BOT_MESSAGES = Counter(
    "chatbot_bot_messages_total",
    "Total number of bot messages sent",
    ["user_id", "model"]
)

# ----- Gauges -----
# TODO: Update this variable if we start adding queuing
# Current queue length (if using async processing)
CHATBOT_QUEUE_LENGTH = Gauge(
    "chatbot_queue_length",
    "Number of messages currently in processing queue",
    ["model"]
)

# ----- Histograms -----
# Response latency histogram
PIPELINE_LATENCY = Histogram(
    "chatbot_pipeline_latency_seconds",
    "Time taken to process and respond to user messages (full pipeline)",
    ["model"]
)

# Retrieval time
RETRIEVAL_TIME = Histogram(
    "chatbot_retrieval_time_seconds",
    "Time taken to process retrieval mechanism",
["model"]
)

# Retrieval time
TOKEN_GENERATION_TIME = Histogram(
    "chatbot_token_generation_time_seconds",
    "Time taken for chatbot token generation",
["model"]
)

# User message lengths
USER_MESSAGE_LENGTH = Histogram(
    "chatbot_user_message_length",
    "Length of user messages in characters",
["model"]
)

# Bot message lengths
BOT_MESSAGE_LENGTH = Histogram(
    "chatbot_bot_message_length",
    "Length of bot messages in characters",
["model"]
)

# ----- Utility Prometheus Logging Functions -----
def observe_user_message(user_id: str, message: str, model: str):
    """Increment user message count and observe length."""
    USER_MESSAGES.labels(user_id=user_id, model=model).inc()
    USER_MESSAGE_LENGTH.labels(model=model).observe(len(message))

def observe_bot_message(user_id: str, message: str, model: str):
    """Increment bot message count and observe length."""
    BOT_MESSAGES.labels(user_id=user_id, model=model).inc()
    BOT_MESSAGE_LENGTH.labels(model=model).observe(len(message))

def observe_pipeline_latency(model: str, pipeline_time: float, retrieval_time: float, token_generation_time: float):
    """Record response latency for the full pipeline."""
    # TODO: Make this more dynamic in prometheus so we can add any arbitrary pipeline latency point
    PIPELINE_LATENCY.labels(model=model).observe(pipeline_time)
    RETRIEVAL_TIME.labels(model=model).observe(retrieval_time)
    TOKEN_GENERATION_TIME.labels(model=model).observe(token_generation_time)

def set_message_queue_length(model: str, length: int):
    """Set current message queue length."""
    CHATBOT_QUEUE_LENGTH.labels(model=model).set(length)