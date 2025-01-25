
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <string>
#include <nlohmann/json.hpp>


#include "LLMGuidance.h"

using namespace std;


LLMGuidance::LLMGuidance(LLMGuidanceConfig config){

    dut_path_ = config.dut_path;
    dut_desc_path_ = config.dut_path + ".des";
    dut_inst_path_ = config.dut_path + ".inst";
    cov_path_ = config.cov_path;
    history_dir_path_ = config.history_dir_path;
    gpt_output_path_ = config.gpt_output_path;
    gpt_input_path_ = config.gpt_input_path;
    default_temperature_ = config.temperature;
    iter_cnt_max_ = config.iter_cnt_max;
    cov_rpst_pattern_ = config.cov_rpst_pattern;
    use_dut_des_ = config.use_dut_des;
    use_dut_inst_ = config.use_dut_inst;
    

    cov_path_total_ = cov_path_ + ".total";
    
    // build history directory
    string cmd = "mkdir " + history_dir_path_;
    system(cmd.c_str());
    
    // extract input signals from dut
    genSignalPrompt();

    // launch gpt robot and connect with the python process
    system("cd ../llm-guidance && bash setup.sh");
    string cmd1 = "python ../llm-guidance/src/RunGPT.py ";
    cmd1 += " -i " + gpt_input_path_;
    cmd1 += " -o " + gpt_output_path_;
    cmd1 += " &";
    system(cmd1.c_str());

    pipe_in.open("../llm-guidance/g2v");
    pipe_out.open("../llm-guidance/v2g");
    
    // Test GPT Python
    pipe_out << "hello"<<endl;
    pipe_out.flush();
    string rsp;
    getline(pipe_in, rsp);
    if(rsp!="hello_end") {
        throw std::runtime_error("Cannot build connect with python GPT");
    }       
}

LLMGuidance::~LLMGuidance() {
    // shut down python gpt process
    pipe_out << "exit"<<endl;
    pipe_out.flush();
    
}

int LLMGuidance::waitForInput() {
    // judge whether need further testing
    iter_cnt_++;    

    if(iter_cnt_>iter_cnt_max_) {
        return 0;
    }
    
    return 1;
}

vector<bool> LLMGuidance::getBitInput() {

    // select strategy
    string input_str = covStrategy1();
    // string input_str = genInput4undirectedCov(iter_cnt_==1, "");
    
    std::vector<bool> bitstream;

    // bool fmt_correct = checkGPTAnswerFormat(input_str);

    // if(!fmt_correct) {
    //     // throw std::runtime_error("GPT return wrong format\n");
    //     cout<<"iter "<<iter_cnt_<<": GPT return wrong format\n";
    //     return bitstream;
    // }

    // cout<<input_str<<endl;

    // bitstream = transGPTAnswer2Bits(input_str);
    bitstream = transJsonGPTAnswer2Bits(input_str);

    // cout<<"bitstream: ";
    // for(auto c: bitstream) cout<<c<<" ";
    // cout<<endl;

    return bitstream;
}

// Update history coverage data
int LLMGuidance::sendCovFeedback(){
    // 1> save prompt=>input=>coverage of this iteration to history directory
    writeHistory();
    
    // 2> keep total coverage

    ifstream in_file(cov_path_total_);
    string cmd;
    if (!in_file.is_open()) {
        // The first iteration
        cmd = "verilator_coverage -write " + cov_path_total_ +  " " + cov_path_;
    } else {
        // cmd: verilator_coverage -write coverage.dat.total coverage.dat.total coverage.dat
        // coverage.dat.total = coverage.dat.total + coverage.dat
        cmd = "verilator_coverage -write " + cov_path_total_ + " " + cov_path_total_ + " " + cov_path_;
    }
    system(cmd.c_str());

    // 3> update coverage information
    pair<int,int> cur_cov_pair = getCoverageNum(cov_path_total_);
    int cur_cov_num = cur_cov_pair.first;
    int total_cov_num = cur_cov_pair.second;

    if(cur_cov_num>cur_covered_num_) {
        covered_stop_iter_num_ = 0;
        cur_covered_num_ = cur_cov_num;
    } else {
        covered_stop_iter_num_++;
    }

    // print log
    ofstream outfile(history_dir_path_+"/cov.log", std::ios_base::app);
    if (!outfile) {
        throw std::runtime_error("Could not open file: " + cov_path_);
    } 
    outfile<<"LLM:  Iter = "<< iter_cnt_<<"   Clk Cycle = "<<clk_cycle_num_<<endl;
    outfile<<"      Cov = "<<(float)cur_cov_num/(float)total_cov_num<<"("<<cur_cov_num<<"/"<<total_cov_num<<")\n";
    outfile.close();
    
    if(cur_cov_num==total_cov_num) {
        return 1;
    }   
    else
        return 0;
}


