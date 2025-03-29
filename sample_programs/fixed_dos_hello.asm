.MODEL SMALL
.STACK 64

.DATA
greeting DB 'Hello from 8086 simulator!$'

.CODE
start:
    ; Set up data segment
    MOV AX, @DATA
    MOV DS, AX
    
    ; Load message address
    MOV AX, OFFSET greeting
    MOV DX, AX
    
    ; Print string using DOS function 9
    MOV AH, 9
    ; INT 21h  (we don't have full interrupt support yet)
    
    ; Exit program
    MOV AX, 0x4C00
    ; INT 21h  (we don't have full interrupt support yet)
    
    ; Halt for simulator
    HLT

END start