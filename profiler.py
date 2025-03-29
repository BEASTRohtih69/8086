"""
Profiler module for 8086 simulator.
Implements performance profiling tools to analyze program execution.
"""
import time
from collections import defaultdict, Counter

class Profiler:
    """Performance profiler for the 8086 simulator."""

    def __init__(self, cpu, memory):
        """Initialize the profiler with CPU and memory references."""
        self.cpu = cpu
        self.memory = memory
        self.reset()

    def reset(self):
        """Reset all profiling data."""
        # Execution time tracking
        self.start_time = None
        self.end_time = None
        self.instruction_count = 0
        
        # Instruction profiling
        self.opcode_counts = Counter()
        self.instruction_times = defaultdict(list)
        
        # Memory access profiling
        self.memory_reads = Counter()
        self.memory_writes = Counter()
        self.segment_accesses = {
            'CS': 0,
            'DS': 0,
            'SS': 0,
            'ES': 0
        }
        
        # Register usage profiling
        self.register_reads = Counter()
        self.register_writes = Counter()
        
        # Execution flow
        self.jump_count = 0
        self.call_count = 0
        self.ret_count = 0

    def start_profiling(self):
        """Start the profiling session."""
        self.reset()
        self.start_time = time.time()

    def stop_profiling(self):
        """Stop the profiling session."""
        self.end_time = time.time()

    def record_instruction(self, opcode, execution_time):
        """Record information about an executed instruction."""
        self.instruction_count += 1
        self.opcode_counts[opcode] += 1
        self.instruction_times[opcode].append(execution_time)

    def record_memory_read(self, address, segment=None):
        """Record a memory read operation."""
        self.memory_reads[address] += 1
        if segment:
            self.segment_accesses[segment] += 1

    def record_memory_write(self, address, segment=None):
        """Record a memory write operation."""
        self.memory_writes[address] += 1
        if segment:
            self.segment_accesses[segment] += 1

    def record_register_read(self, register):
        """Record a register read operation."""
        self.register_reads[register] += 1

    def record_register_write(self, register):
        """Record a register write operation."""
        self.register_writes[register] += 1

    def record_jump(self):
        """Record a jump instruction execution."""
        self.jump_count += 1

    def record_call(self):
        """Record a call instruction execution."""
        self.call_count += 1

    def record_ret(self):
        """Record a return instruction execution."""
        self.ret_count += 1

    def get_total_execution_time(self):
        """Get the total execution time."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0

    def get_instructions_per_second(self):
        """Get the number of instructions executed per second."""
        total_time = self.get_total_execution_time()
        if total_time > 0:
            return self.instruction_count / total_time
        return 0

    def get_average_instruction_time(self, opcode=None):
        """Get the average execution time for an instruction (or all instructions)."""
        if opcode:
            times = self.instruction_times.get(opcode, [])
            if times:
                return sum(times) / len(times)
            return 0
        
        all_times = [time for times in self.instruction_times.values() for time in times]
        if all_times:
            return sum(all_times) / len(all_times)
        return 0

    def get_hotspots(self, top_n=10):
        """Get the top N memory addresses by access frequency."""
        all_accesses = Counter()
        for addr, count in self.memory_reads.items():
            all_accesses[addr] += count
        for addr, count in self.memory_writes.items():
            all_accesses[addr] += count
            
        return all_accesses.most_common(top_n)

    def get_most_used_opcodes(self, top_n=10):
        """Get the most frequently executed opcodes."""
        return self.opcode_counts.most_common(top_n)

    def get_most_used_registers(self, top_n=5):
        """Get the most frequently used registers."""
        register_usage = Counter()
        for reg, count in self.register_reads.items():
            register_usage[reg] += count
        for reg, count in self.register_writes.items():
            register_usage[reg] += count
            
        return register_usage.most_common(top_n)

    def generate_summary_report(self):
        """Generate a summary profiling report."""
        total_time = self.get_total_execution_time()
        ips = self.get_instructions_per_second()
        
        report = []
        report.append("=" * 50)
        report.append("PERFORMANCE PROFILING SUMMARY")
        report.append("=" * 50)
        report.append(f"Total execution time: {total_time:.6f} seconds")
        report.append(f"Instructions executed: {self.instruction_count}")
        report.append(f"Instructions per second: {ips:.2f}")
        report.append(f"Average instruction time: {self.get_average_instruction_time():.9f} seconds")
        
        report.append("\n" + "-" * 50)
        report.append("TOP 10 MOST EXECUTED INSTRUCTIONS")
        report.append("-" * 50)
        for opcode, count in self.get_most_used_opcodes(10):
            percentage = (count / self.instruction_count) * 100 if self.instruction_count > 0 else 0
            avg_time = self.get_average_instruction_time(opcode)
            report.append(f"Opcode 0x{opcode:02X}: {count} times ({percentage:.2f}%) - Avg time: {avg_time:.9f}s")
        
        report.append("\n" + "-" * 50)
        report.append("MEMORY ACCESS PATTERNS")
        report.append("-" * 50)
        report.append(f"Total memory reads: {sum(self.memory_reads.values())}")
        report.append(f"Total memory writes: {sum(self.memory_writes.values())}")
        report.append(f"Unique memory addresses accessed: {len(set(self.memory_reads) | set(self.memory_writes))}")
        
        report.append("\n" + "-" * 50)
        report.append("SEGMENT USAGE")
        report.append("-" * 50)
        for segment, count in self.segment_accesses.items():
            report.append(f"{segment}: {count} accesses")
            
        report.append("\n" + "-" * 50)
        report.append("REGISTER USAGE")
        report.append("-" * 50)
        for reg, count in self.get_most_used_registers():
            report.append(f"{reg}: {count} accesses")
            
        report.append("\n" + "-" * 50)
        report.append("CONTROL FLOW STATISTICS")
        report.append("-" * 50)
        report.append(f"Jump instructions executed: {self.jump_count}")
        report.append(f"Call instructions executed: {self.call_count}")
        report.append(f"Return instructions executed: {self.ret_count}")
        
        report.append("\n" + "=" * 50)
        
        return "\n".join(report)

    def generate_detailed_report(self):
        """Generate a detailed profiling report with visualizations."""
        # This would include more detailed statistics and possibly ASCII charts
        summary = self.generate_summary_report()
        
        detailed = [summary]
        detailed.append("\n\n" + "=" * 50)
        detailed.append("DETAILED MEMORY ACCESS HEATMAP")
        detailed.append("=" * 50)
        
        # Simple ASCII heatmap of memory accesses
        hotspots = self.get_hotspots(20)
        if hotspots:
            max_count = hotspots[0][1]
            for addr, count in hotspots:
                bar_length = int((count / max_count) * 40)
                bar = '#' * bar_length
                detailed.append(f"0x{addr:05X}: {bar} ({count} accesses)")
        
        detailed.append("\n" + "=" * 50)
        detailed.append("OPCODE EXECUTION FREQUENCY")
        detailed.append("=" * 50)
        
        # Simple ASCII chart of opcode frequency
        top_opcodes = self.get_most_used_opcodes(15)
        if top_opcodes:
            max_count = top_opcodes[0][1]
            for opcode, count in top_opcodes:
                bar_length = int((count / max_count) * 40)
                bar = '*' * bar_length
                detailed.append(f"0x{opcode:02X}: {bar} ({count} executions)")
                
        return "\n".join(detailed)

def create_profiler(cpu, memory):
    """Factory function to create a profiler instance."""
    return Profiler(cpu, memory)