"""
Memory module for 8086 simulator.
Implements the memory subsystem with read/write operations.
"""

class Memory:
    """Simulates the memory subsystem of the 8086."""
    
    def __init__(self, size=1024*64):
        """Initialize memory with specified size (default 64KB)."""
        self.size = size
        self.memory = bytearray(size)
        # Profiling hooks
        self.profiler = None
    
    def reset(self):
        """Reset memory to all zeros."""
        # Store the profiler before resetting
        profiler = self.profiler
        self.memory = bytearray(self.size)
        # Restore the profiler after resetting
        self.profiler = profiler
        
    def set_profiler(self, profiler):
        """Set a profiler for performance monitoring."""
        self.profiler = profiler
    
    def read_byte(self, address):
        """Read a byte from memory at the specified address."""
        if not 0 <= address < self.size:
            raise IndexError(f"Memory address out of range: 0x{address:05X}")
        return self.memory[address]
    
    def write_byte(self, address, value):
        """Write a byte to memory at the specified address."""
        if not 0 <= address < self.size:
            raise IndexError(f"Memory address out of range: 0x{address:05X}")
        self.memory[address] = value & 0xFF
    
    def read_word(self, address):
        """Read a word (2 bytes) from memory at the specified address (little-endian)."""
        if not 0 <= address < self.size - 1:
            raise IndexError(f"Memory address out of range for word read: 0x{address:05X}")
        low_byte = self.memory[address]
        high_byte = self.memory[address + 1]
        return (high_byte << 8) | low_byte
    
    def write_word(self, address, value):
        """Write a word (2 bytes) to memory at the specified address (little-endian)."""
        if not 0 <= address < self.size - 1:
            raise IndexError(f"Memory address out of range for word write: 0x{address:05X}")
        self.memory[address] = value & 0xFF  # Low byte
        self.memory[address + 1] = (value >> 8) & 0xFF  # High byte
    
    def read_doubleword(self, address):
        """Read a doubleword (4 bytes) from memory at the specified address (little-endian)."""
        if not 0 <= address < self.size - 3:
            raise IndexError(f"Memory address out of range for doubleword read: 0x{address:05X}")
        low_word = self.read_word(address)
        high_word = self.read_word(address + 2)
        return (high_word << 16) | low_word
    
    def write_doubleword(self, address, value):
        """Write a doubleword (4 bytes) to memory at the specified address (little-endian)."""
        if not 0 <= address < self.size - 3:
            raise IndexError(f"Memory address out of range for doubleword write: 0x{address:05X}")
        self.write_word(address, value & 0xFFFF)  # Low word
        self.write_word(address + 2, (value >> 16) & 0xFFFF)  # High word
    
    def load_bytes(self, address, data):
        """Load a sequence of bytes into memory starting at the specified address."""
        if not 0 <= address < self.size - len(data) + 1:
            raise IndexError(f"Memory address range out of bounds for loading {len(data)} bytes at 0x{address:05X}")
        for i, byte in enumerate(data):
            self.memory[address + i] = byte
    
    def dump(self, start_address, length):
        """Dump a section of memory as a list of bytes."""
        if not 0 <= start_address < self.size:
            raise IndexError(f"Memory start address out of range: 0x{start_address:05X}")
        
        end_address = min(start_address + length, self.size)
        return list(self.memory[start_address:end_address])
