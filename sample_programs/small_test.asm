; Small test program for newly implemented instructions
; Tests: CBW, LAHF, SAHF
; These are the most essential of the new instructions

org 100h  ; Standard COM file format

start:
    ; Test CBW - Convert Byte to Word
    mov al, 0x80     ; AL = -128 (signed)
    cbw             ; AX should become 0xFF80
    
    ; Test LAHF/SAHF - Load/Store AH from/to Flags
    mov ax, 0       ; Clear AX
    add al, 255     ; Set some flags (ZF=1, CF=0, etc.)
    lahf            ; Load flags into AH
    
    ; End program
    mov ah, 0x4C    ; DOS function: Exit program
    mov al, 0       ; Return code
    int 21h         ; Call DOS