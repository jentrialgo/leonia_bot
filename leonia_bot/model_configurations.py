"""This module defines a class to work with model configurations."""

import yaml


class ModelConfigurations:

    """This class contains the possible configurations for the chat bot."""

    def __init__(self, conf_file_name: str) -> None:
        self.confs = self.__read_conf_file(conf_file_name)

    def __read_conf_file(self, conf_file_name: str) -> dict:
        with open(conf_file_name, "r") as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    def params_to_str(self, model_name: str) -> str:
        """This function converts the model parameters to a string."""
        res = ""
        for key, value in self.confs[model_name].items():
            res += f"{key}: {value}\n"

        return res

    def is_valid_name(self, conf_name: str) -> bool:
        """This function checks if the given configuration name is valid."""
        return conf_name in self.confs

    def params(self, conf_name: str) -> dict:
        """This function returns the parameters for the given configuration."""
        return self.confs[conf_name]

    def confs(self) -> dict:
        """This function returns the configurations."""
        return self.confs

    def repo(self, model_name: str) -> str:
        """This function returns the repository for the given configuration."""
        return self.confs[model_name]["repo"]
