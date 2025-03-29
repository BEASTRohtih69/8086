import sys
from cpu import CPU
from memory import Memory
from assembler import Assembler
from instructions import InstructionSet
import fix_instructions

# Create components
memory = Memory()
cpu = CPU(memory)
assembler = Assembler(cpu, memory)
instruction_set = InstructionSet(cpu)

# Reset everything
cpu.reset()
memory.reset()

# Load our simple test file
filename = "sample_programs/test_simple.asm"
print(f"Loading program: {filename}")
fix_instructions.fix_segment_handling(assembler, filename)

# Check memory for the HLT instruction
code_start = 0x0100  # Code segment
found_hlt = False
for i in range(16):  # Just check the first few bytes
    addr = code_start + i
    byte = memory.read_byte(addr)
    print(f"{addr:04X}: {byte:02X} {'(HLT)' if byte == 0xF4 else ''}")
    if byte == 0xF4:
        found_hlt = True

if not found_hlt:
    print("HLT instruction (0xF4) not found in memory")
else:
    print("HLT instruction found in memory")

# Show current CPU state - this is before fix
print(f"Before Fix - CS: {cpu.get_register(cpu.CS):04X}")
print(f"Before Fix - IP: {cpu.get_register(cpu.IP):04X}")

# Calculate physical address
ip = cpu.get_register(cpu.IP)
cs = cpu.get_register(cpu.CS)
physical_addr = cpu.get_physical_address(cs, ip)
opcode = memory.read_byte(physical_addr)
print(f"Before Fix - At CS:IP ({cs:04X}:{ip:04X}) = {physical_addr:05X}, Opcode = {opcode:02X}")

# Fix the CS and IP registers to correctly point to our code
# The formula for physical address is (segment << 4) + offset
# Our HLT instruction is at physical address 0x0100
# So we need to set CS:IP such that (CS << 4) + IP = 0x0100
# Option 1: CS=0x0010, IP=0x0000 → (0x0010 << 4) + 0x0000 = 0x0100
# Option 2: CS=0x0000, IP=0x0100 → (0x0000 << 4) + 0x0100 = 0x0100
# Let's try option 1
cpu.set_register(cpu.CS, 0x0010)  # CS = 0x0010
cpu.set_register(cpu.IP, 0x0000)  # IP = 0x0000

# Show updated CPU state
print(f"After Fix - CS: {cpu.get_register(cpu.CS):04X}")
print(f"After Fix - IP: {cpu.get_register(cpu.IP):04X}")

# Calculate new physical address
ip = cpu.get_register(cpu.IP)
cs = cpu.get_register(cpu.CS)
physical_addr = cpu.get_physical_address(cs, ip)
opcode = memory.read_byte(physical_addr)
print(f"After Fix - At CS:IP ({cs:04X}:{ip:04X}) = {physical_addr:05X}, Opcode = {opcode:02X}")

if opcode == 0xF4:
    print("Found HLT at current IP")
else:
    print("Not at HLT instruction")