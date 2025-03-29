"""
CPU module for 8086 simulator.
Implements the CPU state, registers, flags, and instruction execution.
Includes hooks for performance profiling.
"""

from memory import Memory

class CPU:
    """Simulates the 8086 CPU including registers, flags, and instruction execution."""
    
    # Register indices
    AX, BX, CX, DX = 0, 1, 2, 3
    SP, BP, SI, DI = 4, 5, 6, 7
    CS, DS, SS, ES = 8, 9, 10, 11
    IP = 12
    FLAGS = 13
    
    # Flag bit positions
    CARRY_FLAG = 0
    PARITY_FLAG = 2
    AUXILIARY_CARRY_FLAG = 4
    ZERO_FLAG = 6
    SIGN_FLAG = 7
    TRAP_FLAG = 8
    INTERRUPT_FLAG = 9
    DIRECTION_FLAG = 10
    OVERFLOW_FLAG = 11
    
    # Mapping register indices to names
    REGISTER_NAMES = {
        AX: "AX", BX: "BX", CX: "CX", DX: "DX",
        SP: "SP", BP: "BP", SI: "SI", DI: "DI",
        CS: "CS", DS: "DS", SS: "SS", ES: "ES",
        IP: "IP", FLAGS: "FLAGS"
    }
    
    # Flag names
    FLAG_NAMES = {
        CARRY_FLAG: "CF",
        PARITY_FLAG: "PF",
        AUXILIARY_CARRY_FLAG: "AF",
        ZERO_FLAG: "ZF",
        SIGN_FLAG: "SF",
        TRAP_FLAG: "TF",
        INTERRUPT_FLAG: "IF",
        DIRECTION_FLAG: "DF",
        OVERFLOW_FLAG: "OF"
    }
    
    def __init__(self, memory):
        """Initialize the CPU with default register values."""
        self.memory = memory
        self.registers = [0] * 14  # 14 registers (AX through FLAGS)
        self.halted = False
        self.instruction_count = 0
        
        # Profiling hooks
        self.profiler = None
        
        # Set segment registers for proper memory segmentation
        # In 8086, physical address = (segment << 4) + offset
        # Standard segmentation for COM files:
        self.registers[self.CS] = 0x0010  # Code segment: 0x0010 << 4 = 0x0100
        self.registers[self.DS] = 0x0010  # Data segment: same as CS for COM
        self.registers[self.SS] = 0x0010  # Stack segment: same as CS for COM
        self.registers[self.ES] = 0x0010  # Extra segment: same as CS for COM
        
        # Set IP to point to the start of program (offset 0 from CS)
        self.registers[self.IP] = 0x0000  # Physical address: 0x0010 << 4 + 0x0000 = 0x0100
        
        # Set SP to top of stack (typical 2KB size)
        self.registers[self.SP] = 0xFFFE  # Initialize stack pointer
    
    def reset(self):
        """Reset the CPU to its initial state."""
        # Store the profiler reference before reinitializing
        profiler = self.profiler
        self.__init__(self.memory)
        # Restore the profiler reference after reinitializing
        self.profiler = profiler
        self.halted = False
        
    def set_profiler(self, profiler):
        """Set a profiler for performance monitoring."""
        self.profiler = profiler
    
    def get_register(self, reg):
        """Get the value of a register."""
        return self.registers[reg]
    
    def set_register(self, reg, value):
        """Set the value of a register, ensuring it's within the 16-bit range."""
        self.registers[reg] = value & 0xFFFF  # Ensure 16-bit value
    
    def get_flag(self, flag):
        """Get the value of a specific flag."""
        return (self.registers[self.FLAGS] >> flag) & 1
    
    def set_flag(self, flag, value):
        """Set a specific flag to 0 or 1."""
        if value:
            self.registers[self.FLAGS] |= (1 << flag)
        else:
            self.registers[self.FLAGS] &= ~(1 << flag)
    
    def get_register_high_byte(self, reg):
        """Get the high byte of a register (only valid for AX, BX, CX, DX)."""
        if reg > self.DX:
            raise ValueError(f"Register {self.REGISTER_NAMES[reg]} does not have high/low bytes")
        return (self.registers[reg] >> 8) & 0xFF
    
    def get_register_low_byte(self, reg):
        """Get the low byte of a register (only valid for AX, BX, CX, DX)."""
        if reg > self.DX:
            raise ValueError(f"Register {self.REGISTER_NAMES[reg]} does not have high/low bytes")
        return self.registers[reg] & 0xFF
    
    def set_register_high_byte(self, reg, value):
        """Set the high byte of a register (only valid for AX, BX, CX, DX)."""
        if reg > self.DX:
            raise ValueError(f"Register {self.REGISTER_NAMES[reg]} does not have high/low bytes")
        self.registers[reg] = (self.registers[reg] & 0x00FF) | ((value & 0xFF) << 8)
    
    def set_register_low_byte(self, reg, value):
        """Set the low byte of a register (only valid for AX, BX, CX, DX)."""
        if reg > self.DX:
            raise ValueError(f"Register {self.REGISTER_NAMES[reg]} does not have high/low bytes")
        self.registers[reg] = (self.registers[reg] & 0xFF00) | (value & 0xFF)
    
    def get_physical_address(self, segment, offset):
        """Convert segment:offset address to physical address."""
        return ((segment << 4) + offset) & 0xFFFFF  # 20-bit address space
    
    def fetch_byte(self):
        """Fetch a byte from memory at CS:IP and increment IP."""
        address = self.get_physical_address(self.registers[self.CS], self.registers[self.IP])
        byte = self.memory.read_byte(address)
        self.registers[self.IP] = (self.registers[self.IP] + 1) & 0xFFFF
        return byte
    
    def fetch_word(self):
        """Fetch a word (2 bytes) from memory at CS:IP and increment IP by 2."""
        low_byte = self.fetch_byte()
        high_byte = self.fetch_byte()
        return (high_byte << 8) | low_byte
    
    def push(self, value):
        """Push a 16-bit value onto the stack."""
        self.registers[self.SP] = (self.registers[self.SP] - 2) & 0xFFFF
        sp_address = self.get_physical_address(self.registers[self.SS], self.registers[self.SP])
        self.memory.write_word(sp_address, value)
    
    def pop(self):
        """Pop a 16-bit value from the stack."""
        sp_address = self.get_physical_address(self.registers[self.SS], self.registers[self.SP])
        value = self.memory.read_word(sp_address)
        self.registers[self.SP] = (self.registers[self.SP] + 2) & 0xFFFF
        return value
    
    def execute_instruction(self):
        """Execute the next instruction at CS:IP."""
        if self.halted:
            return False
        
        # Fetch the opcode
        opcode = self.fetch_byte()
        
        # Check if we have an instruction set
        if not hasattr(self, 'instruction_set'):
            from instructions import InstructionSet
            self.instruction_set = InstructionSet(self)
            print("Initialized instruction set within CPU")
        
        # Get instruction info
        instruction_info = self.instruction_set.decode(opcode)
        mnemonic, handler = instruction_info
        
        if handler:
            # If the instruction takes a ModR/M byte, fetch it
            if "r/m" in mnemonic:
                modrm = self.fetch_byte()
                handler(modrm)
            else:
                handler()
            self.instruction_count += 1
            return True
        else:
            print(f"Unimplemented opcode: 0x{opcode:02X}")
            return False
    
    def run(self, max_instructions=None):
        """Run the CPU until halted or max_instructions reached."""
        instruction_counter = 0
        
        while not self.halted:
            if max_instructions is not None and instruction_counter >= max_instructions:
                break
            
            if not self.execute_instruction():
                break
            
            instruction_counter += 1
        
        return instruction_counter
    
    def get_register_state(self):
        """Return a dictionary with the current state of all registers."""
        state = {}
        for reg, name in self.REGISTER_NAMES.items():
            state[name] = self.registers[reg]
        return state
    
    def get_flag_state(self):
        """Return a dictionary with the current state of all flags."""
        state = {}
        for flag, name in self.FLAG_NAMES.items():
            state[name] = self.get_flag(flag)
        return state
    
    def set_ip(self, address):
        """Set the instruction pointer to a specific address."""
        self.registers[self.IP] = address & 0xFFFF
