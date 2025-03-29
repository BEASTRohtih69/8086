#!/usr/bin/env python3
"""
8086 Simulator - Sample Program Runner
This script loads and runs an assembly program file in the 8086 simulator,
showing register and memory state before and after execution.
"""

import sys
import os
from cpu import CPU
from memory import Memory
from assembler import Assembler
from instructions import InstructionSet
from profiler import create_profiler
from fix_instructions import fix_segment_handling

def print_memory(memory, start, length, label):
    """Print a section of memory in a hex dump format"""
    print(f"\n--- {label} ---")
    
    # Calculate how many full rows of 16 bytes we'll print
    rows = length // 16
    if length % 16 > 0:
        rows += 1
    
    for row in range(rows):
        row_addr = start + row * 16
        # Print the address at the start of the row
        print(f"{row_addr:04X}: ", end="")
        
        # Print the hex values
        for col in range(16):
            if row * 16 + col < length:
                addr = start + row * 16 + col
                value = memory.read_byte(addr)
                print(f"{value:02X} ", end="")
            else:
                print("   ", end="")
                
        # Print printable ASCII characters
        print(" |", end="")
        for col in range(16):
            if row * 16 + col < length:
                addr = start + row * 16 + col
                value = memory.read_byte(addr)
                if 32 <= value <= 126:  # Printable ASCII range
                    print(chr(value), end="")
                else:
                    print(".", end="")
            else:
                print(" ", end="")
        print("|")

def print_registers(cpu):
    """Print the values of all CPU registers"""
    print("\n--- Register State ---")
    state = cpu.get_register_state()
    for name, value in state.items():
        print(f"{name}: {value:04X}", end="  ")
        if name in ["AX", "BX", "CX", "DX"]:
            # For general registers, show high and low bytes
            high = cpu.get_register_high_byte(getattr(cpu, name))
            low = cpu.get_register_low_byte(getattr(cpu, name))
            print(f"({name[0]}H: {high:02X}, {name[0]}L: {low:02X})", end="")
        print()

    print("\n--- Flags ---")
    flags = cpu.get_flag_state()
    flag_list = []
    for name, value in flags.items():
        if value:
            flag_list.append(name)
    
    print("Set flags: " + ", ".join(flag_list) if flag_list else "No flags set")

def main():
    """Main entry point for the simulator"""
    if len(sys.argv) < 2:
        print("Usage: python run_sample.py <program.asm> [max_instructions]")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Check if the file exists
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    
    # Parse max_instructions if provided
    max_instructions = None
    if len(sys.argv) > 2:
        try:
            max_instructions = int(sys.argv[2])
        except ValueError:
            print(f"Error: Invalid number of instructions '{sys.argv[2]}'")
            sys.exit(1)
    
    print(f"Running {filename} with 8086 simulator...")
    
    # Initialize components
    memory = Memory()
    cpu = CPU(memory)
    instruction_set = InstructionSet(cpu)
    cpu.instruction_set = instruction_set
    assembler = Assembler(cpu, memory)
    
    # Try to use enhanced segment handling if available
    try:
        fix_segment_handling(assembler, filename)
        print("Using enhanced segment handling")
    except Exception as e:
        # Fall back to basic handling
        print(f"Using basic program loading (error with enhanced: {str(e)})")
        try:
            assembler.load_program(filename)
        except Exception as e2:
            print(f"Error loading program: {str(e2)}")
            sys.exit(1)
    
    # Show initial state
    print_registers(cpu)
    
    # Show memory sections
    code_start = 0x100  # CODE segment physical address
    code_size = 256
    data_start = 0x200  # DATA segment physical address
    data_size = 256
    stack_start = 0x300  # STACK segment physical address
    stack_size = 256
    
    print_memory(memory, code_start, code_size, "CODE Memory Before Execution")
    print_memory(memory, data_start, data_size, "DATA Memory Before Execution")
    
    # Set up profiler if available
    profiler = None
    try:
        profiler = create_profiler(cpu, memory)
        cpu.set_profiler(profiler)
        memory.set_profiler(profiler)
        profiler.start_profiling()
        print("Performance profiling enabled")
    except:
        print("Performance profiling not available")
    
    # Run the program
    print("\n--- Executing Program ---")
    instruction_count = cpu.run(max_instructions=max_instructions)
    print(f"Executed {instruction_count} instructions")
    if cpu.halted:
        print("Program halted normally (HLT instruction)")
    elif max_instructions and instruction_count >= max_instructions:
        print(f"Reached maximum instructions limit ({max_instructions})")
    else:
        print("Program stopped due to an error")
    
    # Show final state
    print_registers(cpu)
    print_memory(memory, code_start, code_size, "CODE Memory After Execution")
    print_memory(memory, data_start, data_size, "DATA Memory After Execution")
    print_memory(memory, stack_start, stack_size, "STACK Memory After Execution")
    
    # Show profiler results if available
    if profiler:
        print("\n--- Profiler Results ---")
        profiler.stop_profiling()
        summary = profiler.generate_summary_report()
        print(summary)

if __name__ == "__main__":
    main()