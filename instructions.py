"""
Instructions module for 8086 simulator.
Contains the instruction set implementation and opcode mappings.
"""

# Dictionary mapping opcodes to their mnemonic and handler function
class InstructionSet:
    """Implements the complete 8086 instruction set."""
    
    def __init__(self, cpu):
        """Initialize the instruction set with a reference to the CPU."""
        self.cpu = cpu
        self.instruction_map = self._build_instruction_map()
        
    def _build_instruction_map(self):
        """Build a mapping of opcodes to handler functions."""
        instruction_map = {}
        
        # MOV instructions (register to register, immediate to register, etc.)
        instruction_map[0x88] = ("MOV r/m8, r8", self._mov_rm8_r8)
        instruction_map[0x89] = ("MOV r/m16, r16", self._mov_rm16_r16)
        instruction_map[0x8A] = ("MOV r8, r/m8", self._mov_r8_rm8)
        instruction_map[0x8B] = ("MOV r16, r/m16", self._mov_r16_rm16)
        
        # MOV immediate to register
        instruction_map[0xB0] = ("MOV AL, imm8", self._mov_al_imm8)
        instruction_map[0xB1] = ("MOV CL, imm8", self._mov_cl_imm8)
        instruction_map[0xB2] = ("MOV DL, imm8", self._mov_dl_imm8)
        instruction_map[0xB3] = ("MOV BL, imm8", self._mov_bl_imm8)
        instruction_map[0xB4] = ("MOV AH, imm8", self._mov_ah_imm8)
        instruction_map[0xB5] = ("MOV CH, imm8", self._mov_ch_imm8)
        instruction_map[0xB6] = ("MOV DH, imm8", self._mov_dh_imm8)
        instruction_map[0xB7] = ("MOV BH, imm8", self._mov_bh_imm8)
        instruction_map[0xB8] = ("MOV AX, imm16", self._mov_ax_imm16)
        instruction_map[0xB9] = ("MOV CX, imm16", self._mov_cx_imm16)
        instruction_map[0xBA] = ("MOV DX, imm16", self._mov_dx_imm16)
        instruction_map[0xBB] = ("MOV BX, imm16", self._mov_bx_imm16)
        instruction_map[0xBC] = ("MOV SP, imm16", self._mov_sp_imm16)
        instruction_map[0xBD] = ("MOV BP, imm16", self._mov_bp_imm16)
        instruction_map[0xBE] = ("MOV SI, imm16", self._mov_si_imm16)
        instruction_map[0xBF] = ("MOV DI, imm16", self._mov_di_imm16)
        
        # Arithmetic operations
        instruction_map[0x00] = ("ADD r/m8, r8", self._add_rm8_r8)
        instruction_map[0x01] = ("ADD r/m16, r16", self._add_rm16_r16)
        instruction_map[0x02] = ("ADD r8, r/m8", self._add_r8_rm8)
        instruction_map[0x03] = ("ADD r16, r/m16", self._add_r16_rm16)
        instruction_map[0x04] = ("ADD AL, imm8", self._add_al_imm8)
        instruction_map[0x05] = ("ADD AX, imm16", self._add_ax_imm16)
        
        instruction_map[0x28] = ("SUB r/m8, r8", self._sub_rm8_r8)
        instruction_map[0x29] = ("SUB r/m16, r16", self._sub_rm16_r16)
        instruction_map[0x2A] = ("SUB r8, r/m8", self._sub_r8_rm8)
        instruction_map[0x2B] = ("SUB r16, r/m16", self._sub_r16_rm16)
        instruction_map[0x2C] = ("SUB AL, imm8", self._sub_al_imm8)
        instruction_map[0x2D] = ("SUB AX, imm16", self._sub_ax_imm16)
        
        # Control flow instructions
        instruction_map[0x70] = ("JO rel8", self._jo_rel8)
        instruction_map[0x71] = ("JNO rel8", self._jno_rel8)
        instruction_map[0x72] = ("JB/JNAE/JC rel8", self._jb_rel8)
        instruction_map[0x73] = ("JNB/JAE/JNC rel8", self._jnb_rel8)
        instruction_map[0x74] = ("JE/JZ rel8", self._je_rel8)
        instruction_map[0x75] = ("JNE/JNZ rel8", self._jne_rel8)
        instruction_map[0x76] = ("JBE/JNA rel8", self._jbe_rel8)
        instruction_map[0x77] = ("JNBE/JA rel8", self._jnbe_rel8)
        instruction_map[0x78] = ("JS rel8", self._js_rel8)
        instruction_map[0x79] = ("JNS rel8", self._jns_rel8)
        instruction_map[0x7A] = ("JP/JPE rel8", self._jp_rel8)
        instruction_map[0x7B] = ("JNP/JPO rel8", self._jnp_rel8)
        instruction_map[0x7C] = ("JL/JNGE rel8", self._jl_rel8)
        instruction_map[0x7D] = ("JNL/JGE rel8", self._jnl_rel8)
        instruction_map[0x7E] = ("JLE/JNG rel8", self._jle_rel8)
        instruction_map[0x7F] = ("JNLE/JG rel8", self._jnle_rel8)
        
        instruction_map[0xE8] = ("CALL rel16", self._call_rel16)
        instruction_map[0xC3] = ("RET", self._ret)
        
        # Stack operations
        instruction_map[0x50] = ("PUSH AX", self._push_ax)
        instruction_map[0x51] = ("PUSH CX", self._push_cx)
        instruction_map[0x52] = ("PUSH DX", self._push_dx)
        instruction_map[0x53] = ("PUSH BX", self._push_bx)
        instruction_map[0x54] = ("PUSH SP", self._push_sp)
        instruction_map[0x55] = ("PUSH BP", self._push_bp)
        instruction_map[0x56] = ("PUSH SI", self._push_si)
        instruction_map[0x57] = ("PUSH DI", self._push_di)
        
        instruction_map[0x58] = ("POP AX", self._pop_ax)
        instruction_map[0x59] = ("POP CX", self._pop_cx)
        instruction_map[0x5A] = ("POP DX", self._pop_dx)
        instruction_map[0x5B] = ("POP BX", self._pop_bx)
        instruction_map[0x5C] = ("POP SP", self._pop_sp)
        instruction_map[0x5D] = ("POP BP", self._pop_bp)
        instruction_map[0x5E] = ("POP SI", self._pop_si)
        instruction_map[0x5F] = ("POP DI", self._pop_di)
        
        # Miscellaneous
        instruction_map[0x90] = ("NOP", self._nop)
        instruction_map[0xF4] = ("HLT", self._hlt)
        instruction_map[0xCD] = ("INT imm8", self._int_imm8)
        
        return instruction_map
    
    def decode(self, opcode):
        """Decode an opcode and return instruction information."""
        if opcode in self.instruction_map:
            return self.instruction_map[opcode]
        else:
            return (f"Unknown opcode: 0x{opcode:02X}", None)
    
    # Instruction implementations
    def _mov_rm8_r8(self, modrm):
        # Implementation for MOV r/m8, r8
        pass
    
    def _mov_rm16_r16(self, modrm):
        # Implementation for MOV r/m16, r16
        pass
    
    def _mov_r8_rm8(self, modrm):
        # Implementation for MOV r8, r/m8
        pass
    
    def _mov_r16_rm16(self, modrm):
        # Implementation for MOV r16, r/m16
        pass
    
    def _mov_al_imm8(self):
        value = self.cpu.fetch_byte()
        self.cpu.set_register_low_byte(self.cpu.AX, value)
    
    def _mov_cl_imm8(self):
        value = self.cpu.fetch_byte()
        self.cpu.set_register_low_byte(self.cpu.CX, value)
    
    def _mov_dl_imm8(self):
        value = self.cpu.fetch_byte()
        self.cpu.set_register_low_byte(self.cpu.DX, value)
    
    def _mov_bl_imm8(self):
        value = self.cpu.fetch_byte()
        self.cpu.set_register_low_byte(self.cpu.BX, value)
    
    def _mov_ah_imm8(self):
        value = self.cpu.fetch_byte()
        self.cpu.set_register_high_byte(self.cpu.AX, value)
    
    def _mov_ch_imm8(self):
        value = self.cpu.fetch_byte()
        self.cpu.set_register_high_byte(self.cpu.CX, value)
    
    def _mov_dh_imm8(self):
        value = self.cpu.fetch_byte()
        self.cpu.set_register_high_byte(self.cpu.DX, value)
    
    def _mov_bh_imm8(self):
        value = self.cpu.fetch_byte()
        self.cpu.set_register_high_byte(self.cpu.BX, value)
    
    def _mov_ax_imm16(self):
        value = self.cpu.fetch_word()
        self.cpu.set_register(self.cpu.AX, value)
    
    def _mov_cx_imm16(self):
        value = self.cpu.fetch_word()
        self.cpu.set_register(self.cpu.CX, value)
    
    def _mov_dx_imm16(self):
        value = self.cpu.fetch_word()
        self.cpu.set_register(self.cpu.DX, value)
    
    def _mov_bx_imm16(self):
        value = self.cpu.fetch_word()
        self.cpu.set_register(self.cpu.BX, value)
    
    def _mov_sp_imm16(self):
        value = self.cpu.fetch_word()
        self.cpu.set_register(self.cpu.SP, value)
    
    def _mov_bp_imm16(self):
        value = self.cpu.fetch_word()
        self.cpu.set_register(self.cpu.BP, value)
    
    def _mov_si_imm16(self):
        value = self.cpu.fetch_word()
        self.cpu.set_register(self.cpu.SI, value)
    
    def _mov_di_imm16(self):
        value = self.cpu.fetch_word()
        self.cpu.set_register(self.cpu.DI, value)
    
    def _add_rm8_r8(self, modrm):
        # Implementation for ADD r/m8, r8
        pass
    
    def _add_rm16_r16(self, modrm):
        # Implementation for ADD r/m16, r16
        pass
    
    def _add_r8_rm8(self, modrm):
        # Implementation for ADD r8, r/m8
        pass
    
    def _add_r16_rm16(self, modrm):
        # Implementation for ADD r16, r/m16
        pass
    
    def _add_al_imm8(self):
        value = self.cpu.fetch_byte()
        result = (self.cpu.get_register_low_byte(self.cpu.AX) + value) & 0xFF
        self.cpu.set_register_low_byte(self.cpu.AX, result)
        # Set flags
        self._update_flags_after_arithmetic(self.cpu.get_register_low_byte(self.cpu.AX), value, result, 8)
    
    def _add_ax_imm16(self):
        value = self.cpu.fetch_word()
        result = (self.cpu.get_register(self.cpu.AX) + value) & 0xFFFF
        self.cpu.set_register(self.cpu.AX, result)
        # Set flags
        self._update_flags_after_arithmetic(self.cpu.get_register(self.cpu.AX), value, result, 16)
    
    def _sub_rm8_r8(self, modrm):
        # Implementation for SUB r/m8, r8
        pass
    
    def _sub_rm16_r16(self, modrm):
        # Implementation for SUB r/m16, r16
        pass
    
    def _sub_r8_rm8(self, modrm):
        # Implementation for SUB r8, r/m8
        pass
    
    def _sub_r16_rm16(self, modrm):
        # Implementation for SUB r16, r/m16
        pass
    
    def _sub_al_imm8(self):
        value = self.cpu.fetch_byte()
        al = self.cpu.get_register_low_byte(self.cpu.AX)
        result = (al - value) & 0xFF
        self.cpu.set_register_low_byte(self.cpu.AX, result)
        # Set flags (carry flag is set if borrow)
        self._update_flags_after_arithmetic(al, value, result, 8, is_subtraction=True)
    
    def _sub_ax_imm16(self):
        value = self.cpu.fetch_word()
        ax = self.cpu.get_register(self.cpu.AX)
        result = (ax - value) & 0xFFFF
        self.cpu.set_register(self.cpu.AX, result)
        # Set flags (carry flag is set if borrow)
        self._update_flags_after_arithmetic(ax, value, result, 16, is_subtraction=True)
    
    def _update_flags_after_arithmetic(self, operand1, operand2, result, bits, is_subtraction=False):
        """Update CPU flags after an arithmetic operation."""
        mask = (1 << bits) - 1
        sign_bit = 1 << (bits - 1)
        
        # Zero flag (ZF): set if result is zero
        self.cpu.set_flag(self.cpu.ZERO_FLAG, (result & mask) == 0)
        
        # Sign flag (SF): set if the most significant bit of the result is set
        self.cpu.set_flag(self.cpu.SIGN_FLAG, (result & sign_bit) != 0)
        
        # Carry flag (CF)
        if is_subtraction:
            # In subtraction, CF is set if a borrow is needed
            self.cpu.set_flag(self.cpu.CARRY_FLAG, (operand1 & mask) < (operand2 & mask))
        else:
            # In addition, CF is set if there's a carry out of the most significant bit
            self.cpu.set_flag(self.cpu.CARRY_FLAG, result > mask)
        
        # Parity flag (PF): set if the number of set bits in the least significant byte is even
        parity = result & 0xFF
        parity ^= parity >> 4
        parity ^= parity >> 2
        parity ^= parity >> 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, (parity & 1) == 0)
        
        # Auxiliary carry flag (AF): set if there was a carry from bit 3 to bit 4
        if is_subtraction:
            self.cpu.set_flag(self.cpu.AUXILIARY_CARRY_FLAG, 
                             ((operand1 & 0xF) - (operand2 & 0xF)) & 0x10)
        else:
            self.cpu.set_flag(self.cpu.AUXILIARY_CARRY_FLAG, 
                             ((operand1 & 0xF) + (operand2 & 0xF)) & 0x10)
        
        # Overflow flag (OF): set if the result has the wrong sign considering the signs of the operands
        if is_subtraction:
            # Overflow if signs of operands differ and result sign differs from first operand
            operand1_sign = (operand1 & sign_bit) != 0
            operand2_sign = (operand2 & sign_bit) != 0
            result_sign = (result & sign_bit) != 0
            self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 
                             operand1_sign != operand2_sign and operand1_sign != result_sign)
        else:
            # Overflow if operands have same sign but result has different sign
            operand1_sign = (operand1 & sign_bit) != 0
            operand2_sign = (operand2 & sign_bit) != 0
            result_sign = (result & sign_bit) != 0
            self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 
                             operand1_sign == operand2_sign and operand1_sign != result_sign)
    
    # Jump instructions
    def _jo_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if self.cpu.get_flag(self.cpu.OVERFLOW_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jno_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if not self.cpu.get_flag(self.cpu.OVERFLOW_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jb_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if self.cpu.get_flag(self.cpu.CARRY_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jnb_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if not self.cpu.get_flag(self.cpu.CARRY_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _je_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if self.cpu.get_flag(self.cpu.ZERO_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jne_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if not self.cpu.get_flag(self.cpu.ZERO_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jbe_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if self.cpu.get_flag(self.cpu.CARRY_FLAG) or self.cpu.get_flag(self.cpu.ZERO_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jnbe_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if not (self.cpu.get_flag(self.cpu.CARRY_FLAG) or self.cpu.get_flag(self.cpu.ZERO_FLAG)):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _js_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if self.cpu.get_flag(self.cpu.SIGN_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jns_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if not self.cpu.get_flag(self.cpu.SIGN_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jp_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if self.cpu.get_flag(self.cpu.PARITY_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jnp_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if not self.cpu.get_flag(self.cpu.PARITY_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jl_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if self.cpu.get_flag(self.cpu.SIGN_FLAG) != self.cpu.get_flag(self.cpu.OVERFLOW_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jnl_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if self.cpu.get_flag(self.cpu.SIGN_FLAG) == self.cpu.get_flag(self.cpu.OVERFLOW_FLAG):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jle_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if self.cpu.get_flag(self.cpu.ZERO_FLAG) or (self.cpu.get_flag(self.cpu.SIGN_FLAG) != self.cpu.get_flag(self.cpu.OVERFLOW_FLAG)):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _jnle_rel8(self):
        offset = self.cpu.fetch_byte()
        if offset & 0x80:  # Sign extend if negative
            offset = offset - 256
        if not self.cpu.get_flag(self.cpu.ZERO_FLAG) and (self.cpu.get_flag(self.cpu.SIGN_FLAG) == self.cpu.get_flag(self.cpu.OVERFLOW_FLAG)):
            self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _call_rel16(self):
        offset = self.cpu.fetch_word()
        # Sign extend the 16-bit offset
        if offset & 0x8000:
            offset = offset - 0x10000
        # Push the current IP onto the stack
        self.cpu.push(self.cpu.get_register(self.cpu.IP))
        # Add the offset to IP
        self.cpu.set_register(self.cpu.IP, (self.cpu.get_register(self.cpu.IP) + offset) & 0xFFFF)
    
    def _ret(self):
        # Pop the return address from the stack
        return_address = self.cpu.pop()
        self.cpu.set_register(self.cpu.IP, return_address)
    
    # Stack operations
    def _push_ax(self):
        self.cpu.push(self.cpu.get_register(self.cpu.AX))
    
    def _push_cx(self):
        self.cpu.push(self.cpu.get_register(self.cpu.CX))
    
    def _push_dx(self):
        self.cpu.push(self.cpu.get_register(self.cpu.DX))
    
    def _push_bx(self):
        self.cpu.push(self.cpu.get_register(self.cpu.BX))
    
    def _push_sp(self):
        # Note: 8086 pushes the value of SP before being decremented
        self.cpu.push(self.cpu.get_register(self.cpu.SP))
    
    def _push_bp(self):
        self.cpu.push(self.cpu.get_register(self.cpu.BP))
    
    def _push_si(self):
        self.cpu.push(self.cpu.get_register(self.cpu.SI))
    
    def _push_di(self):
        self.cpu.push(self.cpu.get_register(self.cpu.DI))
    
    def _pop_ax(self):
        self.cpu.set_register(self.cpu.AX, self.cpu.pop())
    
    def _pop_cx(self):
        self.cpu.set_register(self.cpu.CX, self.cpu.pop())
    
    def _pop_dx(self):
        self.cpu.set_register(self.cpu.DX, self.cpu.pop())
    
    def _pop_bx(self):
        self.cpu.set_register(self.cpu.BX, self.cpu.pop())
    
    def _pop_sp(self):
        self.cpu.set_register(self.cpu.SP, self.cpu.pop())
    
    def _pop_bp(self):
        self.cpu.set_register(self.cpu.BP, self.cpu.pop())
    
    def _pop_si(self):
        self.cpu.set_register(self.cpu.SI, self.cpu.pop())
    
    def _pop_di(self):
        self.cpu.set_register(self.cpu.DI, self.cpu.pop())
    
    # Miscellaneous instructions
    def _nop(self):
        # No operation
        pass
    
    def _hlt(self):
        # Halt the CPU
        self.cpu.halted = True
    
    def _int_imm8(self):
        # Software interrupt
        interrupt_number = self.cpu.fetch_byte()
        # Implement interrupt handling
        if interrupt_number == 0x21:  # DOS services
            ah = self.cpu.get_register_high_byte(self.cpu.AX)
            if ah == 0x09:  # Print string
                # Get the address of the string from DS:DX
                ds = self.cpu.get_register(self.cpu.DS)
                dx = self.cpu.get_register(self.cpu.DX)
                string_address = self.cpu.get_physical_address(ds, dx)
                
                # Read string until '$' character
                string_value = ""
                byte = self.cpu.memory.read_byte(string_address)
                while byte != 0x24:  # '$' character
                    string_value += chr(byte)
                    string_address += 1
                    byte = self.cpu.memory.read_byte(string_address)
                
                # Print the string
                print(string_value, end='')
