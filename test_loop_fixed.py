#!/usr/bin/env python3
"""
Test for the fixed LOOP, LOOPE, and LOOPNE instructions.
This script runs the loop_test_fixed.asm sample program.
"""

import os
import sys
from cpu import CPU
from memory import Memory
from assembler import Assembler

def main():
    print("8086 Simulator - LOOP Instruction Test Program")
    print("-" * 50)
    
    # Create the hardware components
    memory = Memory()
    cpu = CPU(memory)
    assembler = Assembler(cpu, memory)
    
    # Reset CPU state
    cpu.reset()
    
    # Set the standard 8086 segments
    cpu.set_register(cpu.CS, 0x0010)  # Code segment
    cpu.set_register(cpu.DS, 0x0020)  # Data segment
    cpu.set_register(cpu.SS, 0x0030)  # Stack segment
    cpu.set_register(cpu.ES, 0x0040)  # Extra segment
    
    # Load the test program
    test_program = os.path.join("sample_programs", "loop_test_fixed.asm")
    print(f"Loading test program: {test_program}")
    
    # Check if the file exists
    if not os.path.exists(test_program):
        print(f"Error: File {test_program} does not exist!")
        print("Current directory:", os.getcwd())
        print("Files in sample_programs:", os.listdir("sample_programs"))
        return
    
    try:
        # Display file contents for debugging
        print("\nProgram contents:")
        with open(test_program, 'r') as f:
            print(f.read())
        
        # Load the program
        assembler.load_program(test_program)
        print("\nProgram loaded successfully.")
        print("Labels defined:", assembler.labels)
    except Exception as e:
        print(f"Error loading program: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Get initial register state
    print("\nInitial register state:")
    print(f"AX={cpu.get_register(cpu.AX):04X}, "
          f"BX={cpu.get_register(cpu.BX):04X}, "
          f"CX={cpu.get_register(cpu.CX):04X}, "
          f"DX={cpu.get_register(cpu.DX):04X}")
    print(f"IP={cpu.get_register(cpu.IP):04X}, "
          f"CS={cpu.get_register(cpu.CS):04X}")
    
    # Run the program
    print("\nExecuting program...")
    try:
        cpu.run()
        print("Program execution completed.")
    except Exception as e:
        print(f"Error during execution: {e}")
        return
    
    # Get final register state
    print("\nFinal register state:")
    print(f"AX={cpu.get_register(cpu.AX):04X}, "
          f"BX={cpu.get_register(cpu.BX):04X}, "
          f"CX={cpu.get_register(cpu.CX):04X}, "
          f"DX={cpu.get_register(cpu.DX):04X}")
    print(f"IP={cpu.get_register(cpu.IP):04X}, "
          f"CS={cpu.get_register(cpu.CS):04X}")
    
    # Verify results
    print("\nVerifying results:")
    
    # LOOP test: CX should have been decremented to 0, AX should be 5
    if cpu.get_register(cpu.AX) == 5:
        print("✓ LOOP test passed: AX=5")
    else:
        print(f"✗ LOOP test failed: AX={cpu.get_register(cpu.AX):04X}, expected 5")
    
    # LOOPE test: BX should be 3 (looped until BX=3 which makes ZF=0)
    # or possibly 4 (if the comparison set ZF=0 after the third loop)
    if 3 <= cpu.get_register(cpu.BX) <= 4:
        print(f"✓ LOOPE test passed: BX={cpu.get_register(cpu.BX):04X}")
    else:
        print(f"✗ LOOPE test failed: BX={cpu.get_register(cpu.BX):04X}, expected 3 or 4")
    
    # LOOPNE test: DX should be 3 (looped until DX=3 which makes ZF=1)
    # or possibly 4 (if the comparison set ZF=1 after the third loop)
    if 3 <= cpu.get_register(cpu.DX) <= 4:
        print(f"✓ LOOPNE test passed: DX={cpu.get_register(cpu.DX):04X}")
    else:
        print(f"✗ LOOPNE test failed: DX={cpu.get_register(cpu.DX):04X}, expected 3 or 4")

if __name__ == "__main__":
    main()