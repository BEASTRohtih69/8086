; Simple test for string instructions

org 100h

section .data
    source_str db 'Hello, World!', 0    ; Source string
    dest_str   db 20 dup(0)             ; Destination buffer

section .code
    ; Set up segment registers
    mov ax, ds
    mov es, ax
    
    ; Test 1: Copy string using MOVSB with REP prefix
    mov cx, 14                      ; Length of source string
    mov si, source_str              ; Source pointer
    mov di, dest_str                ; Destination pointer
    cld                             ; Clear direction flag (forward)
    
    ; Test each string instruction
    movsb                           ; Move 1 byte
    
    mov al, 'X'                     ; Character to store
    stosb                           ; Store AL to [ES:DI]
    
    mov si, source_str              ; Reset SI to beginning of source
    lodsb                           ; Load byte from [DS:SI] to AL
    
    ; Test successful if we reach here
    mov dx, dest_str                ; Point to the result
    mov ah, 9                       ; DOS print string function
    int 21h                         ; Call DOS
    
    ; Exit program
    mov ax, 4C00h
    int 21h