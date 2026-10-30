0000000000000e28 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl>:
     e28:	mov	x8, xzr
     e2c:	cbz	x1, e58 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x30>
     e30:	ldp	x9, x10, [x0]
     e34:	sub	x11, x1, #0x1
     e38:	sub	x10, x10, x9
     e3c:	asr	x10, x10, #2
     e40:	cmp	x10, x11
     e44:	b.ls	e60 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x38>  // b.plast
     e48:	ldrsw	x12, [x9], #4
     e4c:	subs	x1, x1, #0x1
     e50:	add	x8, x8, x12
     e54:	b.ne	e40 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x18>  // b.any
     e58:	str	x8, [x2]
     e5c:	ret
     e60:	brk	#0x1
