import argparse

from mage_rtl.benchmark_read_helper import (
    TypeBenchmark,
    TypeBenchmarkFile,
    get_benchmark_contents,
)
from mage_rtl.gen_config import Config, get_llm
from mage_rtl.log_utils import get_logger
from mage_rtl.rtl_generator import RTLGenerator

logger = get_logger(__name__)

args_dict = {
    # "model": "claude-3-5-sonnet-20241022",
    "model": "gpt-4o",
    "filter_instance": "^(Prob070_ece241_2013_q2|Prob151_review2015_fsm)$",
}


def main():
    args = argparse.Namespace(**args_dict)
    cfg = Config("./key.cfg")
    llm = get_llm(model=args.model, api_key=cfg["OPENAI_API_KEY"], max_tokens=4096)
    rtl_gen = RTLGenerator(llm)
    spec_dict = get_benchmark_contents(
        TypeBenchmark.VERILOG_EVAL_V2,
        TypeBenchmarkFile.SPEC,
        "../verilog-eval",
        args.filter_instance,
    )
    for key, spec in spec_dict.items():
        rtl_gen.reset()
        logger.info(spec)
        is_pass, code = rtl_gen.chat(spec, key)
        logger.info(is_pass)
        logger.info(code)


if __name__ == "__main__":
    main()
