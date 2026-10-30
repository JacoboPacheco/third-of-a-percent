0000000000000e40 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl>:
     e40:	mov	x8, xzr
     e44:	cbz	x1, e98 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x58>
     e48:	ldp	x9, x10, [x0]
     e4c:	sub	x11, x1, #0x1
     e50:	sub	x10, x10, x9
     e54:	asr	x10, x10, #2
     e58:	nop
     e5c:	nop
     e60:	nop
     e64:	nop
     e68:	nop
     e6c:	nop
     e70:	nop
     e74:	nop
     e78:	nop
     e7c:	nop
     e80:	cmp	x10, x11
     e84:	b.ls	ea0 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x60>  // b.plast
     e88:	ldrsw	x12, [x9], #4
     e8c:	subs	x1, x1, #0x1
     e90:	add	x8, x8, x12
     e94:	b.ne	e80 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x40>  // b.any
     e98:	str	x8, [x2]
     e9c:	ret
     ea0:	brk	#0x1
