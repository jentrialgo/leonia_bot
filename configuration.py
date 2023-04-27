"""This file defines a configuration control that allows selecting models and
their configuration for the chat bot."""

from typing import List

from huggingface_hub import scan_cache_dir
import flet as ft

from chat_bot import HH_MODEL_REPOS, MODEL_PARAMS, ChatBot


def get_init_config(page: ft.Page) -> str:
    """This function initializes the configuration of the chat bot using flet's
    client storage. It returns the model name."""
    if not page.client_storage.contains_key("model"):
        page.client_storage.set("model", "DISTILGPT2")

    return page.client_storage.get("model")


class ConfigurationControl(ft.UserControl):
    """This class implements a configuration control, which is used to
    configure the chat bot."""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.dd_model = None
        self.text_model_info = None
        self.button_apply = None
        self.change_bot_hook = None

    @staticmethod
    def __params_to_str(params: dict) -> str:
        """This function converts the model parameters to a string."""
        s = ""
        for key, value in params.items():
            s += f"{key}: {value}\n"

        return s

    def __dropdown_changed(self, event):
        """This function is called when the user selects a model from the
        dropdown."""
        model_name = self.dd_model.value
        self.text_model_info.value = ConfigurationControl.__params_to_str(
            MODEL_PARAMS[model_name]
        )
        self.text_model_info.update()

    def __on_apply(self, event):
        """This function is called when the user clicks the Apply button. It
        saves the configuration to the client storage."""
        model_name = self.dd_model.value
        self.page.client_storage.set("model", model_name)

        self.conf_change_hook(model_name)

    def __create_model_name_options(self) -> List[ft.dropdown.Option]:
        """This function creates the options for the model dropdown."""
        repos = scan_cache_dir().repos
        repo_names = [repo.repo_id for repo in repos]
        options = []
        for model_name in HH_MODEL_REPOS.keys():
            if HH_MODEL_REPOS[model_name] in repo_names:
                option = HH_MODEL_REPOS[model_name]
            else:
                option = f"{HH_MODEL_REPOS[model_name]} (not downloaded)"
            options.append(ft.dropdown.Option(text=option, key=model_name))

        return options

    def build(self):
        self.dd_model = ft.Dropdown(
            on_change=self.__dropdown_changed,
            label="Model",
            options=self.__create_model_name_options(),
            autofocus=True,
        )

        self.text_model_info = ft.Text("")

        self.button_apply = ft.FilledButton(text="Apply", on_click=self.__on_apply)

        return ft.Container(
            content=ft.Column([self.dd_model, self.text_model_info, self.button_apply]),
            padding=ft.Padding(left=0, top=20, right=0, bottom=0),
        )

    def did_mount(self):
        # This has to be done here because, before, the page is not created
        model_name = get_init_config(self.page)
        self.dd_model.value = model_name
        self.text_model_info.value = ConfigurationControl.__params_to_str(
            MODEL_PARAMS[model_name]
        )
        self.update()

    def set_conf_change_hook(self, hook):
        """This function sets the hook that is called when the user clicks the
        Apply button."""
        self.conf_change_hook = hook
