; Simple addition program for 8086 simulator
; Adds a series of numbers without loops

.CODE
    ; Initialize registers
    MOV AX, 10    ; First number
    MOV BX, 20    ; Second number
    MOV CX, 30    ; Third number
    MOV DX, 40    ; Fourth number
    
    ; Add them together
    ADD AX, BX    ; AX = 30
    ADD AX, CX    ; AX = 60
    ADD AX, DX    ; AX = 100
    
    ; Result is in AX (should be 100)
    HLT