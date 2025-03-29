.MODEL SMALL
.STACK 100h

.DATA
msg1 DB 'First message', 0
msg2 DB 'Second message', 0
count DB 5
buffer DB 20 DUP(0)

.CODE
start:
    ; Set up data segment
    MOV AX, @DATA
    MOV DS, AX
    
    ; Access variables by offset
    MOV SI, OFFSET msg1
    MOV BX, OFFSET msg2
    MOV CL, count
    MOV DI, OFFSET buffer
    
    ; Do some arithmetic
    MOV AX, 1234h
    MOV BX, 5678h
    ADD AX, BX
    
    ; Push and pop values
    PUSH AX
    PUSH BX
    POP CX
    POP DX
    
    ; Done
    HLT

END start