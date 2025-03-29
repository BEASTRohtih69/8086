; Basic String Instructions Test
; Tests simple string operations without complex syntax

.model small
.stack 100h
.data
    source_str DB 'Hello World', 0   ; Test source string
    dest_str   DB 20 DUP(0)          ; Destination buffer

.code
start:
    ; Set up the segment registers
    MOV AX, @data
    MOV DS, AX
    MOV ES, AX
    
    ; Load source and destination addresses
    MOV SI, OFFSET source_str  ; Source index 
    MOV DI, OFFSET dest_str    ; Destination index
    
    ; Test MOVSB - Move String Byte
    CLD                        ; Clear direction flag (forward)
    MOVSB                      ; Move one byte ('H')
    
    ; Test STOSB - Store String Byte
    MOV AL, '!'                ; Character to store
    STOSB                      ; Store AL at ES:DI ('!')
    
    ; Test LODSB - Load String Byte
    LODSB                      ; Load 'e' into AL
    STOSB                      ; Store 'e' at next position
    
    ; Test a few more string operations
    MOVSB                      ; Move another byte ('l')
    MOVSB                      ; Move another byte ('l')
    
    ; Final state: dest_str should contain "H!el"
    
    HLT                        ; Halt execution

end start