"""
Profile runner for 8086 simulator.
This script runs a program with profiling enabled and reports performance statistics.
"""
import sys
import time
from cpu import CPU
from memory import Memory
from assembler import Assembler
from instructions import InstructionSet
import fix_instructions
from profiler import create_profiler

def profile_program(filename, max_instructions=1000, detailed=False):
    """Run a program with profiling enabled and report statistics."""
    # Initialize simulator components
    memory = Memory()
    cpu = CPU(memory)
    assembler = Assembler(cpu, memory)
    instructions = InstructionSet(cpu)
    
    # Create profiler
    profiler = create_profiler(cpu, memory)
    
    # Reset CPU and memory before loading
    cpu.reset()
    memory.reset()
    
    print(f"Loading program for profiling: {filename}")
    labels, variables, segments = fix_instructions.fix_segment_handling(assembler, filename)
    
    # Show basic program info
    print(f"\nProgram size: {len(memory.dump(segments['CODE'], 256))} bytes in CODE segment")
    print(f"DATA segment size: {len(memory.dump(segments['DATA'], 256))} bytes")
    
    # Instrument CPU methods to collect profiling data
    
    # Store the original methods we're going to wrap
    orig_get_register = cpu.get_register
    orig_set_register = cpu.set_register
    orig_memory_read_byte = memory.read_byte
    orig_memory_write_byte = memory.write_byte
    orig_execute_instruction = cpu.execute_instruction
    
    # Wrap the methods to add profiling
    def profiled_get_register(reg):
        profiler.record_register_read(cpu.REGISTER_NAMES.get(reg, f"REG_{reg}"))
        return orig_get_register(reg)
    
    def profiled_set_register(reg, value):
        profiler.record_register_write(cpu.REGISTER_NAMES.get(reg, f"REG_{reg}"))
        return orig_set_register(reg, value)
        
    def profiled_memory_read_byte(address):
        profiler.record_memory_read(address)
        return orig_memory_read_byte(address)
        
    def profiled_memory_write_byte(address, value):
        profiler.record_memory_write(address)
        return orig_memory_write_byte(address, value)

    def profiled_execute_instruction():
        # Get current opcode
        ip = cpu.get_register(cpu.IP)
        cs = cpu.get_register(cpu.CS)
        physical_addr = cpu.get_physical_address(cs, ip)
        opcode = memory.read_byte(physical_addr)
        
        # Time the instruction execution
        start_time = time.time()
        result = orig_execute_instruction()
        end_time = time.time()
        
        # Record profiling data
        execution_time = end_time - start_time
        profiler.record_instruction(opcode, execution_time)
        
        # Track control flow instructions
        if opcode >= 0x70 and opcode <= 0x7F:  # Conditional jumps
            profiler.record_jump()
        elif opcode in [0xEB, 0xE9]:  # JMP instructions
            profiler.record_jump()
        elif opcode == 0xE8:  # CALL instruction
            profiler.record_call()
        elif opcode == 0xC3:  # RET instruction
            profiler.record_ret()
            
        return result
    
    # Apply the instrumented methods
    cpu.get_register = profiled_get_register
    cpu.set_register = profiled_set_register
    memory.read_byte = profiled_memory_read_byte
    memory.write_byte = profiled_memory_write_byte
    cpu.execute_instruction = profiled_execute_instruction
    
    # Start profiling
    profiler.start_profiling()
    
    print("\nRunning program with profiling...")
    
    # Execute the program step by step
    instruction_count = 0
    
    try:
        while instruction_count < max_instructions:
            # Get the current instruction pointer
            ip = cpu.get_register(cpu.IP)
            cs = cpu.get_register(cpu.CS)
            physical_addr = cpu.get_physical_address(cs, ip)
            
            # Get the instruction at the current address
            opcode = memory.read_byte(physical_addr)
            
            # Check for HLT instruction
            if opcode == 0xF4:  # HLT
                print(f"HLT instruction encountered at CS:IP {cs:04X}:{ip:04X} after {instruction_count} instructions.")
                break
                
            # Execute one instruction
            cpu.execute_instruction()
            instruction_count += 1
            
            # Print progress every 100 instructions
            if instruction_count % 100 == 0:
                print(f"Executed {instruction_count} instructions...")
    
    except Exception as e:
        print(f"Execution stopped due to an error: {e}")
    
    # Stop profiling
    profiler.stop_profiling()
    
    # Restore original methods
    cpu.get_register = orig_get_register
    cpu.set_register = orig_set_register
    memory.read_byte = orig_memory_read_byte
    memory.write_byte = orig_memory_write_byte
    cpu.execute_instruction = orig_execute_instruction
    
    # Print profiling results
    print("\nProfiling completed!")
    print(f"Total instructions executed: {instruction_count}")
    
    # Generate and print the profiling report
    if detailed:
        report = profiler.generate_detailed_report()
    else:
        report = profiler.generate_summary_report()
        
    print(report)
    
    # Return the profiler in case additional analysis is needed
    return profiler

def main():
    """Main entry point for the profiler."""
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python profile_program.py <assembly_file> [max_instructions] [--detailed]")
        sys.exit(1)
        
    filename = sys.argv[1]
    max_instructions = 1000  # Default
    detailed = False
    
    if len(sys.argv) > 2:
        if sys.argv[2].isdigit():
            max_instructions = int(sys.argv[2])
            
    if "--detailed" in sys.argv:
        detailed = True
        
    profile_program(filename, max_instructions, detailed)

if __name__ == "__main__":
    main()