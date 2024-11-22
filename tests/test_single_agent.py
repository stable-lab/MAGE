import argparse
import os
import subprocess

import backoff
import openai
import pandas as pd

from mage_rtl.benchmark_read_helper import (
    TypeBenchmark,
    TypeBenchmarkFile,
    get_benchmark_contents,
)
from mage_rtl.gen_config import Config, get_llm
from mage_rtl.log_utils import get_logger
from mage_rtl.rtl_generator import RTLGenerator

# Configuration and Constants
# model = "gpt-4-0314"
model = "gpt-4"
# model = "gpt-3.5-turbo-0301"
temperature = 0.7
n = 1


description_directory = "../Dataset"
output_directory = "output_gen_verilog_4_shot_self_learning"
# circuit_folders = ["adder_16bit"]
# ,"fsm","multi_booth","right_shifter"]  # and other folders
circuit_folders = [
    "accu",
    "adder_32bit",
    "adder_8bit",
    "asyn_fifo",
    "counter_12",
    "edge_detect",
    "fsm",
    "multi_16bit",
    "multi_pipe_4bit",
    "mux",
    "pe",
    "pulse_detect",
    "RAM",
    "right_shifter",
    "signal_generator",
    "width_8to16",
    "adder_16bit",
    "adder_64bit",
    "alu",
    "calendar",
    "div_16bit",
    "freq_div",
    "Johnson_Counter",
    "multi_booth",
    "multi_pipe_8bit",
    "parallel2serial",
    "radix2_div",
    "serial2parallel",
    "traffic_light",
]


max_generations = 20
max_retries = 10


results_columns = [
    "Folder",
    "Generation",
    "Attempt",
    "Result",
    "Syntax Check",
    "Functionality Check",
]
results_df = pd.DataFrame(columns=results_columns)
# Initialize conversation history
conversation_history = []


@backoff.on_exception(backoff.expo, openai.error.OpenAIError, max_tries=2)
def completions_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)


verilog_examples = [
    """Here are Some examples of rtl verilog code:
    Gray to Binary Code Converter:
    This Verilog example demonstrates a parameterized gray to binary code converter using a Verilog generate loop
    module gray2bin
    #(parameter SIZE = 8)
    (
    input [SIZE-1:0] gray,
    output [SIZE-1:0] bin
    )

    Genvar gi;
    for (gi=0; gi<SIZE; gi=gi+1) begin : genbit
    assign bin[gi] = ^gray[SIZE-1:gi];
    end
    endmodule

    adding structure to design :
    module shiftRightAr(a, shiftCnt, z);
    input [31:0] a;
    input [4:0] shiftCnt;
    output [31:0] z;
    wire [31:0] d0, d1, d2, d3, notA;
    assign notA = ~a;
    mux2to1L32 m21_0 (notA,{notA[31], notA[31:1]}, shiftCnt[0], d0);
    mux2to1L32 m21_1 (d0,{{ 2{a[31]}}, d0[31:2]}, shiftCnt[1], d1);
    mux2to1L32 m21_2 (d1,{{ 4{notA[31]}}, d1[31:4]}, shiftCnt[2],
    d2);
    mux2to1L32 m21_3 (d2,{{ 8{a[31]}}, d2[31:8]}, shiftCnt[3], d3);
    mux2to1L32 m21_4 (d3,{{16{notA[31]}}, d3[31:16]},shiftCnt[4],
    z);
    endmodule
    module mux2to1L32 (a, b, s, z);
    input [31:0] a, b;
    input s;
    output [31:0] z;
    assign z = ~(s ? b : a);
    endmodule ",

    "Performing operation in parallel:
    Parallel Search - 11.4 ns, 612 gates (fastest design)
    module arrayCmpV3(clk, reset, inc, index, min);
    input clk, reset, inc;
    input [1:0] index;
    output [1:0] min;
    reg [5:0] cntr[0:4];
    integer i;
    // compare all counters to each other
    wire l32 = cntr[3] < cntr[2];
    wire l31 = cntr[3] < cntr[1];
    wire l30 = cntr[3] < cntr[0];
    wire l21 = cntr[2] < cntr[1];
    wire l20 = cntr[2] < cntr[0];
    wire l10 = cntr[1] < cntr[0];
    // select the smallest value
    assign min = {l31&l30 | l21&l20, l32&l30 | l10&~l21};
    always @(posedge clk)if (reset)
    for( i=0; i<=3; i=i+1 )
    cntr[i] <= 6’d0;
    else if (inc)
    cntr[index] <= cntr[index] + 1;
    endmodule

    Adder Generation:
    This example illustrates an adder generator using Verilog generate loop,
    demonstrating how each iteration creates a new scope with distinct variables
    module addergen1
    #(parameter SIZE = 4)
    (
    input  logic [SIZE-1:0] a, b,
    input  logic            ci,
    output logic            co,
    output logic [SIZE-1:0] sum
    );

    wire [SIZE :0] c;
    genvar i;
    assign c[0] = ci;

    for(i=0; i<SIZE; i=i+1) begin:bitnum
    wire t1, t2, t3;
    xor g1 ( t1, a[i], b[i]);
    xor g2 ( sum[i], t1, c[i]);
    and g3 ( t2, a[i], b[i]);
    and g4 ( t3, t1, c[i]);
    or g5 ( c[i+1], t2, t3);
    end

    assign co = c[SIZE];
    endmodule


    """
]


