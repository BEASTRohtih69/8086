; Simple test program for 8086 simulator
.MODEL SMALL

.DATA
message DB 'Test Message'    ; Simple ASCII string

.CODE
start:
    ; Basic MOV operations
    MOV AX, 1234h            ; MOV register, immediate
    MOV BX, AX               ; MOV register, register
    
    ; Test only ADD operation
    ADD AX, 4321h            ; ADD register, immediate
    
    HLT                      ; Halt the CPU

.STACK 100h

; Entry point must be capitalized for the assembler to match it
END START