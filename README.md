# MAGE: A Multi-Agent Engine for Automated RTL Code Generation

MAGE is an open-source multi-agent LLM RTL code generator.

## Installation guide

### To install the repo itself:
```
pip install -Ue .
```

### To set api key：
You can either:
1. Set "OPENAI_API_KEY", "ANTHROPIC_API_KEY" or other keys in your env variables
2. Set key.cfg file. Each line should be like:

```
OPENAI_API_KEY: 'xxxxxxx'
```

### To install iverilog {.tabset}
You'll need to install [ICARUS verilog](https://github.com/steveicarus/iverilog) 12.0
For latest installation guide, please refer to [iverilog official guide](https://steveicarus.github.io/iverilog/usage/installation.html)

#### Ubuntu
```
apt install -y autoconf gperf make gcc g++ bison flex
```
and
```
$ git clone https://github.com/steveicarus/iverilog.git && cd iverilog \
        && git checkout v12-branch \
        && sh ./autoconf.sh && ./configure && make -j4\
        && make install
```
#### MacOS
```
brew install icarus-verilog
```

### To get benchmarks
```
[verilog-eval](https://github.com/NVlabs/verilog-eval)
```

```
git clone https://github.com/NVlabs/verilog-eval
```

## File structure
```
.
├── README.md
├── action.yml
├── requirements.txt
├── setup.py
├── src
│   └── mage_rtl
│       ├── agent.py
│       ├── bash_tools.py
│       ├── benchmark_read_helper.py
│       ├── gen_config.py
│       ├── log_utils.py
│       ├── prompts.py
│       ├── rtl_editor.py
│       ├── rtl_generator.py
│       ├── sim_judge.py
│       ├── sim_reviewer.py
│       ├── tb_generator.py
│       ├── token_counter.py
│       └── utils.py
├── testbench_generate.ipynb
└── tests
    ├── test_llm_chat.py
    ├── test_rtl_generator.py
    ├── test_single_agent.py
    └── test_top_agent.py
```

## Run Guide
```
python tests/test_top_agent.py
```

Run arguments can be set in the file like:

```
args_dict = {
    "model": "claude-3-5-sonnet-20241022",
    "filter_instance": "^(Prob011_norgate)$",
    "type_benchmark": "verilog_eval_v2",
    "path_benchmark": "../verilog-eval",
    "run_identifier": "claude3.5sonnet_20241113_v2",
    "n": 1,
    "temperature": 0.85,
    "top_p": 0.95,
}
```
Where each argument means:
1. model: The LLM model used. Support for gpt-4o and claude has been verified.
2. filter_instance: A RegEx style instance name filter.
3. type_benchmark: Support running verilog_eval_v1 or verilog_eval_v2
4. path_benchmark: Where the benchmark repo is cloned
5. run_identifier: Unique name to disguish different runs
6. n: Number of repeated run to execute
7. temperature: Argument for LLM generation randomness. Usually between [0, 1]
8. top_p: Argument for LLM generation randomness. Usually between [0, 1]
