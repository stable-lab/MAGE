import json
from typing import Dict, List, Tuple

from llama_index.core.base.llms.types import ChatMessage, ChatResponse, MessageRole
from pydantic import BaseModel

from .log_utils import get_logger
from .prompts import FAILED_TRIAL_PROMPT, ORDER_PROMPT, RTL_4_SHOT_EXAMPLES
from .sim_reviewer import check_syntax
from .token_counter import TokenCounter, TokenCounterCached
from .utils import add_lineno

logger = get_logger(__name__)

SYSTEM_PROMPT = r"""
You are an expert in RTL design. You can always write SystemVerilog code with no syntax errors and always reach correct functionality.
"""

GENERATION_PROMPT = r"""
Please write a module in SystemVerilog RTL language regarding to the given natural language specification.
Try to understand the requirements above and give reasoning steps in natural language to achieve it.
In addition, try to give advice to avoid syntax error.
An SystemVerilog RTL module always starts with a line starting with the keyword 'module' followed by the module name.
It ends with the keyword 'endmodule'.

[Hints]:
For implementing kmap (Karnaugh map), you need to think step by step.
Carefully example how the kmap in input_spec specifies the order of the inputs.
Note that x[i] in x[N:1] means x[i-1] in x[N-1:0].
Then find the inputs corresponding to output=1, 0, and don't-care for each case.

Note in Verilog, for a signal "logic x[M:N]" where M > N, you CANNOT reversely select bits from it like x[1:2];
Instead, you should use concatations like {{x[1], x[2]}}.

The module interface should EXACTLY MATCH module_interface if given.
Otherwise, should EXACTLY MATCH with the description in input_spec.
(Including the module name, input/output ports names, and their types)


{examples_prompt}
<input_spec>
{input_spec}
</input_spec>
"""

EXTRA_ORDER_PROMPT = r"""
Other requirements:
1. Don't use state_t to define the parameter. Use `localparam` or Use 'reg' or 'logic' for signals as registers or Flip-Flops.
2. Declare all ports and signals as logic.
3. Not all the sequential logic need to be reset to 0 when reset is asserted,
    but these without-reset logic should be initialized to a known value with an initial block instead of being X.
4. For combinational logic with an always block do not explicitly specify the sensitivity list; instead use always @(*).
5. NEVER USE 'inside' operator in RTL code. Code like 'state inside {STATE_B, STATE_C, STATE_D}' should NOT be used.
6. Never USE 'unique' or 'unique0' keywords in RTL code. Code like 'unique case' should NOT be used.
"""
# Some prompts above comes from:
# @misc{ho2024verilogcoderautonomousverilogcoding,
#       title={VerilogCoder: Autonomous Verilog Coding Agents with Graph-based Planning and Abstract Syntax Tree (AST)-based Waveform Tracing Tool},
#       author={Chia-Tung Ho and Haoxing Ren and Brucek Khailany},
#       year={2024},
#       eprint={2408.08927},
#       archivePrefix={arXiv},
#       primaryClass={cs.AI},
#       url={https://arxiv.org/abs/2408.08927},
# }

IF_PROMPT = r"""
The module interface is given below:
<module_interface>
{module_interface}
</module_interface>
"""

TB_PROMPT = r"""
Another agent has generated a testbench regarding the given input_spec:
<testbench>
{testbench}
</testbench>
"""

FORMAT_ERROR_PROMPT = r"""
The error below has been reported by the format tool:
<format_error>
{format_error}
</format_error>
To understand the error message better, we offered a version of generated module with line number:
<module_with_lineno>
{module_with_lineno}
</module_with_lineno>
"""

EXAMPLE_OUTPUT = {
    "reasoning": "All reasoning steps and advices to avoid syntax error",
    "module": "Pure SystemVerilog code, a complete module",
}


class RTLOutputFormat(BaseModel):
    reasoning: str
    module: str


