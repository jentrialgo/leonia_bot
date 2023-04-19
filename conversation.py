"""This module implements a Conversation class, which is used to display the
conversation between the user and the chat bot as a flet component."""
from typing import Optional
from time import sleep

import flet as ft


class Conversation:
    """This class implements a Conversation component, which is used to display
    the conversation between the user and the chat bot as a flet component."""

    def __init__(self):
        """This function initializes the Conversation component. It creates the
        main column where the conversation messages are held."""
        self.col_conversation = ft.Column(controls=[])
        self.last_text_bot = None
        self.last_text_elapsed = None

    def _add_text_bubble(self, msg: str, bgcolor, margin) -> ft.Text:
        text = ft.Markdown(
            value=msg,
            # color=ft.colors.WHITE,
            extension_set="gitHubWeb",
            code_theme="atom-one-dark",
            code_style=ft.TextStyle(font_family="Roboto Mono"),
            selectable=True,
            width=500,
        )

        bubble = ft.Container(
            content=text,
            bgcolor=bgcolor,
            padding=20,
            border_radius=30,
            animate_opacity=300,
            animate_scale=200,
            scale=0,
            opacity=0,
            margin=margin,
        )

        self.col_conversation.controls.append(bubble)
        self.col_conversation.update()
        bubble.update()
        sleep(0.1)
        bubble.scale = 1
        bubble.opacity = 1
        bubble.update()

        return text

    def add_bot_msg(self, msg: str, elapsed_sec: Optional[float] = None) -> None:
        """This function adds a message from the chat bot to the conversation."""
        self.last_text_bot = self._add_text_bubble(msg, ft.colors.PURPLE_300, margin=0)

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
        """This function appends a message from the chat bot to the last message
        from the chat bot."""
        if self.last_text_bot is None:
            raise ValueError(
                "No previous bot message. You should call add_bot_msg first."
            )

        self.last_text_bot.value += f"{msg}"

        if self.last_text_elapsed is not None and elapsed_sec is not None:
            self.update_text_elapsed(elapsed_sec)

        self.last_text_bot.update()

    def update_text_elapsed(self, elapsed_sec):
        """This function updates the elapsed time and words per second of the
        last message from the chat bot."""
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
        """This function adds a message from the user to the conversation."""
        self._add_text_bubble(
            msg, "#00c2b9", margin=ft.Margin(top=0, left=150, right=0, bottom=0)
        )

    def clear(self):
        """This function clears the conversation."""
        self.last_text_bot = None
        self.col_conversation.controls = []
        self.col_conversation.update()
