import os

import config
from llama_index.core.llms.llm import LLM
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.openai import OpenAI
from pydantic import BaseModel

from .log_utils import get_logger

logger = get_logger(__name__)


class Config:
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.file_config = {}
        if self.file_path and os.path.isfile(self.file_path):
            self.file_config = config.Config(self.file_path)
        self.fallback_config = {}
        self.fallback_config["OPENAI_API_BASE_URL"] = ""

    def __getitem__(self, index):
        # Values in key.cfg has priority over env variables
        if index in self.file_config:
            return self.file_config[index]
        if index in os.environ:
            return os.environ[index]
        if index in self.fallback_config:
            return self.fallback_config[index]
        raise KeyError(
            f"Cannot find {index} in either cfg file '{self.file_path}' or env variables"
        )


def get_llm(**kwargs) -> LLM:
    err_msgs = []
    args_d = kwargs["args_d"]
    cfg = Config(args_d["key_cfg_path"])
    
    LLM_func = Anthropic
    if args_d["provider"] == "anthropic":
        LLM_func = Anthropic
        api_key_cfg = cfg["ANTHROPIC_API_KEY"]
    elif args_d["provider"] == "openai":
        LLM_func = OpenAI
        api_key_cfg = cfg["OPENAI_API_KEY"]
    # add more providers if needed
    
    #for LLM_func in [OpenAI, Anthropic]:
    try:
        llm: LLM = LLM_func(model=args_d["model"], api_key=api_key_cfg, max_tokens=8192)
        _ = llm.complete("Say 'Hi'")
        #break
    except Exception as e:
        err_msgs.append(str(e))
    """ else:
        raise Exception(
            f"gen_config: Failed to get LLM. Error msgs include:\n"
            + "\n".join(err_msgs)
        ) """
    return llm


class ExperimentSetting(BaseModel):
    """
    Global setting for experiment
    """

    temperature: float = 0.85  # Chat temperature
    top_p: float = 0.95  # Chat top_p


global_exp_setting = ExperimentSetting()


def get_exp_setting() -> ExperimentSetting:
    return global_exp_setting


def set_exp_setting(temperature: float | None = None, top_p: float | None = None):
    if temperature is not None:
        global_exp_setting.temperature = temperature
    if top_p is not None:
        global_exp_setting.top_p = top_p
    return global_exp_setting
