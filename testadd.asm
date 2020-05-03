	global	_testadd
	
	section .text
_testadd:
	mov	eax, [esp+4]
	add	eax, [esp+8]
	ret
	
;nasm -fwin32 add.asm
;use dumpbin to view raw data, don't use ndisasm (for now)
