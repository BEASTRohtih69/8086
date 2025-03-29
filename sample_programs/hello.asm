; Hello World program for 8086 simulator
; This program prints "Hello, World!" to the console using DOS interrupt 21h

.MODEL SMALL     ; Small memory model
.STACK 100h      ; 256 bytes for stack

.DATA
message DB 'Hello, World!$'    ; Define message with $ terminator for DOS function 9h

.CODE
main PROC
    ; Initialize DS register to point to our data segment
    MOV AX, @DATA       ; Load the data segment address to AX
    MOV DS, AX          ; Move the data segment address to DS

    ; Print the message 
    MOV AH, 09h         ; DOS function 9: Print string
    MOV DX, OFFSET message ; Point DX to our message
    INT 21h             ; Call DOS interrupt

    ; Exit the program
    MOV AX, 4C00h       ; DOS function 4Ch: Exit with return code 0
    INT 21h             ; Call DOS interrupt
main ENDP

END main