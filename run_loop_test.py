#!/usr/bin/env python3
"""
Run the loop test program with enhanced debugging
"""

import os
import sys
from cpu import CPU
from memory import Memory
from assembler import Assembler
from ui import UI
import time

def main():
    """Run the loop test program with enhanced debugging"""
    print(f"Running loop test program with enhanced debugging...")
    
    # Initialize simulator components
    memory = Memory()
    cpu = CPU(memory)
    assembler = Assembler(cpu, memory)
    ui = UI(cpu, memory)
    
    # Set up CPU for debugging
    cpu.reset()
    
    # Initialize segment registers for correct addressing
    cpu.set_register(cpu.CS, 0x0010)  # Code segment at 0x0100
    cpu.set_register(cpu.DS, 0x0020)  # Data segment at 0x0200
    cpu.set_register(cpu.SS, 0x0030)  # Stack segment at 0x0300
    cpu.set_register(cpu.ES, 0x0040)  # Extra segment at 0x0400
    
    # Set IP to 0 (will be relative to CS)
    cpu.set_register(cpu.IP, 0)
    
    # Get the program filename or use the default
    filename = 'sample_programs/loop_test.asm'
    
    try:
        # Try the improved segment handling if available
        try:
            from fix_instructions import fix_segment_handling
            print(f"Using improved segment handling for '{filename}'")
            fix_segment_handling(assembler, filename)
            print(f"Program '{filename}' loaded successfully with fixed segment handling.")
        except ImportError:
            # Fall back to standard loading
            print(f"Using standard loader for '{filename}'")
            assembler.load_program(filename)
            print(f"Program '{filename}' loaded successfully.")
            
        # Display initial CPU state
        print("\nInitial CPU state:")
        print(f"CS:IP = {cpu.get_register(cpu.CS):04X}:{cpu.get_register(cpu.IP):04X}")
        print(f"AX = {cpu.get_register(cpu.AX):04X}, CX = {cpu.get_register(cpu.CX):04X}")
        print(f"ZF = {cpu.get_flag(cpu.ZERO_FLAG)}")
        
        print("\nStarting program execution...")
        print("-" * 60)
        
        # Execute each instruction with detailed tracing
        max_instructions = 30  # Safety limit to prevent infinite loops
        instruction_count = 0
        
        while not cpu.halted and instruction_count < max_instructions:
            # Display current IP before execution
            current_ip = cpu.get_register(cpu.IP)
            current_cs = cpu.get_register(cpu.CS)
            phys_addr = cpu.get_physical_address(current_cs, current_ip)
            
            # Execute the instruction
            cpu.execute_instruction()
            instruction_count += 1
            
            # Add a short delay for easier observation
            time.sleep(0.1)
        
        print("-" * 60)
        # Display final CPU state
        print("\nFinal CPU state after execution:")
        print(f"CS:IP = {cpu.get_register(cpu.CS):04X}:{cpu.get_register(cpu.IP):04X}")
        print(f"AX = {cpu.get_register(cpu.AX):04X}, CX = {cpu.get_register(cpu.CX):04X}")
        print(f"ZF = {cpu.get_flag(cpu.ZERO_FLAG)}")
        print(f"Instruction count: {instruction_count}")
        
        if cpu.halted:
            print("CPU halted successfully.")
        else:
            print("Warning: Maximum instruction limit reached without CPU halt.")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()