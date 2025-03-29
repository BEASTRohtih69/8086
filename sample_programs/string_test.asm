; String instructions test program
; Tests MOVSB, STOSB, CMPSB, LODSB, SCASB, and REP prefix

.MODEL SMALL
.STACK 100h

.DATA
    source_str DB 'Hello, World!', 0    ; Source string
    dest_str   DB 20 DUP(?)             ; Destination buffer
    search_str DB 'Hello'                ; String to compare against
    search_char DB 'o'                  ; Character to search for
    message_success DB 'Test passed!', 0Dh, 0Ah, '$'
    message_fail DB 'Test failed!', 0Dh, 0Ah, '$'

.CODE
    main PROC
        ; Set up segment registers
        MOV AX, @DATA
        MOV DS, AX
        MOV ES, AX
        
        ; Test 1: Copy string using MOVSB with REP prefix
        MOV CX, 14                      ; Length of source string
        MOV SI, OFFSET source_str       ; Source pointer
        MOV DI, OFFSET dest_str         ; Destination pointer
        CLD                             ; Clear direction flag (forward)
        REP MOVSB                       ; Copy bytes
        
        ; Test 2: Search for character using SCASB
        MOV AL, search_char             ; Character to search for
        MOV DI, OFFSET dest_str         ; Start of destination string
        MOV CX, 14                      ; Length to search
        CLD                             ; Clear direction flag
        
        ; Search loop
        search_loop:
            SCASB                       ; Compare AL with ES:[DI], increment DI
            JE found_char               ; Jump if character found
            LOOP search_loop            ; Decrement CX and loop if not zero
            JMP char_not_found
            
        found_char:
            ; Success path
            MOV AH, 9
            MOV DX, OFFSET message_success
            INT 21h
            JMP end_program
            
        char_not_found:
            ; Failure path
            MOV AH, 9
            MOV DX, OFFSET message_fail
            INT 21h
            
        end_program:
            ; Exit program
            MOV AX, 4C00h
            INT 21h
    main ENDP

END main