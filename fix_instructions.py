"""
Utility to fix the assembler and properly handle segment directives.
This script is used to fix the segmentation in the 8086 simulator assembler.
"""

def fix_segment_handling(assembler, asm_file):
    """Advanced segment handling for the assembler."""
    # Read the file
    with open(asm_file, 'r') as f:
        lines = f.readlines()
    
    # Initialize state
    segments = {
        'CODE': 0x0100,  # Code starts at 0x100
        'DATA': 0x0200,  # Data starts at 0x200
        'STACK': 0x0300  # Stack starts at 0x300
    }
    
    # Reset labels and variables
    labels = {}
    variables = {}
    
    # First pass: Find model and segment locations
    segment_positions = {'CODE': [], 'DATA': [], 'STACK': []}
    current_segment = None
    
    for i, line in enumerate(lines):
        # Remove comments and whitespace
        line = line.split(';')[0].strip()
        if not line:
            continue
        
        parts = line.split()
        mnemonic = parts[0].upper()
        
        # Handle MODEL directive
        if mnemonic == '.MODEL':
            model = parts[1].upper() if len(parts) > 1 else 'SMALL'
            # Apply model-specific memory layout
            if model == 'SMALL':
                segments = {
                    'CODE': 0x0100,
                    'DATA': 0x0200,
                    'STACK': 0x0300
                }
        
        # Track segment positions
        if mnemonic == '.CODE':
            current_segment = 'CODE'
            segment_positions['CODE'].append(i)
        elif mnemonic == '.DATA':
            current_segment = 'DATA'
            segment_positions['DATA'].append(i)
        elif mnemonic == '.STACK':
            current_segment = 'STACK'
            segment_positions['STACK'].append(i)
    
    print(f"Segment positions: {segment_positions}")
    
    # Second pass: Process labels and data definitions
    current_segment = 'CODE'  # Default
    current_address = segments['CODE']
    
    for i, line in enumerate(lines):
        # Strip comments and whitespace
        line = line.split(';')[0].strip()
        if not line:
            continue
        
        parts = line.split()
        mnemonic = parts[0].upper()
        
        # Track segment changes
        if mnemonic == '.CODE':
            current_segment = 'CODE'
            current_address = segments['CODE']
            continue
        elif mnemonic == '.DATA':
            current_segment = 'DATA' 
            current_address = segments['DATA']
            continue
        elif mnemonic == '.STACK':
            current_segment = 'STACK'
            current_address = segments['STACK']
            continue
        
        # Skip directive processing
        if mnemonic in ['.MODEL', 'END']:
            # Handle END with entry point
            if mnemonic == 'END' and len(parts) > 1:
                entry_point = parts[1].upper()
                assembler.entry_point = entry_point
            continue
        
        # Handle label declarations (name: format)
        if mnemonic.endswith(':'):
            label = mnemonic[:-1]  # Remove colon
            labels[label] = current_address
            labels[label.lower()] = current_address
            labels[label.upper()] = current_address
            
            # If more on this line, process remainder
            if len(parts) > 1:
                # Rest of line after label
                rest_of_line = ' '.join(parts[1:])
                if rest_of_line:
                    # Handle instruction following label
                    size = assembler._get_instruction_size(rest_of_line)
                    current_address += size
            continue
        
        # Handle DB directives
        if len(parts) >= 3 and parts[1].upper() == 'DB':
            var_name = parts[0]
            variables[var_name] = current_address
            variables[var_name.lower()] = current_address
            variables[var_name.upper()] = current_address
            
            # Estimate size of data
            data_part = ' '.join(parts[2:])
            if (data_part.startswith("'") and data_part.endswith("'")) or \
               (data_part.startswith('"') and data_part.endswith('"')):
                # String (minus quotes)
                current_address += len(data_part) - 2
            else:
                # Comma-separated values
                current_address += len(data_part.split(','))
            continue
        
        # For regular instructions, estimate size
        size = assembler._get_instruction_size(line)
        current_address += size
    
    # Update assembler state
    assembler.labels = labels
    assembler.variables = variables
    assembler.segments = segments
    
    # Clear memory before assembling
    for segment, start in segments.items():
        for offset in range(256):  # Clear 256 bytes for each segment
            assembler.memory.write_byte(start + offset, 0)
    
    # Third pass: Actually assemble instructions
    # Process each segment in order: DATA first, then CODE
    
    # First DATA segment
    if segment_positions['DATA']:
        current_segment = 'DATA'
        current_address = segments['DATA']
        assembler.current_segment = current_segment
        assembler.current_address = current_address
        
        print(f"\nAssembling DATA segment at {current_address:04X}")
        
        data_start = segment_positions['DATA'][0]
        data_end = None
        
        # Find end of DATA segment
        for seg, pos_list in segment_positions.items():
            if seg != 'DATA' and pos_list:
                for pos in pos_list:
                    if pos > data_start and (data_end is None or pos < data_end):
                        data_end = pos
        
        # Process DATA section
        in_data_section = False
        for i, line in enumerate(lines):
            if i < data_start:
                continue
            if data_end is not None and i >= data_end:
                break
                
            line = line.split(';')[0].strip()
            if not line:
                continue
                
            parts = line.split()
            mnemonic = parts[0].upper()
            
            # Skip segment directives
            if mnemonic in ['.DATA', '.CODE', '.STACK', '.MODEL', 'END']:
                if mnemonic == '.DATA':
                    in_data_section = True
                continue
                
            if not in_data_section:
                continue
                
            # Skip labels by themselves
            if mnemonic.endswith(':') and len(parts) == 1:
                continue
                
            # Process data declarations
            if len(parts) >= 3 and parts[1].upper() == 'DB':
                print(f"DATA: [{assembler.current_address:04X}] {line}")
                
                # Instead of using the assembler method, handle data directly
                var_name = parts[0]
                data_part = ' '.join(parts[2:])
                
                if data_part.startswith("'") and data_part.endswith("'"):
                    # String literal (remove quotes)
                    string_data = data_part[1:-1]
                    for i, char in enumerate(string_data):
                        assembler.memory.write_byte(assembler.current_address + i, ord(char))
                    # Add space for null terminator if present
                    if ', 0' in line or ',0' in line:
                        assembler.memory.write_byte(assembler.current_address + len(string_data), 0)
                        assembler.current_address += len(string_data) + 1
                    else:
                        assembler.current_address += len(string_data)
                elif ',' in data_part:
                    # Comma-separated values
                    values = [v.strip() for v in data_part.split(',')]
                    for i, val_str in enumerate(values):
                        if val_str.isdigit():
                            val = int(val_str)
                        elif val_str.startswith('0x'):
                            val = int(val_str, 16)
                        else:
                            val = 0  # Default for unrecognized formats
                        assembler.memory.write_byte(assembler.current_address + i, val & 0xFF)
                    assembler.current_address += len(values)
                else:
                    # Single value
                    try:
                        if data_part.isdigit():
                            val = int(data_part)
                        elif data_part.startswith('0x'):
                            val = int(data_part, 16)
                        else:
                            val = 0
                        assembler.memory.write_byte(assembler.current_address, val & 0xFF)
                        assembler.current_address += 1
                    except ValueError:
                        print(f"Warning: Couldn't parse data value '{data_part}'")
                        assembler.current_address += 1
    
    # Next CODE segment
    if segment_positions['CODE'] or not segment_positions['DATA']:
        current_segment = 'CODE'
        current_address = segments['CODE']
        assembler.current_segment = current_segment
        assembler.current_address = current_address
        
        print(f"\nAssembling CODE segment at {current_address:04X}")
        
        code_start = segment_positions['CODE'][0] if segment_positions['CODE'] else 0
        code_end = None
        
        # Find end of CODE segment
        for seg, pos_list in segment_positions.items():
            if seg != 'CODE' and pos_list:
                for pos in pos_list:
                    if pos > code_start and (code_end is None or pos < code_end):
                        code_end = pos
        
        # Process CODE section
        in_code_section = True if not segment_positions['CODE'] else False
        for i, line in enumerate(lines):
            if segment_positions['CODE'] and i < code_start:
                continue
            if code_end is not None and i >= code_end:
                break
                
            line = line.split(';')[0].strip()
            if not line:
                continue
                
            parts = line.split()
            if not parts:
                continue
                
            mnemonic = parts[0].upper()
            
            # Skip segment directives
            if mnemonic in ['.DATA', '.CODE', '.STACK', '.MODEL', 'END']:
                if mnemonic == '.CODE':
                    in_code_section = True
                continue
                
            if not in_code_section:
                continue
                
            # Skip lone labels
            if mnemonic.endswith(':') and len(parts) == 1:
                continue
            
            # Pre-process line to handle special cases
            processed_line = line
            # Replace @DATA with the actual data segment value
            if '@DATA' in line.upper():
                processed_line = line.replace('@DATA', str(segments['DATA']))
                processed_line = processed_line.replace('@data', str(segments['DATA']))
                
            # Handle OFFSET operator for variables
            if 'OFFSET ' in line.upper():
                for var_name, var_addr in variables.items():
                    if f"OFFSET {var_name}" in line.upper():
                        processed_line = processed_line.replace(f"OFFSET {var_name}", str(var_addr))
                        break
            
            # Handle instructions after labels
            if mnemonic.endswith(':') and len(parts) > 1:
                # Process the instruction part
                rest_line = ' '.join(parts[1:])
                # Replace @DATA with actual segment
                if '@DATA' in rest_line.upper():
                    rest_line = rest_line.replace('@DATA', str(segments['DATA']))
                    rest_line = rest_line.replace('@data', str(segments['DATA']))
                    
                # Handle OFFSET operator for variables
                if 'OFFSET ' in rest_line.upper():
                    for var_name, var_addr in variables.items():
                        if f"OFFSET {var_name}" in rest_line.upper():
                            rest_line = rest_line.replace(f"OFFSET {var_name}", str(var_addr))
                            break
                print(f"CODE: [{assembler.current_address:04X}] (after label) {rest_line}")
                assembler._assemble_instruction(rest_line)
            else:
                # Regular instruction
                print(f"CODE: [{assembler.current_address:04X}] {processed_line}")
                assembler._assemble_instruction(processed_line)
    
    # Set up registers for execution
    # In 8086, segment register values must be adjusted so that (segment << 4) + offset = physical_address
    # Convert physical addresses to segment values by dividing by 16 (shift right 4 bits)
    code_segment_value = segments['CODE'] >> 4
    data_segment_value = segments['DATA'] >> 4
    stack_segment_value = segments['STACK'] >> 4
    
    print(f"Setting CS to {code_segment_value:04X} (for physical address {segments['CODE']:04X})")
    print(f"Setting DS to {data_segment_value:04X} (for physical address {segments['DATA']:04X})")
    print(f"Setting SS to {stack_segment_value:04X} (for physical address {segments['STACK']:04X})")
    
    assembler.cpu.set_register(assembler.cpu.CS, code_segment_value)
    assembler.cpu.set_register(assembler.cpu.DS, data_segment_value)
    assembler.cpu.set_register(assembler.cpu.SS, stack_segment_value)
    
    # Set entry point
    # IP should be an offset within the CS segment, not an absolute address
    # So we need to calculate IP = label_address - (CS << 4)
    cs_base = assembler.cpu.get_register(assembler.cpu.CS) << 4
    
    if hasattr(assembler, 'entry_point') and assembler.entry_point:
        entry_name = assembler.entry_point
        if entry_name in labels:
            physical_addr = labels[entry_name]
            ip_offset = physical_addr - cs_base
            assembler.cpu.set_register(assembler.cpu.IP, ip_offset & 0xFFFF)
            print(f"Setting IP to entry point {entry_name}: physical={physical_addr:04X}, offset={ip_offset:04X}")
        elif entry_name.upper() in labels:
            physical_addr = labels[entry_name.upper()]
            ip_offset = physical_addr - cs_base
            assembler.cpu.set_register(assembler.cpu.IP, ip_offset & 0xFFFF)
            print(f"Setting IP to entry point {entry_name.upper()}: physical={physical_addr:04X}, offset={ip_offset:04X}")
        elif entry_name.lower() in labels:
            physical_addr = labels[entry_name.lower()]
            ip_offset = physical_addr - cs_base
            assembler.cpu.set_register(assembler.cpu.IP, ip_offset & 0xFFFF)
            print(f"Setting IP to entry point {entry_name.lower()}: physical={physical_addr:04X}, offset={ip_offset:04X}")
        else:
            print(f"Entry point {entry_name} not found in labels")
            # Default to start label if it exists
            if 'start' in labels:
                physical_addr = labels['start']
                ip_offset = physical_addr - cs_base
                assembler.cpu.set_register(assembler.cpu.IP, ip_offset & 0xFFFF)
                print(f"Using 'start' label: physical={physical_addr:04X}, offset={ip_offset:04X}")
            else:
                # If no entry point or start label, default to IP=0 (beginning of CS segment)
                assembler.cpu.set_register(assembler.cpu.IP, 0)
                print("Defaulting to IP=0000 (beginning of CS segment)")
    elif 'start' in labels:
        physical_addr = labels['start']
        ip_offset = physical_addr - cs_base
        assembler.cpu.set_register(assembler.cpu.IP, ip_offset & 0xFFFF)
        print(f"Using 'start' label: physical={physical_addr:04X}, offset={ip_offset:04X}")
    else:
        # If no entry point or start label, default to IP=0 (beginning of CS segment)
        assembler.cpu.set_register(assembler.cpu.IP, 0)
        print("Defaulting to IP=0000 (beginning of CS segment)")
    
    # Return the updated assembler state
    return labels, variables, segments