def generate_verilog_code(
    description, folder_name, verilog_code="", error_msg="", attempt=0, generation=0
):
    global conversation_history

    print(" Generation number:", generation, "Attempt number:", attempt)
    message_content = ""
    if attempt == 0:
        message_content = (
            "\n".join(verilog_examples)
            + "\nBased on the above examples, "
            + description
        )
        conversation_history = []
        # # For the first attempt of each generation, use the description and reset the history
        # message_content = description
        # conversation_history = []
        # message_content += self_planning
        self_planning = """\n\n Please write a enire verilog code with comments.try to understand the requirements above and give reasoning steps in natural language to achieve it.
           In addition, try to give advice to avoid syntax error.
           \nAfter finish thinking please give me verilog code with explicitly starts with module and end with endmodule.
           \nEven if there is error in testbench give me verilog code with module endmodule.
          \n There sould be always a verilog code with module and endmodule """
        # self_planning = "\n\n#Please act as a professional verilog designer, try to understand the requirements above and give reasoning steps in natural language to achieve it. In addition, try to give advice to avoid syntax error. Then write entire code"
        message_content += self_planning
    else:
        # For subsequent attempts, use the conversation history
        message_content = "\n{}\n\n Please see the errors in previously generated code\n \
Please write entire code by fixing the errors in previous code\n  Do not write testbench. Please only give me the code, \
for anything beside code, please properly comment it out. ".format(
            error_msg
        )

    conversation_history.append({"role": "user", "content": message_content})
    # print("COnversation_history")
    # print(conversation_history[-3:])
    print("============================================================")
    print("This is input prompt to gpt model:\n", message_content)
    print("============================================================")
    result = completions_with_backoff(
        model=model,
        messages=conversation_history[-4:],
        temperature=temperature,
        max_tokens=2048,
        n=n,
    )

    verilog_code_generated = result["choices"][0]["message"]["content"]
    # print("============================================================")
    # print("RAW API Output:\n", verilog_code_generated)
    # print("============================================================")

    # Attempt to extract Verilog code
    start_marker = f"module {folder_name}"
    end_marker = "endmodule"
    start_index = verilog_code_generated.find(start_marker)
    end_index = verilog_code_generated.rfind(end_marker)

    if start_index != -1 and end_index != -1:
        verilog_code_cleaned = verilog_code_generated[
            start_index : end_index + len(end_marker)
        ].strip()
        conversation_history.append(
            {"role": "assistant", "content": verilog_code_cleaned}
        )
    else:
        verilog_code_cleaned = ""
        print("Error: Unable to extract Verilog code from the content!")
        conversation_history.append(
            {"role": "assistant", "content": "Error extracting Verilog code."}
        )

    return verilog_code_cleaned


def save_code(folder, generation, attempt, verilog_code):
    folder_path = os.path.join(output_directory, folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_name = f"generation_{generation}_attempt_{attempt}.v"
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "w") as f:
        f.write(verilog_code)
    print(f"Saved Verilog code to {file_path}")


def check_syntax(verilog_code, task_id):
    generated_sv_file_path = os.path.join("/tmp", f"{task_id}_generated.v")
    with open(generated_sv_file_path, "w") as sv_file:
        sv_file.write(verilog_code)

    cmd = f"iverilog -o /tmp/{task_id}.out {generated_sv_file_path}"

    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return "Pass"
    except subprocess.CalledProcessError:
        return "Fail"


