"""This is a flet application that uses the chat_bot module to implement a chat
bot."""

from contextlib import redirect_stdout
import time
import flet as ft

from chat_bot import ChatBot, BOT_NAME
from conversation import Conversation

INITIAL_MSG = "Hello, how can I help you?"


class TextWithWrite(ft.Text):
    """This class is used to redirect the output of the chat bot to the log
    text control."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = ""

    def write(self, s: str) -> None:
        """This function is called when the chat bot prints something. It
        appends the text to the log text control."""
        self.value += s
        self.update()


def main(page: ft.Page):
    """This function is called when the application starts. It creates the
    flet page and adds the controls to it."""

    def on_submit(event: ft.ControlEvent) -> None:
        """This function is called when the user clicks the Submit button. It
        sends the message to the chat bot and displays the answer in the
        conversation."""
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
            try:
                conversation.append_bot_msg(answer, elapsed_sec)
            except:
                # This can happen if the user clicks "Clear" while the AI is
                # thinking
                return

        progress.visible = False
        progress.update()

        tf_input.update()
        tf_input.focus()

    def on_clear(event: ft.ControlEvent) -> None:
        """This function is called when the user clicks the Clear button. It
        clears the conversation."""
        conversation.clear()
        conversation.add_bot_msg(INITIAL_MSG)
        progress.visible = False
        progress.update()

    page.scroll = True
    page.theme = ft.Theme(color_scheme_seed="#008b84")
    page.title = f"{BOT_NAME} chat"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.auto_scroll = True

    # Create a column container for the configuration
    col_config = ft.Column(
        width=500,
    )

    # Create a column container for the conversation
    col_conversation = ft.Column(
        width=500,
        expand=True,
    )

    page.add(ft.Row([col_config, col_conversation]))

    img = ft.Image(
        src="/lion.png",
        width=200,
        height=200,
        fit=ft.ImageFit.CONTAIN,
    )
    page.add(img)

    conversation = Conversation(page)

    progress_text = ft.Text("I'm turning on. Please wait...")
    progress = ft.Column(
        [ft.ProgressRing(), progress_text],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    page.add(progress)

    # Create a text control for the log
    text_log = TextWithWrite()
    page.add(text_log)

    # Other alternative models (require changes in the tokenizer and the
    # Transformer classes in the chat_bot module):
    # - EleutherAI/pythia-70m
    # - bigscience/bloom-7b1
    # - theblackcat102/pythia-3b-deduped-sft-r1
    # - Dahoas/pythia-6B-sft-response-full-static
    # - OpenAssistant/oasst-sft-1-pythia-12b
    # - oasst-sft-4-pythia-12b-epoch-3.5
    # - distilgpt2
    with redirect_stdout(text_log):
        chat_bot = ChatBot("DISTILGPT2")
        chat_bot.initialize()

    text_log.value = ""
    text_log.visible = False
    text_log.update()

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
        on_submit=on_submit,
        expand=True,
        multiline=True,
    )
    button_submit = ft.FilledButton(
        text="Submit",
        on_click=on_submit,
    )

    row_input = ft.Row(
        [tf_input, button_submit, button_clear],
    )
    page.add(row_input)


ft.app(target=main, view=ft.WEB_BROWSER, assets_dir="./")
