import argparse

from mage_rtl.gen_config import Config, get_llm
from mage_rtl.log_utils import get_logger

logger = get_logger(__name__)

args_dict = {
    "model": "claude-3-5-sonnet-20241022",
}


def main():
    args = argparse.Namespace(**args_dict)
    cfg = Config("./key.cfg")
    get_llm(model=args.model, api_key=cfg["ANTHROPIC_API_KEY"], max_tokens=8192)
    get_llm(model="gpt-4o", api_key=cfg["OPENAI_API_KEY"], max_tokens=8192)


if __name__ == "__main__":
    main()
