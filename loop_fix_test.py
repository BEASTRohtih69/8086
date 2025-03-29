#!/usr/bin/env python3
"""
Comprehensive test for the LOOP instruction fix.
Tests the fixed LOOP, LOOPE, and LOOPNE instructions.
"""

from memory import Memory
from cpu import CPU
from instructions import InstructionSet

def main():
    print("8086 Simulator - LOOP Instruction Fix Test")
    print("-" * 50)
    
    # Create the hardware components
    memory = Memory()
    cpu = CPU(memory)
    
    # Reset CPU state
    cpu.reset()
    
    # Set the standard 8086 segments
    cpu.set_register(cpu.CS, 0x0010)  # Code segment
    cpu.set_register(cpu.DS, 0x0020)  # Data segment
    cpu.set_register(cpu.SS, 0x0030)  # Stack segment
    cpu.set_register(cpu.ES, 0x0040)  # Extra segment
    
    # Physical address for code segment (CS << 4 = 0x0100)
    BASE_ADDR = 0x0100
    
    # Test 1: LOOP instruction
    print("\n--- Test 1: LOOP Instruction ---")
    
    # Set initial state
    cpu.reset()
    cpu.set_register(cpu.CS, 0x0010)
    cpu.set_register(cpu.IP, 0)
    
    # Create a simple program with LOOP
    program_loop = [
        0xB9, 0x05, 0x00,  # MOV CX, 5
        0xB8, 0x00, 0x00,  # MOV AX, 0
        0x40,              # INC AX
        0xE2, 0xFD,        # LOOP -3 (back to INC AX)
        0xF4               # HLT
    ]
    
    # Load program into memory
    for i, byte in enumerate(program_loop):
        memory.write_byte(BASE_ADDR + i, byte)
    
    print("Program loaded, starting execution...")
    
    # Run the program
    instruction_count = 0
    while not cpu.halted and instruction_count < 20:
        instruction_count += 1
        cpu.execute_instruction()
    
    print(f"Program completed after {instruction_count} instructions")
    print(f"Results: AX={cpu.get_register(cpu.AX):04X}, CX={cpu.get_register(cpu.CX):04X}")
    
    # Verify results
    if cpu.get_register(cpu.AX) == 5 and cpu.get_register(cpu.CX) == 0:
        print("✓ LOOP test PASSED")
    else:
        print(f"✗ LOOP test FAILED: Expected AX=5, CX=0, got AX={cpu.get_register(cpu.AX)}, CX={cpu.get_register(cpu.CX)}")
    
    # Test 2: LOOPE instruction
    print("\n--- Test 2: LOOPE Instruction ---")
    
    # Set initial state
    cpu.reset()
    cpu.set_register(cpu.CS, 0x0010)
    cpu.set_register(cpu.IP, 0)
    
    # Create a simple program with LOOPE
    program_loope = [
        0xB9, 0x05, 0x00,  # MOV CX, 5
        0xBB, 0x00, 0x00,  # MOV BX, 0
        0xB8, 0x00, 0x00,  # MOV AX, 0  - for comparison, always 0
        # Loop body
        0x43,              # INC BX
        0x3B, 0xC3,        # CMP AX, BX (AX=0, BX increases, so ZF=0 after first iteration)
        0xE1, 0xFB,        # LOOPE -5 (back to INC BX) - loop while equal and CX != 0
        0xF4               # HLT
    ]
    
    # Load program into memory
    for i, byte in enumerate(program_loope):
        memory.write_byte(BASE_ADDR + i, byte)
    
    print("Program loaded, starting execution...")
    
    # Run the program
    instruction_count = 0
    while not cpu.halted and instruction_count < 20:
        instruction_count += 1
        cpu.execute_instruction()
    
    print(f"Program completed after {instruction_count} instructions")
    print(f"Results: BX={cpu.get_register(cpu.BX):04X}, CX={cpu.get_register(cpu.CX):04X}, ZF={cpu.get_flag(cpu.ZERO_FLAG)}")
    
    # Verify results - BX should be 3 or 4 depending on when ZF became 0
    if 3 <= cpu.get_register(cpu.BX) <= 4 and cpu.get_register(cpu.CX) < 5:
        print("✓ LOOPE test PASSED")
    else:
        print(f"✗ LOOPE test FAILED: Expected BX=3 or 4, CX<5, got BX={cpu.get_register(cpu.BX)}, CX={cpu.get_register(cpu.CX)}")
    
    # Test 3: LOOPNE instruction
    print("\n--- Test 3: LOOPNE Instruction ---")
    
    # Set initial state
    cpu.reset()
    cpu.set_register(cpu.CS, 0x0010)
    cpu.set_register(cpu.IP, 0)
    
    # Create a simple program with LOOPNE
    program_loopne = [
        0xB9, 0x05, 0x00,  # MOV CX, 5
        0xBA, 0x00, 0x00,  # MOV DX, 0
        0xBF, 0x03, 0x00,  # MOV DI, 3  - for comparison
        # Loop body
        0x42,              # INC DX
        0x3B, 0xD7,        # CMP DX, DI (DI is 3, so DX != DI until DX reaches 3)
        0xE0, 0xFA,        # LOOPNE -6 (back to INC DX) - loop while not equal and CX != 0
        0xF4               # HLT
    ]
    
    # Load program into memory
    for i, byte in enumerate(program_loopne):
        memory.write_byte(BASE_ADDR + i, byte)
    
    print("Program loaded, starting execution...")
    
    # Run the program
    instruction_count = 0
    while not cpu.halted and instruction_count < 20:
        instruction_count += 1
        cpu.execute_instruction()
    
    print(f"Program completed after {instruction_count} instructions")
    print(f"Results: DX={cpu.get_register(cpu.DX):04X}, CX={cpu.get_register(cpu.CX):04X}, ZF={cpu.get_flag(cpu.ZERO_FLAG)}")
    
    # Verify results - DX should be 3 and ZF should be 1 (indicating equality)
    if cpu.get_register(cpu.DX) == 3 and cpu.get_flag(cpu.ZERO_FLAG) == 1:
        print("✓ LOOPNE test PASSED")
    else:
        print(f"✗ LOOPNE test FAILED: Expected DX=3, ZF=1, got DX={cpu.get_register(cpu.DX)}, ZF={cpu.get_flag(cpu.ZERO_FLAG)}")
    
    # Print overall results
    print("\n--- Overall Results ---")
    if (cpu.get_register(cpu.AX) == 5 and  # LOOP test
        3 <= cpu.get_register(cpu.BX) <= 4 and  # LOOPE test
        cpu.get_register(cpu.DX) == 3):  # LOOPNE test
        print("✓ All LOOP instruction tests PASSED")
    else:
        print("✗ Some tests FAILED. Check individual results.")

if __name__ == "__main__":
    main()