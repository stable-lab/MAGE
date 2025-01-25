#include "LLMGuidance.h"

class LLMGuidance4CodeCov : public LLMGuidance {
public:

    LLMGuidance4CodeCov(LLMGuidanceConfig config);
    ~LLMGuidance4CodeCov() {};

private:

    string genInput4undirectedCov(bool first_flag = false, float temperature = 0.5);

    // In directedCov, we sent our target to gpt and hope to cover these coverpoints
    string genInput4directedCov(string obj_cov = "");

    // Transform original coverage.dat generate by verilator to gpt-readable coverage representation
    string undirectedCovRpst();

    // Transform target separate coverage to gpt-readable coverage representation
    string directedCovRpst();

};