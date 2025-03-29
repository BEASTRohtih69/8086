.MODEL SMALL

.DATA
message DB 'Hello, World!', 0

.CODE
start:
    ; Set up data segment
    MOV AX, @DATA
    MOV DS, AX
    
    ; Load pointer to message
    MOV SI, OFFSET message
    
    ; Do some arithmetic
    MOV AX, 1234h
    MOV BX, 5678h
    ADD AX, BX
    
    ; Done
    HLT

END start