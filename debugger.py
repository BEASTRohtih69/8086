"""
Debugger module for 8086 simulator.
Implements the debugging functionality with breakpoints, stepping, etc.
"""

class Debugger:
    """Debugger for 8086 CPU simulator with breakpoints, stepping, etc."""
    
    def __init__(self, cpu, memory, ui):
        """Initialize the debugger with CPU, memory, and UI references."""
        self.cpu = cpu
        self.memory = memory
        self.ui = ui
        self.breakpoints = set()
        self.is_running = False
        self.step_mode = False
    
    def toggle_breakpoint(self, address):
        """Toggle a breakpoint at the specified address."""
        if address in self.breakpoints:
            self.breakpoints.remove(address)
            return False
        else:
            self.breakpoints.add(address)
            return True
    
    def clear_breakpoints(self):
        """Clear all breakpoints."""
        self.breakpoints.clear()
    
    def step_instruction(self):
        """Execute a single instruction and update UI."""
        if self.cpu.halted:
            print("CPU is halted. Reset to continue.")
            return False
        
        # Execute one instruction
        result = self.cpu.execute_instruction()
        
        # Update UI
        self.ui.update_display()
        
        return result
    
    def run_to_breakpoint(self):
        """Run until a breakpoint is hit or CPU halts."""
        if self.cpu.halted:
            print("CPU is halted. Reset to continue.")
            return
        
        self.is_running = True
        
        while self.is_running and not self.cpu.halted:
            # Calculate the physical address
            cs = self.cpu.get_register(self.cpu.CS)
            ip = self.cpu.get_register(self.cpu.IP)
            physical_address = self.cpu.get_physical_address(cs, ip)
            
            # Check if we've hit a breakpoint
            if physical_address in self.breakpoints:
                print(f"Breakpoint hit at CS:IP = {cs:04X}:{ip:04X} (Physical: {physical_address:05X})")
                self.is_running = False
                self.ui.update_display()
                break
            
            # Execute one instruction
            result = self.cpu.execute_instruction()
            if not result:
                self.is_running = False
                self.ui.update_display()
                break
            
            # If in step mode, break after each instruction
            if self.step_mode:
                self.is_running = False
                self.ui.update_display()
                break
    
    def stop(self):
        """Stop the execution."""
        self.is_running = False
    
    def set_step_mode(self, enabled):
        """Enable or disable step mode."""
        self.step_mode = enabled
    
    def dump_memory(self, start_address, length):
        """Dump a section of memory."""
        data = self.memory.dump(start_address, length)
        return data
    
    def disassemble(self, start_address, count):
        """Disassemble a section of memory into instructions."""
        # This is a simplified disassembler
        instructions = []
        address = start_address
        
        for _ in range(count):
            try:
                # Save the current CPU state
                saved_cs = self.cpu.get_register(self.cpu.CS)
                saved_ip = self.cpu.get_register(self.cpu.IP)
                
                # Set IP to the address we want to disassemble
                physical_address = address
                self.cpu.set_register(self.cpu.CS, 0)
                self.cpu.set_register(self.cpu.IP, physical_address)
                
                # Fetch the opcode
                opcode = self.cpu.fetch_byte()
                
                # Get instruction information from tables
                from instructions import InstructionSet
                instr_set = InstructionSet(self.cpu)
                mnemonic, _ = instr_set.decode(opcode)
                
                # Restore CPU state
                self.cpu.set_register(self.cpu.CS, saved_cs)
                self.cpu.set_register(self.cpu.IP, saved_ip)
                
                # Simplified: just show the opcode for now
                instructions.append((address, opcode, mnemonic))
                address += 1  # This should be adjusted based on instruction length
            
            except Exception as e:
                instructions.append((address, None, f"Error: {str(e)}"))
                address += 1
        
        return instructions
    
    def interactive_mode(self):
        """Start an interactive debugging session."""
        while True:
            command = input("(8086-dbg) ").strip().lower()
            
            if command in ['q', 'quit', 'exit']:
                break
            
            elif command in ['h', 'help', '?']:
                self._print_help()
            
            elif command in ['r', 'regs', 'registers']:
                self.ui.display_registers()
            
            elif command in ['f', 'flags']:
                self.ui.display_flags()
            
            elif command.startswith('m ') or command == 'm':
                # Memory dump
                if command == 'm':
                    # Default to current CS:IP if no address specified
                    cs = self.cpu.get_register(self.cpu.CS)
                    ip = self.cpu.get_register(self.cpu.IP)
                    address = self.cpu.get_physical_address(cs, ip)
                    length = 16*8  # 8 lines
                else:
                    parts = command.split()
                    if len(parts) >= 2:
                        try:
                            address = self._parse_address(parts[1])
                            length = 16*8  # Default 8 lines
                            if len(parts) >= 3:
                                length = int(parts[2], 16) if parts[2].startswith('0x') else int(parts[2])
                        except ValueError:
                            print("Invalid address or length")
                            continue
                    else:
                        print("Invalid memory command")
                        continue
                
                self.ui.display_memory(address, length)
            
            elif command.startswith('d ') or command == 'd':
                # Disassemble
                if command == 'd':
                    # Default to current CS:IP if no address specified
                    cs = self.cpu.get_register(self.cpu.CS)
                    ip = self.cpu.get_register(self.cpu.IP)
                    address = self.cpu.get_physical_address(cs, ip)
                    count = 10  # Default 10 instructions
                else:
                    parts = command.split()
                    if len(parts) >= 2:
                        try:
                            address = self._parse_address(parts[1])
                            count = 10  # Default 10 instructions
                            if len(parts) >= 3:
                                count = int(parts[2])
                        except ValueError:
                            print("Invalid address or count")
                            continue
                    else:
                        print("Invalid disassemble command")
                        continue
                
                self.ui.display_disassembly(address, count)
            
            elif command == 's' or command == 'step':
                # Step instruction
                if self.step_instruction():
                    cs = self.cpu.get_register(self.cpu.CS)
                    ip = self.cpu.get_register(self.cpu.IP)
                    print(f"Next instruction at CS:IP = {cs:04X}:{ip:04X}")
            
            elif command == 'g' or command == 'go' or command.startswith('g '):
                # Run to breakpoint or address
                if command.startswith('g '):
                    # Run to specific address
                    parts = command.split()
                    if len(parts) >= 2:
                        try:
                            address = self._parse_address(parts[1])
                            # Set a temporary breakpoint
                            self.breakpoints.add(address)
                            self.run_to_breakpoint()
                            # Remove temporary breakpoint
                            self.breakpoints.remove(address)
                        except ValueError:
                            print("Invalid address")
                            continue
                else:
                    # Run to next breakpoint
                    self.run_to_breakpoint()
            
            elif command.startswith('bp ') or command == 'bp':
                # Set or list breakpoints
                if command == 'bp':
                    # List breakpoints
                    if not self.breakpoints:
                        print("No breakpoints set")
                    else:
                        print("Breakpoints:")
                        for addr in sorted(self.breakpoints):
                            print(f"  {addr:05X}")
                else:
                    # Set breakpoint
                    parts = command.split()
                    if len(parts) >= 2:
                        try:
                            address = self._parse_address(parts[1])
                            if self.toggle_breakpoint(address):
                                print(f"Breakpoint set at {address:05X}")
                            else:
                                print(f"Breakpoint removed from {address:05X}")
                        except ValueError:
                            print("Invalid address")
                            continue
                    else:
                        print("Invalid breakpoint command")
                        continue
            
            elif command == 'bc':
                # Clear all breakpoints
                self.clear_breakpoints()
                print("All breakpoints cleared")
            
            elif command.startswith('bc '):
                # Clear specific breakpoint
                parts = command.split()
                if len(parts) >= 2:
                    try:
                        address = self._parse_address(parts[1])
                        if address in self.breakpoints:
                            self.breakpoints.remove(address)
                            print(f"Breakpoint cleared at {address:05X}")
                        else:
                            print(f"No breakpoint at {address:05X}")
                    except ValueError:
                        print("Invalid address")
                        continue
                else:
                    print("Invalid breakpoint clear command")
                    continue
            
            elif command == 'reset':
                # Reset CPU
                self.cpu.reset()
                print("CPU reset")
            
            else:
                print(f"Unknown command: {command}")
                self._print_help()
    
    def _print_help(self):
        """Print help information."""
        help_text = """
        8086 Debugger Commands:
        h, help, ?       - Show this help
        q, quit, exit    - Quit the debugger
        
        r, regs          - Display registers
        f, flags         - Display flags
        
        m [addr] [len]   - Display memory at address (default: CS:IP)
        d [addr] [count] - Disassemble memory (default: CS:IP, 10 instructions)
        
        s, step          - Step one instruction
        g, go            - Run until breakpoint or halt
        g addr           - Run until address
        
        bp               - List breakpoints
        bp addr          - Set breakpoint at address
        bc               - Clear all breakpoints
        bc addr          - Clear breakpoint at address
        
        reset            - Reset CPU
        """
        print(help_text)
    
    def _parse_address(self, addr_str):
        """Parse an address string in various formats."""
        if ':' in addr_str:
            # Segment:offset format
            segment, offset = addr_str.split(':')
            segment = int(segment, 16) if segment.startswith('0x') else int(segment, 16)
            offset = int(offset, 16) if offset.startswith('0x') else int(offset, 16)
            return self.cpu.get_physical_address(segment, offset)
        else:
            # Direct address
            return int(addr_str, 16) if addr_str.startswith('0x') else int(addr_str, 16)
