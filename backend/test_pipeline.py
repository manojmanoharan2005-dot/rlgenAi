import sys
import os
import json

from config.settings import settings
from services.gemini_service import gemini_service
from services.compiler_service import compiler_service
from services.simulation_service import simulation_service
from services.testbench_service import testbench_service
from services.prompts import get_rtl_prompt
from services.rtl_validator import rtl_validator
from database import init_db, save_generation_record

print("=== STEP 1 & 2: EXECUTABLE PATH RESOLUTION ===")
iverilog_bin = compiler_service.get_compiler_bin()
vvp_bin = simulation_service.get_vvp_bin()

print(f"Icarus Verilog binary resolved: {iverilog_bin}")
print(f"VVP Simulator binary resolved: {vvp_bin}")

if not iverilog_bin or not vvp_bin:
    print("ERROR: Icarus Verilog executables not found!")
    sys.exit(1)

print("\n=== STEP 6: RTL GENERATION ===")
spec = "Design a 4-bit synchronous up counter.\nThe counter should increment by 1 on every rising edge of the clock and reset to 0 when reset is asserted."
prompt = get_rtl_prompt(spec)
print(f"Prompt sent to Gemini model ({settings.GEMINI_MODEL}):\n{prompt}")

rtl_code = gemini_service.generate_rtl(prompt)
print(f"\n--- GENERATED RTL ---\n{rtl_code}\n---------------------")

is_valid, val_errors = rtl_validator.validate(rtl_code)
print(f"RTL Validation result: valid={is_valid}, errors={val_errors}")

print("\n=== STEP 7 & 8: TESTBENCH GENERATION, COMPILATION & SIMULATION ===")
tb_result = testbench_service.generate_and_test(rtl_code)

print(f"Testbench Generated:\n{tb_result.get('testbench')}\n")
print(f"Compilation Status: {tb_result.get('compiled')}")
print(f"Simulation Passed: {tb_result.get('simulation_passed')}")
print(f"Logs:\n" + "\n".join(tb_result.get('logs', [])))

print("\n=== STEP 9: DATABASE PERSISTENCE ===")
init_db()
rec_id = save_generation_record(
    prompt=spec,
    rtl_code=rtl_code,
    testbench_code=tb_result.get('testbench'),
    compilation_status=tb_result.get('compiled', False),
    compilation_report=tb_result.get('compile_result', {}),
    simulation_status=tb_result.get('simulation_passed', False),
    simulation_report=tb_result.get('sim_result', {}),
    logs=tb_result.get('logs', [])
)
print(f"Record saved to PostgreSQL with ID: #{rec_id}")
