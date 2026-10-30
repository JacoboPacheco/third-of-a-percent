0000000000000b40 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi>:
 b40:	cmp	w1, #0x1
 b44:	b.lt	c18 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0xd8>  // b.tstop
 b48:	ldp	x9, x8, [x0]
 b4c:	sub	x8, x8, x9
 b50:	asr	x10, x8, #2
 b54:	mov	w8, w1
 b58:	sub	x11, x8, #0x1
 b5c:	cmp	x10, x11
 b60:	csel	x11, x10, x11, cc	// cc = lo, ul, last
 b64:	add	x11, x11, #0x1
 b68:	cmp	x11, #0x8
 b6c:	b.hi	b78 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x38>  // b.pmore
 b70:	mov	x11, xzr
 b74:	b	bdc <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x9c>
 b78:	ands	x12, x11, #0x7
 b7c:	mov	w13, #0x8                   	// #8
 b80:	movi	v0.4s, #0x3
 b84:	movi	v1.4s, #0xc
 b88:	movi	v2.4s, #0x8
 b8c:	csel	x12, x13, x12, eq	// eq = none
 b90:	adrp	x13, 0 <__abi_tag-0x278>
 b94:	sub	x11, x11, x12
 b98:	add	x12, x9, #0x10
 b9c:	ldr	q3, [x13, #3712]
 ba0:	mov	x13, x11
 ba4:	nop
 ba8:	nop
 bac:	nop
 bb0:	nop
 bb4:	nop
 bb8:	nop
 bbc:	nop
 bc0:	mul	v4.4s, v3.4s, v0.4s
 bc4:	add	v3.4s, v3.4s, v2.4s
 bc8:	subs	x13, x13, #0x8
 bcc:	add	v5.4s, v4.4s, v1.4s
 bd0:	stp	q4, q5, [x12, #-16]
 bd4:	add	x12, x12, #0x20
 bd8:	b.ne	bc0 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0x80>  // b.any
 bdc:	add	w12, w11, w11, lsl #1
 be0:	add	x9, x9, x11, lsl #2
 be4:	sub	x10, x10, x11
 be8:	sub	x8, x8, x11
 bec:	nop
 bf0:	nop
 bf4:	nop
 bf8:	nop
 bfc:	nop
 c00:	cbz	x10, c1c <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0xdc>
 c04:	str	w12, [x9], #4
 c08:	subs	x8, x8, #0x1
 c0c:	add	w12, w12, #0x3
 c10:	sub	x10, x10, #0x1
 c14:	b.ne	c00 <_Z15kern_t05_fill_nRNSt3__16vectorIiNS_9allocatorIiEEEEi+0xc0>  // b.any
 c18:	ret
 c1c:	brk	#0x1
