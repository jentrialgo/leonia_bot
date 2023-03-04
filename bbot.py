from typing import Tuple
import flet as ft

from transformers import BloomForCausalLM
from transformers import BloomTokenizerFast

INITIAL_PROMPT = """The following is a conversation between a USER and BLOOM, a very intelligent assistant based on a LLM. BLOOM tries to be helpful and tries to help the user answering his questions. The conversation begins:

USER: OK, Bloom, I’m going to start by quizzing you with a few warm-up questions. Who became president of the USA in 2021?
BLOOM: That would be Joe Biden.
USER: ghjkhjabnufs
BLOOM: That doesn’t seem to be a word. Could you ask me another way?
USER: What is the smallest country in Africa? 
BLOOM: The smallest country in Africa is the Seychelles.
USER: What's Python?
BLOOM: Python is a high-level, interpreted, general-purpose programming language. It is an open source language that emphasizes code readability and allows developers to express concepts in fewer lines of code than other languages. Python supports multiple programming paradigms, including object-oriented, imperative, functional, and procedural, and has a large and comprehensive standard library.
USER: Ok. If I have an equation like y = mx + c, can you rearrange it to be of the form x = ... ?
BLOOM: Sure, it’s x = (y - c) / m when m != 0.
USER: Let's try something more difficult, a question about sports. Who is the greatest quarterback of all time in your opinion?
BLOOM: That is a hard one! Who is the greatest quarterback of all time is an inherently subjective question, but some common picks would be Dan Marino, Peyton Manning, Brett Favre, and of course Tom Brady. Tom Brady is my pick for the best quarterback. Brady became the greatest quarterback in NFL history because of his career records: he has played in 264 games and no one has surpassed his record 581 passing touchdowns. He also won 7 Super Bowls!
USER: """


def add_bot_msg(page: ft.Page, col_conversation: ft.Container, msg: str) -> None:
    text = ft.Text(
        value=msg,
        color=ft.colors.WHITE,
    )
    user_msg = ft.Container(content=text, bgcolor=ft.colors.PURPLE_500, padding=20)

    col_conversation.controls.append(user_msg)
    page.update()


def add_user_msg(page: ft.Page, col_conversation: ft.Container, msg: str) -> None:
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

    col_conversation.controls.append(bot_msg)
    page.update()


# Global for performance
print("Loading model...")
model = BloomForCausalLM.from_pretrained("bigscience/bloom-7b1")
print("Loading tokenizer...")
tokenizer = BloomTokenizerFast.from_pretrained("bigscience/bloom-7b1")


def get_answer_and_prev_prompt(msg: str, prev_prompt: str) -> Tuple[str, str]:
    prompt = prev_prompt + msg + "\nBLOOM: "

    print("prompt:")
    print(prompt)

    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(
        input_ids, max_length=1000, do_sample=True, top_k=50, top_p=0.9
    )
    answer = tokenizer.decode(output[0])

    print("answer:")
    print(answer)
    print("---")

    # Get everything after the prompt
    new_info = answer[len(prompt) - 2 :]

    # Find the first occurrence of the word "USER" in new_info
    # and get everything before that
    bot_msg = new_info[: new_info.find("USER") - 1]

    # Update the prompt
    prev_prompt = prompt + bot_msg + "\nUSER: "

    return bot_msg, prev_prompt


def main(page: ft.Page):
    def on_enter(event: ft.ControlEvent) -> None:
        nonlocal prev_prompt
        add_user_msg(page, col_conversation, tf_input.value)

        answer, prev_prompt = get_answer_and_prev_prompt(tf_input.value, prev_prompt)
        add_bot_msg(page, col_conversation, answer)

        # Clear the input
        tf_input.value = ""
        page.update()

    print("For learning: https://github.com/oobabooga/text-generation-webui")

    prev_prompt = INITIAL_PROMPT

    page.scroll = True
    page.title = "Bbot"

    col_conversation = ft.Column(controls=[])

    add_bot_msg(page, col_conversation, "Hello, I'm Bbot! How can I help you?")

    tf_input = ft.TextField(
        hint_text="Type your message here",
        on_submit=on_enter,
    )
    page.add(col_conversation, tf_input)


ft.app(target=main, view=ft.WEB_BROWSER)
