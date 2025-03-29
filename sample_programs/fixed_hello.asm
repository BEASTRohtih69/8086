.MODEL SMALL

.DATA
msg DB 'Hello, World!'

.CODE
start:
    MOV AX, 0x1234
    HLT

END start