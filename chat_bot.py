from transformers import (
    BloomForCausalLM,
    BloomTokenizerFast,
    GPTNeoXForCausalLM,
    AutoTokenizer,
    AutoModelForCausalLM,
)

BOT_NAME = "Bbot"

INITIAL_PROMPT = f"""The following is a conversation between a USER and {BOT_NAME}, a very intelligent assistant based on a LLM. {BOT_NAME} tries to be helpful and tries to help the user answering his questions. The conversation begins:

USER: OK, {BOT_NAME}, I’m going to start by quizzing you with a few warm-up questions. Who became president of the USA in 2021?
{BOT_NAME}: That would be Joe Biden.
USER: ghjkhjabnufs
{BOT_NAME}: That doesn’t seem to be a word. Could you ask me another way?
USER: What is the smallest country in Africa? 
{BOT_NAME}: The smallest country in Africa is the Seychelles.
USER: What's Python?
{BOT_NAME}: Python is a high-level, interpreted, general-purpose programming language. It is an open source language that emphasizes code readability and allows developers to express concepts in fewer lines of code than other languages. Python supports multiple programming paradigms, including object-oriented, imperative, functional, and procedural, and has a large and comprehensive standard library.
USER: Ok. If I have an equation like y = mx + c, can you rearrange it to be of the form x = ... ?
{BOT_NAME}: Sure, it’s x = (y - c) / m when m != 0.
USER: Let's try something more difficult, a question about sports. Who is the greatest quarterback of all time in your opinion?
{BOT_NAME}: That is a hard one! Who is the greatest quarterback of all time is an inherently subjective question, but some common picks would be Dan Marino, Peyton Manning, Brett Favre, and of course Tom Brady. Tom Brady is my pick for the best quarterback. Brady became the greatest quarterback in NFL history because of his career records: he has played in 264 games and no one has surpassed his record 581 passing touchdowns. He also won 7 Super Bowls!
"""


class ChatBot:
    def __init__(self, model_name: str):
        """Initialize the chat bot. This will load the model and tokenizer.
        The parameters are the same as the ones for the `from_pretrained` method
        of the `BloomForCausalLM` class, i.e., the name of the model or the path
        to the directory containing the model files."""
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.prev_prompt = None

    def initialize(self):
        initial_prompt = INITIAL_PROMPT
        print(f"Loading {self.model_name}...")
        if self.model_name == "EleutherAI/pythia-70m":
            self.model = GPTNeoXForCausalLM.from_pretrained(self.model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        elif self.model_name == "bigscience/bloom-7b1":
            self.model = BloomForCausalLM.from_pretrained(self.model_name)
            self.tokenizer = BloomTokenizerFast.from_pretrained(self.model_name)
        elif self.model_name == "theblackcat102/pythia-3b-deduped-sft":
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            initial_prompt = (
                INITIAL_PROMPT.replace("\nUSER:", "<human>")
                .replace("\nBbot:", "<bot>")
                .replace("between a USER and Bbot", "between a <human> and a <bot>")
                .replace("Ok, Bbot", "Ok, bot")
            )
        else:
            raise ValueError(f"Invalid model name: {self.model_name}")

        self.prev_prompt = initial_prompt

    def next_tokens(self, prompt: str) -> str:
        print("\n\n*****************\n\nprompt:")
        print(prompt)

        input_ids = self.tokenizer.encode(prompt, return_tensors="pt", padding=True)
        output = self.model.generate(
            input_ids,
            max_length=len(input_ids[0]) + 2,
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
        prompt = self.prev_prompt + "<human>" + user_msg + f"<bot> "

        next_tokens = self.next_tokens(prompt)
        new_info = next_tokens
        print("new_info:", new_info)
        yield new_info

        while True:
            prompt = prompt + next_tokens
            next_tokens = self.next_tokens(prompt)
            new_info += next_tokens
            print("Next tokens:", next_tokens)

            # TODO: other models use "\nUSER:"
            end_token = "<|endoftext|>"
            if end_token in new_info:
                yield next_tokens.split(end_token)[0]
                break

            yield next_tokens

        print("Answer finished")

        # Update the prompt
        self.prev_prompt = prompt
