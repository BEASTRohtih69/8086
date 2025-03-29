; Simple calculator program for 8086 simulator
; Iteratively adds numbers in a loop

.CODE
    ; Initialize
    MOV CX, 5     ; Loop counter
    MOV AX, 0     ; Initialize result to 0
    MOV BX, 10    ; Value to add each time
    
loop_start:
    ; Add BX to AX
    ADD AX, BX
    
    ; Decrement counter
    SUB CX, 1
    
    ; Continue if CX > 0
    SUB CX, 0     ; Set flags based on CX value
    JNZ loop_start
    
    ; Result is in AX (should be 50)
    HLT