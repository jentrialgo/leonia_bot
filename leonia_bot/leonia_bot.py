"""This is a flet application that uses the chat_bot module to implement a chat
bot."""

from contextlib import redirect_stderr, redirect_stdout
import time
import flet as ft

from chat_bot import ChatBot, BOT_NAME
from conversation import Conversation
from configuration import ConfigurationControl, get_init_config

INITIAL_MSG = "Hello, how can I help you?"


class TextWithWrite(ft.Text):
    """This class is used to redirect the output of the chat bot to the log
    text control."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = ""
        self.lines = []

    def write(self, msg: str) -> None:
        """This function is called when the chat bot prints something. It
        appends the text to the log text control."""

        # If the new line contains "Downloading" and there are previous lines
        # with "Downloading", leave only the new one. This happens when
        # huggingface downloads the model to show the download progress.
        if "Downloading" in msg:
            lines = [l for l in self.lines if "Downloading" not in l]
            lines.append(msg)
            self.lines = lines
        else:
            if msg not in ("\r", msg != "\n"):
                self.lines.append(msg)

        self.value = ("").join(self.lines)
        self.update()

    def reset(self) -> None:
        """Reset the log text control."""
        self.value = ""
        self.lines = []
        self.update()


class ChatBotApp:
    """This class implements the chat bot application."""

    def __init__(self, page: ft.Page):
        self.page = page

        page.theme = ft.Theme(color_scheme_seed="#008b84")
        page.title = f"{BOT_NAME} chat"
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.CrossAxisAlignment.CENTER

        img = ft.Image(
            src="/leonia.png",
            width=200,
            height=200,
            fit=ft.ImageFit.CONTAIN,
        )

        configuration_control = ConfigurationControl(page)
        col_content = ft.Column(controls=[img], auto_scroll=True, scroll=True)
        col_config = ft.Column(controls=[configuration_control])

        self.tabs = ft.Tabs(
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
        )

        page.add(self.tabs)

        self.chat_bot = None
        self.conversation = Conversation()
        col_content.controls.append(self.conversation.col_conversation)

        self.progress_text = ft.Text("I'm turning on. Please wait...")
        self.progress = ft.Column(
            [ft.ProgressRing(), self.progress_text],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        col_content.controls.append(self.progress)

        # Create a text control for the log
        self.text_log = TextWithWrite()
        col_content.controls.append(self.text_log)
        page.update()

        self.model_name = get_init_config(page)
        self.init_model()

        configuration_control.set_conf_change_hook(self.change_conf)

        self.progress.visible = False
        self.progress.controls[1].value = "Thinking..."

        if self.model_name == "DISTILGPT2":
            self.conversation.add_bot_msg(
                "This model, distilgpt2, is only for testing and produces"
                " gibberish. Select another model in the Configuration tab,"
                " paying attention at the requirements."
            )
        self.conversation.add_bot_msg(INITIAL_MSG)

        button_clear = ft.FilledButton(
            text="Clear",
            icon=ft.icons.CLEAR,
            on_click=self.on_clear,
        )
        self.tf_input = ft.TextField(
            hint_text="Type your message here",
            on_submit=self.on_submit,
            expand=True,
            multiline=True,
        )
        button_submit = ft.FilledButton(
            text="Submit",
            on_click=self.on_submit,
        )

        row_input = ft.Row(
            [self.tf_input, button_submit, button_clear],
        )
        col_content.controls.append(row_input)
        page.update()

    def init_model(self):
        """Initialize the chat bot with the model stored in the model field."""
        with redirect_stdout(self.text_log), redirect_stderr(self.text_log):
            self.chat_bot = ChatBot(self.model_name)
            self.chat_bot.initialize()

        self.text_log.reset()
        self.text_log.visible = False
        self.text_log.update()

    def on_submit(self, event: ft.ControlEvent) -> None:
        """This function is called when the user clicks the Submit button. It
        sends the message to the chat bot and displays the answer in the
        conversation."""
        human_msg = self.tf_input.value

        # If the user clicks the Submit button without entering a message,
        # do nothing.
        if human_msg == "":
            return

        self.tf_input.value = ""
        self.tf_input.update()

        self.conversation.add_user_msg(human_msg)

        self.progress.visible = True
        self.progress.update()

        start = time.time()
        answer_iterator = self.chat_bot.get_answer(human_msg)
        answer = next(answer_iterator)
        end = time.time()
        elapsed_sec = end - start

        self.conversation.add_bot_msg(answer, elapsed_sec)

        for answer in answer_iterator:
            end = time.time()
            elapsed_sec = end - start
            try:
                self.conversation.append_bot_msg(answer, elapsed_sec)
            except:
                # This can happen if the user clicks "Clear" while the AI is
                # thinking
                return

        self.progress.visible = False
        self.progress.update()

        self.tf_input.update()
        self.tf_input.focus()

    def on_clear(self, event: ft.ControlEvent) -> None:
        """This function is called when the user clicks the Clear button. It
        clears the conversation."""
        self.conversation.clear()
        self.conversation.add_bot_msg(INITIAL_MSG)
        self.progress.visible = False
        self.progress.update()

    def change_conf(self, new_model_name: str) -> None:
        """This function is called when the user changes the chat bot. It
        clears the conversation and displays the initial message."""
        self.tabs.selected_index = 0
        self.tabs.update()

        self.progress.visible = True
        self.progress.update()

        if new_model_name == self.model_name:
            return

        self.model_name = new_model_name

        self.chat_bot = ChatBot(self.model_name)
        self.text_log.reset()
        self.text_log.visible = True

        self.init_model()

        self.conversation.clear()
        self.conversation.add_bot_msg(INITIAL_MSG)

        self.progress.visible = False
        self.progress.update()


def main(page: ft.Page):
    """This function is called when the application starts. It creates the
    flet page and adds the controls to it."""
    ChatBotApp(page)


ft.app(target=main, port=8733, view=ft.WEB_BROWSER, assets_dir="./")
