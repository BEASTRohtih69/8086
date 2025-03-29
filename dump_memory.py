#!/usr/bin/env python3
"""
Memory dump tool for the 8086 simulator.
This script loads a program and executes it, then dumps the memory content at specified address.
"""

import sys
import argparse
from cpu import CPU
from memory import Memory
from assembler import Assembler

def main():
    parser = argparse.ArgumentParser(description='Memory dump tool for 8086 simulator')
    parser.add_argument('program', nargs='?', help='Assembly program to load')
    parser.add_argument('--address', '-a', type=str, default='0x0200', 
                      help='Memory address to dump (in hex, e.g., 0x0200)')
    parser.add_argument('--length', '-l', type=int, default=20, 
                      help='Number of bytes to dump')
    parser.add_argument('--stop', '-s', type=str, default='0x0100',
                      help='Stop execution when IP reaches this address (default: 0x0100, ignored if negative)')
    parser.add_argument('--max-instructions', type=int, default=1000,
                      help='Maximum number of instructions to execute (default: 1000)')
    
    args = parser.parse_args()
    
    if not args.program:
        print("Error: You must specify a program file")
        parser.print_help()
        return 1
    
    # Create CPU, memory, and assembler
    memory = Memory()
    cpu = CPU(memory)
    assembler = Assembler(cpu, memory)
    
    try:
        # Load the program
        assembler.load_program(args.program)
        
        # Execute the program
        max_instructions = args.max_instructions
        instruction_count = 0
        stop_address = int(args.stop, 16) if args.stop.startswith('0x') else int(args.stop)
        
        # Set IP to the entry point if it's currently at 0
        if cpu.get_register(cpu.IP) == 0:
            print("Setting IP to 0x0000 (relative to CS)")
            cpu.set_register(cpu.IP, 0)
        
        print(f"Executing program, will stop after {max_instructions} instructions "
              f"or when IP reaches {args.stop}")
        
        # Print initial register state
        print("\nInitial Register State:")
        registers = ['AX', 'BX', 'CX', 'DX', 'SI', 'DI', 'BP', 'SP', 'CS', 'DS', 'SS', 'ES', 'IP', 'FLAGS']
        for reg in registers:
            value = cpu.get_register(getattr(cpu, reg))
            print(f"{reg}: {value:04X}", end="  ")
            if reg in ['DX', 'SP', 'ES']:  # Line break after these registers
                print()
        print("\n")
        
        while instruction_count < max_instructions:
            # Get current IP and physical address
            ip = cpu.get_register(cpu.IP)
            cs = cpu.get_register(cpu.CS)
            physical_addr = ip + (cs << 4)
            
            # Read opcode at current position
            opcode = memory.read_byte(physical_addr)
            
            # Print current instruction info
            print(f"[{instruction_count:04d}] IP:{ip:04X} CS:{cs:04X} Physical:{physical_addr:05X} Opcode:{opcode:02X}")
            
            # Check if we've reached the stop address
            if ip == stop_address:
                print(f"Reached stop address {args.stop}")
                break
                
            # Check for HLT instruction
            if opcode == 0xF4:  # HLT opcode
                print("Program halted (HLT instruction)")
                break
                
            # Execute the instruction
            cpu.execute_instruction()
            instruction_count += 1
            
            # Print register values after each instruction
            if instruction_count <= 25:  # Only for the first 25 instructions to avoid flooding
                for reg in ['AX', 'BX', 'CX', 'DX', 'SI', 'DI', 'ES', 'DS', 'IP', 'FLAGS']:
                    value = cpu.get_register(getattr(cpu, reg))
                    print(f"{reg}:{value:04X} ", end="")
                print("")  # Newline
            
        print(f"Executed {instruction_count} instructions")
        
        # Dump memory content at the specified address
        start_address = int(args.address, 16) if args.address.startswith('0x') else int(args.address)
        length = args.length
        
        print(f"\nMemory dump at address {args.address}, length {length} bytes:")
        print("Addr | Hex          | ASCII")
        print("-" * 50)
        
        # Print in 16-byte rows
        for i in range(0, length, 16):
            addr = start_address + i
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
        
        # Print register state
        print("\nRegister State:")
        registers = ['AX', 'BX', 'CX', 'DX', 'SI', 'DI', 'BP', 'SP', 'CS', 'DS', 'SS', 'ES', 'IP', 'FLAGS']
        for reg in registers:
            value = cpu.get_register(getattr(cpu, reg))
            print(f"{reg}: {value:04X}", end="  ")
            if reg in ['DX', 'SP', 'ES']:  # Line break after these registers
                print()
                
        print("\n")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())