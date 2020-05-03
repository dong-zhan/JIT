	global	_testadd
	
	section .text
_testadd:
	sub   RSP, 8                                   ; Align the stack to a multiple of 16 bytes
 
	mov	rax, RCX
	add	rax, RDX
	
	add RSP, 8

	ret
	
;nasm -fwin64 add64.asm
;use dumpbin to view raw data, don't use ndisasm (for now)
