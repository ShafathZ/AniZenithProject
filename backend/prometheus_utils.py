from prometheus_client import Counter, Histogram, Gauge, Summary
import numpy as np

# ----- Counters -----
# Total user messages received
CHATBOT_USER_MESSAGES_TOTAL_COUNTER = Counter(
    "chatbot_user_messages_total",
    "Total number of user messages received",
    ["user_id", "model"]
)

# Total bot messages sent
CHATBOT_BOT_MESSAGES_TOTAL_COUNTER = Counter(
    "chatbot_bot_messages_total",
    "Total number of bot messages sent",
    ["user_id", "model"]
)

# ----- Gauges -----
# TODO: Update this variable if we start adding queuing
# Current queue length (if using async processing)
CHATBOT_QUEUE_LENGTH_GAUGE = Gauge(
    "chatbot_queue_length",
    "Number of messages currently in processing queue",
    ["model"]
)

# ----- Histograms -----
# Latency of full pipeline stages
CHATBOT_PIPELINE_LATENCY_SUMMARY = Summary(
    "chatbot_pipeline_latency_seconds",
    "Time taken for different stages of chatbot pipeline",
    ["model", "stage"]
)

# User message lengths
CHATBOT_USER_MESSAGE_LENGTH_HISTOGRAM = Histogram(
    "chatbot_user_message_length",
    "Length of user messages in characters",
["model"],
    buckets=list(np.linspace(0, 1000, 21)) # Sets up buckets evenly spaced [0, 50, 100, ...]
)

# Bot message lengths
CHATBOT_BOT_MESSAGE_LENGTH_HISTOGRAM = Histogram(
    "chatbot_bot_message_length",
    "Length of bot messages in characters",
["model"],
    buckets=list(np.linspace(0, 1000, 21)) # Sets up buckets evenly spaced [0, 50, 100, ...]
)

# User token lengths
CHATBOT_USER_TOKEN_LENGTH_HISTOGRAM = Histogram(
    "chatbot_user_token_length",
    "Length of user messages in tokens",
["model"],
    buckets=list(np.linspace(0, 2000, 21)) # Sets up buckets evenly spaced [0, 100, 200, ...]
)

# Bot token lengths
CHATBOT_BOT_TOKEN_LENGTH_HISTOGRAM = Histogram(
    "chatbot_bot_token_length",
    "Length of bot messages in tokens",
["model"],
    buckets=list(np.linspace(0, 2000, 21)) # Sets up buckets evenly spaced [0, 100, 200, ...]
)

# ----- Utility Prometheus Logging Functions -----
def observe_user_message(user_id: str, user_message: str, token_count: int, model: str):
    """Increment user message count and observe length."""
    CHATBOT_USER_MESSAGES_TOTAL_COUNTER.labels(user_id=user_id, model=model).inc()
    CHATBOT_USER_MESSAGE_LENGTH_HISTOGRAM.labels(model=model).observe(len(user_message))
    CHATBOT_USER_TOKEN_LENGTH_HISTOGRAM.labels(model=model).observe(token_count)

def observe_bot_message(user_id: str, bot_message: str, token_count: int, model: str):
    """Increment bot message count and observe length."""
    CHATBOT_BOT_MESSAGES_TOTAL_COUNTER.labels(user_id=user_id, model=model).inc()
    CHATBOT_BOT_MESSAGE_LENGTH_HISTOGRAM.labels(model=model).observe(len(bot_message))
    CHATBOT_BOT_TOKEN_LENGTH_HISTOGRAM.labels(model=model).observe(token_count)

def set_message_queue_length(model: str, length: int):
    """Set current message queue length."""
    CHATBOT_QUEUE_LENGTH_GAUGE.labels(model=model).set(length)