import sys
from cpu import CPU
from memory import Memory
from assembler import Assembler
from instructions import InstructionSet
import fix_instructions

def main():
    memory = Memory()
    cpu = CPU(memory)
    assembler = Assembler(cpu, memory)
    instructions = InstructionSet(cpu)
    
    # Reset CPU and memory before loading
    cpu.reset()
    memory.reset()
    
    # Load the test program
    filename = "sample_programs/sample.asm"
    print(f"Loading program: {filename}")
    labels, variables, segments = fix_instructions.fix_segment_handling(assembler, filename)
    
    # Debug information
    print("\nDebug Information:")
    print(f"Labels: {labels}")
    print(f"Variables: {variables}")
    print(f"Segments: {segments}")
    print(f"CS: {cpu.get_register(cpu.CS):04X}")
    print(f"IP: {cpu.get_register(cpu.IP):04X}")
    
    # Display memory at code segment start
    code_start = segments['CODE']
    print(f"\nCode Segment Memory (0x{code_start:04X}):")
    for i in range(64):  # Show more bytes of code segment
        addr = code_start + i
        byte = memory.read_byte(addr)
        print(f"{addr:04X}: {byte:02X} {'(HLT)' if byte == 0xF4 else ''}")
        
    # Look for the HLT instruction in memory
    found_hlt = False
    for i in range(512):  # Search first 512 bytes
        addr = code_start + i
        byte = memory.read_byte(addr)
        if byte == 0xF4:  # HLT opcode
            print(f"\nFound HLT instruction at {addr:04X}")
            found_hlt = True
            # Set IP to point to the instruction before HLT
            cpu.set_register(cpu.IP, i - 1)
            break
    
    if not found_hlt:
        print("\nCouldn't find HLT instruction in first 512 bytes of code segment.")
    
    # We won't manually set the IP - let the assembler set it correctly
    # The assembler should set IP to the entry point (start label in our sample)
    
    # Show initial registers
    print("Initial register state:")
    for reg_index, reg_name in CPU.REGISTER_NAMES.items():
        if reg_name != "FLAGS":
            print(f"{reg_name}: {cpu.get_register(reg_index):04X}")
    
    # Execute the program step by step
    print("\nExecuting program...")
    instruction_count = 0
    max_instructions = 100  # Safety limit
    
    while instruction_count < max_instructions:
        # Get the current instruction pointer
        ip = cpu.get_register(cpu.IP)
        cs = cpu.get_register(cpu.CS)
        physical_addr = cpu.get_physical_address(cs, ip)
        
        # Get the instruction at the current address
        opcode = memory.read_byte(physical_addr)
        print(f"IP={ip:04X}, CS={cs:04X}, Physical={physical_addr:05X}, Opcode={opcode:02X}")
        
        # Execute one instruction
        if opcode == 0xF4:  # HLT
            print("HLT instruction encountered. Stopping execution.")
            break
            
        cpu.execute_instruction()
        instruction_count += 1
        
        # Display registers after instruction
        print("Register state after instruction:")
        for reg_index, reg_name in CPU.REGISTER_NAMES.items():
            if reg_name != "FLAGS":
                print(f"{reg_name}: {cpu.get_register(reg_index):04X}")
        print()
    
    print(f"Executed {instruction_count} instructions.")
    
    # Display the final state
    print("\nFinal register state:")
    for reg_index, reg_name in CPU.REGISTER_NAMES.items():
        if reg_name != "FLAGS":
            print(f"{reg_name}: {cpu.get_register(reg_index):04X}")
    
    # Display flags
    print("\nFlags:")
    for flag_bit, flag_name in CPU.FLAG_NAMES.items():
        print(f"{flag_name}: {cpu.get_flag(flag_bit)}")
    
    # Display data segment data
    print("\nData segment contents:")
    data_start = 0x0200
    data_length = 32  # Show 32 bytes
    data = memory.dump(data_start, data_length)
    for i in range(0, len(data), 16):
        line = data[i:i+16]
        hex_values = ' '.join([f"{b:02X}" for b in line])
        ascii_values = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in line])
        print(f"{data_start+i:04X}: {hex_values.ljust(48)} | {ascii_values}")

if __name__ == "__main__":
    main()