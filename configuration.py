"""This file defines a configuration control that allows selecting models and
their configuration for the chat bot."""

from typing import List

from huggingface_hub import scan_cache_dir
import flet as ft

from chat_bot import HH_MODEL_REPOS, MODEL_PARAMS


def init_config(page: ft.Page) -> str:
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

    def __params_to_str(self, params: dict) -> str:
        """This function converts the model parameters to a string."""
        s = ""
        for key, value in params.items():
            s += f"{key}: {value}\n"

        return s

    def __dropdown_changed(self, event):
        """This function is called when the user selects a model from the
        dropdown."""
        model_name = self.dd_model.value
        self.text_model_info.value = self.__params_to_str(MODEL_PARAMS[model_name])
        self.text_model_info.update()
        self.page.update()

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
            print(f"key: {model_name}, text: {option}")

        return options

    def build(self):
        # model = init_config(self.page)
        model_name = "DISTILGPT2"
        print("Default model: " + model_name)
        self.dd_model = ft.Dropdown(
            on_change=self.__dropdown_changed,
            label="Model",
            options=self.__create_model_name_options(),
            autofocus=True,
            value=HH_MODEL_REPOS[model_name],
        )

        self.text_model_info = ft.Text(self.__params_to_str(MODEL_PARAMS[model_name]))

        return ft.Container(
            content=ft.Column([self.dd_model, self.text_model_info]),
            padding=ft.Padding(left=0, top=20, right=0, bottom=0),
        )