// send prompt to GPT and return answer
// string -> string
string LLMGuidance::sendMsg2GPT(string msg, float temperature, bool forget_flag) {

    // Set temprature
    pipe_out << "temperature" <<endl;
    pipe_out.flush();
    pipe_out << temperature <<endl;
    pipe_out.flush();
    string rsp;
    getline(pipe_in, rsp);
    if(rsp!="temperature_end") {
        throw std::runtime_error("Set temperature of GPT failed");
    }       
    
    // Choose whether to forget history
    if(forget_flag) {
        pipe_out << "new" <<endl;
        pipe_out.flush();
        string rsp;
        getline(pipe_in, rsp);
        if(rsp!="new_end") {
            throw std::runtime_error("Set GPT forget history failed");
        } 
    }      

    // Send prompt and get answer
    if(msg.size()==0)
        return "";
    
    ofstream outfile(gpt_input_path_);  // write prompt to input file
    if (!outfile.is_open()) {
        throw std::runtime_error("Could not open file: " + gpt_input_path_);
    }
    outfile << msg;
    outfile.close();
    
    pipe_out << "prompt" <<endl;
    pipe_out.flush(); 

    getline(pipe_in, rsp);
    if(rsp!="prompt_end") {
        throw std::runtime_error("Get GPT answer response failed");
    }      

    // Read GPT feedback
    std::ifstream inFile(gpt_output_path_);     // read gpt answer from output file
    std::stringstream buffer;
    if (!inFile.is_open()) {
        throw std::runtime_error("Could not open file: " + gpt_output_path_);
    }
    buffer << inFile.rdbuf();

    return buffer.str();
}


// Generate DUT input signals with pyverilog
// 1> tell gpt which signals this DUT has
// 2> tell gpt what is the format of its generated input
void LLMGuidance::genSignalPrompt() {
    
    // extract signals from pyverilog generated files
    string filePath = "../input-signals.txt";
    std::ifstream inFile(filePath);
    std::vector<std::pair<std::string, int>> data;

    if (!inFile.is_open()) {
        throw std::runtime_error("Could not open file: " + filePath);
    }

    std::string line;
    while (std::getline(inFile, line)) {
        std::istringstream iss(line);
        std::string inputSignal;
        int width;

        if (!(iss >> inputSignal >> width)) {
            throw std::runtime_error("Error parsing line: " + line);
        }

        data.emplace_back(inputSignal, width);
    }
    input_signals_ = data;
    if(input_signals_.size()==0) {
        throw std::runtime_error("No input signals parsing! Wrong DUT! ");
    }

    // generate prompt of input signals
    string signals_prompt = "DUT has the following input signals\n";

    std::stringstream ss;
    for (const auto& pair : data) {
        ss << "Input signal: " << pair.first << ";  Width: " << pair.second << "\n";
    }
    signals_prompt += ss.str();

    input_signal_prompt_ = signals_prompt;

    // generate gpt answer format
    // this answer is gpt-generatd input for DUT
    string answer_prompt = "Please return the answer with the following format\n";
    answer_prompt += "Each value for signal should in binary format, such as 011..., the binary width should equal to signal width\n";

    std::stringstream ss1;
    ss1 << "clk=1:";
    for (const auto& pair : data) {
        ss1 << pair.first << "=x;";
    }
    ss1 <<"\n";
    ss1 << "clk=2:";
    for (const auto& pair : data) {
        ss1 << pair.first << "=x;";
    }
    ss1 <<"\n";
    ss1 << "clk=3:...\n  ";
    answer_prompt += ss1.str();

    answer_prompt += "You are only allowed to response strictly in the above format and DO NOT explain any other extra information\n";

    answer_format_prompt_ = answer_prompt;


}


// Transform the answer string to bits
vector<bool> LLMGuidance::transGPTAnswer2Bits(string answer) {
    istringstream iss(answer);
    string line;
    vector<bool> result;
    while (getline(iss, line)) {
        istringstream lineStream(line);
        string token;

        // Skip "clk=x:"
        getline(lineStream, token, '=');
        if (token != "clk") continue;
        getline(lineStream, token, ':');

        // Parse signal lines
        for (const auto& signal : input_signals_) {
            getline(lineStream, token, '=');
            getline(lineStream, token, ';');
            string binStr = token;

            for (char c : binStr) {
                result.push_back(c == '1');
            }
        }

        clk_cycle_num_++;
    }

    return result;
}   

