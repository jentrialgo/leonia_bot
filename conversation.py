"""This module implements a Conversation class, which is used to display the
conversation between the user and the chat bot as a flet component."""
from typing import Optional

import flet as ft


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
        self.last_text_bot = text_bot

        user_msg = ft.Container(
            content=text_bot, bgcolor=ft.colors.PURPLE_500, padding=20, border_radius=30
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
        words_per_sec_str = f"({words_per_sec:.2f} words per sec)"

        if elapsed_sec < 60:
            elapsed_sec_str = f"{elapsed_sec:.0f} sec"
        else:
            elapsed_sec_str = f"{elapsed_sec // 60:.0f} min {elapsed_sec % 60:.0f} sec"

        self.last_text_elapsed.value = f"{elapsed_sec_str} {words_per_sec_str}"
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
            bgcolor="#00c2b9",
            padding=20,
            margin=ft.Margin(top=0, left=150, right=0, bottom=0),
            border_radius=30,
        )

        self.col_conversation.controls.append(bot_msg)
        self.col_conversation.update()

    def clear(self):
        self.last_text_bot = None
        self.col_conversation.controls = []
        self.col_conversation.update()
