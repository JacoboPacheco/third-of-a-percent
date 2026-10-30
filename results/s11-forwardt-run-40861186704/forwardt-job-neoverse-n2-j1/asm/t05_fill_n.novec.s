0000000000000b28 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi>:
 b28:	cmp	w1, #0x1
 b2c:	b.lt	b50 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x28>  // b.tstop
 b30:	mov	w9, w1
 b34:	ldr	x8, [x0]
 b38:	mov	x10, xzr
 b3c:	add	x9, x9, w1, uxtw #1
 b40:	str	w10, [x8], #4
 b44:	add	x10, x10, #0x3
 b48:	cmp	x9, x10
 b4c:	b.ne	b40 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x18>  // b.any
 b50:	ret
