#!/usr/bin/env python3
"""
Simplified LOOP instruction test.
This script uses the same approach as quick_loop_test.py but runs our fixed LOOP implementation.
"""

from memory import Memory
from cpu import CPU
from instructions import InstructionSet

def main():
    print("8086 Simulator - Simple LOOP Test")
    print("-" * 40)
    
    # Create the hardware components
    memory = Memory()
    cpu = CPU(memory)
    
    # Reset CPU state
    cpu.reset()
    
    # Set the code segment
    cpu.set_register(cpu.CS, 0x0010)  # Code segment
    
    # Load the test program into memory
    # Simple program that uses LOOP to count to 5
    #
    # MOV CX, 5    ; B9 05 00
    # MOV AX, 0    ; B8 00 00
    # label:        
    # INC AX       ; 40
    # LOOP label   ; E2 FD (-3)
    # HLT          ; F4
    
    program = [
        0xB9, 0x05, 0x00,  # MOV CX, 5
        0xB8, 0x00, 0x00,  # MOV AX, 0
        0x40,              # INC AX
        0xE2, 0xFD,        # LOOP -3 (back to INC AX)
        0xF4               # HLT
    ]
    
    # Load program into memory at physical address 0x100 (CS=0x10 << 4)
    for i, byte in enumerate(program):
        memory.write_byte(0x100 + i, byte)
    
    print("Program loaded, starting execution...")
    
    # Execute the program
    instruction_count = 0
    max_instructions = 20  # Safeguard against infinite loops
    
    while not cpu.halted and instruction_count < max_instructions:
        print(f"\nInstruction {instruction_count + 1}:")
        print(f"IP: {cpu.get_register(cpu.IP):04X}, CX: {cpu.get_register(cpu.CX):04X}, AX: {cpu.get_register(cpu.AX):04X}")
        cpu.execute_instruction()
        instruction_count += 1
    
    # Check results
    if cpu.halted:
        print("\nProgram halted successfully.")
    else:
        print("\nProgram did not halt within instruction limit.")
    
    print(f"Final values: AX={cpu.get_register(cpu.AX):04X}, CX={cpu.get_register(cpu.CX):04X}")
    
    # Verify that LOOP worked correctly
    if cpu.get_register(cpu.AX) == 5 and cpu.get_register(cpu.CX) == 0:
        print("✓ LOOP test PASSED - AX is 5 and CX is 0")
    else:
        print(f"✗ LOOP test FAILED - Expected AX=5, CX=0, got AX={cpu.get_register(cpu.AX)}, CX={cpu.get_register(cpu.CX)}")

if __name__ == "__main__":
    main()