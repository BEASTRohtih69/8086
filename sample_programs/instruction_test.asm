.MODEL SMALL
.STACK 100h
.DATA
    test_byte DB 42
    test_word DW 1234h
    string_source DB "Hello, World!", 0
    string_dest DB 20 DUP(0)
.CODE
START:
    ; Test MOV instructions
    MOV AX, 1234h
    MOV BX, 5678h
    MOV CX, 9ABCh
    MOV DX, DEF0h
    
    ; Test stack operations
    PUSH AX
    PUSH BX
    POP CX        ; CX should now be 5678h
    POP DX        ; DX should now be 1234h
    
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
    
    ; Test string operations
    MOV AX, @data
    MOV DS, AX
    MOV ES, AX
    
    MOV SI, OFFSET string_source
    MOV DI, OFFSET string_dest
    MOV CX, 13     ; Length of "Hello, World!" + null terminator
    CLD            ; Clear direction flag (forward)
    REP MOVSB      ; Move bytes from source to destination
    
    MOV SI, OFFSET string_source
    MOV DI, OFFSET string_dest
    MOV CX, 13
    REPE CMPSB     ; Compare strings and set ZF=1 if equal
    
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