// Check GPT feedback answer obey our format rules
bool LLMGuidance::checkGPTAnswerFormat(string answer) {
    istringstream iss(answer);
    string line;
    // int clkCount = 1;

    while (getline(iss, line)) {
        istringstream lineStream(line);
        string token;

        // Check clk
        getline(lineStream, token, '=');
        if (token != "clk") continue;

        getline(lineStream, token, ':');
        // if (stoi(token) != clkCount) return false;
        // ++clkCount;

        // Check signal lines
        for (const auto& signal : input_signals_) {
            getline(lineStream, token, '=');
            if (token != signal.first) return false;

            getline(lineStream, token, ';');
            string binStr = token;
            if (binStr.size() != signal.second) {
                return false;
            }
            for (char c : binStr) {
                if (c != '0' && c != '1') 
                    return false;
            }
        }
    }
    return true;
}

vector<bool> LLMGuidance::transJsonGPTAnswer2Bits(string answer) {

    // Find the start and end of the JSON substring
    std::string start_delimiter = R"([)";
    std::string end_delimiter = R"(])";
    std::size_t start_pos = answer.find(start_delimiter);
    std::size_t end_pos = answer.find(end_delimiter, start_pos);
    std::string json_str = answer.substr(start_pos, end_pos - start_pos + end_delimiter.length());

    // cout<<json_str<<endl;
    // use nlohmann::json to extract string
    nlohmann::json jsonObj = nlohmann::json::parse(json_str);
    vector<bool> result;

    for (nlohmann::json::iterator it = jsonObj.begin(); it != jsonObj.end(); ++it) {
        // pop the input in json in clk order
        for(auto p: input_signals_) {
            bool flag = false;
            // pop the signals in 1 clk cycle
            for (nlohmann::json::iterator obj_it = it->begin(); obj_it != it->end(); ++obj_it) {
                string bin_str = obj_it.value();
                if(obj_it.key() == p.first) {
                    flag = true;
                    if(bin_str[0]=='x') {
                        // llm output is 'x' value
                        for(int i=0;i<p.second;i++) {
                            result.push_back(0);
                        }
                        break;
                    }
                    if(p.second != bin_str.length()) {
                        return vector<bool>();  // return a null vector to indicate a answer wrong format situation
                        // throw std::runtime_error("Get GPT answer in wrong format: Width Mismatch");
                    }
                    for (char c : bin_str) {
                        result.push_back(c == '1');
                    }
                    break;
                }                
            }
            if(!flag) {
                return vector<bool>(); // return a null vector to indicate a answer wrong format situation
                // throw std::runtime_error("Get GPT answer in wrong format: Signal Miss");
            }
        }
        clk_cycle_num_++;
        
        //std::cout << "------------------------\n";
    }

    return result;
}



void LLMGuidance::writeHistory() {
    // write prompt to history
    string prompt_history_file = history_dir_path_ + "/prompt." + to_string(iter_cnt_);
    ofstream outfile(prompt_history_file);
    if (!outfile) {
        throw std::runtime_error("Could not open file: " + prompt_history_file);
    }
    for(string s:prompt_cur_iter_) { outfile << s; }
    outfile.close();
    
    // write gpt answer to history
    string input_history_file = history_dir_path_ + "/answer." + to_string(iter_cnt_);
    ofstream outfile1(input_history_file);
    if (!outfile1) {
        throw std::runtime_error("Could not open file: " + input_history_file);
    }
    for(string s:answer_cur_iter_) {outfile1 << s;}
    outfile1.close();

    // write coverage.dat to history
    ifstream in_file_cov(cov_path_);
    if (!in_file_cov.is_open()) {
        throw std::runtime_error("Could not open file: " + cov_path_);
    } else {
        // cmd: cp coverage.dat history/coverage.dat.x
        string cmd = "cp " + cov_path_ + " " + history_dir_path_ + "/coverage.dat." + to_string(iter_cnt_);
        system(cmd.c_str());
    }
}

string LLMGuidance::getGptOutputJsonFormat() {
    string task = R"(Generate the input sequence in binary format, with the binary width matching the width of the respective signal. 
        If a DUT has a clk signal, a REQUEST1 signal and a REQUEST2 signal, the input sequence should be presented in the following JSON format:)";
    string json_string = R"([
        {"clk":"1","REQUEST1":"x","REQUEST2":"x"},
        {"clk":"2","REQUEST1":"x","REQUEST2":"x"},
        {"clk":"3","REQUEST1":"x","REQUEST2":"x"}
        ]
    )";

    return task + json_string;
}


string LLMGuidance::covStrategy1() {

    string input_str = genInput4undirectedCov(iter_cnt_==1, default_temperature_ + covered_stop_iter_num_ * 0.1);

    return input_str;

}