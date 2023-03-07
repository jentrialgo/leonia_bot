import time
from typing import Optional
import flet as ft

from chat_bot import ChatBot


class Conversation:
    def __init__(self, page):
        self.page = page
        self.col_conversation = ft.Column(controls=[])
        self.last_text_bot = None
        self.last_text_elapsed = None

        self.page.add(self.col_conversation)

    def add_bot_msg(self, msg: str, elapsed_sec: Optional[float] = None) -> None:
        text_bot = ft.Text(
            value=msg,
            color=ft.colors.WHITE,
            selectable=True,
            width=500,
        )
        user_msg = ft.Container(
            content=text_bot, bgcolor=ft.colors.PURPLE_500, padding=20
        )

        self.col_conversation.controls.append(user_msg)

        text_elapsed = None
        if elapsed_sec is not None:
            text_elapsed = ft.Text(
                style=ft.TextThemeStyle.BODY_SMALL,
                color=ft.colors.BLACK38,
            )
            self.col_conversation.controls.append(text_elapsed)
            self.col_conversation.update()
            self.last_text_elapsed = text_elapsed
            self.update_text_elapsed(elapsed_sec)

        self.col_conversation.update()

        self.last_text_bot = text_bot

    def append_bot_msg(self, msg: str, elapsed_sec: Optional[float] = None) -> None:
        if self.last_text_bot is None:
            raise ValueError(
                "No previous bot message. You should call add_bot_msg first."
            )

        self.last_text_bot.value += f"{msg}"

        if self.last_text_elapsed is not None and elapsed_sec is not None:
            self.update_text_elapsed(elapsed_sec)

        self.last_text_bot.update()

    def update_text_elapsed(self, elapsed_sec):
        words = self.last_text_bot.value.split()
        words_per_sec = len(words) / elapsed_sec
        if elapsed_sec < 60:
            self.last_text_elapsed.value = (
                f"{elapsed_sec:.0f} sec ({words_per_sec:.2f} wps)"
            )
        else:
            self.last_text_elapsed.value = f"{elapsed_sec // 60:.0f} min {elapsed_sec % 60:.0f} sec ({words_per_sec:.2f} wps)"
        self.last_text_elapsed.update()

    def add_user_msg(self, msg: str) -> None:
        text = ft.Text(
            value=msg,
            color=ft.colors.WHITE,
            selectable=True,
            width=400,
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

        tf_input.disabled = True
        tf_input.value = ""
        tf_input.update()

        progress.visible = True
        progress.update()

        start = time.time()
        answer_iterator = chat_bot.get_answer(tf_input.value)
        end = time.time()
        elapsed_sec = end - start
        conversation.add_bot_msg(next(answer_iterator), elapsed_sec)
        for answer in answer_iterator:
            end = time.time()
            elapsed_sec = end - start
            conversation.append_bot_msg(answer, elapsed_sec)

        progress.visible = False
        progress.update()

        tf_input.disabled = False
        tf_input.update()

    page.scroll = True
    page.title = "Bbot"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.auto_scroll = True

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
    chat_bot = ChatBot("theblackcat102/pythia-3b-deduped-sft-r1")

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
        expand=True,
    )
    button_submit = ft.FilledButton(
        text="Submit",
        on_click=on_enter,
    )
    row_input = ft.Row(
        [tf_input, button_submit],
    )
    page.add(row_input)


ft.app(target=main, view=ft.WEB_BROWSER, assets_dir="./")
