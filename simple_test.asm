; Simple test program for 8086 simulator
; This program performs basic register operations and arithmetic

org 100h        ; Set origin at 0x100 for COM file format

section .code
    ; Test register MOV operations
    mov ax, 1234h       ; Set AX to 1234h
    mov bx, 5678h       ; Set BX to 5678h
    mov cx, ax          ; Copy AX to CX (CX = 1234h)
    
    ; Test arithmetic operations
    add ax, bx          ; AX = AX + BX (AX = 68ACh)
    sub cx, 34h         ; CX = CX - 34h (CX = 1200h)
    
    ; Test 8-bit register operations
    mov al, 55h         ; Set AL to 55h (AX = 68ACh -> 6855h)
    mov bl, 0AAh        ; Set BL to AAh (BX = 5678h -> 56AAh)
    add al, bl          ; AL = AL + BL (AL = 55h + AAh = FFh with carry)
    
    ; Test stack operations
    push ax             ; Push AX onto stack
    push bx             ; Push BX onto stack
    pop cx              ; Pop into CX (CX = 56AAh)
    pop dx              ; Pop into DX (DX = 68FFh)
    
    ; Halt the processor
    hlt                 ; Stop execution