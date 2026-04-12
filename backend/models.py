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

class Model(ABC):
    """
    Abstract base model.
    Enforces streaming + usage stats.
    """
    def __init__(self, name: str):
        self._usage: Dict[str, Any] = {}
        self.name = name

    # Each subclass must implement streaming
    @abstractmethod
    def stream(self, messages: List[Dict[str, str]]) -> Iterator[str]:
        pass

    # Each subclass must define usage stats
    @abstractmethod
    def get_usage(self) -> Dict[str, Any]:
        pass

    def get_name(self):
        return self.name

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
    def __init__(self, model_id: str):
        super().__init__(model_id)

        # Load local model and tokenizer (use efficient model params)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float16)
        self.model.eval()

        self._usage_data = None

    def stream(self, messages: List[Dict[str, str]]):
        self._usage_data = None
        print("Starting tokenize")
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

        def generate():
            # Ensure no gradients
            with torch.inference_mode():
                try:
                    self.model.generate(input_ids=inputs['input_ids'],
                                        attention_mask=inputs['attention_mask'],
                                        max_new_tokens=MAX_NEW_TOKENS,
                                        do_sample=True,
                                        temperature=TEMPERATURE,
                                        top_p=TOP_P,
                                        use_cache=True, # Use KV Cache
                                        streamer=streamer # Adds the text streamer to capture output callback
                                        )
                except Exception as e:
                    # Stop streamer and propagate error
                    self._thread_error = e
                    streamer.end()

        print("Starting stream")
        # Start another thread to run generation for streaming
        thread = Thread(target=generate)
        thread.start()

        # Accumulate usage
        input_token_count = inputs['input_ids'].shape[-1]
        output_token_count = 0
        for text in streamer:
            yield text
            output_token_count += 1

        # Clean up thread
        thread.join()

        # Add usage data
        self._usage_data = {"input_token_count": input_token_count, "output_token_count": output_token_count}

    def get_usage(self):
        return {
            "model_name": self.get_name(),
            "input_token_count": self._usage_data["input_token_count"],
            "output_token_count": self._usage_data["output_token_count"],
        }


class HFInferenceClientModel(Model):
    def __init__(self, model_id: str):
        super().__init__(model_id)

        self.client = InferenceClient(
            model=model_id,
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
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                yield token
            # Add usage data for logging
            if hasattr(chunk, 'usage') and chunk.usage:
                self._usage_data = chunk.usage

    def get_usage(self):
        return {
            "model_name": self.get_name(),
            "input_token_count": self._usage_data.prompt_tokens,
            "output_token_count": self._usage_data.completion_tokens,
        }