"""
Assembler module for 8086 simulator.
Implements the assembler that translates assembly code to machine code.
"""

import re
import os

class Assembler:
    """8086 assembler for parsing and loading assembly code into memory."""
    
    def __init__(self, cpu, memory):
        """Initialize the assembler with CPU and memory references."""
        self.cpu = cpu
        self.memory = memory
        self.labels = {}  # Label to address mapping
        self.current_address = 0
        self.segment_prefix = None  # Current segment override prefix
        
        # Initialize opcode table
        self._init_opcode_table()
    
    def _init_opcode_table(self):
        """Initialize the opcode mapping table."""
        self.opcodes = {
            # MOV instructions
            'MOV': {
                'r8,r8': 0x88,       # MOV r/m8, r8
                'r16,r16': 0x89,     # MOV r/m16, r16
                'r8,imm8': 0xB0,     # MOV r8, imm8 (base, +reg for different registers)
                'r16,imm16': 0xB8,   # MOV r16, imm16 (base, +reg for different registers)
                'mem,r8': 0x88,      # MOV m8, r8
                'mem,r16': 0x89,     # MOV m16, r16
                'r8,mem': 0x8A,      # MOV r8, m8
                'r16,mem': 0x8B,     # MOV r16, m16
            },
            # ADD instructions
            'ADD': {
                'r8,r8': 0x00,       # ADD r/m8, r8
                'r16,r16': 0x01,     # ADD r/m16, r16
                'r8,imm8': 0x80,     # ADD r/m8, imm8 (group 1)
                'r16,imm16': 0x81,   # ADD r/m16, imm16 (group 1)
                'mem,r8': 0x00,      # ADD m8, r8
                'mem,r16': 0x01,     # ADD m16, r16
                'r8,mem': 0x02,      # ADD r8, m8
                'r16,mem': 0x03,     # ADD r16, m16
                'AL,imm8': 0x04,     # ADD AL, imm8
                'AX,imm16': 0x05,    # ADD AX, imm16
            },
            # SUB instructions
            'SUB': {
                'r8,r8': 0x28,       # SUB r/m8, r8
                'r16,r16': 0x29,     # SUB r/m16, r16
                'r8,imm8': 0x80,     # SUB r/m8, imm8 (group 1)
                'r16,imm16': 0x81,   # SUB r/m16, imm16 (group 1)
                'mem,r8': 0x28,      # SUB m8, r8
                'mem,r16': 0x29,     # SUB m16, r16
                'r8,mem': 0x2A,      # SUB r8, m8
                'r16,mem': 0x2B,     # SUB r16, m16
                'AL,imm8': 0x2C,     # SUB AL, imm8
                'AX,imm16': 0x2D,    # SUB AX, imm16
            },
            # Jump instructions
            'JMP': {
                'rel8': 0xEB,        # JMP rel8
                'rel16': 0xE9,       # JMP rel16
            },
            'JE': {'rel8': 0x74},    # JE rel8
            'JNE': {'rel8': 0x75},   # JNE rel8
            'JL': {'rel8': 0x7C},    # JL rel8
            'JLE': {'rel8': 0x7E},   # JLE rel8
            'JG': {'rel8': 0x7F},    # JG rel8
            'JGE': {'rel8': 0x7D},   # JGE rel8
            'JB': {'rel8': 0x72},    # JB rel8
            'JBE': {'rel8': 0x76},   # JBE rel8
            'JA': {'rel8': 0x77},    # JA rel8
            'JAE': {'rel8': 0x73},   # JAE rel8
            
            # Call and Return
            'CALL': {'rel16': 0xE8}, # CALL rel16
            'RET': {None: 0xC3},     # RET
            
            # Stack operations
            'PUSH': {
                'r16': 0x50,         # PUSH r16 (base, +reg for different registers)
                'imm16': 0x68,       # PUSH imm16
            },
            'POP': {
                'r16': 0x58,         # POP r16 (base, +reg for different registers)
            },
            
            # Miscellaneous
            'NOP': {None: 0x90},     # NOP
            'HLT': {None: 0xF4},     # HLT
            'INT': {'imm8': 0xCD},   # INT imm8
        }
        
        # Register encoding
        self.registers = {
            'AL': (0, 8), 'CL': (1, 8), 'DL': (2, 8), 'BL': (3, 8),
            'AH': (4, 8), 'CH': (5, 8), 'DH': (6, 8), 'BH': (7, 8),
            'AX': (0, 16), 'CX': (1, 16), 'DX': (2, 16), 'BX': (3, 16),
            'SP': (4, 16), 'BP': (5, 16), 'SI': (6, 16), 'DI': (7, 16),
            'CS': (8, 16), 'DS': (9, 16), 'SS': (10, 16), 'ES': (11, 16)
        }
    
    def load_program(self, filename):
        """Load an assembly program from a file into memory."""
        # Reset state
        self.labels = {}
        self.current_address = 0
        self.segment_prefix = None
        
        # First pass: gather labels
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        for line in lines:
            # Remove comments
            comment_pos = line.find(';')
            if comment_pos != -1:
                line = line[:comment_pos]
            
            # Strip whitespace
            line = line.strip()
            if not line:
                continue
            
            # Check for labels
            if ':' in line:
                label, _, rest = line.partition(':')
                label = label.strip()
                self.labels[label] = self.current_address
                line = rest.strip()
                if not line:
                    continue
            
            cleaned_lines.append(line)
            
            # Calculate instruction size
            size = self._get_instruction_size(line)
            self.current_address += size
        
        # Reset address for second pass
        self.current_address = 0
        
        # Second pass: assemble instructions
        for line in cleaned_lines:
            self._assemble_instruction(line)
        
        # Reset IP to start of program
        self.cpu.set_register(self.cpu.IP, 0)
    
    def _get_instruction_size(self, line):
        """Estimate the size of an instruction in bytes."""
        # This is a simplified implementation
        # In a real assembler, you would need to parse the instruction
        # and determine its exact encoding
        parts = line.split()
        mnemonic = parts[0].upper()
        
        # Default size for most instructions
        size = 2
        
        # Special cases
        if mnemonic in ['NOP', 'RET', 'HLT']:
            size = 1
        elif mnemonic in ['MOV', 'ADD', 'SUB', 'CMP']:
            # These instructions could be 2-6 bytes depending on operands
            if len(parts) > 1:
                operands = parts[1].split(',')
                if len(operands) == 2:
                    # Check for immediates, which add 1-2 bytes
                    if any(op.startswith(('0x', '0X', '#')) for op in operands):
                        size += 2
        elif mnemonic in ['JMP', 'CALL']:
            # These could be 2-3 bytes
            size = 3
        
        return size
    
    def _assemble_instruction(self, line):
        """Assemble a single instruction into memory."""
        parts = line.split()
        mnemonic = parts[0].upper()
        
        # Handle directives
        if mnemonic in ['.ORG', 'ORG']:
            address = self._parse_value(parts[1])
            self.current_address = address
            return
        
        # Parse operands if any
        operands = []
        if len(parts) > 1:
            operands_str = parts[1]
            operands = [op.strip() for op in operands_str.split(',')]
        
        # Encode the instruction
        machine_code = self._encode_instruction(mnemonic, operands)
        
        # Write machine code to memory
        for byte in machine_code:
            self.memory.write_byte(self.current_address, byte)
            self.current_address += 1
    
    def _encode_instruction(self, mnemonic, operands):
        """Encode an instruction into machine code bytes."""
        # Simplified encoding for common instructions
        machine_code = []
        
        # Handle each instruction type
        if mnemonic == 'NOP':
            machine_code.append(0x90)
        elif mnemonic == 'HLT':
            machine_code.append(0xF4)
        elif mnemonic == 'RET':
            machine_code.append(0xC3)
        elif mnemonic == 'MOV':
            if len(operands) != 2:
                raise ValueError(f"MOV requires 2 operands, got {len(operands)}")
            
            dest, src = operands
            
            # Determine operand types
            dest_type = self._get_operand_type(dest)
            src_type = self._get_operand_type(src)
            
            # Handle various MOV combinations
            if dest_type == 'register' and src_type == 'immediate':
                reg_num, reg_size = self.registers[dest.upper()]
                
                if reg_size == 8:
                    # MOV r8, imm8
                    opcode = 0xB0 + reg_num
                    machine_code.append(opcode)
                    machine_code.append(self._parse_value(src) & 0xFF)
                else:
                    # MOV r16, imm16
                    opcode = 0xB8 + reg_num
                    machine_code.append(opcode)
                    value = self._parse_value(src)
                    machine_code.append(value & 0xFF)
                    machine_code.append((value >> 8) & 0xFF)
            elif dest_type == 'register' and src_type == 'register':
                dest_num, dest_size = self.registers[dest.upper()]
                src_num, src_size = self.registers[src.upper()]
                
                if dest_size != src_size:
                    raise ValueError(f"Register size mismatch: {dest} ({dest_size}) and {src} ({src_size})")
                
                if dest_size == 8:
                    # MOV r8, r8
                    machine_code.append(0x8A)  # MOV r8, r/m8
                else:
                    # MOV r16, r16
                    machine_code.append(0x8B)  # MOV r16, r/m16
                
                # ModR/M byte: mod=11 (register to register), reg=src, r/m=dest
                modrm = 0xC0 | (src_num << 3) | dest_num
                machine_code.append(modrm)
        
        elif mnemonic == 'ADD':
            if len(operands) != 2:
                raise ValueError(f"ADD requires 2 operands, got {len(operands)}")
            
            dest, src = operands
            
            # Determine operand types
            dest_type = self._get_operand_type(dest)
            src_type = self._get_operand_type(src)
            
            # Handle ADD AL, imm8 and ADD AX, imm16 special cases
            if dest.upper() == 'AL' and src_type == 'immediate':
                machine_code.append(0x04)  # ADD AL, imm8
                machine_code.append(self._parse_value(src) & 0xFF)
            elif dest.upper() == 'AX' and src_type == 'immediate':
                machine_code.append(0x05)  # ADD AX, imm16
                value = self._parse_value(src)
                machine_code.append(value & 0xFF)
                machine_code.append((value >> 8) & 0xFF)
            elif dest_type == 'register' and src_type == 'register':
                dest_num, dest_size = self.registers[dest.upper()]
                src_num, src_size = self.registers[src.upper()]
                
                if dest_size != src_size:
                    raise ValueError(f"Register size mismatch: {dest} ({dest_size}) and {src} ({src_size})")
                
                if dest_size == 8:
                    # ADD r8, r8
                    machine_code.append(0x02)  # ADD r8, r/m8
                else:
                    # ADD r16, r16
                    machine_code.append(0x03)  # ADD r16, r/m16
                
                # ModR/M byte: mod=11 (register to register), reg=dest, r/m=src
                modrm = 0xC0 | (dest_num << 3) | src_num
                machine_code.append(modrm)
        
        elif mnemonic == 'INT':
            if len(operands) != 1:
                raise ValueError(f"INT requires 1 operand, got {len(operands)}")
            
            interrupt_num = self._parse_value(operands[0])
            machine_code.append(0xCD)  # INT opcode
            machine_code.append(interrupt_num & 0xFF)
        
        elif mnemonic.startswith('J'):  # Jump instructions
            if len(operands) != 1:
                raise ValueError(f"{mnemonic} requires 1 operand, got {len(operands)}")
            
            target = operands[0]
            
            # Look up opcode for this jump type
            if mnemonic in self.opcodes and 'rel8' in self.opcodes[mnemonic]:
                opcode = self.opcodes[mnemonic]['rel8']
                machine_code.append(opcode)
                
                # Calculate relative offset
                if target in self.labels:
                    target_address = self.labels[target]
                    # The jump offset is relative to the next instruction
                    # which is 2 bytes after the current address (opcode + offset)
                    offset = target_address - (self.current_address + 2)
                    if not -128 <= offset <= 127:
                        raise ValueError(f"Jump target out of range for short jump: {offset}")
                    machine_code.append(offset & 0xFF)
                else:
                    raise ValueError(f"Unknown label: {target}")
        
        elif mnemonic == 'CALL':
            if len(operands) != 1:
                raise ValueError(f"CALL requires 1 operand, got {len(operands)}")
            
            target = operands[0]
            
            # CALL instruction
            machine_code.append(0xE8)  # CALL rel16
            
            # Calculate relative offset
            if target in self.labels:
                target_address = self.labels[target]
                # The call offset is relative to the next instruction
                # which is 3 bytes after the current address (opcode + offset)
                offset = target_address - (self.current_address + 3)
                machine_code.append(offset & 0xFF)
                machine_code.append((offset >> 8) & 0xFF)
            else:
                raise ValueError(f"Unknown label: {target}")
        
        else:
            raise ValueError(f"Unsupported instruction: {mnemonic}")
        
        return machine_code
    
    def _get_operand_type(self, operand):
        """Determine the type of an operand (register, immediate, memory)."""
        if operand.upper() in self.registers:
            return 'register'
        elif operand.startswith(('[', '(')) and operand.endswith((']', ')')):
            return 'memory'
        elif operand.isdigit() or operand.startswith(('0x', '0X', '#')):
            return 'immediate'
        elif operand in self.labels:
            return 'label'
        else:
            try:
                self._parse_value(operand)
                return 'immediate'
            except ValueError:
                return 'unknown'
    
    def _parse_value(self, value_str):
        """Parse a numeric value from different representations."""
        if isinstance(value_str, int):
            return value_str
        
        value_str = value_str.strip()
        
        # Hexadecimal
        if value_str.startswith(('0x', '0X')):
            return int(value_str[2:], 16)
        
        # Binary
        if value_str.startswith(('0b', '0B')):
            return int(value_str[2:], 2)
        
        # Decimal with immediate prefix
        if value_str.startswith('#'):
            return int(value_str[1:])
        
        # Decimal
        try:
            return int(value_str)
        except ValueError:
            if value_str in self.labels:
                return self.labels[value_str]
            raise ValueError(f"Invalid numeric value: {value_str}")
