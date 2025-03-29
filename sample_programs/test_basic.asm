.MODEL SMALL

.DATA
message DB 'Hello, World!'
null_term DB 0
count DB 5

.CODE
start:
    ; Set up data segment
    MOV AX, 0x0200  ; Our data segment is at 0x0200 
    MOV DS, AX
    
    ; Simple math
    MOV AX, 0x1234
    MOV BX, 0x5678
    ADD AX, BX
    
    ; Halt the CPU
    HLT

.STACK 64
; End of program
END start