class RTLGenerator:
    def __init__(
        self,
        token_counter: TokenCounter,
    ):
        self.token_counter = token_counter
        self.generated_tb: str | None = None
        self.generated_if: str | None = None
        self.failed_trial: List[ChatMessage] = []
        self.history: List[ChatMessage] = []
        self.max_trials = 5
        self.enable_cache = False

    def reset(self):
        self.history = []

    def set_failed_trial(
        self, failed_sim_log: str, previous_code: str, previous_tb: str
    ) -> None:
        cur_failed_trial = FAILED_TRIAL_PROMPT.format(
            failed_sim_log=failed_sim_log,
            previous_code=add_lineno(previous_code),
            previous_tb=add_lineno(previous_tb),
        )
        self.failed_trial.append(
            ChatMessage(content=cur_failed_trial, role=MessageRole.USER)
        )

    def generate(self, messages: List[ChatMessage]) -> ChatResponse:
        logger.info(f"RTL generator input message: {messages}")
        resp, token_cnt = self.token_counter.count_chat(messages)
        logger.info(f"Token count: {token_cnt}")
        logger.info(f"{resp.message.content}")
        return resp

    def batch_generate(
        self, messages_list: List[List[ChatMessage]]
    ) -> List[ChatResponse]:
        resp_token_cnt_list = self.token_counter.count_chat_batch(messages_list)
        responses = []
        for i, ((resp, token_cnt), _) in enumerate(
            zip(resp_token_cnt_list, messages_list)
        ):
            logger.info(f"Message {i+1} token count: {token_cnt}")
            responses.append(resp)
        return responses

    def get_init_prompt_messages(self, input_spec: str) -> List[ChatMessage]:
        ret = [
            ChatMessage(content=SYSTEM_PROMPT, role=MessageRole.SYSTEM),
            ChatMessage(
                content=GENERATION_PROMPT.format(
                    input_spec=input_spec, examples_prompt=RTL_4_SHOT_EXAMPLES
                ),
                role=MessageRole.USER,
            ),
        ]
        if self.generated_tb:
            ret.append(
                ChatMessage(
                    content=TB_PROMPT.format(testbench=self.generated_tb),
                    role=MessageRole.USER,
                )
            )
        if self.failed_trial:
            ret.extend(self.failed_trial)
        if self.generated_if:
            ret.append(
                ChatMessage(
                    content=IF_PROMPT.format(module_interface=self.generated_if),
                    role=MessageRole.USER,
                )
            )
        if (
            isinstance(self.token_counter, TokenCounterCached)
            and self.token_counter.enable_cache
        ):
            self.token_counter.add_cache_tag(ret[-1])
        return ret

    def get_order_prompt_messages(self) -> List[ChatMessage]:
        return [
            ChatMessage(
                content=ORDER_PROMPT.format(
                    output_format="".join(json.dumps(EXAMPLE_OUTPUT, indent=4))
                )
                + EXTRA_ORDER_PROMPT,
                role=MessageRole.USER,
            ),
        ]

    def get_format_error_prompt_messages(
        self, format_error: str, rtl_code: str
    ) -> List[ChatMessage]:
        return [
            ChatMessage(
                content=FORMAT_ERROR_PROMPT.format(
                    format_error=format_error, module_with_lineno=add_lineno(rtl_code)
                ),
                role=MessageRole.USER,
            ),
        ]

    def parse_output(self, response: ChatResponse) -> RTLOutputFormat:
        try:
            output_json_obj: Dict = json.loads(response.message.content, strict=False)
            ret = RTLOutputFormat(
                reasoning=output_json_obj["reasoning"], module=output_json_obj["module"]
            )
        except json.decoder.JSONDecodeError as e:
            ret = RTLOutputFormat(reasoning=f"Json Decode Error: {str(e)}", module="")
        return ret

    def chat(
        self,
        input_spec: str,
        testbench: str,
        interface: str,
        rtl_path: str,
        enable_cache: bool = False,
    ) -> Tuple[bool, str]:
        if isinstance(self.token_counter, TokenCounterCached):
            self.token_counter.set_enable_cache(enable_cache)
        self.history = []
        self.token_counter.set_cur_tag(self.__class__.__name__)
        self.generated_tb = testbench
        self.generated_if = interface
        self.history.extend(self.get_init_prompt_messages(input_spec))
        for _ in range(self.max_trials):
            response = self.generate(self.history + self.get_order_prompt_messages())
            resp_obj = self.parse_output(response)
            if resp_obj.reasoning.startswith("Json Decode Error"):
                logger.info(
                    f"RTL generation Error: {resp_obj.reasoning}, drop this response"
                )
                continue
            rtl_code = resp_obj.module
            with open(rtl_path, "w") as f:
                f.write(rtl_code)
            syntax_correct, syntax_output = check_syntax(rtl_path=rtl_path)
            if syntax_correct:
                break
            self.history.extend(
                [response.message]
                + self.get_format_error_prompt_messages(syntax_output, rtl_code)
            )
        return (syntax_correct, rtl_code)

    def gen_candidates(
        self,
        input_spec: str,
        testbench: str,
        interface: str,
        rtl_path: str,
        candidates_num: int,
        enable_cache: bool = False,
    ) -> List[Tuple[bool, str]]:
        if isinstance(self.token_counter, TokenCounterCached):
            self.token_counter.set_enable_cache(enable_cache)
        self.history = []
        self.token_counter.set_cur_tag(self.__class__.__name__)
        self.generated_tb = testbench
        self.generated_if = interface
        self.history.extend(self.get_init_prompt_messages(input_spec))
        ret: List[Tuple[bool, str]] = [(False, "") for _ in range(candidates_num)]
        messages = [
            self.history + self.get_order_prompt_messages()
            for _ in range(candidates_num)
        ]
        logger.info(f"gen_candidates init input message: {messages[0]}")
        init_responses = self.batch_generate(messages)
        for i, response in enumerate(init_responses):
            rtl_code = self.parse_output(response).module
            candidate_history: List[ChatMessage] = [response.message]
            for j in range(self.max_trials):
                with open(rtl_path, "w") as f:
                    f.write(rtl_code)
                syntax_correct, syntax_output = check_syntax(rtl_path=rtl_path)
                ret[i] = (syntax_correct, rtl_code)
                logger.info(
                    f"Candidate {i + 1} / {candidates_num} trial {j + 1} / {self.max_trials} syntax_correct: {syntax_correct}"
                )
                logger.info(f"RTL code: {rtl_code}")
                if syntax_correct:
                    break
                elif j < self.max_trials - 1:
                    candidate_history.extend(
                        self.get_format_error_prompt_messages(syntax_output, rtl_code)
                    )
                    response = self.generate(
                        self.history
                        + candidate_history
                        + self.get_order_prompt_messages()
                    )
                    rtl_code = self.parse_output(response).module
        return ret

    def ablation_chat(self, input_spec: str, rtl_path: str) -> Tuple[bool, str]:
        if isinstance(self.token_counter, TokenCounterCached):
            self.token_counter.set_enable_cache(False)
        self.history = []
        self.token_counter.set_cur_tag(self.__class__.__name__)
        self.generated_tb = None
        self.generated_if = None
        self.history.extend(self.get_init_prompt_messages(input_spec))
        for _ in range(self.max_trials):
            # Don't add order message into history, to save token
            response = self.generate(self.history + self.get_order_prompt_messages())
            self.history.append(response.message)
            rtl_code = self.parse_output(response).module
            with open(rtl_path, "w") as f:
                f.write(rtl_code)
            syntax_correct, syntax_output = check_syntax(rtl_path=rtl_path)
            if syntax_correct:
                break
            self.history.extend(
                self.get_format_error_prompt_messages(syntax_output, rtl_code)
            )
        return (syntax_correct, rtl_code)
