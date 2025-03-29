; Simple loop test using DEC CX and JNZ
; This program sets CX to 5 and then decrements it in a loop until it's zero

.model small
.stack 100h
.code
start:
    ; Initialize CX to 5 (number of iterations)
    MOV CX, 5
    
    ; Initialize AX to 0 (counter/result)
    MOV AX, 0
    
loop_start:
    ; Increment AX by 1 in each iteration
    ADD AX, 1
    
    ; Decrement CX (loop counter)
    DEC CX
    
    ; Jump to loop_start if CX is not zero (JNZ is alias for JNE)
    JNZ loop_start
    
    ; At this point, AX should be 5 (sum of iterations)
    ; and CX should be 0 (loop counter at end)
    
    ; Halt the CPU
    HLT

end start