; Simple hello world program for 8086 Simulator

.MODEL SMALL
.STACK 100h
.DATA
    message DB 'Hello, World!$'

.CODE
main PROC
    ; Initialize data segment
    MOV AX, @DATA
    MOV DS, AX
    
    ; Display the message
    MOV AH, 09h      ; DOS function: output string
    MOV DX, OFFSET message
    INT 21h          ; Call DOS
    
    ; Exit program
    MOV AX, 4C00h    ; DOS function: terminate with return code
    INT 21h          ; Call DOS
main ENDP
END main
