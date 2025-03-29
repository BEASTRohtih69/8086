"""
Utilities module for 8086 simulator.
Contains various utility functions used by other modules.
"""

def hex_format(value, width=4):
    """Format a value as a hexadecimal string with specified width."""
    return f"0x{value:0{width}X}"

def bin_format(value, width=16):
    """Format a value as a binary string with specified width."""
    return f"0b{value:0{width}b}"

def format_byte_as_binary(byte):
    """Format a byte as a binary string with spacing."""
    binary = format(byte, '08b')
    return f"{binary[0:4]} {binary[4:8]}"

def format_word_as_binary(word):
    """Format a word as a binary string with spacing."""
    binary = format(word, '016b')
    return f"{binary[0:4]} {binary[4:8]} {binary[8:12]} {binary[12:16]}"

def format_register_pairs(registers, names):
    """Format register pairs for display."""
    lines = []
    for i in range(0, len(names), 2):
        if i + 1 < len(names):
            reg1, reg2 = names[i], names[i+1]
            val1, val2 = registers[reg1], registers[reg2]
            lines.append(f"{reg1}: {hex_format(val1)}\t{reg2}: {hex_format(val2)}")
        else:
            reg = names[i]
            val = registers[reg]
            lines.append(f"{reg}: {hex_format(val)}")
    return lines

def parse_int(value_str):
    """Parse an integer from a string with various formats."""
    value_str = value_str.strip()
    
    # Hexadecimal (0x prefix)
    if value_str.startswith(('0x', '0X')):
        return int(value_str[2:], 16)
    
    # Hexadecimal (h suffix)
    if value_str.lower().endswith('h'):
        return int(value_str[:-1], 16)
    
    # Binary (0b prefix)
    if value_str.startswith(('0b', '0B')):
        return int(value_str[2:], 2)
    
    # Binary (b suffix)
    if value_str.lower().endswith('b'):
        return int(value_str[:-1], 2)
    
    # Decimal
    try:
        return int(value_str)
    except ValueError:
        raise ValueError(f"Invalid numeric format: {value_str}")

def is_printable_ascii(byte):
    """Check if a byte represents a printable ASCII character."""
    return 32 <= byte <= 126

def format_flags(flags):
    """Format flags dictionary for display."""
    return ' '.join(f"{name}={value}" for name, value in flags.items())

def split_every_n(text, n=8):
    """Split text every n characters."""
    return ' '.join(text[i:i+n] for i in range(0, len(text), n))

def create_memory_map(memory, start_address, length, bytes_per_row=16):
    """Create a formatted memory map."""
    lines = []
    
    for i in range(0, length, bytes_per_row):
        addr = start_address + i
        hex_values = []
        ascii_values = []
        
        for j in range(bytes_per_row):
            if i + j < length:
                try:
                    byte = memory.read_byte(addr + j)
                    hex_values.append(f"{byte:02X}")
                    ascii_values.append(chr(byte) if is_printable_ascii(byte) else '.')
                except IndexError:
                    hex_values.append("--")
                    ascii_values.append(" ")
            else:
                hex_values.append("  ")
                ascii_values.append(" ")
        
        addr_str = f"{addr:08X}"
        hex_str = " ".join(hex_values)
        ascii_str = "".join(ascii_values)
        
        lines.append(f"{addr_str} | {hex_str} | {ascii_str}")
    
    return lines
