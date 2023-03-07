from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)

BOT_NAME = "Leoniabot"

INITIAL_PROMPT = f"""The following is a conversation between a human and bot, a very intelligent assistant based on a LLM. The bot, named {BOT_NAME}, tries to be helpful and tries to help the user answering his questions. The conversation begins:

<human>OK, {BOT_NAME}, I’m going to start by quizzing you with a few warm-up questions. Who became president of the USA in 2021?<bot>That would be Joe Biden.<human>ghjkhjabnufs<bot>That doesn’t seem to be a word. Could you ask me another way?<human>What is the smallest country in Africa?<bot>The smallest country in Africa is the Seychelles.<human>What's Python?<bot>Python is a high-level, interpreted, general-purpose programming language. It is an open source language that emphasizes code readability and allows developers to express concepts in fewer lines of code than other languages. Python supports multiple programming paradigms, including object-oriented, imperative, functional, and procedural, and has a large and comprehensive standard library.<human>Ok. If I have an equation like y = mx + c, can you rearrange it to be of the form x = ... ?<bot>Sure, it’s x = (y - c) / m when m != 0.<human>Let's try something more difficult, a question about sports. Who is the greatest quarterback of all time in your opinion?<bot>That is a hard one! Who is the greatest quarterback of all time is an inherently subjective question, but some common picks would be Dan Marino, Peyton Manning, Brett Favre, and of course Tom Brady. Tom Brady is my pick for the best quarterback."""


class ChatBot:
    def __init__(self, model_name: str):
        """Initialize the chat bot. This will load the model and tokenizer.
        The parameter is the name for the `from_pretrained` method of the
        `AutoModelForCausalLM` class, i.e., the name of the model or the path to
        the directory containing the model files."""
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.prev_prompt = None

    def initialize(self):
        """Initialize the chat bot. This will load the model and tokenizer."""
        print(f"Loading {self.model_name}...")

        if self.model_name != "theblackcat102/pythia-3b-deduped-sft-r1":
            raise ValueError(f"Invalid model name: {self.model_name}")

        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        self.prev_prompt = INITIAL_PROMPT

    def next_tokens(self, prompt: str) -> str:
        """Get the next tokens for the given prompt."""
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt", padding=True)
        output = self.model.generate(
            input_ids,
            max_length=len(input_ids[0]) + 20,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            early_stopping=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        answer = self.tokenizer.decode(
            output[0], truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"]
        )

        # Get everything after the prompt
        new_info = answer[len(prompt) - 3 :]

        return new_info

    def get_answer(self, user_msg: str) -> str:
        """Get the answer for the given user message."""
        end_token = "<|endoftext|>"

        prompt = self.prev_prompt + "<human>" + user_msg + "<bot>"
        next_tokens = self.next_tokens(prompt)
        new_info = next_tokens

        while True:
            if end_token in new_info:
                yield next_tokens.split(end_token)[0]
                break

            yield next_tokens

            prompt = prompt + next_tokens
            next_tokens = self.next_tokens(prompt)
            new_info += next_tokens

        # Update the prompt
        self.prev_prompt = prompt + new_info.split(end_token)[0]
