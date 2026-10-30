0000000000000e28 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl>:
     e28:	ldp	x8, x9, [x0]
     e2c:	subs	x10, x9, x8
     e30:	b.eq	e5c <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x34>  // b.none
     e34:	asr	x10, x10, #2
     e38:	mov	x9, xzr
     e3c:	cmp	x10, #0x1
     e40:	csinc	x10, x10, xzr, hi	// hi = pmore
     e44:	ldrsw	x11, [x8], #4
     e48:	subs	x10, x10, #0x1
     e4c:	add	x9, x9, x11
     e50:	b.ne	e44 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x1c>  // b.any
     e54:	str	x9, [x1]
     e58:	ret
     e5c:	mov	x9, xzr
     e60:	str	x9, [x1]
     e64:	ret
