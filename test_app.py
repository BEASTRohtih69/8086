#!/usr/bin/env python3
"""
8086 Simulator - Simple Test Application
A minimal test program for the 8086 microprocessor simulator.
"""

from cpu import CPU
from memory import Memory
from assembler import Assembler
from instructions import InstructionSet

def main():
    """Main entry point for the test application"""
    # Initialize system components
    memory = Memory(1024*64)
    cpu = CPU(memory)
    
    # Initialize instruction set
    instruction_set = InstructionSet(cpu)
    cpu.instruction_set = instruction_set
    
    # Create minimal assembler
    assembler = Assembler(cpu, memory)
    
    # Hard-code a simple program directly into memory
    # mov al, 10h
    # mov bl, 20h
    # add al, bl
    # hlt
    
    program = [
        0xB0, 0x10,  # mov al, 10h
        0xB3, 0x20,  # mov bl, 20h
        0x00, 0xD8,  # add al, bl (0x00 = ADD r/m8, r8; 0xD8 = ModR/M for AL, BL)
        0xF4        # hlt
    ]
    
    # Load program at physical address 0x100 (typical COM file start)
    memory.load_bytes(0x100, program)
    
    # Set CS:IP to point to the program
    cpu.set_register(cpu.CS, 0x10)  # 0x10 << 4 = 0x100
    cpu.set_register(cpu.IP, 0)
    
    # Run the program
    print("Initial state:")
    print_registers(cpu)
    
    print("\nExecuting program...")
    while not cpu.halted:
        if not cpu.execute_instruction():
            print("Execution stopped.")
            break
    
    print("\nFinal state:")
    print_registers(cpu)

def print_registers(cpu):
    """Print the values of the main registers"""
    print(f"AX: {cpu.get_register(cpu.AX):04X} (AL: {cpu.get_register_low_byte(cpu.AX):02X}, AH: {cpu.get_register_high_byte(cpu.AX):02X})")
    print(f"BX: {cpu.get_register(cpu.BX):04X} (BL: {cpu.get_register_low_byte(cpu.BX):02X}, BH: {cpu.get_register_high_byte(cpu.BX):02X})")
    print(f"CX: {cpu.get_register(cpu.CX):04X} (CL: {cpu.get_register_low_byte(cpu.CX):02X}, CH: {cpu.get_register_high_byte(cpu.CX):02X})")
    print(f"DX: {cpu.get_register(cpu.DX):04X} (DL: {cpu.get_register_low_byte(cpu.DX):02X}, DH: {cpu.get_register_high_byte(cpu.DX):02X})")
    print(f"SI: {cpu.get_register(cpu.SI):04X}")
    print(f"DI: {cpu.get_register(cpu.DI):04X}")
    print(f"BP: {cpu.get_register(cpu.BP):04X}")
    print(f"SP: {cpu.get_register(cpu.SP):04X}")
    print(f"CS: {cpu.get_register(cpu.CS):04X}")
    print(f"DS: {cpu.get_register(cpu.DS):04X}")
    print(f"ES: {cpu.get_register(cpu.ES):04X}")
    print(f"SS: {cpu.get_register(cpu.SS):04X}")
    print(f"IP: {cpu.get_register(cpu.IP):04X}")
    print(f"FLAGS: {cpu.get_register(cpu.FLAGS):04X}")

if __name__ == "__main__":
    main()