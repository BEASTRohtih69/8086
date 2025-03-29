#!/usr/bin/env python3
"""
Direct program execution test for 8086 simulator.
This script directly loads machine code into memory and executes it,
bypassing the assembler to verify the instruction set implementation.
"""

import sys
import os

# Add parent directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cpu import CPU
from memory import Memory
from instructions import InstructionSet

def main():
    """Load and run a simple program directly in memory"""
    # Initialize components
    memory = Memory()
    cpu = CPU(memory)
    instruction_set = InstructionSet(cpu)
    cpu.instruction_set = instruction_set
    
    # Program: Simple register operations and arithmetic
    # mov ax, 1234h
    # mov bx, 5678h
    # add ax, bx
    # mov cx, ax
    # hlt
    program = [
        0xB8, 0x34, 0x12,  # mov ax, 1234h
        0xBB, 0x78, 0x56,  # mov bx, 5678h
        0x01, 0xD8,        # add ax, bx (ax = 68ACh)
        0x89, 0xC1,        # mov cx, ax
        0xF4              # hlt
    ]
    
    # Get the physical address for CS:IP
    code_addr = cpu.get_physical_address(cpu.get_register(cpu.CS), cpu.get_register(cpu.IP))
    print(f"Loading program at physical address: 0x{code_addr:04X}")
    
    # Load the program into memory
    memory.load_bytes(code_addr, program)
    
    # Show initial state
    print("Initial state:")
    print(f"AX: 0x{cpu.get_register(cpu.AX):04X}")
    print(f"BX: 0x{cpu.get_register(cpu.BX):04X}")
    print(f"CX: 0x{cpu.get_register(cpu.CX):04X}")
    print(f"IP: 0x{cpu.get_register(cpu.IP):04X}")
    
    # Run the program
    print("\nExecuting program...")
    instructions_executed = 0
    while not cpu.halted and instructions_executed < 10:  # Limit to avoid infinite loops
        if not cpu.execute_instruction():
            print("Error executing instruction")
            break
        instructions_executed += 1
        
        # Show state after each instruction
        print(f"After instruction {instructions_executed}:")
        print(f"AX: 0x{cpu.get_register(cpu.AX):04X}")
        print(f"BX: 0x{cpu.get_register(cpu.BX):04X}")
        print(f"CX: 0x{cpu.get_register(cpu.CX):04X}")
        print(f"IP: 0x{cpu.get_register(cpu.IP):04X}")
        print(f"CS:IP = 0x{cpu.get_register(cpu.CS):04X}:0x{cpu.get_register(cpu.IP):04X}")
        print(f"Halted: {cpu.halted}")
        print("---")
    
    # Show final state
    print("\nFinal state:")
    print(f"AX: 0x{cpu.get_register(cpu.AX):04X}")
    print(f"BX: 0x{cpu.get_register(cpu.BX):04X}")
    print(f"CX: 0x{cpu.get_register(cpu.CX):04X}")
    print(f"IP: 0x{cpu.get_register(cpu.IP):04X}")
    print(f"Halted: {cpu.halted}")
    print(f"Instructions executed: {instructions_executed}")

if __name__ == "__main__":
    main()