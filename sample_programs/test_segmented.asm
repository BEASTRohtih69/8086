.MODEL SMALL

.DATA
message DB 'Hello, World!'
null_term DB 0
count DB 5

.CODE
start:
    ; Set up data segment
    MOV AX, @DATA
    MOV DS, AX
    
    ; Load a value from the data segment
    MOV CL, [count]
    
    ; Do some calculations
    MOV AX, 0x1234
    MOV BX, 0x5678
    ADD AX, BX

loop_start:
    ; Loop using the count (we don't have DEC yet, so use SUB)
    SUB CL, 1
    JNZ loop_start
    
    ; Halt the CPU
    HLT

.STACK 64
; End of program
END start