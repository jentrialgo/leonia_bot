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


def init_config(page: ft.Page) -> str:
    """This function initializes the configuration of the chat bot using flet's
    client storage. It returns the model name."""
    if not page.client_storage.contains_key("model"):
        page.client_storage.set("model", "DISTILGPT2")

    return page.client_storage.get("model")


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

    img = ft.Image(
        src="/lion.png",
        width=200,
        height=200,
        fit=ft.ImageFit.CONTAIN,
    )

    col_content = ft.Column(controls=[img], auto_scroll=True)
    col_config = ft.Column(controls=[])

    page.add(
        ft.Tabs(
            expand=1,
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Chat",
                    content=ft.Container(
                        content=col_content,
                        padding=ft.Padding(left=0, top=10, right=0, bottom=0),
                    ),
                ),
                ft.Tab(text="Configuration", content=col_config),
            ],
        ),
    )

    conversation = Conversation()
    col_content.controls.append(conversation.col_conversation)

    progress_text = ft.Text("I'm turning on. Please wait...")
    progress = ft.Column(
        [ft.ProgressRing(), progress_text],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    col_content.controls.append(progress)

    # Create a text control for the log
    text_log = TextWithWrite()
    col_content.controls.append(text_log)
    page.update()

    # Other alternative models (require changes in the tokenizer and the
    # Transformer classes in the chat_bot module):
    # - EleutherAI/pythia-70m
    # - bigscience/bloom-7b1
    # - theblackcat102/pythia-3b-deduped-sft-r1
    # - Dahoas/pythia-6B-sft-response-full-static
    # - OpenAssistant/oasst-sft-1-pythia-12b
    # - oasst-sft-4-pythia-12b-epoch-3.5
    # - distilgpt2
    model_name = init_config(page)
    with redirect_stdout(text_log):
        chat_bot = ChatBot(model_name)
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
    col_content.controls.append(row_input)
    page.update()


ft.app(target=main, view=ft.WEB_BROWSER, assets_dir="./")
