RTL_4_SHOT_EXAMPLES = """
Here are some examples of RTL SystemVerilog code:
Example 1:
<example>
    <input_spec>
        Implement the SystemVerilog module based on the following description.
        Assume that sigals are positive clock/clk triggered unless otherwise stated.

        The module should implement a XOR gate.
    </input_spec>
    <module>
        module TopModule(
            input  logic in0,
            input  logic in1,
            output logic out
        );

            assign out = in0 ^ in1;

        endmodule
    </module>
</example>
Example 2:
<example>
    <input_spec>
        Implement the SystemVerilog module based on the following description.
        Assume that sigals are positive clock/clk triggered unless otherwise stated.

        The module should implement an 8-bit registered incrementer.
        The 8-bit input is first registered and then incremented by one on the next cycle.
        The reset input is active high synchronous and should reset the output to zero.
    </input_spec>
    <module>
        module TopModule(
            input  logic       clk,
            input  logic       reset,
            input  logic [7:0] in_,
            output logic [7:0] out
        );

            // Sequential logic
            logic [7:0] reg_out;
            always @( posedge clk ) begin
                if ( reset )
                reg_out <= 0;
                else
                reg_out <= in_;
            end

            // Combinational logic
            logic [7:0] temp_wire;
            always @(*) begin
                temp_wire = reg_out + 1;
            end

            // Structural connections
            assign out = temp_wire;

        endmodule
    </module>
</example>
Example 3:
<example>
    <input_spec>
        Implement the SystemVerilog module based on the following description.
        Assume that sigals are positive clock/clk triggered unless otherwise stated.

        The module should implement an n-bit registered incrementer where the bitwidth is specified by the parameter nbits.
        The n-bit input is first registered and then incremented by one on the next cycle.
        The reset input is active high synchronous and should reset the output to zero.
    </input_spec>
    <module>
        module TopModule #(
            parameter nbits
        )(
            input  logic             clk,
            input  logic             reset,
            input  logic [nbits-1:0] in_,
            output logic [nbits-1:0] out
        );

            // Sequential logic
            logic [nbits-1:0] reg_out;
            always @( posedge clk ) begin
                if ( reset )
                reg_out <= 0;
                else
                reg_out <= in_;
            end

            // Combinational logic
            logic [nbits-1:0] temp_wire;
            always @(*) begin
                temp_wire = reg_out + 1;
            end

            // Structural connections
            assign out = temp_wire;

        endmodule
    </module>
</example>
Example 4:
<example>
    <input_spec>
        Implement the SystemVerilog module based on the following description.
        Assume that sigals are positive clock/clk triggered unless otherwise stated.

        Build a finite-state machine that takes as input a serial bit stream,
            and outputs a one whenever the bit stream contains two consecutive one's.
        The output is one on the cycle _after_ there are two consecutive one's.
        The reset input is active high synchronous,
            and should reset the finite-state machine to an appropriate initial state.
    </input_spec>
    <module>
        module TopModule(
            input  logic clk,
            input  logic reset,
            input  logic in_,
            output logic out
        );

            // State enum
            localparam STATE_A = 2'b00;
            localparam STATE_B = 2'b01;
            localparam STATE_C = 2'b10;

            // State register
            logic [1:0] state;
            logic [1:0] state_next;
            always @(posedge clk) begin
                if ( reset )
                state <= STATE_A;
                else
                state <= state_next;
            end

            // Next state combinational logic
            always @(*) begin
                state_next = state;
                case ( state )
                STATE_A: state_next = ( in_ ) ? STATE_B : STATE_A;
                STATE_B: state_next = ( in_ ) ? STATE_C : STATE_A;
                STATE_C: state_next = ( in_ ) ? STATE_C : STATE_A;
                endcase
            end

            // Output combinational logic
            always @(*) begin
                out = 1'b0;
                case ( state )
                STATE_A: out = 1'b0;
                STATE_B: out = 1'b0;
                STATE_C: out = 1'b1;
                endcase
            end

        endmodule
    </module>
</example>
"""

