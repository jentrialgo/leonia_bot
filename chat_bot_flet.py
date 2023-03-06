import time
from typing import Optional
import flet as ft

from transformers import BloomForCausalLM
from transformers import BloomTokenizerFast
from transformers import GPTNeoXForCausalLM, AutoTokenizer

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
USER: """


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
        print(f"Loading model {self.model_name}...")
        if self.model_name == "EleutherAI/pythia-70m":
            self.model = GPTNeoXForCausalLM.from_pretrained(self.model_name)
        else:
            self.model = BloomForCausalLM.from_pretrained(self.model_name)

        print("Loading tokenizer...")
        if self.model_name == "EleutherAI/pythia-70m":
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        else:
            self.tokenizer = BloomTokenizerFast.from_pretrained(self.model_name)

        self.prev_prompt = INITIAL_PROMPT

    def next_tokens(self, prompt: str) -> str:
        print("\n\n*****************\n\nprompt:")
        print(prompt)

        input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
        output = self.model.generate(
            input_ids,
            max_length=len(input_ids[0]) + 8,
            do_sample=True,
            top_k=50,
            top_p=0.95,
        )
        answer = self.tokenizer.decode(output[0])

        # Get everything after the prompt
        new_info = answer[len(prompt) - 2 :]

        return new_info

    def get_answer(self, user_msg: str) -> str:
        prompt = self.prev_prompt + user_msg + f"\n{BOT_NAME}: "

        next_tokens = self.next_tokens(prompt)
        new_info = next_tokens
        print(new_info)
        yield new_info

        while True:
            prompt = prompt + " " + next_tokens
            next_tokens = self.next_tokens(prompt)
            new_info += next_tokens
            print("Next tokens:", next_tokens)

            if "\nUSER:" in new_info:
                yield next_tokens.split("\nUSER: ")[0]
                break

            yield next_tokens + " "

        print("Answer finished")

        # Update the prompt
        self.prev_prompt = prompt


class Conversation:
    def __init__(self, page):
        self.page = page
        self.col_conversation = ft.Column(controls=[])
        self.last_text_bot = None

        self.page.add(self.col_conversation)

    def add_bot_msg(self, msg: str, elapsed_sec: Optional[float] = None) -> None:
        text_bot = ft.Text(
            value=msg,
            color=ft.colors.WHITE,
        )
        user_msg = ft.Container(
            content=text_bot, bgcolor=ft.colors.PURPLE_500, padding=20
        )

        self.col_conversation.controls.append(user_msg)

        if elapsed_sec is not None:
            text_elapsed = ft.Text(
                value=f"{elapsed_sec:.2f} sec = {elapsed_sec / 60:.2f} min",
                style=ft.TextThemeStyle.BODY_SMALL,
                color=ft.colors.BLACK38,
            )
            self.col_conversation.controls.append(text_elapsed)

        self.col_conversation.update()

        self.last_text_bot = text_bot

    def append_bot_msg(self, msg: str) -> None:
        if self.last_text_bot is None:
            raise ValueError("No previous bot message")

        self.last_text_bot.value += f"{msg}"
        self.last_text_bot.update()

    def add_user_msg(self, msg: str) -> None:
        text = ft.Text(
            value=msg,
            color=ft.colors.WHITE,
        )
        bot_msg = ft.Container(
            content=text,
            bgcolor=ft.colors.GREEN_500,
            padding=20,
            margin=ft.Margin(top=0, left=150, right=0, bottom=0),
        )

        self.col_conversation.controls.append(bot_msg)
        self.col_conversation.update()


def main(page: ft.Page):
    def on_enter(event: ft.ControlEvent) -> None:
        conversation.add_user_msg(tf_input.value)

        progress.visible = True
        progress.update()

        start = time.time()
        answer_iterator = chat_bot.get_answer(tf_input.value)
        end = time.time()
        elapsed_sec = end - start
        conversation.add_bot_msg(next(answer_iterator), elapsed_sec)
        for answer in answer_iterator:
            print("answer:", answer)
            conversation.append_bot_msg(answer)

        progress.visible = False
        progress.update()

        # Clear the input
        tf_input.value = ""
        tf_input.update()

    page.scroll = True
    page.title = "Bbot"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER

    img = ft.Image(
        src=f"/lion.png",
        width=200,
        height=200,
        fit=ft.ImageFit.CONTAIN,
    )
    page.add(img)

    conversation = Conversation(page)

    # Other alternative models:
    # - EleutherAI/pythia-70m
    # - bigscience/bloom-7b1
    # - theblackcat102/pythia-1b-deduped-sft
    chat_bot = ChatBot("bigscience/bloom-7b1")

    progress_text = ft.Text("I'm turning on. Please wait...")
    progress = ft.Column(
        [ft.ProgressRing(), progress_text],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    page.add(progress)

    chat_bot.initialize()

    progress.visible = False
    progress.controls[1].value = "Thinking..."

    conversation.add_bot_msg(f"Hello, I'm {BOT_NAME}! How can I help you?")

    tf_input = ft.TextField(
        hint_text="Type your message here",
        on_submit=on_enter,
    )
    page.add(tf_input)


ft.app(target=main, view=ft.WEB_BROWSER, assets_dir="./")
