"""
UI module for 8086 simulator.
Implements the user interface for the simulator.
"""

import os
import sys
from collections import deque

class UI:
    """User interface for the 8086 simulator."""
    
    def __init__(self, cpu, memory):
        """Initialize the UI with CPU and memory references."""
        self.cpu = cpu
        self.memory = memory
        self.command_history = deque(maxlen=20)
        self.input_buffer = ""
        self.output_lines = []
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_welcome(self):
        """Display the welcome message."""
        welcome_msg = """
        ╔═════════════════════════════════════════════════════════════╗
        ║                   8086 Microprocessor Simulator             ║
        ╠═════════════════════════════════════════════════════════════╣
        ║ Type 'help' or 'h' for a list of commands                   ║
        ║ Press 'q' to quit                                           ║
        ╚═════════════════════════════════════════════════════════════╝
        """
        print(welcome_msg)
    
    def update_display(self):
        """Update the display with current CPU and memory state."""
        self.clear_screen()
        self.show_welcome()
        self.display_registers()
        self.display_flags()
        
        # Show disassembly at current IP
        cs = self.cpu.get_register(self.cpu.CS)
        ip = self.cpu.get_register(self.cpu.IP)
        physical_address = self.cpu.get_physical_address(cs, ip)
        self.display_disassembly(physical_address, 5)
    
    def display_registers(self):
        """Display the current register values."""
        print("\n╔═══ Registers ════════════════════════════════════════════════╗")
        
        # General purpose registers
        print("║  AX: {:04X}  BX: {:04X}  CX: {:04X}  DX: {:04X}                     ║".format(
            self.cpu.get_register(self.cpu.AX),
            self.cpu.get_register(self.cpu.BX),
            self.cpu.get_register(self.cpu.CX),
            self.cpu.get_register(self.cpu.DX)
        ))
        
        # Pointer and index registers
        print("║  SP: {:04X}  BP: {:04X}  SI: {:04X}  DI: {:04X}                     ║".format(
            self.cpu.get_register(self.cpu.SP),
            self.cpu.get_register(self.cpu.BP),
            self.cpu.get_register(self.cpu.SI),
            self.cpu.get_register(self.cpu.DI)
        ))
        
        # Segment registers and IP
        print("║  CS: {:04X}  DS: {:04X}  SS: {:04X}  ES: {:04X}  IP: {:04X}         ║".format(
            self.cpu.get_register(self.cpu.CS),
            self.cpu.get_register(self.cpu.DS),
            self.cpu.get_register(self.cpu.SS),
            self.cpu.get_register(self.cpu.ES),
            self.cpu.get_register(self.cpu.IP)
        ))
        
        print("╚═════════════════════════════════════════════════════════════╝")
    
    def display_flags(self):
        """Display the current flag values."""
        print("\n╔═══ Flags ═══════════════════════════════════════════════════╗")
        
        # Flag names and values
        flags = [
            ("CF", self.cpu.get_flag(self.cpu.CARRY_FLAG)),
            ("PF", self.cpu.get_flag(self.cpu.PARITY_FLAG)),
            ("AF", self.cpu.get_flag(self.cpu.AUXILIARY_CARRY_FLAG)),
            ("ZF", self.cpu.get_flag(self.cpu.ZERO_FLAG)),
            ("SF", self.cpu.get_flag(self.cpu.SIGN_FLAG)),
            ("TF", self.cpu.get_flag(self.cpu.TRAP_FLAG)),
            ("IF", self.cpu.get_flag(self.cpu.INTERRUPT_FLAG)),
            ("DF", self.cpu.get_flag(self.cpu.DIRECTION_FLAG)),
            ("OF", self.cpu.get_flag(self.cpu.OVERFLOW_FLAG))
        ]
        
        flag_str = " ".join(f"{name}:{val}" for name, val in flags)
        print(f"║  {flag_str}                           ║")
        
        # Flag representation
        flags_value = self.cpu.get_register(self.cpu.FLAGS)
        flag_bits = format(flags_value, '016b')
        print(f"║  Flags: {flags_value:04X} ({flag_bits})                             ║")
        
        print("╚═════════════════════════════════════════════════════════════╝")
    
    def display_memory(self, start_address, length):
        """Display a section of memory."""
        print("\n╔═══ Memory Dump ════════════════════════════════════════════╗")
        print("║  Address   | 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | ASCII    ║")
        print("║───────────┼────────────────────────────────────────────────┼──────────║")
        
        # Round to 16-byte boundary for display
        start_row = start_address & 0xFFFFF0
        end_address = start_address + length
        
        row = start_row
        while row < end_address:
            # Address
            line = f"║  {row:08X} | "
            
            # Hex values
            ascii_repr = ""
            for i in range(16):
                addr = row + i
                if addr < self.memory.size:
                    try:
                        value = self.memory.read_byte(addr)
                        line += f"{value:02X} "
                        
                        # ASCII representation
                        if 32 <= value <= 126:  # Printable ASCII
                            ascii_repr += chr(value)
                        else:
                            ascii_repr += "."
                    except:
                        line += "-- "
                        ascii_repr += " "
                else:
                    line += "-- "
                    ascii_repr += " "
            
            # Fill in ASCII part
            line += f"| {ascii_repr:{16}} ║"
            print(line)
            
            row += 16
        
        print("╚═════════════════════════════════════════════════════════════╝")
    
    def display_disassembly(self, start_address, count):
        """Display disassembled instructions."""
        print("\n╔═══ Disassembly ════════════════════════════════════════════╗")
        
        # Simplified disassembly for demonstration
        cs = self.cpu.get_register(self.cpu.CS)
        ip = self.cpu.get_register(self.cpu.IP)
        current_address = self.cpu.get_physical_address(cs, ip)
        
        address = start_address
        for _ in range(count):
            if address >= self.memory.size:
                break
            
            try:
                # Mark the current instruction
                prefix = "->" if address == current_address else "  "
                
                # Fetch opcode
                opcode = self.memory.read_byte(address)
                
                # Simple opcode lookup
                instruction = self._get_instruction_name(opcode)
                
                # Display the instruction
                print(f"║ {prefix} {address:08X}: {opcode:02X}        {instruction:<20} ║")
                
                # Move to next instruction (simplified, assumes 1 byte instructions)
                address += 1
            
            except Exception as e:
                print(f"║    {address:08X}: Error: {str(e):<30} ║")
                address += 1
        
        print("╚═════════════════════════════════════════════════════════════╝")
    
    def _get_instruction_name(self, opcode):
        """Get a simplified instruction name for an opcode."""
        # This is a very simplified implementation
        # A real disassembler would be much more complex
        opcodes = {
            0x90: "NOP",
            0xF4: "HLT",
            0xB8: "MOV AX,imm16",
            0xB9: "MOV CX,imm16",
            0xBA: "MOV DX,imm16",
            0xBB: "MOV BX,imm16",
            0x89: "MOV r/m16,r16",
            0x8B: "MOV r16,r/m16",
            0x01: "ADD r/m16,r16",
            0x03: "ADD r16,r/m16",
            0x05: "ADD AX,imm16",
            0x29: "SUB r/m16,r16",
            0x2B: "SUB r16,r/m16",
            0x2D: "SUB AX,imm16",
            0x50: "PUSH AX",
            0x51: "PUSH CX",
            0x52: "PUSH DX",
            0x53: "PUSH BX",
            0x58: "POP AX",
            0x59: "POP CX",
            0x5A: "POP DX",
            0x5B: "POP BX",
            0xE8: "CALL rel16",
            0xC3: "RET",
            0x74: "JE rel8",
            0x75: "JNE rel8",
            0xEB: "JMP rel8",
            0xCD: "INT imm8"
        }
        
        return opcodes.get(opcode, f"Unknown opcode: {opcode:02X}")
    
    def run_simulation(self, cpu, max_instructions=None):
        """Run the simulation with a simple UI and optional instruction limit."""
        instruction_count = 0
        
        while not cpu.halted:
            # Check if we've reached the instruction limit
            if max_instructions is not None and instruction_count >= max_instructions:
                print(f"\nReached maximum instruction count: {max_instructions}")
                break
                
            self.update_display()
            
            command = input("\nPress Enter to step, 'q' to quit: ").strip().lower()
            if command == 'q':
                break
            
            result = cpu.execute_instruction()
            if result:
                instruction_count += 1
            if not result:
                break
        
        self.update_display()
        print(f"\nSimulation ended after executing {instruction_count} instructions.")
