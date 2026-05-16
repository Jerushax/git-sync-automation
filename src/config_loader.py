from dataclasses import dataclass
from typing import Any, Dict

import yaml

from src.constants import CONFIG_FILE


@dataclass
class Config:
    data: Dict[str, Any]


class ConfigLoader:
    @staticmethod
    def load() -> Config:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        return Config(data=config)