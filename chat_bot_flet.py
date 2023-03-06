import time
from typing import Optional
import flet as ft

from chat_bot import ChatBot


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
    # - theblackcat102/pythia-3b-deduped-sft
    chat_bot = ChatBot("theblackcat102/pythia-3b-deduped-sft")

    progress_text = ft.Text("I'm turning on. Please wait...")
    progress = ft.Column(
        [ft.ProgressRing(), progress_text],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    page.add(progress)

    chat_bot.initialize()

    progress.visible = False
    progress.controls[1].value = "Thinking..."

    conversation.add_bot_msg(f"Hello, How can I help you?")

    tf_input = ft.TextField(
        hint_text="Type your message here",
        on_submit=on_enter,
    )
    page.add(tf_input)


ft.app(target=main, view=ft.WEB_BROWSER, assets_dir="./")
