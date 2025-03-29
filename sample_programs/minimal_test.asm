; Minimal test for basic 8086 instructions
; Tests the most basic instructions only

.model small
.stack 100h
.data
    test_byte DB 42           ; Test data byte
    test_word DW 1234         ; Test data word

.code
start:
    ; Simple MOV instructions only
    MOV AX, 100
    MOV BX, 200
    MOV CX, 300
    
    ; Simple flag operations
    CLC                       ; Clear carry flag
    STC                       ; Set carry flag
    
    ; End program
    HLT                       ; Halt execution

end start