; Loop example for 8086 simulator
; This program demonstrates decrementing and looping

.CODE
    ; Initialize counter
    MOV CX, 5        ; Start with counter = 5
    MOV AX, 0        ; Initialize accumulator to 0
    
start_loop:
    ADD AX, CX       ; Add current counter value to accumulator
    
    DEC CX           ; Decrement counter
    JNZ start_loop   ; Jump if not zero (loop until CX = 0)
    
    ; At this point, AX should contain the sum: 5 + 4 + 3 + 2 + 1 = 15
    
    ; Store result in BX for verification
    MOV BX, AX
    
    HLT              ; Halt the processor