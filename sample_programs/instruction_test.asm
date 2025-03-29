; 8086 Instruction Set Test Program
; This program tests a variety of 8086 instructions

.model small
.stack 100h
.code

start:
    ; Initialize registers with test values
    MOV AX, 1234h    ; Test MOV immediate to register
    MOV BX, 5678h
    MOV CX, 10       ; Loop counter
    MOV DX, 0
    
    ; Test stack operations
    PUSH AX          ; Test PUSH
    PUSH BX
    POP CX           ; Test POP (CX should now be 5678h)
    POP DX           ; Test POP (DX should now be 1234h)
    
    ; Test arithmetic operations
    MOV AX, 5        ; Test basic addition
    ADD AX, 10       ; AX = 15
    
    MOV BX, 20
    SUB BX, 5        ; BX = 15, test subtraction
    
    ; Test flag-setting operations
    CMP AX, BX       ; Compare AX and BX (should be equal, setting ZF=1)
    
    ; Test conditional jumps
    JE equal         ; Jump if equal (ZF=1)
    ADD DX, 1        ; This should be skipped
    
equal:
    ADD DX, 2        ; DX = 1234h + 2 = 1236h
    
    ; Test LOOP instruction
    MOV CX, 5        ; Initialize loop counter
    MOV SI, 0        ; Initialize sum
    
loop_start:
    ADD SI, CX       ; Add current CX value to SI
    LOOP loop_start  ; Decrement CX and loop if not zero
    
    ; At the end, SI should be 5+4+3+2+1 = 15
    
    ; Test DEC and JNZ for backwards compatibility
    MOV CX, 3        ; Another loop counter
    MOV DI, 0        ; Another accumulator
    
dec_loop:
    ADD DI, 2        ; Add 2 to DI each time
    DEC CX           ; Decrement CX
    JNZ dec_loop     ; Jump if not zero
    
    ; At the end, DI should be 6 (2*3)
    
    ; Move results to more visible registers
    MOV AX, SI       ; AX = 15 (LOOP result)
    MOV BX, DI       ; BX = 6 (DEC+JNZ result)
    
    ; Test interrupts (if we had INT 21h implementation)
    ; INT 21h
    
    ; Halt the CPU
    HLT

end start