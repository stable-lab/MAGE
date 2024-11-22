import json
import os
import re
from enum import Enum
from typing import Dict, Tuple

from .log_utils import get_logger

logger = get_logger(__name__)


class TypeBenchmark(Enum):
    VERILOG_EVAL_V1 = 1
    VERILOG_EVAL_V2 = 2


class TypeBenchmarkFile(Enum):
    SPEC = 0
    TEST_PATH = 1
    GOLDEN_PATH = 2


def load_json(filename):
    des_data = []
    with open(filename, "r") as f:
        for line in f:
            data = json.loads(line)
            des_data.append(data)
    return des_data


def get_benchmark_contents(
    benchmark_type: TypeBenchmark,
    file_type: TypeBenchmarkFile,
    benchmark_repo: str,
    filter_instance: str,
) -> Dict[str, str]:
    """
    Get Dict of {problem_name: problem_content/testbench_content} for given benchmark
    """
    if (
        benchmark_type == TypeBenchmark.VERILOG_EVAL_V1
        or benchmark_type == TypeBenchmark.VERILOG_EVAL_V2
    ):
        folder = os.path.join(
            benchmark_repo,
            (
                "dataset_code-complete-iccad2023"
                if benchmark_type == TypeBenchmark.VERILOG_EVAL_V1
                else "dataset_spec-to-rtl"
            ),
        )
        files = os.listdir(folder)
        files.sort()
        re_str = r"$^"  # dummy
        if file_type == TypeBenchmarkFile.SPEC:
            re_str = r"(.*)_prompt.txt"
        elif file_type == TypeBenchmarkFile.TEST_PATH:
            re_str = r"(.*)_test.sv"
        elif file_type == TypeBenchmarkFile.GOLDEN_PATH:
            re_str = r"(.*)_ref.sv"
        else:
            raise ValueError(f"Invalid file_type: {file_type}")

        def is_target(file_name: str) -> Tuple[str, str] | None:
            full_path = os.path.join(folder, file_name)
            if not os.path.isfile(full_path):
                return None
            m = re.match(re_str, file_name)
            if not m:
                return None
            if not re.match(filter_instance, m[1]):
                return None
            return (m[1], full_path)

        ret = {}

        for file in files:

            p = is_target(file)
            if not p:
                continue

            if file_type == TypeBenchmarkFile.SPEC:
                with open(p[1], "r") as f:
                    ret[p[0]] = f.read()
            elif (
                file_type == TypeBenchmarkFile.TEST_PATH
                or file_type == TypeBenchmarkFile.GOLDEN_PATH
            ):
                ret[p[0]] = p[1]

        return ret
    raise ValueError(f"Invalid benchmark_type: {benchmark_type}")