def check_correctness(problem, verilog_code, timeout=20):
    task_id = problem["task_id"]
    generated_sv_file_path = os.path.join("/tmp", "{}_generated.v".format(task_id))
    testbench_file_path = problem["test"]

    with open(generated_sv_file_path, "w") as sv_file:
        sv_file.write(verilog_code)

    cmd = "iverilog -Wall -Winfloop -Wno-timescale -g2012 -s {}_tb -o /tmp/test_{}.vvp {} {}; vvp -n /tmp/test_{}.vvp".format(
        task_id, task_id, generated_sv_file_path, testbench_file_path, task_id
    )

    try:
        process = subprocess.run(
            cmd, shell=True, timeout=timeout, capture_output=True, text=True
        )
        output_str = process.stdout
        error_str = process.stderr

        # print("*****************output of the command**************************")
        # print("Output of the command:", output_str)
        # print("Error in the command:", error_str)
        # print("*****************output of the command**************************")

        # Check for pass, fail, and error conditions
        if "Your Design Passed" in output_str and "error" not in error_str.lower():
            result = "Passed"
        elif (
            "Failed" in output_str
            or "error" in output_str.lower()
            or "error" in error_str.lower()
        ):
            result = "Failed"
        elif "failures" in output_str.lower():
            result = "Failed"
        else:
            result = "Unknown Result"

        return {"result": result, "output": output_str, "error": error_str}

    except subprocess.TimeoutExpired:
        return {
            "result": "Timeout",
            "output": "Simulation timeout occurred. This may indicate a complex simulation or an issue in the Verilog code/testbench.",
        }


logger = get_logger(__name__)

args_dict = {
    # "model": "claude-3-5-sonnet-20241022",
    "model": "gpt-4o",
    "filter_instance": "^(Prob070_ece241_2013_q2|Prob151_review2015_fsm)$",
}


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

test_dict = get_benchmark_contents(
    TypeBenchmark.VERILOG_EVAL_V2,
    TypeBenchmarkFile.TEST_PATH,
    "../verilog-eval",
    args.filter_instance,
)

for key, spec in spec_dict.items():
    rtl_gen.reset()
    logger.info(spec)
    is_pass, code = rtl_gen.chat(spec, key)
    logger.info(is_pass)
    logger.info(code)
    testbench_file_path = test_dict[key]

    for generation_attempt in range(max_generations):
        verilog_code = ""
        simulator_errors = ""
        code_generation_attempt = 0

        while code_generation_attempt < max_retries:
            verilog_code = generate_verilog_code(
                spec,
                key,
                verilog_code,
                simulator_errors,
                code_generation_attempt,
                generation_attempt,
            )
            save_code(key, generation_attempt, code_generation_attempt, verilog_code)

            print(
                "++++++++++++++++++++this is cleaned verilog code+++++++++++++++++++++++++++++++++++++"
            )
            print(verilog_code)
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            problem = {
                "test": testbench_file_path,
                "prompt": spec,
                "task_id": key,
            }
            correctness_result = check_correctness(problem, verilog_code)

            # print("%%%%%%%%%%%%%%%%%%%%%%%%%%")
            # print(correctness_result)
            # print("************************************0")
            # print(correctness_result['output'])
            # print("************************************0")
            # print(correctness_result['error'])
            # print("%%%%%%%%%%%%%%%%%%%%%%%%%%")
            # Update the DataFrame with the attempt data
            syntax_result = check_syntax(verilog_code, key)
            functionality_result = correctness_result["result"]
            # print("####################################################################")
            # print("syntax check:",syntax_result)
            # print("functionality_result:", functionality_result)
            # print("####################################################################")

            # Update the DataFrame with the attempt data
            attempt_data = {
                "Folder": key,
                "Generation": generation_attempt + 1,
                "Attempt": code_generation_attempt + 1,
                "Result": functionality_result,
                "Syntax Check": syntax_result,
                "Functionality Check": (
                    "Fail" if functionality_result not in ["Passed", "Pass"] else "Pass"
                ),
            }
            results_df = pd.concat(
                [results_df, pd.DataFrame([attempt_data])], ignore_index=True
            )

            if correctness_result["result"] == "Passed":
                print(
                    "Code passed on attempt {} of generation {}.".format(
                        code_generation_attempt + 1, generation_attempt + 1
                    )
                )
                break
            elif correctness_result["result"] in ["Error", "Failed"]:
                print(
                    f"An error occurred during simulation: {correctness_result['error']}\n {correctness_result['output']}"
                )
                # simulator_errors = f"feedback for attempt {code_generation_attempt + 1}: {correctness_result['output']}\n"
                simulator_errors = f"Issues in the previous code \nError Details: {correctness_result['error']}\nOutput: {correctness_result['output']}"
                code_generation_attempt += 1
            else:
                print("Error or timeout. Retrying...")
                code_generation_attempt += 1

        print(f"Generation attempt {generation_attempt + 1} complete for {key}.")


# Save the DataFrame to an Excel file
results_df.to_csv("gpt4_4shot_rtllm.csv")
