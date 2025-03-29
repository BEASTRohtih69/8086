import sys
import argparse
from cpu import CPU
from memory import Memory
from assembler import Assembler
from instructions import InstructionSet
import fix_instructions
from profiler import create_profiler

def run_program(filename, max_instructions=100, debug_mode=True, profile=False, dump_memory=True):
    """
    Run an 8086 assembly program with configurable options.
    
    Args:
        filename: Path to the assembly file
        max_instructions: Maximum number of instructions to execute
        debug_mode: Whether to print debug information
        profile: Whether to collect and display performance metrics
        dump_memory: Whether to dump memory contents after execution
    
    Returns:
        A tuple containing (CPU, memory, instruction_count, profiler or None)
    """
    memory = Memory()
    cpu = CPU(memory)
    assembler = Assembler(cpu, memory)
    instructions = InstructionSet(cpu)
    
    # Create profiler if requested
    profiler = None
    if profile:
        profiler = create_profiler(cpu, memory)
        cpu.set_profiler(profiler)
        memory.set_profiler(profiler)
        profiler.start_profiling()
    
    # Reset CPU and memory before loading
    cpu.reset()
    memory.reset()
    
    # Load the test program
    if debug_mode:
        print(f"Loading program: {filename}")
    
    labels, variables, segments = fix_instructions.fix_segment_handling(assembler, filename)
    
    # Debug information
    if debug_mode:
        print("\nDebug Information:")
        print(f"Labels: {labels}")
        print(f"Variables: {variables}")
        print(f"Segments: {segments}")
        print(f"CS: {cpu.get_register(cpu.CS):04X}")
        print(f"IP: {cpu.get_register(cpu.IP):04X}")
        
        # Display memory at code segment start
        code_start = segments['CODE']
        print(f"\nCode Segment Memory (0x{code_start:04X}):")
        for i in range(32):  # Show first 32 bytes of code segment
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
                print(f"Current IP: {cpu.get_register(cpu.IP):04X}")
                break
        
        if not found_hlt:
            print("\nCouldn't find HLT instruction in first 512 bytes of code segment.")
        
        # Show initial registers
        print("Initial register state:")
        for reg_index, reg_name in CPU.REGISTER_NAMES.items():
            if reg_name != "FLAGS":
                print(f"{reg_name}: {cpu.get_register(reg_index):04X}")
    
    # Execute the program step by step
    if debug_mode:
        print("\nExecuting program...")
    
    instruction_count = 0
    
    while instruction_count < max_instructions:
        # Get the current instruction pointer
        ip = cpu.get_register(cpu.IP)
        cs = cpu.get_register(cpu.CS)
        physical_addr = cpu.get_physical_address(cs, ip)
        
        # Get the instruction at the current address
        opcode = memory.read_byte(physical_addr)
        
        if debug_mode:
            print(f"IP={ip:04X}, CS={cs:04X}, Physical={physical_addr:05X}, Opcode={opcode:02X}")
        
        # Execute one instruction
        if opcode == 0xF4:  # HLT
            if debug_mode:
                print("HLT instruction encountered. Stopping execution.")
            break
            
        cpu.execute_instruction()
        instruction_count += 1
        
        # Display registers after instruction
        if debug_mode:
            print("Register state after instruction:")
            for reg_index, reg_name in CPU.REGISTER_NAMES.items():
                if reg_name != "FLAGS":
                    print(f"{reg_name}: {cpu.get_register(reg_index):04X}")
            print()
    
    if debug_mode:
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
    if dump_memory:
        data_start = 0x0200  # Common data segment
        data_length = 32  # Show 32 bytes
        data = memory.dump(data_start, data_length)
        
        if debug_mode:
            print("\nData segment contents:")
            for i in range(0, len(data), 16):
                line = data[i:i+16]
                hex_values = ' '.join([f"{b:02X}" for b in line])
                ascii_values = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in line])
                print(f"{data_start+i:04X}: {hex_values.ljust(48)} | {ascii_values}")
    
    # Stop profiling if enabled
    if profile and profiler:
        profiler.stop_profiling()
        if debug_mode:
            print("\nProfiling results:")
            print(profiler.generate_summary_report())
    
    return cpu, memory, instruction_count, profiler

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run an 8086 assembly program with various options.')
    parser.add_argument('filename', nargs='?', default='sample_programs/sample.asm',
                        help='Path to the assembly file to run')
    parser.add_argument('-m', '--max-instructions', type=int, default=100,
                        help='Maximum number of instructions to execute')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Print detailed debug information')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Run in quiet mode with minimal output')
    parser.add_argument('-p', '--profile', action='store_true',
                        help='Enable performance profiling')
    parser.add_argument('--dump-memory', action='store_true',
                        help='Dump memory contents after execution')
    
    args = parser.parse_args()
    
    # Determine debug mode
    debug_mode = args.debug and not args.quiet
    
    # Run the program
    cpu, memory, instruction_count, profiler = run_program(
        args.filename,
        max_instructions=args.max_instructions,
        debug_mode=debug_mode,
        profile=args.profile,
        dump_memory=args.dump_memory
    )
    
    # Print a summary if in quiet mode
    if args.quiet:
        print(f"Executed {instruction_count} instructions from {args.filename}")
        print(f"Final AX: {cpu.get_register(cpu.AX):04X}, BX: {cpu.get_register(cpu.BX):04X}, "
              f"CX: {cpu.get_register(cpu.CX):04X}, DX: {cpu.get_register(cpu.DX):04X}")
        
        # Show profiling summary if requested
        if args.profile and profiler:
            ips = profiler.get_instructions_per_second()
            total_time = profiler.get_total_execution_time()
            print(f"Execution time: {total_time:.6f} seconds")
            print(f"Instructions per second: {ips:.2f}")

if __name__ == "__main__":
    main()