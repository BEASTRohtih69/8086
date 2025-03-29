; Testing the LOOP instruction (opcode 0xE2)
; LOOP automatically decrements CX and jumps if CX is not zero

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
    
    ; LOOP instruction automatically decrements CX and jumps if CX != 0
    LOOP loop_start
    
    ; At this point, AX should be 5 (sum of iterations)
    ; and CX should be 0 (loop counter at end)
    
    ; Halt the CPU
    HLT

end start