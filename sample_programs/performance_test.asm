; Ultra-simple performance test program for 8086 simulator
; This is just a sequence of MOV and ADD instructions

; Code segment
.CODE
    ; Initialize registers
    MOV AX, 1
    MOV BX, 2
    MOV CX, 3
    MOV DX, 4
    
    ; Do a sequence of operations
    ADD AX, BX       ; AX = 3
    ADD CX, DX       ; CX = 7
    ADD AX, CX       ; AX = 10
    
    MOV BX, 5
    MOV CX, 6
    ADD BX, CX       ; BX = 11
    ADD AX, BX       ; AX = 21
    
    MOV CX, 7
    MOV DX, 8
    ADD CX, DX       ; CX = 15
    ADD AX, CX       ; AX = 36
    
    MOV BX, 9
    MOV CX, 10
    ADD BX, CX       ; BX = 19
    ADD AX, BX       ; AX = 55
    
    ; Exit
    HLT