TB_4_SHOT_EXAMPLES = """
Here are some examples of SystemVerilog testbench code:
Example 1:
<example>
    <input_spec>
        Implement the SystemVerilog module based on the following description.
        Assume that sigals are positive clock/clk triggered unless otherwise stated.

        The module should implement a XOR gate.
    </input_spec>
    <interface>
        module TopModule(
            input  logic in0,
            input  logic in1,
            output logic out
        );
    </interface>
    <testbench>
        module TopModule_tb();
            // Signal declarations
            logic in0;
            logic in1;
            logic out;
            logic expected_out;
            int mismatch_count;

            // Instantiate the Device Under Test (DUT)
            TopModule dut (
                .in0(in0),
                .in1(in1),
                .out(out)
            );

            // Expected output calculation
            assign expected_out = in0 ^ in1;

            // Initialize signals
            initial begin
                // Initialize signals
                in0 = 0;
                in1 = 0;
                mismatch_count = 0;

                // Test all input combinations
                for (int i = 0; i < 4; i++) begin
                    {in0, in1} = i;
                    #10; // Wait for outputs to settle

                    // Check for mismatches
                    if (out !== expected_out) begin
                        $display("Mismatch at time %0t:", $time);
                        $display("  Inputs: in0=%b, in1=%b", in0, in1);
                        $display("  Expected output: %b, Actual output: %b", expected_out, out);
                        mismatch_count++;
                    end else begin
                        $display("Match at time %0t:", $time);
                        $display("  Inputs: in0=%b, in1=%b", in0, in1);
                        $display("  Output: %b", out);
                    end
                end

                // Display final simulation results
                #10;
                if (mismatch_count == 0)
                    $display("SIMULATION PASSED");
                else
                    $display("SIMULATION FAILED - %0d mismatches detected", mismatch_count);

                $finish;
            end

            // Optional: Generate VCD file for waveform viewing
            initial begin
                $dumpfile("xor_test.vcd");
                $dumpvars(0, TopModule_tb);
            end
        endmodule
    </testbench>
</example>
Example 2:
<example>
    <input_spec>
        Implement the SystemVerilog module based on the following description.
        Assume that sigals are positive clock/clk triggered unless otherwise stated.

        The module should implement an 8-bit registered incrementer.
        The 8-bit input is first registered and then incremented by one on the next cycle.
        The reset input is active high synchronous and should reset the output to zero.
    </input_spec>
    <interface>
        module TopModule(
            input  logic       clk,
            input  logic       reset,
            input  logic [7:0] in_,
            output logic [7:0] out
        );
    </interface>
    <testbench>
        module TopModule_tb();
            // Signal declarations
            logic       clk;
            logic       reset;
            logic [7:0] in_;
            logic [7:0] out;
            logic [7:0] expected_out;

            // Mismatch counter
            int mismatch_count;

            // Instantiate the DUT (Design Under Test)
            TopModule dut (
                .clk(clk),
                .reset(reset),
                .in_(in_),
                .out(out)
            );

            // Clock generation
            always begin
                clk = 0;
                #5;
                clk = 1;
                #5;
            end

            // Test stimulus
            initial begin
                // Initialize signals
                reset = 0;
                in_ = 8'h00;
                mismatch_count = 0;
                expected_out = 8'h00;

                // Reset check
                @(posedge clk);
                reset = 1;
                @(posedge clk);
                @(negedge clk);
                check_output();

                reset = 0;

                // Test case 1: Normal increment operation
                for (int i = 0; i < 10; i++) begin
                    in_ = $urandom_range(0, 255);
                    @(posedge clk);  // Wait for input to be registered
                    expected_out = in_;  // First cycle: input gets registered
                    @(negedge clk);
                    check_output();

                    @(posedge clk);  // Wait for increment
                    expected_out = in_ + 1;  // Second cycle: registered value gets incremented
                    @(negedge clk);
                    check_output();
                end

                // Test case 2: Overflow condition
                in_ = 8'hFF;
                @(posedge clk);
                expected_out = 8'hFF;
                @(negedge clk);
                check_output();

                @(posedge clk);
                expected_out = 8'h00;  // Should overflow to 0
                @(negedge clk);
                check_output();

                // Test case 3: Reset during operation
                in_ = 8'h55;
                @(posedge clk);
                expected_out = 8'h55;
                @(negedge clk);
                check_output();

                reset = 1;
                @(posedge clk);
                expected_out = 8'h00;  // Should reset to 0
                @(negedge clk);
                check_output();

                // End simulation
                if (mismatch_count == 0)
                    $display("SIMULATION PASSED");
                else
                    $display("SIMULATION FAILED with %0d mismatches", mismatch_count);

                $finish;
            end

            // Task to check output and log mismatches
            task check_output();
                if (out !== expected_out) begin
                    $display("Time %0t: Mismatch detected!", $time);
                    $display("Input = %h, Expected output = %h, Actual output = %h",
                            in_, expected_out, out);
                    mismatch_count++;
                end else begin
                    $display("Time %0t: Match detected!", $time);
                    $display("Input = %h, Output = %h", in_, out);
                end
            endtask

        endmodule
    </testbench>
</example>
Example 3:
<example>
    <input_spec>
        Implement the SystemVerilog module based on the following description.
        Assume that sigals are positive clock/clk triggered unless otherwise stated.

        The module should implement an n-bit registered incrementer where the bitwidth is specified by the parameter nbits.
        The n-bit input is first registered and then incremented by one on the next cycle.
        The reset input is active high synchronous and should reset the output to zero.
    </input_spec>
    <interface>
        module TopModule #(
            parameter nbits
        )(
            input  logic             clk,
            input  logic             reset,
            input  logic [nbits-1:0] in_,
            output logic [nbits-1:0] out
        );
    </interface>
    <testbench>
        `timescale 1ns/1ps

        module TopModule_tb();

            // Parameters
            parameter nbits = 8;
            parameter CLK_PERIOD = 10;

            // Signals declaration
            logic             clk;
            logic             reset;
            logic [nbits-1:0] in_;
            logic [nbits-1:0] out;
            logic [nbits-1:0] expected_out;

            // Counter for mismatches
            int mismatch_count;

            // DUT instantiation
            TopModule #(
                .nbits(nbits)
            ) dut (
                .clk(clk),
                .reset(reset),
                .in_(in_),
                .out(out)
            );

            // Clock generation
            initial begin
                clk = 0;
                forever #(CLK_PERIOD/2) clk = ~clk;
            end

            // Test stimulus
            initial begin
                // Initialize signals
                reset = 1;
                in_ = 0;
                mismatch_count = 0;
                expected_out = 0;

                // Wait for 2 clock cycles in reset
                repeat(2) @(posedge clk);

                // Release reset
                reset = 0;

                // Test case 1: Regular increment
                for(int i = 0; i < 10; i++) begin
                    in_ = $random;
                    @(posedge clk);
                    expected_out = in_;
                    @(negedge clk);
                    check_output();
                    @(posedge clk);
                    expected_out = expected_out + 1;
                    @(negedge clk);
                    check_output();
                end

                // Test case 2: Reset during operation
                in_ = 8'hAA;
                @(posedge clk);
                reset = 1;
                @(posedge clk);
                expected_out = 0;
                @(negedge clk);
                check_output();

                // Test case 3: Overflow condition
                reset = 0;
                in_ = {nbits{1'b1}};  // All ones
                @(posedge clk);
                @(posedge clk);
                expected_out = 0;
                @(negedge clk);
                check_output();

                // End simulation
                #(CLK_PERIOD);
                if(mismatch_count == 0)
                    $display("SIMULATION PASSED");
                else
                    $display("SIMULATION FAILED with %0d mismatches", mismatch_count);

                $finish;
            end

            // Task to check output and log mismatches
            task check_output();
                if (out !== expected_out) begin
                    $display("Time %0t: Mismatch detected!", $time);
                    $display("Input = %h, Expected output = %h, Actual output = %h",
                            in_, expected_out, out);
                    mismatch_count++;
                end else begin
                    $display("Time %0t: Match detected!", $time);
                    $display("Input = %h, Output = %h", in_, out);
                end
            endtask

        endmodule
    </testbench>
</example>
Example 4:
<example>
    <input_spec>
        Implement the SystemVerilog module based on the following description.
        Assume that sigals are positive clock/clk triggered unless otherwise stated.

        Build a finite-state machine that takes as input a serial bit stream,
            and outputs a one whenever the bit stream contains two consecutive one's.
        The output is one on the cycle _after_ there are two consecutive one's.
        The reset input is active high synchronous,
            and should reset the finite-state machine to an appropriate initial state.
    </input_spec>
    <interface>
        module TopModule(
            input  logic clk,
            input  logic reset,
            input  logic in_,
            output logic out
        );
    </interface>
    <testbench>
        module TopModule_tb();
            // Signal declarations
            logic clk;
            logic reset;
            logic in_;
            logic out;
            logic expected_out;
            int mismatch_count;

            // Instantiate the DUT
            TopModule dut(
                .clk(clk),
                .reset(reset),
                .in_(in_),
                .out(out)
            );

            // Clock generation
            initial begin
                clk = 0;
                forever #5 clk = ~clk;
            end

            // Test stimulus and checking
            initial begin
                // Initialize signals
                reset = 1;
                in_ = 0;
                mismatch_count = 0;
                expected_out = 0;

                // Wait for 2 clock cycles and release reset
                @(posedge clk);
                @(posedge clk);
                reset = 0;

                // Test case 1: No consecutive ones
                @(posedge clk); in_ = 0; expected_out = 0;
                @(posedge clk); in_ = 1; expected_out = 0;
                @(posedge clk); in_ = 0; expected_out = 0;
                @(posedge clk); in_ = 1; expected_out = 0;

                // Test case 2: Two consecutive ones
                @(posedge clk); in_ = 1; expected_out = 0;
                @(posedge clk); in_ = 1; expected_out = 0;
                @(posedge clk); in_ = 0; expected_out = 1;
                @(posedge clk); in_ = 0; expected_out = 0;

                // Test case 3: Three consecutive ones
                @(posedge clk); in_ = 1; expected_out = 0;
                @(posedge clk); in_ = 1; expected_out = 0;
                @(posedge clk); in_ = 1; expected_out = 1;
                @(posedge clk); in_ = 0; expected_out = 1;

                // Test case 4: Reset during operation
                @(posedge clk); in_ = 1; expected_out = 0;
                @(posedge clk); in_ = 1; expected_out = 0;
                @(posedge clk); reset = 1; in_ = 0; expected_out = 0;
                @(posedge clk); reset = 0; in_ = 0; expected_out = 0;

                // End simulation
                #20 $finish;
            end

            // Monitor changes and check outputs
            always @(negedge clk) begin
                if (out !== expected_out) begin
                    $display("Mismatch at time %0t: input=%b, actual_output=%b, expected_output=%b",
                            $time, in_, out, expected_out);
                    mismatch_count++;
                end else begin
                    $display("Match at time %0t: input=%b, output=%b",
                            $time, in_, out);
                end
            end

            // Final check and display results
            final begin
                if (mismatch_count == 0)
                    $display("SIMULATION PASSED");
                else
                    $display("SIMULATION FAILED: %0d mismatches found", mismatch_count);
            end

        endmodule
    </testbench>
</example>
"""

FAILED_TRIAL_PROMPT = r"""
There was a generation trial that failed simulation:
<failed_sim_log>
{failed_sim_log}
</failed_sim_log>
<previous_code>
{previous_code}
</previous_code>
<previous_tb>
{previous_tb}
</previous_tb>
"""

ORDER_PROMPT = r"""
Your response will be processed by a program, not human.
So, please STRICTLY FOLLOW the output format given as XML tag content below to generate a VALID JSON OBJECT:
<output_format>
{output_format}
</output_format>
DO NOT include any other information in your response, like 'json', 'reasoning' or '<output_format>'.
"""
