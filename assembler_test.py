#!/usr/bin/env python3
"""
Test for the assembler's handling of LOOP instructions and labels.
This script tests how the assembler processes loop_test_fixed.asm.
"""

import os
import sys
from cpu import CPU
from memory import Memory
from assembler import Assembler

def main():
    print("8086 Simulator - Assembler Test for LOOP Instructions")
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
            for i, line in enumerate(f):
                print(f"{i+1:02d}: {line.rstrip()}")
        
        # Reset the assembler state before loading
        assembler.current_address = 0x0100  # Base address for code
        assembler.labels = {}
        
        # First pass: just collect labels
        print("\nFirst pass: collecting labels")
        with open(test_program, 'r') as f:
            address = 0x0100
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith(';'):
                    continue
                
                # Check for label definitions
                if ':' in line:
                    label, rest = line.split(':', 1)
                    label = label.strip()
                    assembler.labels[label] = address
                    print(f"Label {label} defined at 0x{address:04X}")
                    line = rest.strip()
                    if not line:
                        continue
                
                # Estimate instruction size
                instr_size = assembler._get_instruction_size(line)
                address += instr_size
        
        # Reset for second pass
        assembler.current_address = 0x0100
        
        # Second pass: assemble instructions
        print("\nSecond pass: assembling instructions")
        with open(test_program, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith(';'):
                    continue
                
                # Remove label from line
                if ':' in line:
                    label, line = line.split(':', 1)
                    line = line.strip()
                    if not line:
                        continue
                
                # Assemble the instruction and print debug info
                try:
                    machine_code = assembler._assemble_instruction(line)
                    hex_code = ' '.join([f"{b:02X}" for b in machine_code])
                    print(f"0x{assembler.current_address:04X}: {line:<25} -> {hex_code}")
                    
                    # Load into memory
                    for i, byte in enumerate(machine_code):
                        memory.write_byte(assembler.current_address + i, byte)
                    
                    # Update address
                    assembler.current_address += len(machine_code)
                except Exception as e:
                    print(f"Error at line {line_num}: {e}")
                    print(f"  Line: {line}")
                    continue
        
        print("\nFinal labels:")
        for label, address in assembler.labels.items():
            print(f"{label}: 0x{address:04X}")
        
        # Reset IP to start of program
        cpu.set_register(cpu.IP, 0)
        
        # Execute the program
        print("\nExecuting program...")
        instruction_count = 0
        while not cpu.halted and instruction_count < 30:  # Safety limit
            instruction_count += 1
            
            ip = cpu.get_register(cpu.IP)
            phys_addr = cpu.get_physical_address(cpu.get_register(cpu.CS), ip)
            
            print(f"\nInstruction {instruction_count} at IP=0x{ip:04X}, Physical=0x{phys_addr:04X}:")
            cpu.execute_instruction()
            
            print(f"Registers: AX=0x{cpu.get_register(cpu.AX):04X}, "
                  f"BX=0x{cpu.get_register(cpu.BX):04X}, "
                  f"CX=0x{cpu.get_register(cpu.CX):04X}, "
                  f"DX=0x{cpu.get_register(cpu.DX):04X}")
        
        print(f"\nProgram {'halted normally' if cpu.halted else 'did not halt (max instructions reached)'}.")
        print(f"\nFinal register state (after {instruction_count} instructions):")
        print(f"AX=0x{cpu.get_register(cpu.AX):04X}, "
              f"BX=0x{cpu.get_register(cpu.BX):04X}, "
              f"CX=0x{cpu.get_register(cpu.CX):04X}, "
              f"DX=0x{cpu.get_register(cpu.DX):04X}")
    
    except Exception as e:
        print(f"Error during assembly or execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()