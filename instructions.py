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
        
        # ----- DATA TRANSFER INSTRUCTIONS -----
        
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

        # XCHG instructions - Comment them out for now to avoid execution issues
        # instruction_map[0x86] = ("XCHG r/m8, r8", self._xchg_rm8_r8)
        # instruction_map[0x87] = ("XCHG r/m16, r16", self._xchg_rm16_r16)
        # instruction_map[0x91] = ("XCHG AX, CX", self._xchg_ax_cx)
        # instruction_map[0x92] = ("XCHG AX, DX", self._xchg_ax_dx)
        # instruction_map[0x93] = ("XCHG AX, BX", self._xchg_ax_bx)
        # instruction_map[0x94] = ("XCHG AX, SP", self._xchg_ax_sp)
        # instruction_map[0x95] = ("XCHG AX, BP", self._xchg_ax_bp)
        # instruction_map[0x96] = ("XCHG AX, SI", self._xchg_ax_si)
        # instruction_map[0x97] = ("XCHG AX, DI", self._xchg_ax_di)
        
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
        
        # Load effective address
        instruction_map[0x8D] = ("LEA r16, m", self._lea_r16_m)
        
        # Load pointer using DS/ES
        instruction_map[0xC4] = ("LES r16, m16", self._les_r16_m16)
        instruction_map[0xC5] = ("LDS r16, m16", self._lds_r16_m16)
        
        # Flag register operations
        instruction_map[0x9C] = ("PUSHF", self._pushf)
        instruction_map[0x9D] = ("POPF", self._popf)
        instruction_map[0x9E] = ("SAHF", self._sahf)
        instruction_map[0x9F] = ("LAHF", self._lahf)
        
        # XLAT (translate)
        instruction_map[0xD7] = ("XLAT", self._xlat)
        
        # IN/OUT - I/O port operations
        instruction_map[0xE4] = ("IN AL, imm8", self._in_al_imm8)
        instruction_map[0xE5] = ("IN AX, imm8", self._in_ax_imm8)
        instruction_map[0xEC] = ("IN AL, DX", self._in_al_dx)
        instruction_map[0xED] = ("IN AX, DX", self._in_ax_dx)
        
        instruction_map[0xE6] = ("OUT imm8, AL", self._out_imm8_al)
        instruction_map[0xE7] = ("OUT imm8, AX", self._out_imm8_ax)
        instruction_map[0xEE] = ("OUT DX, AL", self._out_dx_al)
        instruction_map[0xEF] = ("OUT DX, AX", self._out_dx_ax)
        
        # ----- ARITHMETIC INSTRUCTIONS -----
        
        # ADD instructions
        instruction_map[0x00] = ("ADD r/m8, r8", self._add_rm8_r8)
        instruction_map[0x01] = ("ADD r/m16, r16", self._add_rm16_r16)
        instruction_map[0x02] = ("ADD r8, r/m8", self._add_r8_rm8)
        instruction_map[0x03] = ("ADD r16, r/m16", self._add_r16_rm16)
        instruction_map[0x04] = ("ADD AL, imm8", self._add_al_imm8)
        instruction_map[0x05] = ("ADD AX, imm16", self._add_ax_imm16)
        
        # ADC (Add with Carry) instructions
        instruction_map[0x10] = ("ADC r/m8, r8", self._adc_rm8_r8)
        instruction_map[0x11] = ("ADC r/m16, r16", self._adc_rm16_r16)
        instruction_map[0x12] = ("ADC r8, r/m8", self._adc_r8_rm8)
        instruction_map[0x13] = ("ADC r16, r/m16", self._adc_r16_rm16)
        instruction_map[0x14] = ("ADC AL, imm8", self._adc_al_imm8)
        instruction_map[0x15] = ("ADC AX, imm16", self._adc_ax_imm16)
        
        # SUB instructions
        instruction_map[0x28] = ("SUB r/m8, r8", self._sub_rm8_r8)
        instruction_map[0x29] = ("SUB r/m16, r16", self._sub_rm16_r16)
        instruction_map[0x2A] = ("SUB r8, r/m8", self._sub_r8_rm8)
        instruction_map[0x2B] = ("SUB r16, r/m16", self._sub_r16_rm16)
        instruction_map[0x2C] = ("SUB AL, imm8", self._sub_al_imm8)
        instruction_map[0x2D] = ("SUB AX, imm16", self._sub_ax_imm16)
        
        # SBB (Subtract with Borrow) instructions
        instruction_map[0x18] = ("SBB r/m8, r8", self._sbb_rm8_r8)
        instruction_map[0x19] = ("SBB r/m16, r16", self._sbb_rm16_r16)
        instruction_map[0x1A] = ("SBB r8, r/m8", self._sbb_r8_rm8)
        instruction_map[0x1B] = ("SBB r16, r/m16", self._sbb_r16_rm16)
        instruction_map[0x1C] = ("SBB AL, imm8", self._sbb_al_imm8)
        instruction_map[0x1D] = ("SBB AX, imm16", self._sbb_ax_imm16)
        
        # INC instructions (increment)
        instruction_map[0x40] = ("INC AX", self._inc_ax)
        instruction_map[0x41] = ("INC CX", self._inc_cx)
        instruction_map[0x42] = ("INC DX", self._inc_dx)
        instruction_map[0x43] = ("INC BX", self._inc_bx)
        instruction_map[0x44] = ("INC SP", self._inc_sp)
        instruction_map[0x45] = ("INC BP", self._inc_bp)
        instruction_map[0x46] = ("INC SI", self._inc_si)
        instruction_map[0x47] = ("INC DI", self._inc_di)
        
        # DEC instructions (decrement)
        instruction_map[0x48] = ("DEC AX", self._dec_ax)
        instruction_map[0x49] = ("DEC CX", self._dec_cx)
        instruction_map[0x4A] = ("DEC DX", self._dec_dx)
        instruction_map[0x4B] = ("DEC BX", self._dec_bx)
        instruction_map[0x4C] = ("DEC SP", self._dec_sp)
        instruction_map[0x4D] = ("DEC BP", self._dec_bp)
        instruction_map[0x4E] = ("DEC SI", self._dec_si)
        instruction_map[0x4F] = ("DEC DI", self._dec_di)
        
        # NEG (negate) is typically part of group 3 (0xF6/0xF7) with ModR/M byte
        # The 0xF6/0xF7 instructions are implemented separately with ModR/M parsing
        
        # CMP (compare) instructions
        instruction_map[0x38] = ("CMP r/m8, r8", self._cmp_rm8_r8)
        instruction_map[0x39] = ("CMP r/m16, r16", self._cmp_rm16_r16)
        instruction_map[0x3A] = ("CMP r8, r/m8", self._cmp_r8_rm8)
        instruction_map[0x3B] = ("CMP r16, r/m16", self._cmp_r16_rm16)
        instruction_map[0x3C] = ("CMP AL, imm8", self._cmp_al_imm8)
        instruction_map[0x3D] = ("CMP AX, imm16", self._cmp_ax_imm16)
        
        # Multiplication and division instructions
        instruction_map[0xF6] = ("MUL/DIV Group", self._f6_group_handler)  # Opcode 0xF6 covers multiple instructions
        instruction_map[0xF7] = ("MUL/DIV Group Word", self._f7_group_handler)  # Opcode 0xF7 covers multiple word instructions
        
        # Conversion instructions
        instruction_map[0x98] = ("CBW", self._cbw)  # Convert byte to word
        instruction_map[0x99] = ("CWD", self._cwd)  # Convert word to doubleword
        
        # Decimal adjust instructions
        instruction_map[0x27] = ("DAA", self._daa)  # Decimal adjust after addition
        instruction_map[0x2F] = ("DAS", self._das)  # Decimal adjust after subtraction
        instruction_map[0x37] = ("AAA", self._aaa)  # ASCII adjust after addition
        instruction_map[0x3F] = ("AAS", self._aas)  # ASCII adjust after subtraction
        instruction_map[0xD4] = ("AAM", self._aam)  # ASCII adjust after multiplication
        instruction_map[0xD5] = ("AAD", self._aad)  # ASCII adjust before division
        
        # ----- LOGICAL INSTRUCTIONS -----
        
        # AND instructions
        instruction_map[0x20] = ("AND r/m8, r8", self._and_rm8_r8)
        instruction_map[0x21] = ("AND r/m16, r16", self._and_rm16_r16)
        instruction_map[0x22] = ("AND r8, r/m8", self._and_r8_rm8)
        instruction_map[0x23] = ("AND r16, r/m16", self._and_r16_rm16)
        instruction_map[0x24] = ("AND AL, imm8", self._and_al_imm8)
        instruction_map[0x25] = ("AND AX, imm16", self._and_ax_imm16)
        
        # OR instructions
        instruction_map[0x08] = ("OR r/m8, r8", self._or_rm8_r8)
        instruction_map[0x09] = ("OR r/m16, r16", self._or_rm16_r16)
        instruction_map[0x0A] = ("OR r8, r/m8", self._or_r8_rm8)
        instruction_map[0x0B] = ("OR r16, r/m16", self._or_r16_rm16)
        instruction_map[0x0C] = ("OR AL, imm8", self._or_al_imm8)
        instruction_map[0x0D] = ("OR AX, imm16", self._or_ax_imm16)
        
        # XOR instructions
        instruction_map[0x30] = ("XOR r/m8, r8", self._xor_rm8_r8)
        instruction_map[0x31] = ("XOR r/m16, r16", self._xor_rm16_r16)
        instruction_map[0x32] = ("XOR r8, r/m8", self._xor_r8_rm8)
        instruction_map[0x33] = ("XOR r16, r/m16", self._xor_r16_rm16)
        instruction_map[0x34] = ("XOR AL, imm8", self._xor_al_imm8)
        instruction_map[0x35] = ("XOR AX, imm16", self._xor_ax_imm16)
        
        # NOT is typically part of group 3 (0xF6/0xF7) with ModR/M byte
        # Will be handled by the F6/F7 group handlers
        
        # TEST instructions
        instruction_map[0x84] = ("TEST r/m8, r8", self._test_rm8_r8)
        instruction_map[0x85] = ("TEST r/m16, r16", self._test_rm16_r16)
        instruction_map[0xA8] = ("TEST AL, imm8", self._test_al_imm8)
        instruction_map[0xA9] = ("TEST AX, imm16", self._test_ax_imm16)
        
        # Shift and rotate instructions
        instruction_map[0xD0] = ("Shift/Rotate Group Byte 1", self._d0_group_handler)
        instruction_map[0xD1] = ("Shift/Rotate Group Word 1", self._d1_group_handler)
        instruction_map[0xD2] = ("Shift/Rotate Group Byte CL", self._d2_group_handler)
        instruction_map[0xD3] = ("Shift/Rotate Group Word CL", self._d3_group_handler)
        
        # ----- STRING INSTRUCTIONS -----
        
        # String movement instructions
        instruction_map[0xA4] = ("MOVSB", self._movsb)
        instruction_map[0xA5] = ("MOVSW", self._movsw)
        instruction_map[0xA6] = ("CMPSB", self._cmpsb)
        instruction_map[0xA7] = ("CMPSW", self._cmpsw)
        instruction_map[0xAE] = ("SCASB", self._scasb)
        instruction_map[0xAF] = ("SCASW", self._scasw)
        instruction_map[0xAA] = ("STOSB", self._stosb)
        instruction_map[0xAB] = ("STOSW", self._stosw)
        instruction_map[0xAC] = ("LODSB", self._lodsb)
        instruction_map[0xAD] = ("LODSW", self._lodsw)
        
        # REP prefixes
        instruction_map[0xF2] = ("REPNE/REPNZ", self._repne_prefix)
        instruction_map[0xF3] = ("REP/REPE/REPZ", self._rep_prefix)
        
        # ----- CONTROL TRANSFER INSTRUCTIONS -----
        
        # JMP instructions
        instruction_map[0xEB] = ("JMP rel8", self._jmp_rel8)
        instruction_map[0xE9] = ("JMP rel16", self._jmp_rel16)
        instruction_map[0xEA] = ("JMP ptr16:16", self._jmp_ptr16_16)
        instruction_map[0xFF] = ("JMP/CALL Indirect Group", self._ff_group_handler)
        
        # Conditional jumps
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
        
        # JCXZ instruction
        instruction_map[0xE3] = ("JCXZ rel8", self._jcxz_rel8)
        
        # Loop instructions
        instruction_map[0xE2] = ("LOOP rel8", self._loop_rel8)
        instruction_map[0xE1] = ("LOOPE/LOOPZ rel8", self._loope_rel8)
        instruction_map[0xE0] = ("LOOPNE/LOOPNZ rel8", self._loopne_rel8)
        
        # CALL instructions
        instruction_map[0xE8] = ("CALL rel16", self._call_rel16)
        instruction_map[0x9A] = ("CALL ptr16:16", self._call_ptr16_16)
        
        # RET instructions
        instruction_map[0xC3] = ("RET", self._ret)
        instruction_map[0xC2] = ("RET imm16", self._ret_imm16)
        instruction_map[0xCB] = ("RET far", self._ret_far)
        instruction_map[0xCA] = ("RET far imm16", self._ret_far_imm16)
        
        # Interrupt instructions
        instruction_map[0xCD] = ("INT imm8", self._int_imm8)
        instruction_map[0xCE] = ("INTO", self._into)
        instruction_map[0xCF] = ("IRET", self._iret)
        
        # ----- PROCESSOR CONTROL INSTRUCTIONS -----
        
        # Flag manipulation
        instruction_map[0xF8] = ("CLC", self._clc)  # Clear carry flag
        instruction_map[0xF9] = ("STC", self._stc)  # Set carry flag
        instruction_map[0xF5] = ("CMC", self._cmc)  # Complement carry flag
        instruction_map[0xFC] = ("CLD", self._cld)  # Clear direction flag
        instruction_map[0xFD] = ("STD", self._std)  # Set direction flag
        instruction_map[0xFA] = ("CLI", self._cli)  # Clear interrupt flag
        instruction_map[0xFB] = ("STI", self._sti)  # Set interrupt flag
        
        # Processor control
        instruction_map[0x90] = ("NOP", self._nop)  # No operation
        instruction_map[0xF4] = ("HLT", self._hlt)  # Halt
        instruction_map[0x9B] = ("WAIT", self._wait)  # Wait
        instruction_map[0xF0] = ("LOCK", self._lock_prefix)  # Lock prefix
        
        # Coprocessor escape
        # ESC is a family of instructions starting with 0xD8-0xDF
        instruction_map[0xD8] = ("ESC 0", lambda: self.cpu.fetch_byte())  # Just consume the ModR/M byte
        instruction_map[0xD9] = ("ESC 1", lambda: self.cpu.fetch_byte())
        instruction_map[0xDA] = ("ESC 2", lambda: self.cpu.fetch_byte())
        instruction_map[0xDB] = ("ESC 3", lambda: self.cpu.fetch_byte())
        instruction_map[0xDC] = ("ESC 4", lambda: self.cpu.fetch_byte())
        instruction_map[0xDD] = ("ESC 5", lambda: self.cpu.fetch_byte())
        instruction_map[0xDE] = ("ESC 6", lambda: self.cpu.fetch_byte())
        instruction_map[0xDF] = ("ESC 7", lambda: self.cpu.fetch_byte())
        
        return instruction_map
    
    def decode(self, opcode):
        """Decode an opcode and return instruction information."""
        if opcode in self.instruction_map:
            return self.instruction_map[opcode]
        else:
            return (f"Unknown opcode: 0x{opcode:02X}", None)
            
    def get_instruction_name(self, opcode):
        """Get the mnemonic for an opcode (useful for debugging)."""
        if opcode in self.instruction_map:
            return self.instruction_map[opcode][0]
        else:
            return f"Unknown opcode: 0x{opcode:02X}"
    
    # Instruction implementations
    def _decode_modrm(self, modrm_byte):
        """Decode a ModR/M byte into its components."""
        mod = (modrm_byte >> 6) & 0x03
        reg = (modrm_byte >> 3) & 0x07
        rm = modrm_byte & 0x07
        return mod, reg, rm
        
    def _get_effective_address(self, mod, rm):
        """Calculate the effective address for memory operands."""
        if mod == 0:
            if rm == 0:  # [BX + SI]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    (self.cpu.get_register(self.cpu.BX) + self.cpu.get_register(self.cpu.SI)) & 0xFFFF
                )
            elif rm == 1:  # [BX + DI]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    (self.cpu.get_register(self.cpu.BX) + self.cpu.get_register(self.cpu.DI)) & 0xFFFF
                )
            elif rm == 2:  # [BP + SI]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.SS),
                    (self.cpu.get_register(self.cpu.BP) + self.cpu.get_register(self.cpu.SI)) & 0xFFFF
                )
            elif rm == 3:  # [BP + DI]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.SS),
                    (self.cpu.get_register(self.cpu.BP) + self.cpu.get_register(self.cpu.DI)) & 0xFFFF
                )
            elif rm == 4:  # [SI]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    self.cpu.get_register(self.cpu.SI)
                )
            elif rm == 5:  # [DI]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    self.cpu.get_register(self.cpu.DI)
                )
            elif rm == 6:  # Direct address
                disp_low = self.cpu.fetch_byte()
                disp_high = self.cpu.fetch_byte()
                disp = (disp_high << 8) | disp_low
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    disp
                )
            elif rm == 7:  # [BX]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    self.cpu.get_register(self.cpu.BX)
                )
        elif mod == 1:
            # 8-bit displacement
            disp = self.cpu.fetch_byte()
            if disp & 0x80:  # Sign extend
                disp = disp - 256
                
            if rm == 0:  # [BX + SI + disp8]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    (self.cpu.get_register(self.cpu.BX) + self.cpu.get_register(self.cpu.SI) + disp) & 0xFFFF
                )
            elif rm == 1:  # [BX + DI + disp8]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    (self.cpu.get_register(self.cpu.BX) + self.cpu.get_register(self.cpu.DI) + disp) & 0xFFFF
                )
            elif rm == 2:  # [BP + SI + disp8]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.SS),
                    (self.cpu.get_register(self.cpu.BP) + self.cpu.get_register(self.cpu.SI) + disp) & 0xFFFF
                )
            elif rm == 3:  # [BP + DI + disp8]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.SS),
                    (self.cpu.get_register(self.cpu.BP) + self.cpu.get_register(self.cpu.DI) + disp) & 0xFFFF
                )
            elif rm == 4:  # [SI + disp8]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    (self.cpu.get_register(self.cpu.SI) + disp) & 0xFFFF
                )
            elif rm == 5:  # [DI + disp8]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    (self.cpu.get_register(self.cpu.DI) + disp) & 0xFFFF
                )
            elif rm == 6:  # [BP + disp8]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.SS),
                    (self.cpu.get_register(self.cpu.BP) + disp) & 0xFFFF
                )
            elif rm == 7:  # [BX + disp8]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    (self.cpu.get_register(self.cpu.BX) + disp) & 0xFFFF
                )
        elif mod == 2:
            # 16-bit displacement
            disp_low = self.cpu.fetch_byte()
            disp_high = self.cpu.fetch_byte()
            disp = (disp_high << 8) | disp_low
            
            if rm == 0:  # [BX + SI + disp16]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    (self.cpu.get_register(self.cpu.BX) + self.cpu.get_register(self.cpu.SI) + disp) & 0xFFFF
                )
            elif rm == 1:  # [BX + DI + disp16]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    (self.cpu.get_register(self.cpu.BX) + self.cpu.get_register(self.cpu.DI) + disp) & 0xFFFF
                )
            elif rm == 2:  # [BP + SI + disp16]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.SS),
                    (self.cpu.get_register(self.cpu.BP) + self.cpu.get_register(self.cpu.SI) + disp) & 0xFFFF
                )
            elif rm == 3:  # [BP + DI + disp16]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.SS),
                    (self.cpu.get_register(self.cpu.BP) + self.cpu.get_register(self.cpu.DI) + disp) & 0xFFFF
                )
            elif rm == 4:  # [SI + disp16]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    (self.cpu.get_register(self.cpu.SI) + disp) & 0xFFFF
                )
            elif rm == 5:  # [DI + disp16]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    (self.cpu.get_register(self.cpu.DI) + disp) & 0xFFFF
                )
            elif rm == 6:  # [BP + disp16]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.SS),
                    (self.cpu.get_register(self.cpu.BP) + disp) & 0xFFFF
                )
            elif rm == 7:  # [BX + disp16]
                return self.cpu.get_physical_address(
                    self.cpu.get_register(self.cpu.DS),
                    (self.cpu.get_register(self.cpu.BX) + disp) & 0xFFFF
                )
        
        # Should not reach here
        raise ValueError(f"Invalid ModR/M combination: mod={mod}, rm={rm}")
    
    def _get_register_by_index(self, reg_index, is_byte=False):
        """Get register value by index from ModR/M byte."""
        if is_byte:
            # 8-bit registers
            if reg_index == 0:  # AL
                return self.cpu.get_register_low_byte(self.cpu.AX)
            elif reg_index == 1:  # CL
                return self.cpu.get_register_low_byte(self.cpu.CX)
            elif reg_index == 2:  # DL
                return self.cpu.get_register_low_byte(self.cpu.DX)
            elif reg_index == 3:  # BL
                return self.cpu.get_register_low_byte(self.cpu.BX)
            elif reg_index == 4:  # AH
                return self.cpu.get_register_high_byte(self.cpu.AX)
            elif reg_index == 5:  # CH
                return self.cpu.get_register_high_byte(self.cpu.CX)
            elif reg_index == 6:  # DH
                return self.cpu.get_register_high_byte(self.cpu.DX)
            elif reg_index == 7:  # BH
                return self.cpu.get_register_high_byte(self.cpu.BX)
        else:
            # 16-bit registers
            if reg_index == 0:  # AX
                return self.cpu.get_register(self.cpu.AX)
            elif reg_index == 1:  # CX
                return self.cpu.get_register(self.cpu.CX)
            elif reg_index == 2:  # DX
                return self.cpu.get_register(self.cpu.DX)
            elif reg_index == 3:  # BX
                return self.cpu.get_register(self.cpu.BX)
            elif reg_index == 4:  # SP
                return self.cpu.get_register(self.cpu.SP)
            elif reg_index == 5:  # BP
                return self.cpu.get_register(self.cpu.BP)
            elif reg_index == 6:  # SI
                return self.cpu.get_register(self.cpu.SI)
            elif reg_index == 7:  # DI
                return self.cpu.get_register(self.cpu.DI)
        # Default fallback
        return 0
    
    def _set_register_by_index(self, reg_index, value, is_byte=False):
        """Set register by index from ModR/M byte."""
        if is_byte:
            # 8-bit registers
            if reg_index == 0:  # AL
                self.cpu.set_register_low_byte(self.cpu.AX, value)
            elif reg_index == 1:  # CL
                self.cpu.set_register_low_byte(self.cpu.CX, value)
            elif reg_index == 2:  # DL
                self.cpu.set_register_low_byte(self.cpu.DX, value)
            elif reg_index == 3:  # BL
                self.cpu.set_register_low_byte(self.cpu.BX, value)
            elif reg_index == 4:  # AH
                self.cpu.set_register_high_byte(self.cpu.AX, value)
            elif reg_index == 5:  # CH
                self.cpu.set_register_high_byte(self.cpu.CX, value)
            elif reg_index == 6:  # DH
                self.cpu.set_register_high_byte(self.cpu.DX, value)
            elif reg_index == 7:  # BH
                self.cpu.set_register_high_byte(self.cpu.BX, value)
        else:
            # 16-bit registers
            if reg_index == 0:  # AX
                self.cpu.set_register(self.cpu.AX, value)
            elif reg_index == 1:  # CX
                self.cpu.set_register(self.cpu.CX, value)
            elif reg_index == 2:  # DX
                self.cpu.set_register(self.cpu.DX, value)
            elif reg_index == 3:  # BX
                self.cpu.set_register(self.cpu.BX, value)
            elif reg_index == 4:  # SP
                self.cpu.set_register(self.cpu.SP, value)
            elif reg_index == 5:  # BP
                self.cpu.set_register(self.cpu.BP, value)
            elif reg_index == 6:  # SI
                self.cpu.set_register(self.cpu.SI, value)
            elif reg_index == 7:  # DI
                self.cpu.set_register(self.cpu.DI, value)
    
    def _mov_rm8_r8(self, modrm):
        """Implementation for MOV r/m8, r8 (88)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get the value from the source register
        reg_value = self._get_register_by_index(reg, is_byte=True)
        
        if mod == 3:
            # Register to register
            self._set_register_by_index(rm, reg_value, is_byte=True)
        else:
            # Register to memory
            effective_addr = self._get_effective_address(mod, rm)
            self.cpu.memory.write_byte(effective_addr, reg_value)
    
    def _mov_rm16_r16(self, modrm):
        """Implementation for MOV r/m16, r16 (89)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get the value from the source register
        reg_value = self._get_register_by_index(reg, is_byte=False)
        
        if mod == 3:
            # Register to register
            self._set_register_by_index(rm, reg_value, is_byte=False)
        else:
            # Register to memory
            effective_addr = self._get_effective_address(mod, rm)
            self.cpu.memory.write_word(effective_addr, reg_value)
    
    def _mov_r8_rm8(self, modrm):
        """Implementation for MOV r8, r/m8 (8A)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        if mod == 3:
            # Register to register
            rm_value = self._get_register_by_index(rm, is_byte=True)
            self._set_register_by_index(reg, rm_value, is_byte=True)
        else:
            # Memory to register
            effective_addr = self._get_effective_address(mod, rm)
            value = self.cpu.memory.read_byte(effective_addr)
            self._set_register_by_index(reg, value, is_byte=True)
    
    def _mov_r16_rm16(self, modrm):
        """Implementation for MOV r16, r/m16 (8B)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        if mod == 3:
            # Register to register
            rm_value = self._get_register_by_index(rm, is_byte=False)
            self._set_register_by_index(reg, rm_value, is_byte=False)
        else:
            # Memory to register
            effective_addr = self._get_effective_address(mod, rm)
            value = self.cpu.memory.read_word(effective_addr)
            self._set_register_by_index(reg, value, is_byte=False)
    
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
        """Implementation for ADD r/m8, r8 (00)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get the value from the source register
        reg_value = self._get_register_by_index(reg, is_byte=True)
        
        if mod == 3:
            # Register to register
            rm_value = self._get_register_by_index(rm, is_byte=True)
            result = (rm_value + reg_value) & 0xFF
            self._set_register_by_index(rm, result, is_byte=True)
            self._update_flags_after_arithmetic(rm_value, reg_value, result, 8)
        else:
            # Memory and register
            effective_addr = self._get_effective_address(mod, rm)
            memory_value = self.cpu.memory.read_byte(effective_addr)
            result = (memory_value + reg_value) & 0xFF
            self.cpu.memory.write_byte(effective_addr, result)
            self._update_flags_after_arithmetic(memory_value, reg_value, result, 8)
    
    def _add_rm16_r16(self, modrm):
        """Implementation for ADD r/m16, r16 (01)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get the value from the source register
        reg_value = self._get_register_by_index(reg, is_byte=False)
        
        if mod == 3:
            # Register to register
            rm_value = self._get_register_by_index(rm, is_byte=False)
            result = (rm_value + reg_value) & 0xFFFF
            self._set_register_by_index(rm, result, is_byte=False)
            self._update_flags_after_arithmetic(rm_value, reg_value, result, 16)
        else:
            # Memory and register
            effective_addr = self._get_effective_address(mod, rm)
            memory_value = self.cpu.memory.read_word(effective_addr)
            result = (memory_value + reg_value) & 0xFFFF
            self.cpu.memory.write_word(effective_addr, result)
            self._update_flags_after_arithmetic(memory_value, reg_value, result, 16)
    
    def _add_r8_rm8(self, modrm):
        """Implementation for ADD r8, r/m8 (02)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get the value from the destination register
        reg_value = self._get_register_by_index(reg, is_byte=True)
        
        if mod == 3:
            # Register to register
            rm_value = self._get_register_by_index(rm, is_byte=True)
            result = (reg_value + rm_value) & 0xFF
            self._set_register_by_index(reg, result, is_byte=True)
            self._update_flags_after_arithmetic(reg_value, rm_value, result, 8)
        else:
            # Memory and register
            effective_addr = self._get_effective_address(mod, rm)
            memory_value = self.cpu.memory.read_byte(effective_addr)
            result = (reg_value + memory_value) & 0xFF
            self._set_register_by_index(reg, result, is_byte=True)
            self._update_flags_after_arithmetic(reg_value, memory_value, result, 8)
    
    def _add_r16_rm16(self, modrm):
        """Implementation for ADD r16, r/m16 (03)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get the value from the destination register
        reg_value = self._get_register_by_index(reg, is_byte=False)
        
        if mod == 3:
            # Register to register
            rm_value = self._get_register_by_index(rm, is_byte=False)
            result = (reg_value + rm_value) & 0xFFFF
            self._set_register_by_index(reg, result, is_byte=False)
            self._update_flags_after_arithmetic(reg_value, rm_value, result, 16)
        else:
            # Memory and register
            effective_addr = self._get_effective_address(mod, rm)
            memory_value = self.cpu.memory.read_word(effective_addr)
            result = (reg_value + memory_value) & 0xFFFF
            self._set_register_by_index(reg, result, is_byte=False)
            self._update_flags_after_arithmetic(reg_value, memory_value, result, 16)
    
    def _add_al_imm8(self):
        """Implementation for ADD AL, imm8 (04)"""
        value = self.cpu.fetch_byte()
        al = self.cpu.get_register_low_byte(self.cpu.AX)
        result = (al + value) & 0xFF
        self.cpu.set_register_low_byte(self.cpu.AX, result)
        self._update_flags_after_arithmetic(al, value, result, 8)
    
    def _add_ax_imm16(self):
        value = self.cpu.fetch_word()
        result = (self.cpu.get_register(self.cpu.AX) + value) & 0xFFFF
        self.cpu.set_register(self.cpu.AX, result)
        # Set flags
        self._update_flags_after_arithmetic(self.cpu.get_register(self.cpu.AX), value, result, 16)
    
    # ADC (Add with Carry) instructions
    def _adc_rm8_r8(self, modrm):
        """Implementation for ADC r/m8, r8 (10)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg, is_byte=True)
        carry = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm, is_byte=True)
            result = (rm_val + reg_val + carry) & 0xFF
            self._set_register_by_index(rm, result, is_byte=True)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_byte(addr)
            result = (rm_val + reg_val + carry) & 0xFF
            self.cpu.memory.write_byte(addr, result)
        
        # Update flags
        self._update_flags_after_arithmetic(rm_val, reg_val + carry, result, 8)
    
    def _adc_rm16_r16(self, modrm):
        """Implementation for ADC r/m16, r16 (11)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg)
        carry = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm)
            result = (rm_val + reg_val + carry) & 0xFFFF
            self._set_register_by_index(rm, result)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_word(addr)
            result = (rm_val + reg_val + carry) & 0xFFFF
            self.cpu.memory.write_word(addr, result)
        
        # Update flags
        self._update_flags_after_arithmetic(rm_val, reg_val + carry, result, 16)
    
    def _adc_r8_rm8(self, modrm):
        """Implementation for ADC r8, r/m8 (12)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg, is_byte=True)
        carry = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm, is_byte=True)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_byte(addr)
        
        # Perform ADC operation
        result = (reg_val + rm_val + carry) & 0xFF
        
        # Store result in register
        self._set_register_by_index(reg, result, is_byte=True)
        
        # Update flags
        self._update_flags_after_arithmetic(reg_val, rm_val + carry, result, 8)
    
    def _adc_r16_rm16(self, modrm):
        """Implementation for ADC r16, r/m16 (13)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg)
        carry = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_word(addr)
        
        # Perform ADC operation
        result = (reg_val + rm_val + carry) & 0xFFFF
        
        # Store result in register
        self._set_register_by_index(reg, result)
        
        # Update flags
        self._update_flags_after_arithmetic(reg_val, rm_val + carry, result, 16)
    
    def _adc_al_imm8(self):
        """Implementation for ADC AL, imm8 (14)"""
        imm8 = self.cpu.fetch_byte()
        al_value = self.cpu.get_register_low_byte(self.cpu.AX)
        carry = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        
        # Perform ADC operation
        result = (al_value + imm8 + carry) & 0xFF
        
        # Store result in AL
        self.cpu.set_register_low_byte(self.cpu.AX, result)
        
        # Update flags
        self._update_flags_after_arithmetic(al_value, imm8 + carry, result, 8)
    
    def _adc_ax_imm16(self):
        """Implementation for ADC AX, imm16 (15)"""
        imm16 = self.cpu.fetch_word()
        ax_value = self.cpu.get_register(self.cpu.AX)
        carry = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        
        # Perform ADC operation
        result = (ax_value + imm16 + carry) & 0xFFFF
        
        # Store result in AX
        self.cpu.set_register(self.cpu.AX, result)
        
        # Update flags
        self._update_flags_after_arithmetic(ax_value, imm16 + carry, result, 16)
    
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
    
    # SBB (Subtract with Borrow) instructions
    def _sbb_rm8_r8(self, modrm):
        """Implementation for SBB r/m8, r8 (18)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg, is_byte=True)
        borrow = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm, is_byte=True)
            result = (rm_val - reg_val - borrow) & 0xFF
            self._set_register_by_index(rm, result, is_byte=True)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_byte(addr)
            result = (rm_val - reg_val - borrow) & 0xFF
            self.cpu.memory.write_byte(addr, result)
        
        # Update flags
        self._update_flags_after_arithmetic(rm_val, reg_val + borrow, result, 8, is_subtraction=True)
    
    def _sbb_rm16_r16(self, modrm):
        """Implementation for SBB r/m16, r16 (19)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg)
        borrow = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm)
            result = (rm_val - reg_val - borrow) & 0xFFFF
            self._set_register_by_index(rm, result)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_word(addr)
            result = (rm_val - reg_val - borrow) & 0xFFFF
            self.cpu.memory.write_word(addr, result)
        
        # Update flags
        self._update_flags_after_arithmetic(rm_val, reg_val + borrow, result, 16, is_subtraction=True)
    
    def _sbb_r8_rm8(self, modrm):
        """Implementation for SBB r8, r/m8 (1A)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg, is_byte=True)
        borrow = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm, is_byte=True)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_byte(addr)
        
        # Perform SBB operation
        result = (reg_val - rm_val - borrow) & 0xFF
        
        # Store result in register
        self._set_register_by_index(reg, result, is_byte=True)
        
        # Update flags
        self._update_flags_after_arithmetic(reg_val, rm_val + borrow, result, 8, is_subtraction=True)
    
    def _sbb_r16_rm16(self, modrm):
        """Implementation for SBB r16, r/m16 (1B)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg)
        borrow = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_word(addr)
        
        # Perform SBB operation
        result = (reg_val - rm_val - borrow) & 0xFFFF
        
        # Store result in register
        self._set_register_by_index(reg, result)
        
        # Update flags
        self._update_flags_after_arithmetic(reg_val, rm_val + borrow, result, 16, is_subtraction=True)
    
    def _sbb_al_imm8(self):
        """Implementation for SBB AL, imm8 (1C)"""
        imm8 = self.cpu.fetch_byte()
        al_value = self.cpu.get_register_low_byte(self.cpu.AX)
        borrow = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        
        # Perform SBB operation
        result = (al_value - imm8 - borrow) & 0xFF
        
        # Store result in AL
        self.cpu.set_register_low_byte(self.cpu.AX, result)
        
        # Update flags
        self._update_flags_after_arithmetic(al_value, imm8 + borrow, result, 8, is_subtraction=True)
    
    def _sbb_ax_imm16(self):
        """Implementation for SBB AX, imm16 (1D)"""
        imm16 = self.cpu.fetch_word()
        ax_value = self.cpu.get_register(self.cpu.AX)
        borrow = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        
        # Perform SBB operation
        result = (ax_value - imm16 - borrow) & 0xFFFF
        
        # Store result in AX
        self.cpu.set_register(self.cpu.AX, result)
        
        # Update flags
        self._update_flags_after_arithmetic(ax_value, imm16 + borrow, result, 16, is_subtraction=True)
    
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
    
    # ----- STRING INSTRUCTIONS -----
    
    def _movsb(self):
        """Implementation for MOVSB (A4) - Move byte from string to string"""
        # Get the source and destination addresses
        si = self.cpu.get_register(self.cpu.SI)
        di = self.cpu.get_register(self.cpu.DI)
        ds = self.cpu.get_register(self.cpu.DS)
        es = self.cpu.get_register(self.cpu.ES)
        
        # Get physical addresses
        source_addr = self.cpu.get_physical_address(ds, si)
        dest_addr = self.cpu.get_physical_address(es, di)
        
        # Move byte from source to destination
        byte = self.cpu.memory.read_byte(source_addr)
        self.cpu.memory.write_byte(dest_addr, byte)
        
        # Update SI and DI based on direction flag
        if self.cpu.get_flag(self.cpu.DIRECTION_FLAG):
            # Decrement
            self.cpu.set_register(self.cpu.SI, (si - 1) & 0xFFFF)
            self.cpu.set_register(self.cpu.DI, (di - 1) & 0xFFFF)
        else:
            # Increment
            self.cpu.set_register(self.cpu.SI, (si + 1) & 0xFFFF)
            self.cpu.set_register(self.cpu.DI, (di + 1) & 0xFFFF)
    
    def _movsw(self):
        """Implementation for MOVSW (A5) - Move word from string to string"""
        # Get the source and destination addresses
        si = self.cpu.get_register(self.cpu.SI)
        di = self.cpu.get_register(self.cpu.DI)
        ds = self.cpu.get_register(self.cpu.DS)
        es = self.cpu.get_register(self.cpu.ES)
        
        # Get physical addresses
        source_addr = self.cpu.get_physical_address(ds, si)
        dest_addr = self.cpu.get_physical_address(es, di)
        
        # Move word from source to destination
        word = self.cpu.memory.read_word(source_addr)
        self.cpu.memory.write_word(dest_addr, word)
        
        # Update SI and DI based on direction flag
        if self.cpu.get_flag(self.cpu.DIRECTION_FLAG):
            # Decrement
            self.cpu.set_register(self.cpu.SI, (si - 2) & 0xFFFF)
            self.cpu.set_register(self.cpu.DI, (di - 2) & 0xFFFF)
        else:
            # Increment
            self.cpu.set_register(self.cpu.SI, (si + 2) & 0xFFFF)
            self.cpu.set_register(self.cpu.DI, (di + 2) & 0xFFFF)
    
    def _cmpsb(self):
        """Implementation for CMPSB (A6) - Compare bytes in string"""
        # Get the source and destination addresses
        si = self.cpu.get_register(self.cpu.SI)
        di = self.cpu.get_register(self.cpu.DI)
        ds = self.cpu.get_register(self.cpu.DS)
        es = self.cpu.get_register(self.cpu.ES)
        
        # Get physical addresses
        source_addr = self.cpu.get_physical_address(ds, si)
        dest_addr = self.cpu.get_physical_address(es, di)
        
        # Compare bytes
        source_byte = self.cpu.memory.read_byte(source_addr)
        dest_byte = self.cpu.memory.read_byte(dest_addr)
        
        # Update flags (similar to CMP instruction)
        result = (source_byte - dest_byte) & 0xFF
        self._update_flags_after_arithmetic(source_byte, dest_byte, result, 8, is_subtraction=True)
        
        # Update SI and DI based on direction flag
        if self.cpu.get_flag(self.cpu.DIRECTION_FLAG):
            # Decrement
            self.cpu.set_register(self.cpu.SI, (si - 1) & 0xFFFF)
            self.cpu.set_register(self.cpu.DI, (di - 1) & 0xFFFF)
        else:
            # Increment
            self.cpu.set_register(self.cpu.SI, (si + 1) & 0xFFFF)
            self.cpu.set_register(self.cpu.DI, (di + 1) & 0xFFFF)
    
    def _cmpsw(self):
        """Implementation for CMPSW (A7) - Compare words in string"""
        # Get the source and destination addresses
        si = self.cpu.get_register(self.cpu.SI)
        di = self.cpu.get_register(self.cpu.DI)
        ds = self.cpu.get_register(self.cpu.DS)
        es = self.cpu.get_register(self.cpu.ES)
        
        # Get physical addresses
        source_addr = self.cpu.get_physical_address(ds, si)
        dest_addr = self.cpu.get_physical_address(es, di)
        
        # Compare words
        source_word = self.cpu.memory.read_word(source_addr)
        dest_word = self.cpu.memory.read_word(dest_addr)
        
        # Update flags (similar to CMP instruction)
        result = (source_word - dest_word) & 0xFFFF
        self._update_flags_after_arithmetic(source_word, dest_word, result, 16, is_subtraction=True)
        
        # Update SI and DI based on direction flag
        if self.cpu.get_flag(self.cpu.DIRECTION_FLAG):
            # Decrement
            self.cpu.set_register(self.cpu.SI, (si - 2) & 0xFFFF)
            self.cpu.set_register(self.cpu.DI, (di - 2) & 0xFFFF)
        else:
            # Increment
            self.cpu.set_register(self.cpu.SI, (si + 2) & 0xFFFF)
            self.cpu.set_register(self.cpu.DI, (di + 2) & 0xFFFF)
    
    def _stosb(self):
        """Implementation for STOSB (AA) - Store AL in string"""
        # Get the destination address
        di = self.cpu.get_register(self.cpu.DI)
        es = self.cpu.get_register(self.cpu.ES)
        
        # Get the value to store
        al = self.cpu.get_register_low_byte(self.cpu.AX)
        
        # Get physical address
        dest_addr = self.cpu.get_physical_address(es, di)
        
        # Store byte
        self.cpu.memory.write_byte(dest_addr, al)
        
        # Update DI based on direction flag
        if self.cpu.get_flag(self.cpu.DIRECTION_FLAG):
            # Decrement
            self.cpu.set_register(self.cpu.DI, (di - 1) & 0xFFFF)
        else:
            # Increment
            self.cpu.set_register(self.cpu.DI, (di + 1) & 0xFFFF)
    
    def _stosw(self):
        """Implementation for STOSW (AB) - Store AX in string"""
        # Get the destination address
        di = self.cpu.get_register(self.cpu.DI)
        es = self.cpu.get_register(self.cpu.ES)
        
        # Get the value to store
        ax = self.cpu.get_register(self.cpu.AX)
        
        # Get physical address
        dest_addr = self.cpu.get_physical_address(es, di)
        
        # Store word
        self.cpu.memory.write_word(dest_addr, ax)
        
        # Update DI based on direction flag
        if self.cpu.get_flag(self.cpu.DIRECTION_FLAG):
            # Decrement
            self.cpu.set_register(self.cpu.DI, (di - 2) & 0xFFFF)
        else:
            # Increment
            self.cpu.set_register(self.cpu.DI, (di + 2) & 0xFFFF)
    
    def _lodsb(self):
        """Implementation for LODSB (AC) - Load byte from string to AL"""
        # Get the source address
        si = self.cpu.get_register(self.cpu.SI)
        ds = self.cpu.get_register(self.cpu.DS)
        
        # Get physical address
        source_addr = self.cpu.get_physical_address(ds, si)
        
        # Load byte into AL
        byte = self.cpu.memory.read_byte(source_addr)
        self.cpu.set_register_low_byte(self.cpu.AX, byte)
        
        # Update SI based on direction flag
        if self.cpu.get_flag(self.cpu.DIRECTION_FLAG):
            # Decrement
            self.cpu.set_register(self.cpu.SI, (si - 1) & 0xFFFF)
        else:
            # Increment
            self.cpu.set_register(self.cpu.SI, (si + 1) & 0xFFFF)
    
    def _lodsw(self):
        """Implementation for LODSW (AD) - Load word from string to AX"""
        # Get the source address
        si = self.cpu.get_register(self.cpu.SI)
        ds = self.cpu.get_register(self.cpu.DS)
        
        # Get physical address
        source_addr = self.cpu.get_physical_address(ds, si)
        
        # Load word into AX
        word = self.cpu.memory.read_word(source_addr)
        self.cpu.set_register(self.cpu.AX, word)
        
        # Update SI based on direction flag
        if self.cpu.get_flag(self.cpu.DIRECTION_FLAG):
            # Decrement
            self.cpu.set_register(self.cpu.SI, (si - 2) & 0xFFFF)
        else:
            # Increment
            self.cpu.set_register(self.cpu.SI, (si + 2) & 0xFFFF)
    
    def _scasb(self):
        """Implementation for SCASB (AE) - Scan string for byte equal to AL"""
        # Get the destination address
        di = self.cpu.get_register(self.cpu.DI)
        es = self.cpu.get_register(self.cpu.ES)
        
        # Get the value to compare
        al = self.cpu.get_register_low_byte(self.cpu.AX)
        
        # Get physical address
        dest_addr = self.cpu.get_physical_address(es, di)
        
        # Compare AL with byte at ES:DI
        dest_byte = self.cpu.memory.read_byte(dest_addr)
        
        # Update flags (similar to CMP instruction)
        result = (al - dest_byte) & 0xFF
        self._update_flags_after_arithmetic(al, dest_byte, result, 8, is_subtraction=True)
        
        # Update DI based on direction flag
        if self.cpu.get_flag(self.cpu.DIRECTION_FLAG):
            # Decrement
            self.cpu.set_register(self.cpu.DI, (di - 1) & 0xFFFF)
        else:
            # Increment
            self.cpu.set_register(self.cpu.DI, (di + 1) & 0xFFFF)
    
    def _scasw(self):
        """Implementation for SCASW (AF) - Scan string for word equal to AX"""
        # Get the destination address
        di = self.cpu.get_register(self.cpu.DI)
        es = self.cpu.get_register(self.cpu.ES)
        
        # Get the value to compare
        ax = self.cpu.get_register(self.cpu.AX)
        
        # Get physical address
        dest_addr = self.cpu.get_physical_address(es, di)
        
        # Compare AX with word at ES:DI
        dest_word = self.cpu.memory.read_word(dest_addr)
        
        # Update flags (similar to CMP instruction)
        result = (ax - dest_word) & 0xFFFF
        self._update_flags_after_arithmetic(ax, dest_word, result, 16, is_subtraction=True)
        
        # Update DI based on direction flag
        if self.cpu.get_flag(self.cpu.DIRECTION_FLAG):
            # Decrement
            self.cpu.set_register(self.cpu.DI, (di - 2) & 0xFFFF)
        else:
            # Increment
            self.cpu.set_register(self.cpu.DI, (di + 2) & 0xFFFF)
    
    def _rep_prefix(self):
        """Implementation for REP/REPE/REPZ prefix (F3)"""
        # Get the opcode of the next instruction
        opcode = self.cpu.fetch_byte()
        
        # Get the repetition count from CX
        count = self.cpu.get_register(self.cpu.CX)
        
        # If CX is 0, skip the instruction
        if count == 0:
            # Skip the instruction - just consume any ModR/M byte if needed
            if opcode in [0x6C, 0x6D, 0x6E, 0x6F, 0xA4, 0xA5, 0xAA, 0xAB, 0xAC, 0xAD]:
                pass  # These opcodes don't have a ModR/M byte
            else:
                self.cpu.fetch_byte()  # Consume ModR/M byte
            return
        
        # Otherwise, execute the instruction repeatedly
        instruction_info = self.instruction_map.get(opcode)
        if instruction_info:
            name, handler = instruction_info
            
            # For CMPS and SCAS, repeat while CX != 0 and ZF = 1
            if opcode in [0xA6, 0xA7, 0xAE, 0xAF]:  # CMPSB, CMPSW, SCASB, SCASW
                while count > 0 and self.cpu.get_flag(self.cpu.ZERO_FLAG):
                    handler()
                    count = (count - 1) & 0xFFFF
                    self.cpu.set_register(self.cpu.CX, count)
                    if count == 0:
                        break
            # For other string operations, just repeat while CX != 0
            else:
                while count > 0:
                    handler()
                    count = (count - 1) & 0xFFFF
                    self.cpu.set_register(self.cpu.CX, count)
                    if count == 0:
                        break
        else:
            raise ValueError(f"Unknown opcode after REP prefix: {opcode:02X}")
    
    def _repne_prefix(self):
        """Implementation for REPNE/REPNZ prefix (F2)"""
        # Get the opcode of the next instruction
        opcode = self.cpu.fetch_byte()
        
        # Get the repetition count from CX
        count = self.cpu.get_register(self.cpu.CX)
        
        # If CX is 0, skip the instruction
        if count == 0:
            # Skip the instruction - just consume any ModR/M byte if needed
            if opcode in [0x6C, 0x6D, 0x6E, 0x6F, 0xA4, 0xA5, 0xAA, 0xAB, 0xAC, 0xAD]:
                pass  # These opcodes don't have a ModR/M byte
            else:
                self.cpu.fetch_byte()  # Consume ModR/M byte
            return
        
        # Otherwise, execute the instruction repeatedly
        instruction_info = self.instruction_map.get(opcode)
        if instruction_info:
            name, handler = instruction_info
            
            # For CMPS and SCAS, repeat while CX != 0 and ZF = 0
            if opcode in [0xA6, 0xA7, 0xAE, 0xAF]:  # CMPSB, CMPSW, SCASB, SCASW
                while count > 0 and not self.cpu.get_flag(self.cpu.ZERO_FLAG):
                    handler()
                    count = (count - 1) & 0xFFFF
                    self.cpu.set_register(self.cpu.CX, count)
                    if count == 0:
                        break
            # For other string operations, REPNE doesn't really make sense but handle anyway
            else:
                while count > 0:
                    handler()
                    count = (count - 1) & 0xFFFF
                    self.cpu.set_register(self.cpu.CX, count)
                    if count == 0:
                        break
        else:
            raise ValueError(f"Unknown opcode after REPNE prefix: {opcode:02X}")
    
    # ----- PROCESSOR CONTROL INSTRUCTIONS -----
    
    def _clc(self):
        """CLC - Clear carry flag (F8)"""
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
    
    def _stc(self):
        """STC - Set carry flag (F9)"""
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 1)
    
    def _cmc(self):
        """CMC - Complement carry flag (F5)"""
        current = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 1 if current == 0 else 0)
    
    def _cld(self):
        """CLD - Clear direction flag (FC)"""
        self.cpu.set_flag(self.cpu.DIRECTION_FLAG, 0)
    
    def _std(self):
        """STD - Set direction flag (FD)"""
        self.cpu.set_flag(self.cpu.DIRECTION_FLAG, 1)
    
    def _cli(self):
        """CLI - Clear interrupt flag (FA)"""
        self.cpu.set_flag(self.cpu.INTERRUPT_FLAG, 0)
    
    def _sti(self):
        """STI - Set interrupt flag (FB)"""
        self.cpu.set_flag(self.cpu.INTERRUPT_FLAG, 1)
    
    def _wait(self):
        """WAIT - Wait for coprocessor (9B)"""
        # In a real 8086, this would wait for a signal from the coprocessor
        # For simulation, just a NOP
        pass
    
    def _lock_prefix(self):
        """LOCK - Lock the bus for the next instruction (F0)"""
        # In a real 8086, this would assert the LOCK signal during the next instruction
        # For simulation, just fetch and execute the next instruction normally
        opcode = self.cpu.fetch_byte()
        instruction_info = self.instruction_map.get(opcode)
        if instruction_info:
            name, handler = instruction_info
            print(f"Executing with LOCK prefix: {name}")
            handler()
        else:
            raise ValueError(f"Unknown opcode: {opcode:02X}")
                
    # DEC instructions - decrement a register by 1
    def _dec_ax(self):
        """Decrement AX by 1."""
        value = self.cpu.get_register(self.cpu.AX)
        result = (value - 1) & 0xFFFF
        self.cpu.set_register(self.cpu.AX, result)
        # Update flags (note: CF is not affected by DEC)
        self._update_flags_after_dec(value, result)
        
    def _dec_cx(self):
        """Decrement CX by 1."""
        value = self.cpu.get_register(self.cpu.CX)
        result = (value - 1) & 0xFFFF
        self.cpu.set_register(self.cpu.CX, result)
        self._update_flags_after_dec(value, result)
        
    def _dec_dx(self):
        """Decrement DX by 1."""
        value = self.cpu.get_register(self.cpu.DX)
        result = (value - 1) & 0xFFFF
        self.cpu.set_register(self.cpu.DX, result)
        self._update_flags_after_dec(value, result)
        
    def _dec_bx(self):
        """Decrement BX by 1."""
        value = self.cpu.get_register(self.cpu.BX)
        result = (value - 1) & 0xFFFF
        self.cpu.set_register(self.cpu.BX, result)
        self._update_flags_after_dec(value, result)
        
    def _dec_sp(self):
        """Decrement SP by 1."""
        value = self.cpu.get_register(self.cpu.SP)
        result = (value - 1) & 0xFFFF
        self.cpu.set_register(self.cpu.SP, result)
        self._update_flags_after_dec(value, result)
        
    def _dec_bp(self):
        """Decrement BP by 1."""
        value = self.cpu.get_register(self.cpu.BP)
        result = (value - 1) & 0xFFFF
        self.cpu.set_register(self.cpu.BP, result)
        self._update_flags_after_dec(value, result)
        
    def _dec_si(self):
        """Decrement SI by 1."""
        value = self.cpu.get_register(self.cpu.SI)
        result = (value - 1) & 0xFFFF
        self.cpu.set_register(self.cpu.SI, result)
        self._update_flags_after_dec(value, result)
        
    def _dec_di(self):
        """Decrement DI by 1."""
        value = self.cpu.get_register(self.cpu.DI)
        result = (value - 1) & 0xFFFF
        self.cpu.set_register(self.cpu.DI, result)
        self._update_flags_after_dec(value, result)
    
    def _update_flags_after_dec(self, operand, result):
        """Update flags after a DEC operation (note: CF is not affected by DEC)."""
        # Set ZF if result is zero
        self.cpu.set_flag(self.cpu.ZERO_FLAG, result == 0)
        
        # Set SF if the result is negative (bit 15 for 16-bit result)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, (result & 0x8000) != 0)
        
        # Set PF if the number of bits set in the lower byte is even
        parity = 1
        low_byte = result & 0xFF
        for i in range(8):
            parity ^= ((low_byte >> i) & 1)
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity == 0)
        
        # Set AF if there was a borrow from bit 3 to bit 4
        self.cpu.set_flag(self.cpu.AUXILIARY_CARRY_FLAG, ((operand ^ 1 ^ result) & 0x10) != 0)
        
        # Set OF if there was an overflow (rare for DEC but can happen when decrementing 0x8000)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, operand == 0x8000)
    
    # INC instructions implementations
    def _inc_ax(self):
        """Increment AX by 1."""
        value = self.cpu.get_register(self.cpu.AX)
        result = (value + 1) & 0xFFFF
        self.cpu.set_register(self.cpu.AX, result)
        # Update flags (note: CF is not affected by INC)
        self._update_flags_after_inc(value, result)
        
    def _inc_cx(self):
        """Increment CX by 1."""
        value = self.cpu.get_register(self.cpu.CX)
        result = (value + 1) & 0xFFFF
        self.cpu.set_register(self.cpu.CX, result)
        self._update_flags_after_inc(value, result)
        
    def _inc_dx(self):
        """Increment DX by 1."""
        value = self.cpu.get_register(self.cpu.DX)
        result = (value + 1) & 0xFFFF
        self.cpu.set_register(self.cpu.DX, result)
        self._update_flags_after_inc(value, result)
        
    def _inc_bx(self):
        """Increment BX by 1."""
        value = self.cpu.get_register(self.cpu.BX)
        result = (value + 1) & 0xFFFF
        self.cpu.set_register(self.cpu.BX, result)
        self._update_flags_after_inc(value, result)
        
    def _inc_sp(self):
        """Increment SP by 1."""
        value = self.cpu.get_register(self.cpu.SP)
        result = (value + 1) & 0xFFFF
        self.cpu.set_register(self.cpu.SP, result)
        self._update_flags_after_inc(value, result)
        
    def _inc_bp(self):
        """Increment BP by 1."""
        value = self.cpu.get_register(self.cpu.BP)
        result = (value + 1) & 0xFFFF
        self.cpu.set_register(self.cpu.BP, result)
        self._update_flags_after_inc(value, result)
        
    def _inc_si(self):
        """Increment SI by 1."""
        value = self.cpu.get_register(self.cpu.SI)
        result = (value + 1) & 0xFFFF
        self.cpu.set_register(self.cpu.SI, result)
        self._update_flags_after_inc(value, result)
        
    def _inc_di(self):
        """Increment DI by 1."""
        value = self.cpu.get_register(self.cpu.DI)
        result = (value + 1) & 0xFFFF
        self.cpu.set_register(self.cpu.DI, result)
        self._update_flags_after_inc(value, result)
    
    def _update_flags_after_inc(self, operand, result):
        """Update flags after an INC operation (note: CF is not affected by INC)."""
        # Set ZF if result is zero
        self.cpu.set_flag(self.cpu.ZERO_FLAG, result == 0)
        
        # Set SF if the result is negative (bit 15 for 16-bit result)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, (result & 0x8000) != 0)
        
        # Set PF if the number of bits set in the lower byte is even
        parity = 1
        low_byte = result & 0xFF
        for i in range(8):
            parity ^= ((low_byte >> i) & 1)
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity == 0)
        
        # Set AF if there was a carry from bit 3 to bit 4
        self.cpu.set_flag(self.cpu.AUXILIARY_CARRY_FLAG, ((operand ^ 1 ^ result) & 0x10) != 0)
        
        # Set OF if there was an overflow (e.g., 0x7FFF + 1 = 0x8000)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, operand == 0x7FFF)
    
    # CMP instructions implementations
    def _cmp_rm8_r8(self, modrm):
        """Implementation for CMP r/m8, r8 (38)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get the value from the source register
        reg_value = self._get_register_by_index(reg, is_byte=True)
        
        if mod == 3:
            # Register with register
            rm_value = self._get_register_by_index(rm, is_byte=True)
            # Perform the comparison (subtraction without storing result)
            self._update_flags_after_arithmetic(rm_value, reg_value, (rm_value - reg_value) & 0xFF, 8, is_subtraction=True)
        else:
            # Memory with register
            effective_addr = self._get_effective_address(mod, rm)
            memory_value = self.cpu.memory.read_byte(effective_addr)
            # Perform the comparison
            self._update_flags_after_arithmetic(memory_value, reg_value, (memory_value - reg_value) & 0xFF, 8, is_subtraction=True)
    
    def _cmp_rm16_r16(self, modrm):
        """Implementation for CMP r/m16, r16 (39)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get the value from the source register
        reg_value = self._get_register_by_index(reg, is_byte=False)
        
        if mod == 3:
            # Register with register
            rm_value = self._get_register_by_index(rm, is_byte=False)
            # Perform the comparison (subtraction without storing result)
            self._update_flags_after_arithmetic(rm_value, reg_value, (rm_value - reg_value) & 0xFFFF, 16, is_subtraction=True)
        else:
            # Memory with register
            effective_addr = self._get_effective_address(mod, rm)
            memory_value = self.cpu.memory.read_word(effective_addr)
            # Perform the comparison
            self._update_flags_after_arithmetic(memory_value, reg_value, (memory_value - reg_value) & 0xFFFF, 16, is_subtraction=True)
    
    def _cmp_r8_rm8(self, modrm):
        """Implementation for CMP r8, r/m8 (3A)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get the value from the register
        reg_value = self._get_register_by_index(reg, is_byte=True)
        
        if mod == 3:
            # Register with register
            rm_value = self._get_register_by_index(rm, is_byte=True)
            # Perform the comparison (subtraction without storing result)
            self._update_flags_after_arithmetic(reg_value, rm_value, (reg_value - rm_value) & 0xFF, 8, is_subtraction=True)
        else:
            # Register with memory
            effective_addr = self._get_effective_address(mod, rm)
            memory_value = self.cpu.memory.read_byte(effective_addr)
            # Perform the comparison
            self._update_flags_after_arithmetic(reg_value, memory_value, (reg_value - memory_value) & 0xFF, 8, is_subtraction=True)
    
    def _cmp_r16_rm16(self, modrm):
        """Implementation for CMP r16, r/m16 (3B)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get the value from the register
        reg_value = self._get_register_by_index(reg, is_byte=False)
        
        if mod == 3:
            # Register with register
            rm_value = self._get_register_by_index(rm, is_byte=False)
            # Perform the comparison (subtraction without storing result)
            self._update_flags_after_arithmetic(reg_value, rm_value, (reg_value - rm_value) & 0xFFFF, 16, is_subtraction=True)
        else:
            # Register with memory
            effective_addr = self._get_effective_address(mod, rm)
            memory_value = self.cpu.memory.read_word(effective_addr)
            # Perform the comparison
            self._update_flags_after_arithmetic(reg_value, memory_value, (reg_value - memory_value) & 0xFFFF, 16, is_subtraction=True)
    
    def _cmp_al_imm8(self):
        """Implementation for CMP AL, imm8 (3C)"""
        imm8 = self.cpu.fetch_byte()
        al_value = self.cpu.get_register_low_byte(self.cpu.AX)
        # Perform the comparison
        self._update_flags_after_arithmetic(al_value, imm8, (al_value - imm8) & 0xFF, 8, is_subtraction=True)
    
    def _cmp_ax_imm16(self):
        """Implementation for CMP AX, imm16 (3D)"""
        imm16 = self.cpu.fetch_word()
        ax_value = self.cpu.get_register(self.cpu.AX)
        # Perform the comparison
        self._update_flags_after_arithmetic(ax_value, imm16, (ax_value - imm16) & 0xFFFF, 16, is_subtraction=True)
    
    # Loop instructions implementations
    def _loop_rel8(self):
        """LOOP instruction: decrement CX and jump if CX != 0."""
        # Get the displacement
        offset = self.cpu.fetch_byte()
        
        # Sign extend the offset
        if offset & 0x80:
            offset = offset - 256
        
        # Decrement CX
        cx_value = self.cpu.get_register(self.cpu.CX)
        cx_value = (cx_value - 1) & 0xFFFF
        self.cpu.set_register(self.cpu.CX, cx_value)
        
        # Jump if CX != 0
        if cx_value != 0:
            # In the LOOP instruction, the offset is relative to the next instruction
            # after the LOOP instruction. Since we've already fetched the opcode (1 byte)
            # and the offset (1 byte), the IP is already pointing 2 bytes ahead.
            
            # The actual calculation is:
            # new_ip = ip + offset
            # Where ip is the address of the next instruction after the LOOP
            ip = self.cpu.get_register(self.cpu.IP)
            new_ip = (ip + offset) & 0xFFFF
            
            self.cpu.set_register(self.cpu.IP, new_ip)
        
        # Return success
        return True
    
    def _loope_rel8(self):
        """LOOPE/LOOPZ instruction: decrement CX and jump if CX != 0 and ZF=1."""
        # Get the displacement
        offset = self.cpu.fetch_byte()
        
        # Sign extend the offset
        if offset & 0x80:
            offset = offset - 256
        
        # Decrement CX
        cx_value = self.cpu.get_register(self.cpu.CX)
        cx_value = (cx_value - 1) & 0xFFFF
        self.cpu.set_register(self.cpu.CX, cx_value)
        
        # Jump if CX != 0 and ZF=1
        if cx_value != 0 and self.cpu.get_flag(self.cpu.ZERO_FLAG):
            ip = self.cpu.get_register(self.cpu.IP)
            new_ip = (ip + offset) & 0xFFFF
            self.cpu.set_register(self.cpu.IP, new_ip)
        
        # Return success
        return True
    
    def _loopne_rel8(self):
        """LOOPNE/LOOPNZ instruction: decrement CX and jump if CX != 0 and ZF=0."""
        # Get the displacement
        offset = self.cpu.fetch_byte()
        
        # Sign extend the offset
        if offset & 0x80:
            offset = offset - 256
        
        # Decrement CX
        cx_value = self.cpu.get_register(self.cpu.CX)
        cx_value = (cx_value - 1) & 0xFFFF
        self.cpu.set_register(self.cpu.CX, cx_value)
        
        # Jump if CX != 0 and ZF=0
        if cx_value != 0 and not self.cpu.get_flag(self.cpu.ZERO_FLAG):
            ip = self.cpu.get_register(self.cpu.IP)
            new_ip = (ip + offset) & 0xFFFF
            self.cpu.set_register(self.cpu.IP, new_ip)
        
        # Return success
        return True
        
    # ----- LOGICAL INSTRUCTIONS -----
    
    def _and_rm8_r8(self, modrm):
        """Implementation for AND r/m8, r8 (20)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg, is_byte=True)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm, is_byte=True)
            result = rm_val & reg_val
            self._set_register_by_index(rm, result, is_byte=True)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_byte(addr)
            result = rm_val & reg_val
            self.cpu.memory.write_byte(addr, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)  # Always cleared
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)  # Always cleared
        
        if result & 0x80:  # Sign flag - set if result is negative
            self.cpu.set_flag(self.cpu.SIGN_FLAG, 1)
        else:
            self.cpu.set_flag(self.cpu.SIGN_FLAG, 0)
            
        if result == 0:  # Zero flag - set if result is zero
            self.cpu.set_flag(self.cpu.ZERO_FLAG, 1)
        else:
            self.cpu.set_flag(self.cpu.ZERO_FLAG, 0)
            
        # Parity flag - set if the number of 1 bits in the result is even
        parity = 1
        for i in range(8):
            if result & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _and_rm16_r16(self, modrm):
        """Implementation for AND r/m16, r16 (21)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm)
            result = rm_val & reg_val
            self._set_register_by_index(rm, result)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_word(addr)
            result = rm_val & reg_val
            self.cpu.memory.write_word(addr, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)  # Always cleared
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)  # Always cleared
        
        if result & 0x8000:  # Sign flag - set if result is negative
            self.cpu.set_flag(self.cpu.SIGN_FLAG, 1)
        else:
            self.cpu.set_flag(self.cpu.SIGN_FLAG, 0)
            
        if result == 0:  # Zero flag - set if result is zero
            self.cpu.set_flag(self.cpu.ZERO_FLAG, 1)
        else:
            self.cpu.set_flag(self.cpu.ZERO_FLAG, 0)
            
        # Parity flag - set if the number of 1 bits in the least significant byte is even
        parity = 1
        for i in range(8):
            if (result & 0xFF) & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _and_r8_rm8(self, modrm):
        """Implementation for AND r8, r/m8 (22)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get destination register value
        reg_val = self._get_register_by_index(reg, is_byte=True)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm, is_byte=True)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_byte(addr)
        
        # Perform AND operation
        result = reg_val & rm_val
        
        # Store result in register
        self._set_register_by_index(reg, result, is_byte=True)
        
        # Update flags - same as in _and_rm8_r8
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x80 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if result & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _and_r16_rm16(self, modrm):
        """Implementation for AND r16, r/m16 (23)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get destination register value
        reg_val = self._get_register_by_index(reg)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_word(addr)
        
        # Perform AND operation
        result = reg_val & rm_val
        
        # Store result in register
        self._set_register_by_index(reg, result)
        
        # Update flags - same as in _and_rm16_r16
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x8000 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if (result & 0xFF) & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _and_al_imm8(self):
        """Implementation for AND AL, imm8 (24)"""
        imm8 = self.cpu.fetch_byte()
        al = self.cpu.get_register_low_byte(self.cpu.AX)
        
        # Perform AND operation
        result = al & imm8
        
        # Store result in AL
        self.cpu.set_register_low_byte(self.cpu.AX, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x80 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if result & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _and_ax_imm16(self):
        """Implementation for AND AX, imm16 (25)"""
        imm16 = self.cpu.fetch_word()
        ax = self.cpu.get_register(self.cpu.AX)
        
        # Perform AND operation
        result = ax & imm16
        
        # Store result in AX
        self.cpu.set_register(self.cpu.AX, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x8000 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if (result & 0xFF) & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _or_rm8_r8(self, modrm):
        """Implementation for OR r/m8, r8 (08)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg, is_byte=True)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm, is_byte=True)
            result = rm_val | reg_val
            self._set_register_by_index(rm, result, is_byte=True)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_byte(addr)
            result = rm_val | reg_val
            self.cpu.memory.write_byte(addr, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)  # Always cleared
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)  # Always cleared
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x80 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if result & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _or_rm16_r16(self, modrm):
        """Implementation for OR r/m16, r16 (09)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm)
            result = rm_val | reg_val
            self._set_register_by_index(rm, result)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_word(addr)
            result = rm_val | reg_val
            self.cpu.memory.write_word(addr, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x8000 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if (result & 0xFF) & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _or_r8_rm8(self, modrm):
        """Implementation for OR r8, r/m8 (0A)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get destination register value
        reg_val = self._get_register_by_index(reg, is_byte=True)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm, is_byte=True)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_byte(addr)
        
        # Perform OR operation
        result = reg_val | rm_val
        
        # Store result in register
        self._set_register_by_index(reg, result, is_byte=True)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x80 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if result & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _or_r16_rm16(self, modrm):
        """Implementation for OR r16, r/m16 (0B)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get destination register value
        reg_val = self._get_register_by_index(reg)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_word(addr)
        
        # Perform OR operation
        result = reg_val | rm_val
        
        # Store result in register
        self._set_register_by_index(reg, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x8000 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if (result & 0xFF) & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _or_al_imm8(self):
        """Implementation for OR AL, imm8 (0C)"""
        imm8 = self.cpu.fetch_byte()
        al = self.cpu.get_register_low_byte(self.cpu.AX)
        
        # Perform OR operation
        result = al | imm8
        
        # Store result in AL
        self.cpu.set_register_low_byte(self.cpu.AX, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x80 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if result & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _or_ax_imm16(self):
        """Implementation for OR AX, imm16 (0D)"""
        imm16 = self.cpu.fetch_word()
        ax = self.cpu.get_register(self.cpu.AX)
        
        # Perform OR operation
        result = ax | imm16
        
        # Store result in AX
        self.cpu.set_register(self.cpu.AX, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x8000 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if (result & 0xFF) & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _xor_rm8_r8(self, modrm):
        """Implementation for XOR r/m8, r8 (30)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg, is_byte=True)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm, is_byte=True)
            result = rm_val ^ reg_val
            self._set_register_by_index(rm, result, is_byte=True)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_byte(addr)
            result = rm_val ^ reg_val
            self.cpu.memory.write_byte(addr, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)  # Always cleared
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)  # Always cleared
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x80 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if result & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _xor_rm16_r16(self, modrm):
        """Implementation for XOR r/m16, r16 (31)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm)
            result = rm_val ^ reg_val
            self._set_register_by_index(rm, result)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_word(addr)
            result = rm_val ^ reg_val
            self.cpu.memory.write_word(addr, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x8000 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if (result & 0xFF) & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _xor_r8_rm8(self, modrm):
        """Implementation for XOR r8, r/m8 (32)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get destination register value
        reg_val = self._get_register_by_index(reg, is_byte=True)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm, is_byte=True)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_byte(addr)
        
        # Perform XOR operation
        result = reg_val ^ rm_val
        
        # Store result in register
        self._set_register_by_index(reg, result, is_byte=True)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x80 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if result & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _xor_r16_rm16(self, modrm):
        """Implementation for XOR r16, r/m16 (33)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get destination register value
        reg_val = self._get_register_by_index(reg)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_word(addr)
        
        # Perform XOR operation
        result = reg_val ^ rm_val
        
        # Store result in register
        self._set_register_by_index(reg, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x8000 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if (result & 0xFF) & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _xor_al_imm8(self):
        """Implementation for XOR AL, imm8 (34)"""
        imm8 = self.cpu.fetch_byte()
        al = self.cpu.get_register_low_byte(self.cpu.AX)
        
        # Perform XOR operation
        result = al ^ imm8
        
        # Store result in AL
        self.cpu.set_register_low_byte(self.cpu.AX, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x80 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if result & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _xor_ax_imm16(self):
        """Implementation for XOR AX, imm16 (35)"""
        imm16 = self.cpu.fetch_word()
        ax = self.cpu.get_register(self.cpu.AX)
        
        # Perform XOR operation
        result = ax ^ imm16
        
        # Store result in AX
        self.cpu.set_register(self.cpu.AX, result)
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x8000 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if (result & 0xFF) & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _test_rm8_r8(self, modrm):
        """Implementation for TEST r/m8, r8 (84)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg, is_byte=True)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm, is_byte=True)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_byte(addr)
        
        # Perform TEST (AND without storing result)
        result = rm_val & reg_val
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)  # Always cleared
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)  # Always cleared
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x80 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if result & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _test_rm16_r16(self, modrm):
        """Implementation for TEST r/m16, r16 (85)"""
        mod, reg, rm = self._decode_modrm(modrm)
        
        # Get values
        reg_val = self._get_register_by_index(reg)
        
        if mod == 3:  # Register operand
            rm_val = self._get_register_by_index(rm)
        else:  # Memory operand
            addr = self._get_effective_address(mod, rm)
            rm_val = self.cpu.memory.read_word(addr)
        
        # Perform TEST (AND without storing result)
        result = rm_val & reg_val
        
        # Update flags
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x8000 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if (result & 0xFF) & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _test_al_imm8(self):
        """Implementation for TEST AL, imm8 (A8)"""
        imm8 = self.cpu.fetch_byte()
        al = self.cpu.get_register_low_byte(self.cpu.AX)
        
        # Perform TEST operation
        result = al & imm8
        
        # Update flags (don't store result)
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x80 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if result & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    def _test_ax_imm16(self):
        """Implementation for TEST AX, imm16 (A9)"""
        imm16 = self.cpu.fetch_word()
        ax = self.cpu.get_register(self.cpu.AX)
        
        # Perform TEST operation
        result = ax & imm16
        
        # Update flags (don't store result)
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
        self.cpu.set_flag(self.cpu.OVERFLOW_FLAG, 0)
        self.cpu.set_flag(self.cpu.SIGN_FLAG, 1 if result & 0x8000 else 0)
        self.cpu.set_flag(self.cpu.ZERO_FLAG, 1 if result == 0 else 0)
        
        parity = 1
        for i in range(8):
            if (result & 0xFF) & (1 << i):
                parity = parity ^ 1
        self.cpu.set_flag(self.cpu.PARITY_FLAG, parity)
    
    # ----- CONTROL TRANSFER INSTRUCTIONS -----

    def _jmp_rel8(self):
        """Implementation for JMP rel8 (EB)"""
        offset = self.cpu.fetch_byte()
        
        # Sign extend the offset
        if offset & 0x80:
            offset = offset - 256
        
        # Calculate the new instruction pointer
        ip = self.cpu.get_register(self.cpu.IP)
        new_ip = (ip + offset) & 0xFFFF
        
        # Set the new instruction pointer
        self.cpu.set_register(self.cpu.IP, new_ip)
    
    def _jmp_rel16(self):
        """Implementation for JMP rel16 (E9)"""
        offset = self.cpu.fetch_word()
        
        # Sign extend the offset (16-bit to 16-bit, so it's already done)
        if offset & 0x8000:
            offset = offset - 0x10000
        
        # Calculate the new instruction pointer
        ip = self.cpu.get_register(self.cpu.IP)
        new_ip = (ip + offset) & 0xFFFF
        
        # Set the new instruction pointer
        self.cpu.set_register(self.cpu.IP, new_ip)
    
    def _jmp_ptr16_16(self):
        """Implementation for JMP ptr16:16 (EA)"""
        offset = self.cpu.fetch_word()
        segment = self.cpu.fetch_word()
        
        # Set the new CS:IP
        self.cpu.set_register(self.cpu.CS, segment)
        self.cpu.set_register(self.cpu.IP, offset)
    
    def _jcxz_rel8(self):
        """Implementation for JCXZ rel8 (E3)"""
        offset = self.cpu.fetch_byte()
        
        # Sign extend the offset
        if offset & 0x80:
            offset = offset - 256
        
        # Jump if CX == 0
        if self.cpu.get_register(self.cpu.CX) == 0:
            ip = self.cpu.get_register(self.cpu.IP)
            new_ip = (ip + offset) & 0xFFFF
            self.cpu.set_register(self.cpu.IP, new_ip)
    
    def _call_ptr16_16(self):
        """Implementation for CALL ptr16:16 (9A)"""
        offset = self.cpu.fetch_word()
        segment = self.cpu.fetch_word()
        
        # Push current CS
        self.cpu.push(self.cpu.get_register(self.cpu.CS))
        
        # Push current IP
        self.cpu.push(self.cpu.get_register(self.cpu.IP))
        
        # Jump to new CS:IP
        self.cpu.set_register(self.cpu.CS, segment)
        self.cpu.set_register(self.cpu.IP, offset)
    
    def _ret_imm16(self):
        """Implementation for RET imm16 (C2)"""
        imm16 = self.cpu.fetch_word()
        
        # Pop IP
        ip = self.cpu.pop()
        self.cpu.set_register(self.cpu.IP, ip)
        
        # Add immediate to SP (remove parameters)
        sp = self.cpu.get_register(self.cpu.SP)
        self.cpu.set_register(self.cpu.SP, (sp + imm16) & 0xFFFF)
    
    def _ret_far(self):
        """Implementation for RET far (CB)"""
        # Pop IP
        ip = self.cpu.pop()
        self.cpu.set_register(self.cpu.IP, ip)
        
        # Pop CS
        cs = self.cpu.pop()
        self.cpu.set_register(self.cpu.CS, cs)
    
    def _ret_far_imm16(self):
        """Implementation for RET far imm16 (CA)"""
        imm16 = self.cpu.fetch_word()
        
        # Pop IP
        ip = self.cpu.pop()
        self.cpu.set_register(self.cpu.IP, ip)
        
        # Pop CS
        cs = self.cpu.pop()
        self.cpu.set_register(self.cpu.CS, cs)
        
        # Add immediate to SP (remove parameters)
        sp = self.cpu.get_register(self.cpu.SP)
        self.cpu.set_register(self.cpu.SP, (sp + imm16) & 0xFFFF)
    
    def _into(self):
        """Implementation for INTO (CE)"""
        # Check overflow flag
        if self.cpu.get_flag(self.cpu.OVERFLOW_FLAG):
            # Generate interrupt 4
            # Push FLAGS
            self.cpu.push(self.cpu.get_register(self.cpu.FLAGS))
            
            # Push CS
            self.cpu.push(self.cpu.get_register(self.cpu.CS))
            
            # Push IP
            self.cpu.push(self.cpu.get_register(self.cpu.IP))
            
            # Clear IF and TF flags
            self.cpu.set_flag(self.cpu.INTERRUPT_FLAG, 0)
            self.cpu.set_flag(self.cpu.TRAP_FLAG, 0)
            
            # In a real 8086, this would load the interrupt vector
            # For simulation, just log it
            print("INTO called, overflow flag set")
    
    def _iret(self):
        """Implementation for IRET (CF)"""
        # Pop IP
        ip = self.cpu.pop()
        self.cpu.set_register(self.cpu.IP, ip)
        
        # Pop CS
        cs = self.cpu.pop()
        self.cpu.set_register(self.cpu.CS, cs)
        
        # Pop FLAGS
        flags = self.cpu.pop()
        self.cpu.set_register(self.cpu.FLAGS, flags)
    
    # ----- PROCESSOR CONTROL INSTRUCTIONS -----
    
    def _clc(self):
        """CLC - Clear carry flag (F8)"""
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 0)
    
    def _stc(self):
        """STC - Set carry flag (F9)"""
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 1)
    
    def _cmc(self):
        """CMC - Complement carry flag (F5)"""
        current = self.cpu.get_flag(self.cpu.CARRY_FLAG)
        self.cpu.set_flag(self.cpu.CARRY_FLAG, 1 if current == 0 else 0)
    
    def _cld(self):
        """CLD - Clear direction flag (FC)"""
        self.cpu.set_flag(self.cpu.DIRECTION_FLAG, 0)
    
    def _std(self):
        """STD - Set direction flag (FD)"""
        self.cpu.set_flag(self.cpu.DIRECTION_FLAG, 1)
    
    def _cli(self):
        """CLI - Clear interrupt flag (FA)"""
        self.cpu.set_flag(self.cpu.INTERRUPT_FLAG, 0)
    
    def _sti(self):
        """STI - Set interrupt flag (FB)"""
        self.cpu.set_flag(self.cpu.INTERRUPT_FLAG, 1)
    
    def _nop(self):
        """NOP - No operation (90)"""
        pass  # Do nothing
    
    def _hlt(self):
        """HLT - Halt the processor (F4)"""
        self.cpu.halted = True
        print("CPU halted.")
    
    def _wait(self):
        """WAIT - Wait for coprocessor (9B)"""
        # In a real 8086, this would wait for a signal from the coprocessor
        # For simulation, just a NOP
        pass
    
    def _lock_prefix(self):
        """LOCK - Lock the bus for the next instruction (F0)"""
        # In a real 8086, this would assert the LOCK signal during the next instruction
        # For simulation, just fetch and execute the next instruction normally
        opcode = self.cpu.fetch_byte()
        instruction_info = self.instruction_map.get(opcode)
        if instruction_info:
            name, handler = instruction_info
            print(f"Executing with LOCK prefix: {name}")
            handler()
        else:
            raise ValueError(f"Unknown opcode: {opcode:02X}")
