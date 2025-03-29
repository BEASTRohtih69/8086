#!/usr/bin/env python3
"""
Test runner for the 8086 simulator
"""

from cpu import CPU
from memory import Memory
from assembler import Assembler
import sys
import os

def main():
    """Simple test runner for the simulator"""
    if len(sys.argv) < 2:
        print("Usage: python test_runner.py <assembly_file>")
        sys.exit(1)
        
    program_file = sys.argv[1]
    
    if not os.path.exists(program_file):
        print(f"File not found: {program_file}")
        sys.exit(1)
    
    memory = Memory()
    cpu = CPU(memory)
    assembler = Assembler(cpu, memory)
    
    try:
        assembler.load_program(program_file)
        print(f"Program '{program_file}' loaded successfully.")
        
        # CS register already set by the assembler to the appropriate segment
        
        # Print initial CPU state
        print("\nInitial CPU state:")
        for reg_name, reg_id in [("AX", cpu.AX), ("BX", cpu.BX), ("CX", cpu.CX), ("DX", cpu.DX), 
                                ("SP", cpu.SP), ("BP", cpu.BP), ("SI", cpu.SI), ("DI", cpu.DI),
                                ("CS", cpu.CS), ("DS", cpu.DS), ("SS", cpu.SS), ("ES", cpu.ES),
                                ("IP", cpu.IP)]:
            print(f"{reg_name}: {cpu.get_register(reg_id):04X}", end=" ")
        
        print("\nRunning program...")
        instruction_count = 0
        max_instructions = 100  # Limit to prevent infinite loops
        
        while instruction_count < max_instructions:
            # Print current instruction pointer and the next instruction
            cs = cpu.get_register(cpu.CS)
            ip = cpu.get_register(cpu.IP)
            print(f"CS:{cs:04X} IP:{ip:04X} ", end="")
            
            # Execute the instruction
            halted = cpu.execute_instruction()
            instruction_count += 1
            
            # Print register state
            print("AX:{:04X} BX:{:04X} CX:{:04X} DX:{:04X} ".format(
                cpu.get_register(cpu.AX),
                cpu.get_register(cpu.BX),
                cpu.get_register(cpu.CX),
                cpu.get_register(cpu.DX)
            ), end="")
            
            print("Flags: ", end="")
            flag_bits = {
                "CF": cpu.CARRY_FLAG,
                "ZF": cpu.ZERO_FLAG,
                "SF": cpu.SIGN_FLAG,
                "OF": cpu.OVERFLOW_FLAG
            }
            for flag_name, flag_bit in flag_bits.items():
                print(f"{flag_name}:{cpu.get_flag(flag_bit)} ", end="")
            print()
            
            if halted:
                print("Program halted.")
                break
        
        if instruction_count >= max_instructions:
            print("Maximum instruction count reached.")
        
        # Dump some memory
        print("\nMemory dump (first 64 bytes):")
        for i in range(0, 64, 16):
            line = f"{i:04X}: "
            for j in range(16):
                line += f"{memory.read_byte(i+j):02X} "
            print(line)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()