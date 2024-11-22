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
git clone https://github.com/NVlabs/verilog-eval
```
