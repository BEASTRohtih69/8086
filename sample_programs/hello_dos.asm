; Hello World program for 8086 simulator
; This program prints "Hello, World!" to the console using DOS interrupt 21h

; DATA SECTION
; Define the message with $ terminator (for DOS function 9h)
message DB 'Hello, World!$'

; CODE SECTION
; Start of the program
MOV AX, 0        ; Load segment 0 into AX
MOV DS, AX       ; Set DS to 0

; Load message address into DX
MOV DX, message  ; Offset of the message

; Call DOS function to print the string
MOV AH, 09h      ; DOS function 9: Print string
INT 21h          ; Call DOS interrupt

; Exit the program
MOV AX, 4C00h    ; DOS function 4Ch: Exit with return code 0
INT 21h          ; Call DOS interrupt

; END
HLT              ; Halt the processor (in case the DOS exit doesn't work)