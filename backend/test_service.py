import os
import dotenv
from services.gemini_service import GeminiService

def main():
    print("Testing GeminiService initialization...")
    service = GeminiService()
    print(f"Using Model: {service.model}")
    
    print("\n1. Testing Connection...")
    conn_result = service.test_connection()
    print(f"Connection test result: {conn_result}")
    
    print("\n2. Testing RTL Generation...")
    prompt = "Create a simple 4-bit synchronous binary counter in Verilog with reset and enable inputs."
    code = service.generate_rtl(prompt)
    print("Generated RTL Code Output:")
    print("----------------------------------------")
    print(code)
    print("----------------------------------------")

if __name__ == "__main__":
    main()
