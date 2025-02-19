from datetime import datetime

import yaml


class Config:
    config: dict = {}
    user_upstage_api_key: str = ""

    @classmethod
    def load(
        cls,
        config_path="config.yml",
        action_config_path="prompt/template/classification/action.yaml",
        category_config_path="prompt/template/classification/category.yaml",
    ):
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        config["gmail"]["start_date"] = (
            "2025/01/10" if not config["gmail"]["start_date"] else config["gmail"]["start_date"]
        )
        config["gmail"]["end_date"] = (
            datetime.now().strftime("%Y/%m/%d") if not config["gmail"]["end_date"] else config["gmail"]["end_date"]
        )
        cls.config = config
        with open(action_config_path, "r", encoding="utf-8") as file:
            cls.action_config = yaml.safe_load(file)
        with open(category_config_path, "r", encoding="utf-8") as file:
            cls.category_config = yaml.safe_load(file)
