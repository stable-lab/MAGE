#include <iostream>
#include <fstream>
#include <sstream>
#include <string>

#include "LLMGuidance4CodeCov.h"

using namespace std;

LLMGuidance4CodeCov::LLMGuidance4CodeCov(LLMGuidanceConfig config) 
    : LLMGuidance(config) {
    
}

string LLMGuidance4CodeCov::genInput4undirectedCov(bool first_flag, float temperature) {
    // cout<<"==========="<<endl;
    // cout<<"unDirected test generation\n";
    // cout<<"Temprature = "<<temperature<<endl;

    //
    // Stage 1: make GPT return input in a nature sematic description
    //
    string prompt1 = "";
    if(first_flag) {
        // read verilog dut
        ifstream input_file(dut_path_);
        stringstream buffer;
        buffer << input_file.rdbuf();
        string dut_prompt = buffer.str();

        string task_prompt = R"(Your task involves a Verilog Design Under Test (DUT) that is currently in its initial phase of testing. 
            The assignment requires you to generate a binary input sequence to maximize code coverage. 
            To achieve this, you need to analyze the DUT, considering the logic operations and transitions within the circuit. 
            This careful analysis will allow you to discern the relationship between the input sequence and the uncovered lines, and thus generate an effective input sequence.)";
        // task_prompt += input_signal_prompt_;
        if(use_dut_des_) {
            task_prompt += "\n### DUT Description ###\n";
            ifstream input_file(dut_desc_path_);
            stringstream buffer;
            buffer << input_file.rdbuf();
            string des_prompt = buffer.str();
            task_prompt += des_prompt;
        }
        if(use_dut_inst_) {
            task_prompt += "\n### DUT Test Instruction ###\n";
            ifstream input_file(dut_inst_path_);
            stringstream buffer;
            buffer << input_file.rdbuf();
            string des_prompt = buffer.str();
            task_prompt += des_prompt;
        }
        task_prompt += "\n### DUT ###\n";
        // prompt = task_prompt + "\n" + dut_prompt + "\n" + input_signal_prompt_ + "\n" + answer_format_prompt_;
        prompt1 = task_prompt + "\n" + dut_prompt + "\n";
    } else {
        
        string dut_cov_prompt = undirectedCovRpst();
        string task_prompt = R"(Your task involves a Verilog Design Under Test (DUT) that is currently in its initial phase of testing. 
        The assignment requires you to generate a binary input sequence to cover these uncovered lines with mark 'TO BE COVERED'. 
        To achieve this, you need to analyze the DUT, considering the logic operations and transitions within the circuit. 
        This careful analysis will allow you to discern the relationship between the input sequence and the uncovered lines, and thus generate an effective input sequence.)";
        // task_prompt += input_signal_prompt_;
        if(use_dut_des_) {
            task_prompt += "\n### DUT Description ###\n";
            ifstream input_file(dut_desc_path_);
            stringstream buffer;
            buffer << input_file.rdbuf();
            string des_prompt = buffer.str();
            task_prompt += des_prompt;
        }
        if(use_dut_inst_) {
            task_prompt += "\n### DUT Test Guidance ###\n";
            ifstream input_file(dut_inst_path_);
            stringstream buffer;
            buffer << input_file.rdbuf();
            string des_prompt = buffer.str();
            task_prompt += des_prompt;
        }
        task_prompt += "\n### DUT ###\n";

        // prompt = task_prompt + "\n" + dut_cov_prompt + "\n" + input_signal_prompt_ + "\n" + answer_format_prompt_;
        prompt1 = task_prompt + "\n" + dut_cov_prompt + "\n"; 
    }

    // prompt1 += R"(Answer: Let's think step by step.)";

    string answer1 = sendMsg2GPT(prompt1, temperature, true);   //forget history

    // cout<<prompt1<<endl;
    // cout<<answer1<<endl;

    //
    // Stage2: The second QA make GPT translate its answer in Json format
    //
    string prompt2 = "";
    prompt2 += input_signal_prompt_;

    prompt2 +=  "Please translate that content with the following format\n";

    prompt2 += "### Instruction ###\n" + getGptOutputJsonFormat();
    prompt2 +=  R"(Ensure your response strictly adheres to this format and does not include any additional or irrelevant information. 
        Focus on providing the binary input sequence for each signal after an in-depth analysis of the DUT.\n)";

    string answer2 = sendMsg2GPT(prompt2, temperature, false);

    prompt_cur_iter_.clear();
    prompt_cur_iter_.push_back("\n###PROMPT1###\n" + prompt1);
    prompt_cur_iter_.push_back("\n###PROMPT2###\n" + prompt2);

    answer_cur_iter_.clear();
    answer_cur_iter_.push_back("\n###ANSWER1###\n" + answer1);
    answer_cur_iter_.push_back("\n###ANSWER2###\n" + answer2);

    // cout<<prompt2<<endl;
    // cout<<answer2<<endl;

    return answer2;
}

// In directedCov, we sent our target to gpt and hope to cover these coverpoints
string LLMGuidance4CodeCov::genInput4directedCov(string obj_cov) {
    return "";

}

// Transform original coverage.dat generate by verilator to gpt-readable coverage representation
string LLMGuidance4CodeCov::undirectedCovRpst() {
    ostringstream oss;
    if(cov_rpst_pattern_ == 2)
    {
        ifstream input_file("logs/coverage.dat.total");
        oss << input_file.rdbuf();
    }
    else if(cov_rpst_pattern_ == 1)
    {
        string cmd = "";
        cmd += "verilator_coverage --annotate logs/total-annotated logs/coverage.dat.total --annotate-min 1 > /dev/null";
        int result = system(cmd.c_str());
        ifstream input_file("logs/total-annotated/top.v");
        // fix the cov info: delete the hit count before 'if', this will confuse GPT
        oss << input_file.rdbuf();
    }
    else 
    {
        string cmd = "";
        // this cmd will not generate a annotated top.v if 100% covpoint is hit 
        cmd += "verilator_coverage --annotate logs/total-annotated logs/coverage.dat.total --annotate-min 1 > /dev/null";
        int result = system(cmd.c_str());
        ifstream input_file("logs/total-annotated/top.v");
        // fix the cov info: delete the hit count before 'if', this will confuse GPT
        string line;
        getline(input_file, line); // erase the first line "// // verilator_coverage annotation"
        while (getline(input_file, line)) {
            istringstream iss(line);
            string number, rest;

            // read number and the left part
            iss >> number;
            getline(iss, rest);

            // line with cover points 
            if(number[0]=='0' || number[0]=='%')  { 
            // not line with 'if'
               if (rest.find("if") == string::npos) {
                // to be cover
                    if(number[0]=='%') {
                    rest += "  // TO BE COVER";
                    }
                } 
                string space = string(number.length(), ' ');
                oss << space << rest << '\n';
            } 
            else {
                oss << line << "\n";
            }
        }
    }
    // return verilator_coverage dat
    return oss.str();

}

// Transform target separate coverage to gpt-readable coverage representation
// random select a coverage point to represent with DUT
string LLMGuidance4CodeCov::directedCovRpst() {
    return "";

}