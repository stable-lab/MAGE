
#pragma once

#include <string>
#include <memory>
#include "../../src-basic/Guidance.h"
using namespace std;

typedef struct LLMGuidanceConfig {
    string dut_path;
    string cov_path;
    string history_dir_path;
    string gpt_input_path;
    string gpt_output_path;
    int iter_cnt_max;
    float temperature;
    int cov_rpst_pattern;   // 0 llm rpst; 1 num rpst; 2 original dat rpst
    bool use_dut_des;
    bool use_dut_inst;
} LLMGuidanceConfig;

class LLMGuidance : public Guidance {
public:

    LLMGuidance(LLMGuidanceConfig config);
    ~LLMGuidance();
    
    // If Guidance prepared for a new loop, return true
    int waitForInput();

    // Get input from Guidance
    std::vector<bool> getBitInput();

    // Send hardware simulation coverage as feedback to Guidance
    int sendCovFeedback();

protected:
    // send msg to gpt and return answer
    string sendMsg2GPT(string msg, float temperature, bool forget_flag);

    // We use string to represent coverage
    // In undirectedCov, we sent current coverage to gpt and hope to cover the left coverage
    // If this is the first time to generate input, we try to cover at most coverage
    virtual string genInput4undirectedCov(bool first_flag = false, float temperature = 0.5) = 0;

    // In directedCov, we sent our target to gpt and hope to cover these coverpoints
    virtual string genInput4directedCov(string obj_cov = "") = 0;

    // Transform original coverage.dat generate by verilator to gpt-readable coverage representation
    virtual string undirectedCovRpst() = 0;

    // Transform target separate coverage to gpt-readable coverage representation
    virtual string directedCovRpst() = 0;

    // Generate DUT input signals with pyverilog
    // 1> tell gpt which signals this DUT has
    // 2> tell gpt what is the format of its generated input
    void genSignalPrompt();

    string getGptOutputJsonFormat();

    // old format not json
    // clk:x; input1: x, input2:x ...
    // Check whether GPT feedback answer obey our format rules
    vector<bool> transGPTAnswer2Bits(string answer);
    // Transform the answer string to bits
    bool checkGPTAnswerFormat(string answer);

    // json format translator
    vector<bool> transJsonGPTAnswer2Bits(string answer);


    // Log
    void writeHistory();

    // Test generation strategies
    string covStrategy1();

    
    
protected:
    // DUT Information
    // path of dut verilog file
    string dut_path_;
    // description of DUT
    string dut_desc_path_;
    // description of DUT
    string dut_inst_path_;
    // path that verilator write back coverage result, it is the cov data of one QA iteration
    string cov_path_;
    // path that save the total coverage from test beginning
    string cov_path_total_;
    // DUT input signals names and width
    vector<pair<string, int>> input_signals_;


    // GPT Model Information
    // path that python read prompt and write gpt feedback answer
    string gpt_output_path_;
    string gpt_input_path_;

    // llm parameter
    float default_temperature_;

    // Prompt Information
    // signal prompt to tell gpt which signals dut has
    string input_signal_prompt_;
    // signal prompt to tell gpt the generated input format
    string answer_format_prompt_;
    // Prompt Setting
    // coverage report sent to llm
    // 0  llm-readable cov rpst;
    // 1  verilator annotated cov rpst; 
    // 2  verilator-provided original dat rpst
    int cov_rpst_pattern_;  
    // whether use dut description
    bool use_dut_des_;
    // whether use manual instruction
    bool use_dut_inst_;

    // History Information
    // pair.first: input (in our format)
    // pair.second: true simulation cov (in origin coverage.dat format)
    vector<pair<string, string>> history_cov; 
    string history_dir_path_;
    // record prompt gpt-generated input for this iteration 
    vector<string> answer_cur_iter_;
    vector<string> prompt_cur_iter_;

    // Statistic Information
    int iter_cnt_ = 0;
    int iter_cnt_max_;
    int cur_covered_num_ = 0;
    int covered_stop_iter_num_ = 0; //record iteration times that total coverage cannot improve
    int clk_cycle_num_ = 0;

private:
    // connect with gpt python
    std::ifstream pipe_in;
    std::ofstream pipe_out;
};
