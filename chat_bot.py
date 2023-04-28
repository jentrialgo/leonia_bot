"""This module contains the `ChatBot` class, which is used to interact with the
chat bot."""

from typing import Iterator
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)

BOT_NAME = "Leonia Bot"

MODEL_INFO = {
    "OASST_SFT_4_PYTHIA_12B_EPOCH_3_5": {
        "repo": "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5",
        "requirements": "48 GB RAM, 23 GB disk",
        "max_length": 1000,
        "do_sample": True,
        "top_k": 50,
        "top_p": 0.95,
        "num_return_sequences": 1,
        "padding": True,
        "token_end": "<|endoftext|>",
        "token_human": "<|prompter|>",
        "token_bot": "<|assistant|>",
    },
    "OASST_SFT_7_STABLELM_7B_EPOCH_3": {
        "repo": "OpenAssistant/stablelm-7b-sft-v7-epoch-3",
        "requirements": "32 GB RAM (CPU), 15 GB disk",
        "max_length": 1000,
        "do_sample": True,
        "top_k": 50,
        "top_p": 0.95,
        "num_return_sequences": 1,
        "padding": True,
        "token_end": "<|endoftext|>",
        "token_human": "<|USER|>",
        "token_bot": "<|ASSISTANT|>",
    },
    "STABLELM-TUNED-ALPHA-3B": {
        "repo": "stabilityai/stablelm-tuned-alpha-3b",
        "requirements": "16 GB RAM (CPU), 14 GB disk",
        "max_length": 1000,
        "do_sample": True,
        "top_k": 50,
        "top_p": 0.95,
        "num_return_sequences": 1,
        "padding": False,
        "token_end": "<|endoftext|>",
        "token_human": "<|USER|>",
        "token_bot": "<|ASSISTANT|>",
    },
    "DISTILGPT2": {  # Just for testing. Produces gibberish.
        "repo": "distilgpt2",
        "max_length": 1000,
        "do_sample": True,
        "top_k": 50,
        "top_p": 0.95,
        "num_return_sequences": 1,
        "padding": False,
        "token_end": "<|endoftext|>",
        "token_human": "<|prompter|>",
        "token_bot": "<|assistant|>",
    },
}

INITIAL_PROMPT = f"""The following is a conversation between a human and bot, a very intelligent assistant based on a LLM. The bot, named {BOT_NAME}, tries to be helpful and tries to help the user answering his questions. The conversation begins:

<human>OK, {BOT_NAME}, I’m going to start by quizzing you with a few warm-up questions. Who became president of the USA in 2021?<bot>That would be Joe Biden.<human>ghjkhjabnufs<bot>That doesn’t seem to be a word. Could you ask me another way?<human>What is the smallest country in Africa?<bot>The smallest country in Africa is the Seychelles.<human>What's Python?<bot>Python is a high-level, interpreted, general-purpose programming language. It is an open source language that emphasizes code readability and allows developers to express concepts in fewer lines of code than other languages. Python supports multiple programming paradigms, including object-oriented, imperative, functional, and procedural, and has a large and comprehensive standard library.<human>Ok. If I have an equation like y = mx + c, can you rearrange it to be of the form x = ... ?<bot>Sure, it’s x = (y - c) / m when m != 0.<human>Let's try something more difficult, a question about sports. Who is the greatest quarterback of all time in your opinion?<bot>That is a hard one! Who is the greatest quarterback of all time is an inherently subjective question, but some common picks would be Dan Marino, Peyton Manning, Brett Favre, and of course Tom Brady. Tom Brady is my pick for the best quarterback."""


class ChatBotConf:
    """This class contains the configuration for the chat bot."""

    def __init__(self, model_name: str):
        """Initialize the configuration. The parameter is the name for the
        `from_pretrained` method of the `AutoModelForCausalLM` class, i.e., the
        name of the model or the path to the directory containing the model
        files."""
        self.model_name = model_name

        if self.model_name not in MODEL_INFO:
            raise ValueError(f"Invalid model name: {self.model_name}")

        params = MODEL_INFO[self.model_name]
        self.token_end = params["token_end"]
        self.token_human = params["token_human"]
        self.token_bot = params["token_bot"]


class ChatBot:
    """This class implements the chat bot."""

    def __init__(self, model_name: str):
        """Initialize the chat bot. This will load the model and tokenizer.
        The parameter is the name for the `from_pretrained` method of the
        `AutoModelForCausalLM` class, i.e., the name of the model or the path to
        the directory containing the model files."""
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.prev_prompt = None
        self.conf = ChatBotConf(model_name)

    def initialize(self):
        """Initialize the chat bot. This will load the model and tokenizer."""
        print(f"Loading {MODEL_INFO[self.model_name]['repo']}...")

        if self.model_name not in MODEL_INFO:
            raise ValueError(f"Invalid model name: {self.model_name}")

        repo = MODEL_INFO[self.model_name]["repo"]
        self.model = AutoModelForCausalLM.from_pretrained(repo)
        self.tokenizer = AutoTokenizer.from_pretrained(repo)

        self.prev_prompt = INITIAL_PROMPT

    def next_tokens(self, prompt: str) -> str:
        """Get the next tokens for the given prompt."""
        params = MODEL_INFO[self.model_name]
        input_ids = self.tokenizer.encode(
            prompt,
            return_tensors="pt",
            padding=params["padding"],
        )
        output = self.model.generate(
            input_ids,
            max_length=len(input_ids[0]) + 20,
            do_sample=True,
            top_k=params["top_k"],
            top_p=params["top_p"],
            early_stopping=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        answer = self.tokenizer.decode(
            output[0], truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"]
        )

        # Get everything after the prompt
        new_info = answer[len(prompt) - 3 :]

        return new_info

    def get_answer(self, user_msg: str) -> Iterator[str]:
        """Get the answer for the given user message."""
        prompt = (
            self.prev_prompt + self.conf.token_human + user_msg + self.conf.token_bot
        )
        next_tokens = self.next_tokens(prompt)
        new_info = next_tokens

        while True:
            if self.conf.token_end in new_info:
                yield next_tokens.split(self.conf.token_end)[0]
                break

            yield next_tokens

            prompt = prompt + next_tokens
            next_tokens = self.next_tokens(prompt)
            new_info += next_tokens

        # Update the prompt
        self.prev_prompt = prompt + new_info.split(self.conf.token_end)[0]
