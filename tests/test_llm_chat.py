import argparse

from mage.gen_config import get_llm
from mage.log_utils import get_logger

logger = get_logger(__name__)

args_dict = {
    "provider": "vertexanthropic",
    "model": "claude-3-7-sonnet@20250219",
    "n": 1,
    "temperature": 0.85,
    "top_p": 0.95,
    "max_token": 8192,
    "key_cfg_path": "./key.cfg",
}


def main():
    args = argparse.Namespace(**args_dict)
    get_llm(
        model=args.model,
        cfg_path=args.key_cfg_path,
        max_token=args.max_token,
        provider=args.provider,
    )


if __name__ == "__main__":
    main()
