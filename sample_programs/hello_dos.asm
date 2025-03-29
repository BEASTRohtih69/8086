; Hello World program for 8086 simulator
; This program prints "Hello, World!" to the console using DOS interrupt 21h

.MODEL SMALL     ; Use small memory model
.STACK 100h      ; Define stack segment

.DATA
message DB 'Hello, World!$'  ; Message with $ terminator for DOS function 9

.CODE
main PROC
    ; Set up data segment
    MOV AX, @DATA   ; Get data segment address
    MOV DS, AX      ; Set DS register
    
    ; Print message using DOS function
    MOV DX, OFFSET message  ; Load message address
    MOV AH, 09h             ; DOS function 9: Print string
    INT 21h                 ; Call DOS interrupt
    
    ; Exit program
    MOV AX, 4C00h    ; DOS function 4Ch: Exit with return code 0
    INT 21h          ; Call DOS interrupt
    
    HLT              ; Halt processor (in case INT 21h doesn't work)
main ENDP
END main             ; End of program with entry point