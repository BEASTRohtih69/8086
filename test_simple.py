#!/usr/bin/env python3
"""
8086 Simulator - Simple Test Runner
A simple non-interactive test script to verify CPU instruction execution
"""

import sys
import argparse
from cpu import CPU
from memory import Memory
from assembler import Assembler
from instructions import InstructionSet

def main():
    """Main entry point for the test script"""
    parser = argparse.ArgumentParser(description='Test the 8086 simulator with a simple program')
    parser.add_argument('program', help='Assembly program file to test')
    parser.add_argument('--max-instructions', type=int, default=20, 
                      help='Maximum number of instructions to execute (default: 20)')
    parser.add_argument('--verbose', action='store_true',
                      help='Show detailed information about each instruction')
    parser.add_argument('--dump-memory', type=str, default=None,
                      help='Memory range to dump after execution (format: "start:length", e.g. "0x200:32")')
    
    args = parser.parse_args()
    
    # Initialize components
    memory = Memory(1024*64)  # 64K memory
    cpu = CPU(memory)
    cpu.debug_mode = args.verbose  # Set CPU debug mode based on verbose flag
    assembler = Assembler(cpu, memory)
    
    # Load the program with improved segment handling
    try:
        from fix_instructions import fix_segment_handling
        print(f"Loading test program '{args.program}'")
        fix_segment_handling(assembler, args.program)
        print(f"Program loaded successfully")
    except Exception as e:
        print(f"Error loading program: {e}")
        return 1
    
    # Display initial state
    print("\nInitial Register State:")
    for reg in ['AX', 'BX', 'CX', 'DX', 'SI', 'DI', 'BP', 'SP', 'CS', 'DS', 'SS', 'ES', 'IP', 'FLAGS']:
        value = cpu.get_register(getattr(cpu, reg))
        print(f"{reg}: {value:04X}", end="  ")
        if reg in ['DX', 'SP', 'ES']:  # Line break after these registers
            print()
    print("\n")
    
    # Execute instructions with debug output
    print(f"Executing up to {args.max_instructions} instructions:")
    instruction_count = 0
    
    while not cpu.halted and instruction_count < args.max_instructions:
        # Show current instruction
        cs = cpu.get_register(cpu.CS)
        ip = cpu.get_register(cpu.IP)
        physical_addr = cpu.get_physical_address(cs, ip)
        opcode = memory.read_byte(physical_addr)
        
        print(f"[{instruction_count:04d}] Executing at {physical_addr:04X}, opcode: {opcode:02X}")
        
        # Execute the instruction
        if not hasattr(cpu, 'instruction_set'):
            from instructions import InstructionSet
            cpu.instruction_set = InstructionSet(cpu)
            print("Initialized instruction set within CPU")
        
        result = cpu.execute_instruction()
        if not result:
            print(f"Failed to execute instruction with opcode: {opcode:02X}")
            break
        
        instruction_count += 1
        
        # Show register state after each instruction
        print("Registers: ", end="")
        for reg in ['AX', 'CX', 'DX', 'BX', 'IP', 'FLAGS']:
            value = cpu.get_register(getattr(cpu, reg))
            print(f"{reg}={value:04X} ", end="")
        print()
        
        # Provide special debug for flag instructions
        if opcode in [0xF8, 0xF9, 0xF5, 0xFC, 0xFD, 0xFA, 0xFB]:  # Flag instructions
            flags = " ".join(f"{name}={cpu.get_flag(flag)}" 
                      for flag, name in cpu.FLAG_NAMES.items())
            print(f"Flags: {flags}")
    
    print(f"\nExecution completed. Executed {instruction_count} instructions.")
    
    # Dump memory if requested
    if args.dump_memory:
        try:
            start, length = args.dump_memory.split(':')
            start_addr = int(start, 16) if start.startswith('0x') else int(start)
            length = int(length)
            
            print(f"\nMemory dump at {start_addr:04X}, length {length} bytes:")
            print("Addr | Hex          | ASCII")
            print("-" * 50)
            
            # Print in 16-byte rows
            for i in range(0, length, 16):
                addr = start_addr + i
                hex_values = []
                ascii_values = []
                
                # Process up to 16 bytes (or remaining length)
                row_length = min(16, length - i)
                for j in range(row_length):
                    byte = memory.read_byte(addr + j)
                    hex_values.append(f"{byte:02X}")
                    
                    # Convert to ASCII if printable
                    if 32 <= byte <= 126:  # Printable ASCII range
                        ascii_values.append(chr(byte))
                    else:
                        ascii_values.append('.')
                
                # Print the row
                hex_str = ' '.join(hex_values).ljust(48)
                ascii_str = ''.join(ascii_values)
                print(f"{addr:04X} | {hex_str} | {ascii_str}")
        except Exception as e:
            print(f"Error dumping memory: {e}")
    
    # Final register state
    print("\nFinal Register State:")
    for reg in ['AX', 'BX', 'CX', 'DX', 'SI', 'DI', 'BP', 'SP', 'CS', 'DS', 'SS', 'ES', 'IP', 'FLAGS']:
        value = cpu.get_register(getattr(cpu, reg))
        print(f"{reg}: {value:04X}", end="  ")
        if reg in ['DX', 'SP', 'ES']:  # Line break after these registers
            print()
    print("\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())