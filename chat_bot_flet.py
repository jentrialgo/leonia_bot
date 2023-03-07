import time
import flet as ft

from chat_bot import ChatBot, BOT_NAME
from conversation import Conversation

INITIAL_MSG = "Hello, how can I help you?"


def main(page: ft.Page):
    def on_enter(event: ft.ControlEvent) -> None:
        human_msg = tf_input.value
        tf_input.value = ""
        tf_input.update()

        conversation.add_user_msg(human_msg)

        progress.visible = True
        progress.update()

        start = time.time()
        answer_iterator = chat_bot.get_answer(human_msg)
        answer = next(answer_iterator)
        end = time.time()
        elapsed_sec = end - start

        conversation.add_bot_msg(answer, elapsed_sec)

        for answer in answer_iterator:
            end = time.time()
            elapsed_sec = end - start
            conversation.append_bot_msg(answer, elapsed_sec)

        progress.visible = False
        progress.update()

        tf_input.update()
        tf_input.focus()

    def on_clear(event: ft.ControlEvent) -> None:
        conversation.clear()
        conversation.add_bot_msg(INITIAL_MSG)

    page.scroll = True
    page.theme = ft.Theme(color_scheme_seed="#008b84")
    page.title = f"{BOT_NAME} chat"
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

    conversation.add_bot_msg(INITIAL_MSG)

    button_clear = ft.FilledButton(
        text="Clear",
        icon=ft.icons.CLEAR,
        on_click=on_clear,
    )
    tf_input = ft.TextField(
        hint_text="Type your message here",
        on_submit=on_enter,
        expand=True,
        multiline=True,
    )
    button_submit = ft.FilledButton(
        text="Submit",
        on_click=on_enter,
    )
    row_input = ft.Row(
        [tf_input, button_submit, button_clear],
    )
    page.add(row_input)


ft.app(target=main, view=ft.WEB_BROWSER, assets_dir="./")
