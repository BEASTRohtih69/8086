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
        
        # Segment flags to track which section we're in
        self.in_data_segment = False
        self.in_code_segment = True
        self.in_stack_segment = False
        
        # Segment addresses (for .MODEL, .DATA, .CODE directives)
        self.segments = {
            'CODE': 0x0000,  # Default code segment
            'DATA': 0x0000,  # Default data segment
            'STACK': 0x0000  # Default stack segment
        }
        
        self.current_segment = 'CODE'  # Default to code segment
        self.variables = {}  # Variable to address mapping (for .DATA section)
        self.entry_point = None  # Entry point for the program
        
        # Model sizes (memory models in MASM)
        self.memory_models = {
            'TINY': {'CODE': 0x0100, 'DATA': 0x0100, 'STACK': 0x0100},
            'SMALL': {'CODE': 0x0100, 'DATA': 0x0200, 'STACK': 0x0300},
            'MEDIUM': {'CODE': 0x1000, 'DATA': 0x2000, 'STACK': 0x3000},
            'COMPACT': {'CODE': 0x0100, 'DATA': 0x1000, 'STACK': 0x2000},
            'LARGE': {'CODE': 0x1000, 'DATA': 0x2000, 'STACK': 0x3000},
            'HUGE': {'CODE': 0x1000, 'DATA': 0x2000, 'STACK': 0x3000}
        }
        
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
            'JZ': {'rel8': 0x74},     # JZ rel8 (alias for JE)
            'JNZ': {'rel8': 0x75},    # JNZ rel8 (alias for JNE)
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
            
            # DEC instructions
            'DEC': {
                'AX': 0x48,  # DEC AX
                'CX': 0x49,  # DEC CX
                'DX': 0x4A,  # DEC DX
                'BX': 0x4B,  # DEC BX
                'SP': 0x4C,  # DEC SP
                'BP': 0x4D,  # DEC BP
                'SI': 0x4E,  # DEC SI
                'DI': 0x4F,  # DEC DI
            },
            
            # Stack operations
            'PUSH': {
                'r16': 0x50,         # PUSH r16 (base, +reg for different registers)
                'imm16': 0x68,       # PUSH imm16
            },
            'POP': {
                'r16': 0x58,         # POP r16 (base, +reg for different registers)
            },
            
            # String Operations
            'MOVSB': {None: 0xA4},   # MOVSB
            'MOVSW': {None: 0xA5},   # MOVSW
            'CMPSB': {None: 0xA6},   # CMPSB
            'CMPSW': {None: 0xA7},   # CMPSW
            'STOSB': {None: 0xAA},   # STOSB
            'STOSW': {None: 0xAB},   # STOSW
            'LODSB': {None: 0xAC},   # LODSB
            'LODSW': {None: 0xAD},   # LODSW
            'SCASB': {None: 0xAE},   # SCASB
            'SCASW': {None: 0xAF},   # SCASW
            
            # String Repeat Prefixes
            'REP': {None: 0xF3},     # REP prefix
            'REPE': {None: 0xF3},    # REPE/REPZ prefix (same as REP)
            'REPZ': {None: 0xF3},    # REPE/REPZ prefix (same as REP)
            'REPNE': {None: 0xF2},   # REPNE/REPNZ prefix
            'REPNZ': {None: 0xF2},   # REPNE/REPNZ prefix (same as REPNE)
            
            # Processor Control
            'CLD': {None: 0xFC},     # Clear direction flag
            'STD': {None: 0xFD},     # Set direction flag
            'CLC': {None: 0xF8},     # Clear carry flag
            'STC': {None: 0xF9},     # Set carry flag
            'CLI': {None: 0xFA},     # Clear interrupt flag
            'STI': {None: 0xFB},     # Set interrupt flag
            'CMC': {None: 0xF5},     # Complement carry flag
            
            # LOOP Instructions
            'LOOP': {None: 0xE2},    # LOOP
            'LOOPE': {None: 0xE1},   # LOOPE/LOOPZ
            'LOOPZ': {None: 0xE1},   # LOOPE/LOOPZ
            'LOOPNE': {None: 0xE0},  # LOOPNE/LOOPNZ
            'LOOPNZ': {None: 0xE0},  # LOOPNE/LOOPNZ
            
            # Conversion Instructions
            'CBW': {None: 0x98},     # Convert Byte to Word
            'CWD': {None: 0x99},     # Convert Word to Doubleword
            
            # Flag Register Operations
            'LAHF': {None: 0x9F},    # Load AH from Flags
            'SAHF': {None: 0x9E},    # Store AH to Flags
            
            # Multiplication/Division Instructions
            'MUL': {'r8': 0xF6, 'r16': 0xF7},  # Unsigned multiply
            'DIV': {'r8': 0xF6, 'r16': 0xF7},  # Unsigned divide
            
            # Shift/Rotate Instructions
            'ROL': {'r8,1': 0xD0, 'r16,1': 0xD1, 'r8,CL': 0xD2, 'r16,CL': 0xD3},  # Rotate left
            'ROR': {'r8,1': 0xD0, 'r16,1': 0xD1, 'r8,CL': 0xD2, 'r16,CL': 0xD3},  # Rotate right
            
            # Logical Operations
            'AND': {
                'r8,r8': 0x20,       # AND r/m8, r8
                'r16,r16': 0x21,     # AND r/m16, r16
                'r8,imm8': 0x80,     # AND r/m8, imm8 (group 1)
                'r16,imm16': 0x81,   # AND r/m16, imm16 (group 1)
                'mem,r8': 0x20,      # AND m8, r8
                'mem,r16': 0x21,     # AND m16, r16
                'r8,mem': 0x22,      # AND r8, m8
                'r16,mem': 0x23,     # AND r16, m16
                'AL,imm8': 0x24,     # AND AL, imm8
                'AX,imm16': 0x25,    # AND AX, imm16
            },
            'OR': {
                'r8,r8': 0x08,       # OR r/m8, r8
                'r16,r16': 0x09,     # OR r/m16, r16
                'r8,imm8': 0x80,     # OR r/m8, imm8 (group 1)
                'r16,imm16': 0x81,   # OR r/m16, imm16 (group 1)
                'mem,r8': 0x08,      # OR m8, r8
                'mem,r16': 0x09,     # OR m16, r16
                'r8,mem': 0x0A,      # OR r8, m8
                'r16,mem': 0x0B,     # OR r16, m16
                'AL,imm8': 0x0C,     # OR AL, imm8
                'AX,imm16': 0x0D,    # OR AX, imm16
            },
            'XOR': {
                'r8,r8': 0x30,       # XOR r/m8, r8
                'r16,r16': 0x31,     # XOR r/m16, r16
                'r8,imm8': 0x80,     # XOR r/m8, imm8 (group 1)
                'r16,imm16': 0x81,   # XOR r/m16, imm16 (group 1)
                'mem,r8': 0x30,      # XOR m8, r8
                'mem,r16': 0x31,     # XOR m16, r16
                'r8,mem': 0x32,      # XOR r8, m8
                'r16,mem': 0x33,     # XOR r16, m16
                'AL,imm8': 0x34,     # XOR AL, imm8
                'AX,imm16': 0x35,    # XOR AX, imm16
            },
            'CMP': {
                'r8,r8': 0x38,       # CMP r/m8, r8
                'r16,r16': 0x39,     # CMP r/m16, r16
                'r8,imm8': 0x80,     # CMP r/m8, imm8 (group 1)
                'r16,imm16': 0x81,   # CMP r/m16, imm16 (group 1)
                'mem,r8': 0x38,      # CMP m8, r8
                'mem,r16': 0x39,     # CMP m16, r16
                'r8,mem': 0x3A,      # CMP r8, m8
                'r16,mem': 0x3B,     # CMP r16, m16
                'AL,imm8': 0x3C,     # CMP AL, imm8
                'AX,imm16': 0x3D,    # CMP AX, imm16
            },
            'TEST': {
                'r8,r8': 0x84,       # TEST r/m8, r8
                'r16,r16': 0x85,     # TEST r/m16, r16
                'r8,imm8': 0xF6,     # TEST r/m8, imm8 (group 3)
                'r16,imm16': 0xF7,   # TEST r/m16, imm16 (group 3)
                'mem,r8': 0x84,      # TEST m8, r8
                'mem,r16': 0x85,     # TEST m16, r16
                'AL,imm8': 0xA8,     # TEST AL, imm8
                'AX,imm16': 0xA9,    # TEST AX, imm16
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
        self.variables = {}
        self.current_address = 0
        self.segment_prefix = None
        self.current_segment = 'CODE'
        self.entry_point = None
        
        # Initialize segment flags
        in_data_segment = False
        in_code_segment = True
        in_stack_segment = False
        
        # Reset segments to defaults with fixed offsets
        self.segments = {
            'CODE': 0x0100,  # Start from 0x100 (like COM files)
            'DATA': 0x0200,  # Data starts at 0x200
            'STACK': 0x0300  # Stack starts at 0x300
        }
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return False
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
            
        # First pass: Calculate total size of each segment
        # and collect segment markers in the assembly file
        segment_markers = []  # [(line_index, segment_type), ...]
        proc_active = None
        
        processed_lines = []
        
        for line in lines:
            # Remove comments
            comment_pos = line.find(';')
            if comment_pos != -1:
                line = line[:comment_pos]
            
            # Strip whitespace
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            mnemonic = parts[0].upper()
            
            # Handle memory model directive
            if mnemonic == '.MODEL':
                model = parts[1].upper() if len(parts) > 1 else 'SMALL'
                if model in self.memory_models:
                    for segment, address in self.memory_models[model].items():
                        self.segments[segment] = address
                continue
            
            # Handle segment directives
            if mnemonic == '.STACK':
                in_data_segment = False
                in_code_segment = False
                self.current_segment = 'STACK'
                # Set SS register
                self.cpu.set_register(self.cpu.SS, self.segments['STACK'])
                if len(parts) > 1:
                    stack_size = self._parse_value(parts[1])
                    self.cpu.set_register(self.cpu.SP, stack_size)
                continue
            
            if mnemonic == '.DATA':
                in_data_segment = True
                in_code_segment = False
                self.current_segment = 'DATA'
                # Set current address to data segment
                self.current_address = self.segments['DATA']
                continue
            
            if mnemonic == '.CODE':
                in_data_segment = False
                in_code_segment = True
                self.current_segment = 'CODE'
                # Set current address to code segment
                self.current_address = self.segments['CODE']
                continue
            
            # Handle procedure directives
            if mnemonic == 'PROC':
                proc_active = parts[1] if len(parts) > 1 else None
                self.labels[proc_active] = self.current_address
                continue
            
            if mnemonic == 'ENDP':
                proc_active = None
                continue
            
            if mnemonic == 'END':
                # End of program, can set entry point if specified
                if len(parts) > 1:
                    entry_point = parts[1]
                    if entry_point in self.labels:
                        self.cpu.set_register(self.cpu.IP, self.labels[entry_point])
                continue
            
            # Handle variable definitions in data segment
            if self.in_data_segment and ' DB ' in line.upper():
                var_parts = line.split(' DB ', 1)
                var_name = var_parts[0].strip()
                self.variables[var_name] = self.current_address
                # We'll process the actual data in the second pass
                processed_lines.append(line)
                # Estimate size (rough estimate for now)
                data_value = var_parts[1].strip()
                if (data_value.startswith("'") and data_value.endswith("'")) or \
                   (data_value.startswith('"') and data_value.endswith('"')):
                    size = len(data_value) - 2  # Subtract quotes
                else:
                    # Comma-separated values
                    size = len(data_value.split(','))
                self.current_address += size
                continue
            
            # Check for procedures with format "label PROC"
            if ' PROC' in line.upper():
                parts = line.upper().split(' PROC')
                proc_name = parts[0].strip()
                # Store procedure name with all case variations
                self.labels[proc_name] = self.current_address
                self.labels[proc_name.lower()] = self.current_address
                self.labels[proc_name.upper()] = self.current_address
                continue
                
            # Check for regular labels with colon
            if ':' in line:
                label, _, rest = line.partition(':')
                label = label.strip()
                # Store label with all case variations
                self.labels[label] = self.current_address
                self.labels[label.lower()] = self.current_address
                self.labels[label.upper()] = self.current_address
                print(f"DEBUG - Label {label} defined at address {self.current_address:04X}")
                line = rest.strip()
                if not line:
                    continue
            
            # Add to processed lines for second pass
            processed_lines.append(line)
            
            # Calculate instruction size for address tracking
            size = self._get_instruction_size(line)
            self.current_address += size
        
        # Reset for second pass
        self.current_address = 0
        self.current_segment = 'CODE'
        in_data_segment = False
        in_code_segment = True
        
        # Second pass: perform a complete rewrite to fix segment handling
        print("\nSecond pass: rewriting segment handling")
        print(f"Segments: CODE={self.segments['CODE']}, DATA={self.segments['DATA']}, STACK={self.segments['STACK']}")
        print(f"Labels: {self.labels}")
        print(f"Variables: {self.variables}")
        
        # Clear memory 
        for addr in range(0, 0xFFFF, 256):
            for offset in range(256):
                self.memory.write_byte(addr + offset, 0)
            
        # Process DATA segment first
        self.current_segment = 'DATA'
        self.current_address = self.segments['DATA']
        print(f"Processing DATA segment at {self.current_address:04X}")
        
        # Initialize segment detection flags based on an initial pass
        in_data_segment = False
        in_code_segment = False
        in_stack_segment = False
        
        # Initial pass just to find segment markers
        current_section = None
        for i, line in enumerate(processed_lines):
            if not line.strip():
                continue
                
            parts = line.split()
            if not parts:
                continue
                
            mnemonic = parts[0].upper()
            
            print(f"Checking line: '{line}' - parsed mnemonic: '{mnemonic}'")
            
            # Match .DATA segment markers
            if mnemonic == '.DATA':
                current_section = 'DATA'
                print(f"Line {i+1}: Found DATA section marker")
            # Match .CODE segment markers
            elif mnemonic == '.CODE':
                current_section = 'CODE'
                print(f"Line {i+1}: Found CODE section marker")
            # Match .STACK segment markers
            elif mnemonic == '.STACK':
                current_section = 'STACK'
                print(f"Line {i+1}: Found STACK section marker")
            
        print(f"Initial section detection: {'Found sections' if current_section else 'No sections found'}")
        
        # If no section markers found, default to CODE section for backward compatibility
        if current_section is None:
            print("No section markers found, assuming all code is in CODE section")
            # Process everything as CODE
            in_code_segment = True
            in_data_segment = False
            in_stack_segment = False
        
        # Now do the actual data segment processing with proper flags
        in_data_segment = False
        for line in processed_lines:
            if not line.strip():
                continue
                
            parts = line.split()
            if not parts:
                continue
                
            mnemonic = parts[0].upper()
            
            print(f"DATA check: {line}")
            
            if mnemonic == '.DATA':
                in_data_segment = True
                in_code_segment = False
                in_stack_segment = False
                print(f"  Entering DATA segment")
                continue
                
            if mnemonic == '.CODE' or mnemonic == '.STACK':
                in_data_segment = False
                print(f"  Leaving DATA segment")
                continue
                
            if not in_data_segment:
                continue
                
            # Skip labels and directives
            if mnemonic.endswith(':') or mnemonic in ['.MODEL', 'END', 'PROC', 'ENDP']:
                print(f"  Skipping label/directive: {line}")
                continue
            
            print(f"DATA: Assembling at {self.current_address:04X}: {line}")
            self._assemble_instruction(line)
            
        # Process CODE segment next
        self.current_segment = 'CODE'
        self.current_address = self.segments['CODE'] 
        print(f"Processing CODE segment at {self.current_address:04X}")
        
        in_code_segment = False
        for line in processed_lines:
            if not line.strip():
                continue
                
            parts = line.split()
            if not parts:
                continue
                
            mnemonic = parts[0].upper()
            
            print(f"CODE check: {line}")
            
            if mnemonic == '.CODE':
                in_code_segment = True
                in_data_segment = False
                in_stack_segment = False
                print(f"  Entering CODE segment")
                continue
                
            if mnemonic == '.DATA':
                in_code_segment = False
                in_data_segment = True
                in_stack_segment = False
                print(f"  Leaving CODE segment, entering DATA")
                continue
                
            if mnemonic == '.STACK':
                in_code_segment = False
                in_data_segment = False
                in_stack_segment = True
                print(f"  Leaving CODE segment, entering STACK")
                continue
                
            if not in_code_segment:
                continue
                
            # Skip labels and directives
            if mnemonic.endswith(':') or mnemonic in ['.MODEL', 'END', 'PROC', 'ENDP']:
                print(f"  Skipping label/directive: {line}")
                continue
                
            print(f"CODE: Assembling at {self.current_address:04X}: {line}")
            self._assemble_instruction(line)
            
        # Finally, process STACK segment if needed
        self.current_segment = 'STACK'
        self.current_address = self.segments['STACK']
        print(f"Processing STACK segment at {self.current_address:04X}")
        
        in_stack_segment = False
        for line in processed_lines:
            if not line.strip():
                continue
                
            parts = line.split()
            mnemonic = parts[0].upper()
            
            if mnemonic == '.STACK':
                in_stack_segment = True
                # Handle stack size if specified
                if len(parts) > 1:
                    stack_size = self._parse_value(parts[1])
                    self.cpu.set_register(self.cpu.SS, self.segments['STACK'])
                    self.cpu.set_register(self.cpu.SP, stack_size)
                continue
                
            if mnemonic == '.DATA' or mnemonic == '.CODE':
                in_stack_segment = False
                continue
                
            if not in_stack_segment:
                continue
                
            # Skip labels and directives in stack segment
            if mnemonic.endswith(':') or mnemonic in ['.MODEL', 'END', 'PROC', 'ENDP']:
                continue
                
            print(f"STACK: Assembling at {self.current_address:04X}: {line}")
            self._assemble_instruction(line)
        
        # Make sure IP points to code segment (entry point)
        print(f"\nSetting entry point:")
        print(f"Entry point from END: {self.entry_point}")
        print(f"Labels: {self.labels}")
        print(f"Variables: {self.variables}")
        
        if self.entry_point is not None:
            # Entry point was specified with END directive
            self.cpu.set_register(self.cpu.IP, self.entry_point)
            print(f"Using specified entry point: {self.entry_point:04X}")
        elif 'start' in self.labels:
            # Use 'start' as a common entry point name
            self.cpu.set_register(self.cpu.IP, self.labels['start'])
            print(f"Using 'start' label as entry point: {self.labels['start']:04X}")
        elif 'main' in self.labels:
            # Default to main label if entry point not specified
            self.cpu.set_register(self.cpu.IP, self.labels['main'])
            print(f"Using 'main' label as entry point: {self.labels['main']:04X}")
        elif 'main' in self.variables:
            # Check variable map too (some labels might be stored there)
            self.cpu.set_register(self.cpu.IP, self.variables['main'])
            print(f"Using 'main' variable as entry point: {self.variables['main']:04X}")
        else:
            # No entry point found, default to the start of code segment
            self.cpu.set_register(self.cpu.IP, 0)
            print(f"No entry point found, defaulting to IP=0000")
        
        # Set CS to code segment
        self.cpu.set_register(self.cpu.CS, self.segments['CODE'])
        # Set DS to data segment
        self.cpu.set_register(self.cpu.DS, self.segments['DATA'])
    
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
        # Strip any comments from the line
        if ';' in line:
            line = line.split(';', 1)[0].strip()
            
        parts = line.split()
        if not parts:
            return  # Empty line after removing comments
            
        mnemonic = parts[0].upper()
        
        # Handle memory model directives
        if mnemonic == '.MODEL':
            if len(parts) > 1:
                model = parts[1].upper()
                if model in self.memory_models:
                    # Set the segment addresses based on the memory model
                    for segment, address in self.memory_models[model].items():
                        self.segments[segment] = address
            return
        
        # Handle segment directives
        if mnemonic == '.STACK':
            self.current_segment = 'STACK'
            # Set stack size if specified
            if len(parts) > 1:
                stack_size = self._parse_value(parts[1])
                # Set SS and SP registers
                self.cpu.set_register(self.cpu.SS, self.segments['STACK'])
                self.cpu.set_register(self.cpu.SP, stack_size)
            return
        
        if mnemonic == '.DATA':
            self.current_segment = 'DATA'
            # Set DS register to data segment address
            self.cpu.set_register(self.cpu.DS, self.segments['DATA'])
            # Reset current address to start of data segment
            self.current_address = self.segments['DATA']
            return
        
        if mnemonic == '.CODE':
            self.current_segment = 'CODE'
            # Set CS register to code segment address
            self.cpu.set_register(self.cpu.CS, self.segments['CODE'])
            # Reset current address to start of code segment
            self.current_address = self.segments['CODE']
            return
        
        # Handle procedure directives
        if mnemonic == 'PROC':
            # Save the procedure name
            if len(parts) > 1:
                proc_name = parts[1]
                # Store with all case variations for flexibility
                self.labels[proc_name] = self.current_address
                self.labels[proc_name.lower()] = self.current_address
                self.labels[proc_name.upper()] = self.current_address
            return
        
        if mnemonic == 'ENDP':
            # End of procedure
            return
        
        if mnemonic == 'END':
            # End of program with optional entry point
            if len(parts) > 1:
                entry_point = parts[1]
                # Store entry point with all case variations
                entry_lower = entry_point.lower()
                entry_upper = entry_point.upper()
                
                # Check if the entry point is defined
                if entry_point in self.labels:
                    self.entry_point = self.labels[entry_point]
                elif entry_lower in self.labels:
                    self.entry_point = self.labels[entry_lower]
                elif entry_upper in self.labels:
                    self.entry_point = self.labels[entry_upper]
                else:
                    print(f"Warning: Entry point {entry_point} not found in labels")
            return
        
        # Handle variable/label definition with DB (Define Byte)
        if len(parts) >= 3 and parts[1].upper() == 'DB':
            var_name = parts[0]
            # Save variable address with all case variations for flexibility
            self.variables[var_name] = self.current_address
            self.variables[var_name.lower()] = self.current_address
            self.variables[var_name.upper()] = self.current_address
            
            # Process the data
            rest = ' '.join(parts[2:])
            # Check if it's a string in quotes
            if (rest.startswith("'") and rest.endswith("'")) or (rest.startswith('"') and rest.endswith('"')):
                # String literal
                string_value = rest[1:-1]
                for char in string_value:
                    self.memory.write_byte(self.current_address, ord(char))
                    self.current_address += 1
            else:
                # Byte values separated by commas
                for value_str in rest.split(','):
                    value = self._parse_value(value_str.strip())
                    self.memory.write_byte(self.current_address, value & 0xFF)
                    self.current_address += 1
            return
        
        # Handle data definition directives
        if mnemonic == 'DB':
            # Define byte
            if len(parts) > 1:
                rest = ' '.join(parts[1:])
                # Check if it's a string in quotes
                if (rest.startswith("'") and rest.endswith("'")) or (rest.startswith('"') and rest.endswith('"')):
                    # String literal
                    string_value = rest[1:-1]
                    for char in string_value:
                        self.memory.write_byte(self.current_address, ord(char))
                        self.current_address += 1
                else:
                    # Byte values separated by commas
                    for value_str in rest.split(','):
                        value = self._parse_value(value_str.strip())
                        self.memory.write_byte(self.current_address, value & 0xFF)
                        self.current_address += 1
            return
        
        # Handle ORG directive (set current address)
        if mnemonic in ['.ORG', 'ORG']:
            address = self._parse_value(parts[1])
            self.current_address = address
            return
        
        # Special handling for OFFSET operator
        parsed_operands = []
        if len(parts) > 1:
            operands_str = ' '.join(parts[1:])
            # Split on commas, but respect parentheses and quotes
            operands = []
            current = ""
            in_quotes = False
            paren_level = 0
            
            for char in operands_str:
                if char == ',' and not in_quotes and paren_level == 0:
                    operands.append(current.strip())
                    current = ""
                else:
                    if char == '"' or char == "'":
                        in_quotes = not in_quotes
                    elif char == '(' or char == '[':
                        paren_level += 1
                    elif char == ')' or char == ']':
                        paren_level -= 1
                    current += char
            
            if current:
                operands.append(current.strip())
            
            # Process each operand
            for operand in operands:
                # Handle OFFSET operator
                if 'OFFSET' in operand.upper():
                    label_orig = operand.upper().replace('OFFSET', '').strip()
                    # Try with different case variations
                    label_lower = label_orig.lower()
                    label_upper = label_orig.upper()
                    
                    # Check variables first
                    if label_orig in self.variables:
                        parsed_operands.append(str(self.variables[label_orig]))
                    elif label_lower in self.variables:
                        parsed_operands.append(str(self.variables[label_lower]))
                    elif label_upper in self.variables:
                        parsed_operands.append(str(self.variables[label_upper]))
                    # Then check labels
                    elif label_orig in self.labels:
                        parsed_operands.append(str(self.labels[label_orig]))
                    elif label_lower in self.labels:
                        parsed_operands.append(str(self.labels[label_lower]))
                    elif label_upper in self.labels:
                        parsed_operands.append(str(self.labels[label_upper]))
                    else:
                        raise ValueError(f"Unknown label for OFFSET: {label_orig}, tried {label_lower} and {label_upper} too")
                # Handle @DATA pseudo-register
                elif '@DATA' in operand.upper():
                    # @DATA refers to the data segment address
                    parsed_operands.append(str(self.segments['DATA']))
                else:
                    parsed_operands.append(operand)
        
        # Encode the instruction
        machine_code = self._encode_instruction(mnemonic, parsed_operands)
        
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
            
        # Conversion instructions with no operands
        elif mnemonic == 'CBW':
            machine_code.append(0x98)
        elif mnemonic == 'CWD':
            machine_code.append(0x99)
            
        # Flag register operations with no operands
        elif mnemonic == 'LAHF':
            machine_code.append(0x9F)
        elif mnemonic == 'SAHF':
            machine_code.append(0x9E)
        # Processor control instructions (flag operations)
        elif mnemonic == 'CLD':
            machine_code.append(0xFC)  # Clear direction flag
        elif mnemonic == 'STD':
            machine_code.append(0xFD)  # Set direction flag
        elif mnemonic == 'CLC':
            machine_code.append(0xF8)  # Clear carry flag
        elif mnemonic == 'STC':
            machine_code.append(0xF9)  # Set carry flag
        elif mnemonic == 'CLI':
            machine_code.append(0xFA)  # Clear interrupt flag
        elif mnemonic == 'STI':
            machine_code.append(0xFB)  # Set interrupt flag
        elif mnemonic == 'CMC':
            machine_code.append(0xF5)  # Complement carry flag
        # String operations
        elif mnemonic == 'MOVSB':
            machine_code.append(0xA4)  # Move byte from string to string
        elif mnemonic == 'MOVSW':
            machine_code.append(0xA5)  # Move word from string to string
        elif mnemonic == 'CMPSB':
            machine_code.append(0xA6)  # Compare bytes in string
        elif mnemonic == 'CMPSW':
            machine_code.append(0xA7)  # Compare words in string
        elif mnemonic == 'STOSB':
            machine_code.append(0xAA)  # Store AL in string
        elif mnemonic == 'STOSW':
            machine_code.append(0xAB)  # Store AX in string
        elif mnemonic == 'LODSB':
            machine_code.append(0xAC)  # Load byte from string to AL
        elif mnemonic == 'LODSW':
            machine_code.append(0xAD)  # Load word from string to AX
        elif mnemonic == 'SCASB':
            machine_code.append(0xAE)  # Scan string for byte equal to AL
        elif mnemonic == 'SCASW':
            machine_code.append(0xAF)  # Scan string for word equal to AX
        # String repeat prefixes
        elif mnemonic == 'REP' or mnemonic == 'REPE' or mnemonic == 'REPZ':
            machine_code.append(0xF3)  # REP/REPE/REPZ prefix
        elif mnemonic == 'REPNE' or mnemonic == 'REPNZ':
            machine_code.append(0xF2)  # REPNE/REPNZ prefix
        elif mnemonic == 'PUSH':
            if len(operands) != 1:
                raise ValueError(f"PUSH requires 1 operand, got {len(operands)}")
            
            reg = operands[0]
            reg_type = self._get_operand_type(reg)
            
            if reg_type == 'register':
                reg_num, reg_size = self.registers[reg.upper()]
                
                if reg_size == 16:  # Only 16-bit registers can be pushed
                    opcode = 0x50 + reg_num
                    machine_code.append(opcode)
                else:
                    raise ValueError(f"Cannot PUSH 8-bit register {reg}")
            else:
                raise ValueError(f"Unsupported PUSH operand type: {reg_type}")
        elif mnemonic == 'POP':
            if len(operands) != 1:
                raise ValueError(f"POP requires 1 operand, got {len(operands)}")
            
            reg = operands[0]
            reg_type = self._get_operand_type(reg)
            
            if reg_type == 'register':
                reg_num, reg_size = self.registers[reg.upper()]
                
                if reg_size == 16:  # Only 16-bit registers can be popped
                    opcode = 0x58 + reg_num
                    machine_code.append(opcode)
                else:
                    raise ValueError(f"Cannot POP 8-bit register {reg}")
            else:
                raise ValueError(f"Unsupported POP operand type: {reg_type}")
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
                
        elif mnemonic == 'SUB':
            if len(operands) != 2:
                raise ValueError(f"SUB requires 2 operands, got {len(operands)}")
            
            dest, src = operands
            
            # Determine operand types
            dest_type = self._get_operand_type(dest)
            src_type = self._get_operand_type(src)
            
            # Handle SUB AL, imm8 and SUB AX, imm16 special cases
            if dest.upper() == 'AL' and src_type == 'immediate':
                machine_code.append(0x2C)  # SUB AL, imm8
                machine_code.append(self._parse_value(src) & 0xFF)
            elif dest.upper() == 'AX' and src_type == 'immediate':
                machine_code.append(0x2D)  # SUB AX, imm16
                value = self._parse_value(src)
                machine_code.append(value & 0xFF)
                machine_code.append((value >> 8) & 0xFF)
            elif dest_type == 'register' and src_type == 'immediate':
                # SUB r/m16, imm16
                reg_num, reg_size = self.registers[dest.upper()]
                if reg_size == 16:
                    # SUB r16, imm16
                    machine_code.append(0x81)  # SUB r/m16, imm16
                    modrm = 0xE8 | reg_num  # 0xE8 = 11101000 (mod=11, reg=101 for SUB, r/m=reg)
                    machine_code.append(modrm)
                    
                    value = self._parse_value(src)
                    machine_code.append(value & 0xFF)
                    machine_code.append((value >> 8) & 0xFF)
                else:
                    # SUB r8, imm8
                    machine_code.append(0x80)  # SUB r/m8, imm8
                    modrm = 0xE8 | reg_num  # 0xE8 = 11101000 (mod=11, reg=101 for SUB, r/m=reg)
                    machine_code.append(modrm)
                    
                    machine_code.append(self._parse_value(src) & 0xFF)
            elif dest_type == 'register' and src_type == 'register':
                dest_num, dest_size = self.registers[dest.upper()]
                src_num, src_size = self.registers[src.upper()]
                
                if dest_size != src_size:
                    raise ValueError(f"Register size mismatch: {dest} ({dest_size}) and {src} ({src_size})")
                
                if dest_size == 8:
                    # SUB r8, r8
                    machine_code.append(0x2A)  # SUB r8, r/m8
                else:
                    # SUB r16, r16
                    machine_code.append(0x2B)  # SUB r16, r/m16
                
                # ModR/M byte: mod=11 (register to register), reg=dest, r/m=src
                modrm = 0xC0 | (dest_num << 3) | src_num
                machine_code.append(modrm)
                
        elif mnemonic == 'CMP':
            if len(operands) != 2:
                raise ValueError(f"CMP requires 2 operands, got {len(operands)}")
            
            dest, src = operands
            
            # Determine operand types
            dest_type = self._get_operand_type(dest)
            src_type = self._get_operand_type(src)
            
            # Handle CMP AL, imm8 and CMP AX, imm16 special cases
            if dest.upper() == 'AL' and src_type == 'immediate':
                machine_code.append(0x3C)  # CMP AL, imm8
                machine_code.append(self._parse_value(src) & 0xFF)
            elif dest.upper() == 'AX' and src_type == 'immediate':
                machine_code.append(0x3D)  # CMP AX, imm16
                value = self._parse_value(src)
                machine_code.append(value & 0xFF)
                machine_code.append((value >> 8) & 0xFF)
            elif dest_type == 'register' and src_type == 'immediate':
                # CMP r/m16, imm16
                reg_num, reg_size = self.registers[dest.upper()]
                if reg_size == 16:
                    # CMP r16, imm16
                    machine_code.append(0x81)  # CMP r/m16, imm16
                    modrm = 0xF8 | reg_num  # 0xF8 = 11111000 (mod=11, reg=111 for CMP, r/m=reg)
                    machine_code.append(modrm)
                    
                    value = self._parse_value(src)
                    machine_code.append(value & 0xFF)
                    machine_code.append((value >> 8) & 0xFF)
                else:
                    # CMP r8, imm8
                    machine_code.append(0x80)  # CMP r/m8, imm8
                    modrm = 0xF8 | reg_num  # 0xF8 = 11111000 (mod=11, reg=111 for CMP, r/m=reg)
                    machine_code.append(modrm)
                    
                    machine_code.append(self._parse_value(src) & 0xFF)
            elif dest_type == 'register' and src_type == 'register':
                dest_num, dest_size = self.registers[dest.upper()]
                src_num, src_size = self.registers[src.upper()]
                
                if dest_size != src_size:
                    raise ValueError(f"Register size mismatch: {dest} ({dest_size}) and {src} ({src_size})")
                
                if dest_size == 8:
                    # CMP r8, r8
                    machine_code.append(0x3A)  # CMP r8, r/m8
                else:
                    # CMP r16, r16
                    machine_code.append(0x3B)  # CMP r16, r/m16
                
                # ModR/M byte: mod=11 (register to register), reg=dest, r/m=src
                modrm = 0xC0 | (dest_num << 3) | src_num
                machine_code.append(modrm)
        
        # Multiplication and Division instructions
        elif mnemonic == 'MUL':
            if len(operands) != 1:
                raise ValueError(f"MUL requires 1 operand, got {len(operands)}")
            
            operand = operands[0]
            operand_type = self._get_operand_type(operand)
            
            if operand_type == 'register':
                reg_num, reg_size = self.registers[operand.upper()]
                
                if reg_size == 8:
                    # MUL r8 - Multiply AL by r8, result in AX
                    machine_code.append(0xF6)  # Group 4 byte operations
                    # ModR/M byte: mod=11 (register mode), reg=100 (MUL opcode), r/m=register
                    modrm = 0xE0 | reg_num  # 0xE0 = 11100000 (mod=11, reg=100 for MUL, r/m=reg)
                    machine_code.append(modrm)
                else:
                    # MUL r16 - Multiply AX by r16, result in DX:AX
                    machine_code.append(0xF7)  # Group 4 word operations
                    # ModR/M byte: mod=11 (register mode), reg=100 (MUL opcode), r/m=register
                    modrm = 0xE0 | reg_num  # 0xE0 = 11100000 (mod=11, reg=100 for MUL, r/m=reg)
                    machine_code.append(modrm)
            else:
                raise ValueError(f"Unsupported MUL operand type: {operand_type}")
                
        elif mnemonic == 'DIV':
            if len(operands) != 1:
                raise ValueError(f"DIV requires 1 operand, got {len(operands)}")
            
            operand = operands[0]
            operand_type = self._get_operand_type(operand)
            
            if operand_type == 'register':
                reg_num, reg_size = self.registers[operand.upper()]
                
                if reg_size == 8:
                    # DIV r8 - Divide AX by r8, quotient in AL, remainder in AH
                    machine_code.append(0xF6)  # Group 4 byte operations
                    # ModR/M byte: mod=11 (register mode), reg=110 (DIV opcode), r/m=register
                    modrm = 0xF0 | reg_num  # 0xF0 = 11110000 (mod=11, reg=110 for DIV, r/m=reg)
                    machine_code.append(modrm)
                else:
                    # DIV r16 - Divide DX:AX by r16, quotient in AX, remainder in DX
                    machine_code.append(0xF7)  # Group 4 word operations
                    # ModR/M byte: mod=11 (register mode), reg=110 (DIV opcode), r/m=register
                    modrm = 0xF0 | reg_num  # 0xF0 = 11110000 (mod=11, reg=110 for DIV, r/m=reg)
                    machine_code.append(modrm)
            else:
                raise ValueError(f"Unsupported DIV operand type: {operand_type}")
                
        # Shift/Rotate instructions
        elif mnemonic == 'ROL' or mnemonic == 'ROR':
            if len(operands) != 2:
                raise ValueError(f"{mnemonic} requires 2 operands, got {len(operands)}")
            
            dest, count = operands
            dest_type = self._get_operand_type(dest)
            
            if dest_type != 'register':
                raise ValueError(f"Unsupported {mnemonic} destination type: {dest_type}")
                
            reg_num, reg_size = self.registers[dest.upper()]
            
            # Determine if count is 1 or CL register
            if count == '1':
                # ROL/ROR r8/r16, 1
                if reg_size == 8:
                    machine_code.append(0xD0)  # Shift/rotate r/m8 by 1
                else:
                    machine_code.append(0xD1)  # Shift/rotate r/m16 by 1
                    
                # ModR/M byte: mod=11 (register mode), reg=000 for ROL or 001 for ROR, r/m=register
                if mnemonic == 'ROL':
                    modrm = 0xC0 | (0 << 3) | reg_num  # reg=000 for ROL
                else:  # ROR
                    modrm = 0xC0 | (1 << 3) | reg_num  # reg=001 for ROR
                machine_code.append(modrm)
                
            elif count.upper() == 'CL':
                # ROL/ROR r8/r16, CL
                if reg_size == 8:
                    machine_code.append(0xD2)  # Shift/rotate r/m8 by CL
                else:
                    machine_code.append(0xD3)  # Shift/rotate r/m16 by CL
                    
                # ModR/M byte: mod=11 (register mode), reg=000 for ROL or 001 for ROR, r/m=register
                if mnemonic == 'ROL':
                    modrm = 0xC0 | (0 << 3) | reg_num  # reg=000 for ROL
                else:  # ROR
                    modrm = 0xC0 | (1 << 3) | reg_num  # reg=001 for ROR
                machine_code.append(modrm)
            else:
                # For other immediate counts, would need to handle specially
                raise ValueError(f"Unsupported {mnemonic} count: {count}, must be 1 or CL")
        
        elif mnemonic == 'INT':
            if len(operands) != 1:
                raise ValueError(f"INT requires 1 operand, got {len(operands)}")
            
            interrupt_num = self._parse_value(operands[0])
            machine_code.append(0xCD)  # INT opcode
            machine_code.append(interrupt_num & 0xFF)
        
        elif mnemonic.startswith('J') or mnemonic.startswith('LOOP'):  # Jump and loop instructions
            if len(operands) != 1:
                raise ValueError(f"{mnemonic} requires 1 operand, got {len(operands)}")
            
            target = operands[0]
            
            # Look up opcode for this instruction type
            if mnemonic.startswith('LOOP'):
                if mnemonic == 'LOOP':
                    opcode = 0xE2
                elif mnemonic == 'LOOPE' or mnemonic == 'LOOPZ':
                    opcode = 0xE1
                elif mnemonic == 'LOOPNE' or mnemonic == 'LOOPNZ':
                    opcode = 0xE0
                else:
                    raise ValueError(f"Unknown LOOP instruction: {mnemonic}")
                    
                machine_code.append(opcode)
                
                # Calculate relative offset for LOOP
                target_address = None
                
                # Check for the label in different case formats
                if target in self.labels:
                    target_address = self.labels[target]
                elif target.lower() in self.labels:
                    target_address = self.labels[target.lower()]
                elif target.upper() in self.labels:
                    target_address = self.labels[target.upper()]
                    
                if target_address is not None:
                    # The loop offset is relative to the next instruction
                    # which is 2 bytes after the current address (opcode + offset)
                    offset = target_address - (self.current_address + 2)
                    if not -128 <= offset <= 127:
                        raise ValueError(f"Loop target out of range for short jump: {offset}")
                    
                    machine_code.append(offset & 0xFF)
                    
                    # Print debug info
                    print(f"LOOP {mnemonic} to {target}: from {self.current_address + 2:04X} to {target_address:04X}, offset {offset}")
                else:
                    print(f"Label {target} not found. Available labels: {list(self.labels.keys())}")
                    raise ValueError(f"Unknown label: {target}")
                
            # For jumps (J*)
            elif mnemonic in self.opcodes and 'rel8' in self.opcodes[mnemonic]:
                opcode = self.opcodes[mnemonic]['rel8']
                machine_code.append(opcode)
                
                # Calculate relative offset for jumps
                target_address = None
                
                # Check for the label in different case formats
                if target in self.labels:
                    target_address = self.labels[target]
                elif target.lower() in self.labels:
                    target_address = self.labels[target.lower()]
                elif target.upper() in self.labels:
                    target_address = self.labels[target.upper()]
                
                if target_address is not None:
                    # The jump offset is relative to the next instruction
                    # which is 2 bytes after the current address (opcode + offset)
                    offset = target_address - (self.current_address + 2)
                    if not -128 <= offset <= 127:
                        raise ValueError(f"Jump target out of range for short jump: {offset}")
                    
                    machine_code.append(offset & 0xFF)
                    
                    # Print debug info
                    print(f"JUMP {mnemonic} to {target}: from {self.current_address + 2:04X} to {target_address:04X}, offset {offset}")
                else:
                    print(f"Label {target} not found. Available labels: {list(self.labels.keys())}")
                    raise ValueError(f"Unknown label: {target}")
        
        elif mnemonic == 'CALL':
            if len(operands) != 1:
                raise ValueError(f"CALL requires 1 operand, got {len(operands)}")
            
            target = operands[0]
            
            # CALL instruction
            machine_code.append(0xE8)  # CALL rel16
            
            # Calculate relative offset for CALL
            target_address = None
            
            # Check for the label in different case formats
            if target in self.labels:
                target_address = self.labels[target]
            elif target.lower() in self.labels:
                target_address = self.labels[target.lower()]
            elif target.upper() in self.labels:
                target_address = self.labels[target.upper()]
            
            if target_address is not None:
                # The call offset is relative to the next instruction
                # which is 3 bytes after the current address (opcode + offset)
                offset = target_address - (self.current_address + 3)
                machine_code.append(offset & 0xFF)
                machine_code.append((offset >> 8) & 0xFF)
                
                # Print debug info
                print(f"CALL to {target}: from {self.current_address + 3:04X} to {target_address:04X}, offset {offset}")
            else:
                print(f"Label {target} not found. Available labels: {list(self.labels.keys())}")
                raise ValueError(f"Unknown label: {target}")
        
        elif mnemonic == 'DEC':
            if len(operands) != 1:
                raise ValueError(f"DEC requires 1 operand, got {len(operands)}")
            
            reg = operands[0].upper()
            
            # DEC register (16-bit)
            if reg in self.registers:
                reg_num, reg_size = self.registers[reg]
                
                if reg_size == 16:
                    # Check that it's one of the main registers (AX, CX, DX, BX, SP, BP, SI, DI)
                    if reg in ['AX', 'CX', 'DX', 'BX', 'SP', 'BP', 'SI', 'DI']:
                        # DEC r16 - opcode is 0x48 + register number
                        opcode = 0x48 + reg_num
                        machine_code.append(opcode)
                    else:
                        raise ValueError(f"DEC not supported for register {reg}")
                else:
                    raise ValueError(f"DEC for 8-bit registers not implemented yet")
            else:
                raise ValueError(f"Unknown register: {reg}")
                
        elif mnemonic == 'INC':
            if len(operands) != 1:
                raise ValueError(f"INC requires 1 operand, got {len(operands)}")
            
            reg = operands[0].upper()
            
            # INC register (16-bit)
            if reg in self.registers:
                reg_num, reg_size = self.registers[reg]
                
                if reg_size == 16:
                    # Check that it's one of the main registers (AX, CX, DX, BX, SP, BP, SI, DI)
                    if reg in ['AX', 'CX', 'DX', 'BX', 'SP', 'BP', 'SI', 'DI']:
                        # INC r16 - opcode is 0x40 + register number
                        opcode = 0x40 + reg_num
                        machine_code.append(opcode)
                    else:
                        raise ValueError(f"INC not supported for register {reg}")
                else:
                    raise ValueError(f"INC for 8-bit registers not implemented yet")
            else:
                raise ValueError(f"Unknown register: {reg}")
                
        # Handle logical operations (AND, OR, XOR)
        elif mnemonic in ['AND', 'OR', 'XOR']:
            if len(operands) != 2:
                raise ValueError(f"{mnemonic} requires 2 operands, got {len(operands)}")
                
            # Get operand types and values
            dest = operands[0].upper()
            src = operands[1]
                
            # Handle register-register operations
            if dest in self.registers and src.upper() in self.registers:
                dest_num, dest_size = self.registers[dest]
                src_num, src_size = self.registers[src.upper()]
                
                # Both 16-bit registers
                if dest_size == 16 and src_size == 16:
                    if mnemonic == 'AND':
                        machine_code.append(0x21)  # AND r/m16, r16
                    elif mnemonic == 'OR':
                        machine_code.append(0x09)  # OR r/m16, r16
                    elif mnemonic == 'XOR':
                        machine_code.append(0x31)  # XOR r/m16, r16
                        
                    # Create ModR/M byte: mod 11 (register to register) + reg (src) + r/m (dest)
                    mod_rm = 0xC0 | (src_num << 3) | dest_num
                    machine_code.append(mod_rm)
                # Handle 8-bit registers
                elif dest_size == 8 and src_size == 8:
                    if mnemonic == 'AND':
                        machine_code.append(0x20)  # AND r/m8, r8
                    elif mnemonic == 'OR':
                        machine_code.append(0x08)  # OR r/m8, r8
                    elif mnemonic == 'XOR':
                        machine_code.append(0x30)  # XOR r/m8, r8
                        
                    # Create ModR/M byte: mod 11 (register to register) + reg (src) + r/m (dest)
                    mod_rm = 0xC0 | (src_num << 3) | dest_num
                    machine_code.append(mod_rm)
                else:
                    raise ValueError(f"Operand size mismatch for {mnemonic}")
            
            # Handle register-immediate operations for AX/AL
            elif (dest == 'AX' or dest == 'AL') and self._get_operand_type(src) == 'immediate':
                imm_value = self._parse_value(src)
                
                if dest == 'AX':
                    # Operation with AX and immediate
                    if mnemonic == 'AND':
                        machine_code.append(0x25)  # AND AX, imm16
                    elif mnemonic == 'OR':
                        machine_code.append(0x0D)  # OR AX, imm16
                    elif mnemonic == 'XOR':
                        machine_code.append(0x35)  # XOR AX, imm16
                    
                    # Append immediate value (16-bit, little endian)
                    machine_code.append(imm_value & 0xFF)
                    machine_code.append((imm_value >> 8) & 0xFF)
                
                elif dest == 'AL':
                    # Operation with AL and immediate (8-bit)
                    if mnemonic == 'AND':
                        machine_code.append(0x24)  # AND AL, imm8
                    elif mnemonic == 'OR':
                        machine_code.append(0x0C)  # OR AL, imm8
                    elif mnemonic == 'XOR':
                        machine_code.append(0x34)  # XOR AL, imm8
                    
                    # Append immediate value (8-bit)
                    machine_code.append(imm_value & 0xFF)
            else:
                raise ValueError(f"Unsupported operand combination for {mnemonic}: {dest}, {src}")
                
        # Handle compare operations (CMP)
        elif mnemonic == 'CMP':
            if len(operands) != 2:
                raise ValueError(f"CMP requires 2 operands, got {len(operands)}")
                
            # Get operand types and values
            dest = operands[0].upper()
            src = operands[1]
                
            # Handle register-register operations
            if dest in self.registers and src.upper() in self.registers:
                dest_num, dest_size = self.registers[dest]
                src_num, src_size = self.registers[src.upper()]
                
                # Both 16-bit registers
                if dest_size == 16 and src_size == 16:
                    machine_code.append(0x39)  # CMP r/m16, r16
                    # Create ModR/M byte: mod 11 (register to register) + reg (src) + r/m (dest)
                    mod_rm = 0xC0 | (src_num << 3) | dest_num
                    machine_code.append(mod_rm)
                # Handle 8-bit registers
                elif dest_size == 8 and src_size == 8:
                    machine_code.append(0x38)  # CMP r/m8, r8
                    # Create ModR/M byte: mod 11 (register to register) + reg (src) + r/m (dest)
                    mod_rm = 0xC0 | (src_num << 3) | dest_num
                    machine_code.append(mod_rm)
                else:
                    raise ValueError(f"Operand size mismatch for CMP")
            
            # Handle register-immediate operations for AX/AL
            elif (dest == 'AX' or dest == 'AL') and self._get_operand_type(src) == 'immediate':
                imm_value = self._parse_value(src)
                
                if dest == 'AX':
                    machine_code.append(0x3D)  # CMP AX, imm16
                    # Append immediate value (16-bit, little endian)
                    machine_code.append(imm_value & 0xFF)
                    machine_code.append((imm_value >> 8) & 0xFF)
                
                elif dest == 'AL':
                    machine_code.append(0x3C)  # CMP AL, imm8
                    # Append immediate value (8-bit)
                    machine_code.append(imm_value & 0xFF)
            else:
                raise ValueError(f"Unsupported operand combination for CMP: {dest}, {src}")
        
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
        
        # Hexadecimal with 0x prefix
        if value_str.startswith(('0x', '0X')):
            return int(value_str[2:], 16)
        
        # Hexadecimal with h suffix (common in assembly)
        if value_str.endswith(('h', 'H')):
            # Remove suffix and parse as hex
            hex_value = value_str[:-1]
            # Make sure it's a valid hex number
            try:
                return int(hex_value, 16)
            except ValueError:
                raise ValueError(f"Invalid hexadecimal value: {value_str}")
        
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
            
            # Last resort - check if it could be a hex value with no prefix
            # This is a common convention in some assemblers
            try:
                if all(c in '0123456789ABCDEFabcdef' for c in value_str):
                    return int(value_str, 16)
                else:
                    raise ValueError
            except ValueError:
                raise ValueError(f"Invalid numeric value: {value_str}")
