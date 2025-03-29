
    ; Simple LOOP Test Program
    
    .model small
    .stack 100h
    .code
    
    start:
        ; Initialize registers with test values
        MOV CX, 5        ; Set counter to 5
        MOV AX, 0        ; Initialize accumulator
        
    loop_start:
        INC AX           ; Increment AX
        LOOP loop_start  ; Decrement CX and loop while CX > 0
        
        ; AX should be 5 at the end
        HLT              ; Stop the CPU
    
    end start
    