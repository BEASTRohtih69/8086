#!/usr/bin/env python3
"""
8086 Simulator - Main Entry Point
A complete 8086 microprocessor simulator with full instruction set support and debugging capabilities.
"""

import argparse
import os
import sys
from cpu import CPU
from memory import Memory
from assembler import Assembler
from debugger import Debugger
from ui import UI


def main():
    """Main entry point for the 8086 simulator"""
    parser = argparse.ArgumentParser(description='8086 Microprocessor Simulator')
    parser.add_argument('program', nargs='?', help='Assembly program file to load (optional)')
    parser.add_argument('-d', '--debug', action='store_true', help='Start in debug mode')
    parser.add_argument('-m', '--memory', type=int, default=1024*64, 
                        help='Memory size in bytes (default: 64KB)')
    parser.add_argument('-i', '--interactive', action='store_true', 
                        help='Start in interactive mode even with a program loaded')
    
    args = parser.parse_args()
    
    # Initialize system components
    memory = Memory(args.memory)
    cpu = CPU(memory)
    assembler = Assembler(cpu, memory)
    ui = UI(cpu, memory)
    debugger = Debugger(cpu, memory, ui)
    
    # If a program file is provided, load it
    if args.program and os.path.exists(args.program):
        try:
            assembler.load_program(args.program)
            print(f"Program '{args.program}' loaded successfully.")
        except Exception as e:
            print(f"Error loading program: {e}")
            sys.exit(1)
    
    # If debug mode is requested or interactive mode
    if args.debug or args.interactive or not args.program:
        ui.show_welcome()
        debugger.interactive_mode()
    else:
        # Run the program normally
        ui.show_welcome()
        ui.run_simulation(cpu)
    
    print("Simulator exited.")


if __name__ == "__main__":
    main()
