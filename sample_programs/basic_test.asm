.MODEL SMALL
.DATA
    test_byte DB 42
.CODE
START:
    ; Test MOV instructions
    MOV AX, 1234h
    MOV BX, 5678h
    MOV CX, 9ABCh
    MOV DX, DEF0h
    
    ; Test arithmetic operations
    MOV AX, 5      
    MOV BX, 3
    ADD AX, BX     ; AX = 8
    MOV CX, 10
    SUB CX, BX     ; CX = 7
    INC AX         ; AX = 9
    DEC BX         ; BX = 2
    
    ; Test logical operations
    MOV AX, 0F0Fh  
    MOV BX, 0FF00h
    AND AX, BX     ; AX = 0F00h
    MOV CX, 0F0F0h
    OR CX, BX      ; CX = 0FFF0h
    XOR BX, BX     ; BX = 0
    
    ; Test flag manipulation
    CLC            ; Clear carry flag
    STC            ; Set carry flag
    CLD            ; Clear direction flag
    STD            ; Set direction flag
    
    ; Test conditional jumps
    MOV AX, 5
    MOV BX, 5
    CMP AX, BX
    JE equal_jump  ; This should jump
    MOV CX, 1      ; Should be skipped
    JMP end_jumps
    
equal_jump:
    MOV CX, 2      ; This should execute
    
end_jumps:
    ; Test loop
    MOV CX, 5      ; Counter
    MOV AX, 0      ; Initialize sum
    
loop_start:
    ADD AX, CX     ; Add counter to sum
    LOOP loop_start ; Decrement CX and loop if not zero
    
    ; AX should be 15 (5+4+3+2+1)
    
    HLT
END START