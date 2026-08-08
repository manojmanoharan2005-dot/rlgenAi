import time
from typing import List, Tuple
from pyverilog.vparser.parser import VerilogParser
from pyverilog.vparser.ast import ModuleDef
from core.logging import logger

class RTLValidator:
    def __init__(self):
        pass

    def validate(self, rtl_code: str) -> Tuple[bool, List[str]]:
        """
        Validates the Verilog RTL code syntax using PyVerilog.
        Checks for parser errors (missing endmodule, balanced begin/end, semicolons, etc.)
        and ensures at least one module is declared.
        Returns (is_valid, list_of_errors).
        """
        start_time = time.time()
        logger.info("Validation Started")
        
        errors = []
        is_valid = False
        
        if not rtl_code or not rtl_code.strip():
            logger.error("Validation Failed: Empty RTL")
            return False, ["Empty RTL code."]

        try:
            parser = VerilogParser()
            ast = parser.parse(rtl_code)
            
            # Additional semantic checks on the AST
            modules_found = 0
            module_names = set()
            
            if hasattr(ast, 'description') and ast.description:
                for definition in ast.description.definitions:
                    if isinstance(definition, ModuleDef):
                        modules_found += 1
                        if definition.name in module_names:
                            errors.append(f"Duplicate module name: {definition.name}")
                        module_names.add(definition.name)
            
            if modules_found == 0:
                errors.append("Missing module declaration.")
                
            is_valid = len(errors) == 0

        except Exception as e:
            # Catching generic parser failures
            error_str = str(e)
            if "LexToken" in error_str or "Parse error" in error_str:
                errors.append(f"Parser failure: Unexpected token encountered. Ensure balanced begin/end, balanced parentheses, and missing semicolons are resolved.")
            else:
                errors.append(f"Parser failure: {error_str}")
                
        process_time = time.time() - start_time
        
        if is_valid:
            logger.info(f"Validation Passed - Validation Time: {process_time:.4f}s")
        else:
            logger.info(f"Validation Failed - Validation Time: {process_time:.4f}s - Errors: {errors}")

        return is_valid, errors

rtl_validator = RTLValidator()
