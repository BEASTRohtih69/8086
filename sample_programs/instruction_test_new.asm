; Test program for newly implemented instructions
; Tests: 
; - CBW, CWD (Conversion) 
; - LAHF, SAHF (Flag register operations)
; - MUL, DIV (Multiplication and division)
; - ROL, ROR (Rotate operations)

org 100h  ; Standard COM file format

start:
    ; Test CBW - Convert Byte to Word
    mov al, 0x80     ; AL = -128 (signed)
    cbw             ; AX should become 0xFF80
    
    ; Test CWD - Convert Word to Doubleword
    mov ax, 0x8000  ; AX = -32768 (signed)
    cwd             ; DX:AX should become 0xFFFF:0x8000
    
    ; Test LAHF/SAHF - Load/Store AH from/to Flags
    mov ax, 0       ; Clear AX
    add al, 255     ; Set some flags (ZF=1, CF=0, etc.)
    lahf            ; Load flags into AH
    mov bx, ax      ; Save AX to BX
    
    add ax, 1       ; Change some flags
    mov ax, bx      ; Restore AX
    sahf            ; Restore flags from AH
    
    ; Test MUL - Unsigned multiplication
    mov al, 5       ; AL = 5
    mov bl, 10      ; BL = 10
    mul bl          ; AX = AL * BL = 5 * 10 = 50 (0x32)
    
    ; Test DIV - Unsigned division
    mov ax, 100     ; AX = 100
    mov bl, 3       ; BL = 3
    div bl          ; AL = AX / BL = 33, AH = AX % BL = 1
    
    ; Test ROL - Rotate Left
    mov al, 0x81    ; AL = 10000001b
    rol al, 1       ; AL should become 00000011b = 0x03, CF=1
    
    ; Test ROR - Rotate Right
    mov al, 0x81    ; AL = 10000001b
    ror al, 1       ; AL should become 11000000b = 0xC0, CF=1
    
    ; End program
    mov ah, 0x4C    ; DOS function: Exit program
    mov al, 0       ; Return code
    int 21h         ; Call DOS