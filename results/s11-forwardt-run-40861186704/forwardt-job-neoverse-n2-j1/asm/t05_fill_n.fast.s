0000000000000b28 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi>:
 b28:	cmp	w1, #0x1
 b2c:	b.lt	bd0 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0xa8>  // b.tstop
 b30:	ldp	x9, x8, [x0]
 b34:	sub	x8, x8, x9
 b38:	asr	x10, x8, #2
 b3c:	mov	w8, w1
 b40:	sub	x11, x8, #0x1
 b44:	cmp	x10, x11
 b48:	csel	x11, x10, x11, cc	// cc = lo, ul, last
 b4c:	add	x11, x11, #0x1
 b50:	cmp	x11, #0x8
 b54:	b.hi	b60 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x38>  // b.pmore
 b58:	mov	x11, xzr
 b5c:	b	ba8 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x80>
 b60:	ands	x12, x11, #0x7
 b64:	mov	w13, #0x8                   	// #8
 b68:	movi	v0.4s, #0x3
 b6c:	movi	v1.4s, #0xc
 b70:	movi	v2.4s, #0x8
 b74:	csel	x12, x13, x12, eq	// eq = none
 b78:	adrp	x13, 0 <__abi_tag-0x278>
 b7c:	sub	x11, x11, x12
 b80:	add	x12, x9, #0x10
 b84:	ldr	q3, [x13, #3568]
 b88:	mov	x13, x11
 b8c:	mul	v4.4s, v3.4s, v0.4s
 b90:	add	v3.4s, v3.4s, v2.4s
 b94:	subs	x13, x13, #0x8
 b98:	add	v5.4s, v4.4s, v1.4s
 b9c:	stp	q4, q5, [x12, #-16]
 ba0:	add	x12, x12, #0x20
 ba4:	b.ne	b8c <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x64>  // b.any
 ba8:	add	w12, w11, w11, lsl #1
 bac:	add	x9, x9, x11, lsl #2
 bb0:	sub	x10, x10, x11
 bb4:	sub	x8, x8, x11
 bb8:	cbz	x10, bd4 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0xac>
 bbc:	str	w12, [x9], #4
 bc0:	subs	x8, x8, #0x1
 bc4:	add	w12, w12, #0x3
 bc8:	sub	x10, x10, #0x1
 bcc:	b.ne	bb8 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x90>  // b.any
 bd0:	ret
 bd4:	brk	#0x1
