from typing import Optional
import os
from pathlib import Path
import pydantic
from ruamel.yaml import YAML, YAMLError
from ruamel.yaml.scalarstring import FoldedScalarString
from agentstack import ValidationError


INPUTS_FILENAME: Path = Path("src/config/inputs.yaml")

yaml = YAML()
yaml.preserve_quotes = True  # Preserve quotes in existing data


class InputsConfig:
    """
    Interface for interacting with inputs configuration.

    Use it as a context manager to make and save edits:
    ```python
    with InputsConfig() as inputs:
        inputs.topic = "Open Source Aritifical Intelligence"
    ```
    """

    _attributes: dict[str, str]

    def __init__(self, path: Optional[Path] = None):
        self.path = path if path else Path()
        filename = self.path / INPUTS_FILENAME
        
        if not os.path.exists(filename):
            os.makedirs(filename.parent, exist_ok=True)
            filename.touch()

        try:
            with open(filename, 'r') as f:
                self._attributes = yaml.load(f) or {}
        except YAMLError as e:
            # TODO format MarkedYAMLError lines/messages
            raise ValidationError(f"Error parsing inputs file: {filename}\n{e}")

    def __getitem__(self, key: str) -> str:
        return self._attributes[key]

    def __setitem__(self, key: str, value: str):
        self._attributes[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._attributes

    def to_dict(self) -> dict[str, str]:
        return self._attributes

    def model_dump(self) -> dict:
        dump = {}
        for key, value in self._attributes.items():
            dump[key] = FoldedScalarString(value)
        return dump

    def write(self):
        with open(self.path / INPUTS_FILENAME, 'w') as f:
            yaml.dump(self.model_dump(), f)

    def __enter__(self) -> 'InputsConfig':
        return self

    def __exit__(self, *args):
        self.write()


def get_inputs(path: Optional[Path] = None) -> dict:
    path = path if path else Path()
    config = InputsConfig(path)
    return config.to_dict()