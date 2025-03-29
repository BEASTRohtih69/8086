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

# Import the GUI module
try:
    from gui import start_gui
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


def main():
    """Main entry point for the 8086 simulator"""
    parser = argparse.ArgumentParser(description='8086 Microprocessor Simulator')
    parser.add_argument('program', nargs='?', help='Assembly program file to load (optional)')
    parser.add_argument('-d', '--debug', action='store_true', help='Start in debug mode')
    parser.add_argument('-m', '--memory', type=int, default=1024*64, 
                        help='Memory size in bytes (default: 64KB)')
    parser.add_argument('-i', '--interactive', action='store_true', 
                        help='Start in interactive mode even with a program loaded')
    parser.add_argument('-g', '--gui', action='store_true',
                       help='Start with graphical user interface (if available)')
    parser.add_argument('-t', '--text', action='store_true',
                       help='Force text mode (no GUI)')
    
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
            # Use the improved segment handling for program loading
            try:
                from fix_instructions import fix_segment_handling
                print(f"Using improved segment handling for '{args.program}'")
                fix_segment_handling(assembler, args.program)
                print(f"Program '{args.program}' loaded successfully with fixed segment handling.")
            except ImportError:
                # Fall back to standard loading if improved handling isn't available
                print(f"Using standard loader for '{args.program}'")
                assembler.load_program(args.program)
                print(f"Program '{args.program}' loaded successfully.")
        except Exception as e:
            print(f"Error loading program: {e}")
            sys.exit(1)
    
    # Check if we should use the GUI
    use_gui = args.gui or (GUI_AVAILABLE and not args.text)
    
    if use_gui and GUI_AVAILABLE:
        # Launch the graphical interface
        from gui import start_gui
        start_gui(cpu, memory, assembler, debugger)
    else:
        # Use the text-based interface
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
