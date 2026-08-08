def get_rtl_prompt(specification: str) -> str:
    """
    Returns a structured prompt for generating Verilog RTL based on the given specification.
    """
    return f"""You are an expert hardware designer.
Generate a clean, synthesizable Verilog module based on the following specification:

Specification:
{specification}

REQUIREMENTS:
- Return ONLY valid raw Verilog code. Do NOT wrap in markdown or backticks (no ```verilog).
- Do NOT include markdown text, explanations, or commentary before or after the code.
- Ensure ports match standard naming: clk (or clock), rst (or reset, rst_n if active low), count (or out/q).
- Ensure the module is complete, correct, and synthesizable.
"""

def get_testbench_prompt(rtl: str) -> str:
    return f"""You are a Senior RTL Verification Engineer.
Given the following Verilog RTL module:

{rtl}

Generate a complete, self-checking Verilog Testbench for this module.

REQUIREMENTS:
1. Module name must be `tb` or `top_tb`.
2. Do NOT use input/output ports on the testbench module itself.
3. Include clock generation using `always #5 clk = ~clk;` or initial clock toggle logic.
4. Verify reset behavior (sets output to 0).
5. Verify incrementing count sequence on every rising clock edge (e.g., 0 -> 1 -> 2 -> 3 -> 4).
6. Verify rollover behavior (e.g. max value 15 -> 0 for 4-bit counter).
7. Print step-by-step progress and verification status using `$display`.
   Example:
   $display("TEST PASSED: Counter reset verified successfully.");
   $display("TEST PASSED: Count sequence 0->1->2->3->4 verified.");
   $display("SIMULATION COMPLETE - ALL TESTS PASSED");
8. Include `$finish;` at the end of simulation.
9. Return ONLY raw Verilog code. Do NOT wrap in markdown (no ```verilog) and do NOT include any commentary.
"""
