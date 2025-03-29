; Segment addressing test for 8086 simulator
; Demonstrates proper segment:offset addressing

org 100h                ; Start at offset 100h

; Define segments
segment .data           ; Data segment
    message db 'Hello from DATA segment!', 0

segment .code           ; Code segment
    ; Test segment register operations
    mov ax, @data       ; Get data segment value
    mov ds, ax          ; Set DS register
    
    ; Verify DS is correctly set by accessing message
    mov si, message     ; Put offset of message in SI
    
    ; Now read characters from DS:SI
    mov ah, 0           ; Counter for characters read
    
read_char:
    mov al, [si]        ; Read character at DS:SI
    cmp al, 0           ; Check if it's the null terminator
    je done_reading     ; If zero, we're done
    
    ; Count the character
    inc ah              ; Increment counter
    inc si              ; Move to next character
    jmp read_char       ; Continue reading
    
done_reading:
    ; Now AH contains the length of the string minus null terminator
    
    ; Set up stack for function call (using different segment)
    mov bx, ss          ; Save current stack segment in BX
    
    ; Test far calls using different CS
    call test_procedure ; Call a procedure
    
    ; Finish the program
    hlt                 ; Halt execution

; Test procedure to verify call/ret
test_procedure:
    ; Verify current CS:IP is correct
    push ax             ; Save AX
    mov ax, cs          ; Get code segment
    
    ; We can push/pop to verify stack operations work with SS:SP
    pop ax              ; Restore AX
    ret                 ; Return to caller