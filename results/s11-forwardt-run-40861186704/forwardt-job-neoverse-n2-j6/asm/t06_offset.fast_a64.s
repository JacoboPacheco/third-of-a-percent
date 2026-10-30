0000000000000c00 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii>:
     c00:	cmp	w2, #0x1
     c04:	b.lt	d24 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x124>  // b.tstop
     c08:	ldp	x8, x9, [x0]
     c0c:	sxtw	x10, w3
     c10:	ldp	x12, x13, [x1]
     c14:	mov	w11, w2
     c18:	sub	x15, x11, #0x1
     c1c:	sub	x9, x9, x8
     c20:	asr	x9, x9, #2
     c24:	sub	x13, x13, x12
     c28:	asr	x13, x13, #2
     c2c:	subs	x14, x9, x10
     c30:	csel	x14, xzr, x14, cc	// cc = lo, ul, last
     c34:	cmp	x14, x15
     c38:	csel	x14, x14, x15, cc	// cc = lo, ul, last
     c3c:	cmp	x14, x13
     c40:	csel	x14, x14, x13, cc	// cc = lo, ul, last
     c44:	add	x15, x14, #0x1
     c48:	mov	x14, xzr
     c4c:	cmp	x15, #0x8
     c50:	b.ls	cd8 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xd8>  // b.plast
     c54:	lsl	x14, x10, #2
     c58:	add	x16, x14, x8
     c5c:	sub	x14, x16, x12
     c60:	cmp	x14, #0x20
     c64:	b.cs	c70 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x70>  // b.hs, b.nlast
     c68:	mov	x14, xzr
     c6c:	b	cd8 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xd8>
     c70:	ands	x14, x15, #0x7
     c74:	mov	w17, #0x8                   	// #8
     c78:	add	x16, x16, #0x10
     c7c:	csel	x14, x17, x14, eq	// eq = none
     c80:	sub	x14, x15, x14
     c84:	add	x15, x12, #0x10
     c88:	mov	x17, x14
     c8c:	nop
     c90:	nop
     c94:	nop
     c98:	nop
     c9c:	nop
     ca0:	nop
     ca4:	nop
     ca8:	nop
     cac:	nop
     cb0:	nop
     cb4:	nop
     cb8:	nop
     cbc:	nop
     cc0:	ldp	q0, q1, [x15, #-16]
     cc4:	subs	x17, x17, #0x8
     cc8:	add	x15, x15, #0x20
     ccc:	stp	q0, q1, [x16, #-16]
     cd0:	add	x16, x16, #0x20
     cd4:	b.ne	cc0 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xc0>  // b.any
     cd8:	add	x12, x12, x14, lsl #2
     cdc:	sub	x13, x13, x14
     ce0:	add	x10, x14, x10
     ce4:	sub	x11, x11, x14
     ce8:	nop
     cec:	nop
     cf0:	nop
     cf4:	nop
     cf8:	nop
     cfc:	nop
     d00:	cbz	x13, d28 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x128>
     d04:	cmp	x9, x10
     d08:	b.ls	d28 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x128>  // b.plast
     d0c:	ldr	w14, [x12], #4
     d10:	subs	x11, x11, #0x1
     d14:	str	w14, [x8, x10, lsl #2]
     d18:	sub	x13, x13, #0x1
     d1c:	add	x10, x10, #0x1
     d20:	b.ne	d00 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x100>  // b.any
     d24:	ret
     d28:	brk	#0x1
