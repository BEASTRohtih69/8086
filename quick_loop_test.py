"""
Quick Loop Test - Minimal program to test the LOOP instruction without timeouts
"""

from memory import Memory
from cpu import CPU
from assembler import Assembler
import fix_instructions

def main():
    # Initialize components
    memory = Memory()
    cpu = CPU(memory)
    assembler = Assembler(cpu, memory)
    
    # Set up a minimal test program with hardcoded machine code
    print("Setting up test program...")
    
    # Manual opcodes for the intended sequence:
    # MOV CX, 5
    # MOV AX, 0
    # loop_start: (here at offset 0x06)
    # INC AX
    # LOOP loop_start
    # HLT
    
    # Reset CPU and memory first
    cpu.reset()
    
    # CS:IP points to physical address 0x0100
    phys_addr = cpu.get_physical_address(cpu.get_register(cpu.CS), 0)
    
    # Write the test program bytes directly to memory
    # MOV CX, 5 (0xB9 0x05 0x00)
    memory.write_byte(phys_addr + 0x00, 0xB9) 
    memory.write_byte(phys_addr + 0x01, 0x05)
    memory.write_byte(phys_addr + 0x02, 0x00)
    
    # MOV AX, 0 (0xB8 0x00 0x00)
    memory.write_byte(phys_addr + 0x03, 0xB8)
    memory.write_byte(phys_addr + 0x04, 0x00)
    memory.write_byte(phys_addr + 0x05, 0x00)
    
    # loop_start at 0x06
    # INC AX (0x40)
    memory.write_byte(phys_addr + 0x06, 0x40)
    
    # LOOP loop_start (0xE2 0xFD)
    # offset is -3 (0xFD) to go back from 0x09 to 0x06
    memory.write_byte(phys_addr + 0x07, 0xE2)
    memory.write_byte(phys_addr + 0x08, 0xFD)
    
    # HLT (0xF4)
    memory.write_byte(phys_addr + 0x09, 0xF4)
    
    print("Program with corrected machine code loaded at physical address 0x0100")
    
    # Execute instructions one by one with debug
    print("\nExecuting program...")
    max_instructions = 30  # Set a reasonable limit
    instruction_count = 0
    
    print("\nRegister state before execution:")
    print_registers(cpu)
    
    while not cpu.halted and instruction_count < max_instructions:
        print(f"\nInstruction {instruction_count + 1}:")
        if not cpu.execute_instruction():
            print("Execution failed, stopping...")
            break
        
        print_registers(cpu)
        instruction_count += 1
    
    if cpu.halted:
        print("\nProgram halted normally.")
    else:
        print("\nProgram stopped due to instruction limit.")
    
    print(f"\nFinal register state (after {instruction_count} instructions):")
    print_registers(cpu)

def print_registers(cpu):
    """Print the key registers for debugging"""
    ax = cpu.get_register(cpu.AX)
    cx = cpu.get_register(cpu.CX)
    ip = cpu.get_register(cpu.IP)
    cs = cpu.get_register(cpu.CS)
    
    # Get physical address for current instruction
    phys_addr = cpu.get_physical_address(cs, ip)
    
    # Get flags that are relevant
    zf = cpu.get_flag(cpu.ZERO_FLAG)
    cf = cpu.get_flag(cpu.CARRY_FLAG)
    
    print(f"AX={ax:04X}, CX={cx:04X}, IP={ip:04X}, CS={cs:04X}, PHYS={phys_addr:05X}, ZF={zf}, CF={cf}")

if __name__ == "__main__":
    main()