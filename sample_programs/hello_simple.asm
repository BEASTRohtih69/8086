; Simplified Hello World program for 8086 simulator
; Uses more basic instructions compatible with our current implementation

MOV AX, 0x1234  ; Load a test value into AX
MOV BX, 0x5678  ; Load a test value into BX
ADD AX, BX      ; Perform addition
HLT             ; Halt the processor