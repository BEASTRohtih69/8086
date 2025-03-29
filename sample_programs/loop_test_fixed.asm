; Loop Test Program
; This program tests the LOOP instruction and various loop patterns

; Initialize registers
MOV CX, 5       ; Set loop counter to 5
MOV AX, 0       ; Initialize accumulator to 0

loop_start:
    INC AX      ; Increment accumulator
    LOOP loop_start  ; Decrement CX and jump back if CX != 0
    
; At this point, AX should be 5 and CX should be 0

; Test LOOPE (Loop while Equal)
MOV CX, 5       ; Reset loop counter
MOV BX, 0       ; Initialize BX to 0
MOV AX, 1       ; Set AX to 1 to trigger comparison

loope_start:
    INC BX          ; Increment BX
    CMP BX, 3       ; Compare BX with 3
    LOOPE loope_start  ; Loop while equal (ZF=1) and CX != 0
    
; Test LOOPNE (Loop while Not Equal)
MOV CX, 5       ; Reset loop counter
MOV DX, 0       ; Initialize DX to 0

loopne_start:
    INC DX          ; Increment DX
    CMP DX, 3       ; Compare DX with 3
    LOOPNE loopne_start  ; Loop while not equal (ZF=0) and CX != 0

; Program end
HLT