import os
from abc import ABC, abstractmethod
from threading import Thread
from typing import Iterator, Dict, Any, List

import torch
from huggingface_hub import InferenceClient
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

from backend.constants import MAX_NEW_TOKENS, TEMPERATURE, TOP_P

# TODO: Move to config management system
HF_TOKEN = os.getenv('HF_TOKEN')
local_model_id = "Qwen/Qwen3-0.6B"
external_model_id = "openai/gpt-oss-20b"

class Model(ABC):
    """
    Abstract base model.
    Enforces streaming + usage stats.
    """
    def __init__(self):
        self._usage: Dict[str, Any] = {}

    # Each subclass must implement streaming
    @abstractmethod
    def stream(self, messages: List[Dict[str, str]]) -> Iterator[str]:
        pass

    # Each subclass must define usage stats
    @abstractmethod
    def get_usage(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    # Generate runs stream and accumulates, then returns
    def generate(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Runs stream(), accumulates output, returns final text + usage.
        """
        output = []

        for chunk in self.stream(messages):
            output.append(chunk)

        result_text = "".join(output)

        return {
            "text": result_text,
            "usage": self.get_usage()
        }

class HFLocalModel(Model):
    def __init__(self):
        super().__init__()

        # Load local model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(local_model_id)
        self.model = AutoModelForCausalLM.from_pretrained(local_model_id, device_map="auto", torch_dtype=torch.float16)

        self._usage_data = None

    def stream(self, messages: List[Dict[str, str]]):
        self._usage_data = None
        # Apply chat template & tokenize input
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            return_tensors="pt",
            add_generation_prompt=True
        ).to(self.model.device)

        # Initialize streamer
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )

        # Make generation config
        gen_kwargs = dict(
            input_ids=inputs,
            streamer=streamer,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=TEMPERATURE,
            top_p=TOP_P
        )

        # Start another thread to run generation for streaming
        thread = Thread(target=self.model.generate, kwargs=gen_kwargs)
        thread.start()

        # Accumulate usage
        input_tokens = inputs["input_ids"].shape[-1]
        output_tokens = 0
        for text in streamer:
            yield text
            output_tokens += 1

        # Add usage data
        self._usage_data = {"input_tokens": input_tokens, "output_tokens": output_tokens}

    def get_usage(self):
        return {
            "model_name": self.get_name(),
            "input_tokens": self._usage_data["input_tokens"],
            "output_tokens": self._usage_data["output_tokens"],
        }

    def get_name(self):
        return local_model_id


class HFInferenceClientModel(Model):
    def __init__(self):
        super().__init__()

        self.client = InferenceClient(
            model=external_model_id,
            token=HF_TOKEN,
        )

        self._usage_data = None

    def stream(self, messages: List[Dict[str, str]]):
        self._usage_data = None

        # Use built in InferenceClient chat completion
        for chunk in self.client.chat_completion(
                messages=messages,
                max_tokens=MAX_NEW_TOKENS,
                stream=True,
                temperature=TEMPERATURE,
                top_p=TOP_P,
        ):
            yield chunk
            if hasattr(chunk, 'usage') and chunk.usage:
                self._usage_data = chunk.usage

    def get_name(self):
        return external_model_id

    def get_usage(self):
        return {
            "model_name": self.get_name(),
            "input_tokens": self._usage_data.prompt_tokens,
            "output_tokens": self._usage_data.completion_tokens,
        }