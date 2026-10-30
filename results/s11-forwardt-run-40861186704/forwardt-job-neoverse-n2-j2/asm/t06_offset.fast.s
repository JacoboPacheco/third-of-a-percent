0000000000000be8 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii>:
 be8:	cmp	w2, #0x1
 bec:	b.lt	cc0 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xd8>  // b.tstop
 bf0:	ldp	x8, x9, [x0]
 bf4:	sxtw	x10, w3
 bf8:	ldp	x12, x13, [x1]
 bfc:	mov	w11, w2
 c00:	sub	x15, x11, #0x1
 c04:	sub	x9, x9, x8
 c08:	asr	x9, x9, #2
 c0c:	sub	x13, x13, x12
 c10:	asr	x13, x13, #2
 c14:	subs	x14, x9, x10
 c18:	csel	x14, xzr, x14, cc	// cc = lo, ul, last
 c1c:	cmp	x14, x15
 c20:	csel	x14, x14, x15, cc	// cc = lo, ul, last
 c24:	cmp	x14, x13
 c28:	csel	x14, x14, x13, cc	// cc = lo, ul, last
 c2c:	add	x15, x14, #0x1
 c30:	mov	x14, xzr
 c34:	cmp	x15, #0x8
 c38:	b.ls	c8c <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xa4>  // b.plast
 c3c:	lsl	x14, x10, #2
 c40:	add	x16, x14, x8
 c44:	sub	x14, x16, x12
 c48:	cmp	x14, #0x20
 c4c:	b.cs	c58 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x70>  // b.hs, b.nlast
 c50:	mov	x14, xzr
 c54:	b	c8c <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xa4>
 c58:	ands	x14, x15, #0x7
 c5c:	mov	w17, #0x8                   	// #8
 c60:	add	x16, x16, #0x10
 c64:	csel	x14, x17, x14, eq	// eq = none
 c68:	sub	x14, x15, x14
 c6c:	add	x15, x12, #0x10
 c70:	mov	x17, x14
 c74:	ldp	q0, q1, [x15, #-16]
 c78:	subs	x17, x17, #0x8
 c7c:	add	x15, x15, #0x20
 c80:	stp	q0, q1, [x16, #-16]
 c84:	add	x16, x16, #0x20
 c88:	b.ne	c74 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x8c>  // b.any
 c8c:	add	x12, x12, x14, lsl #2
 c90:	sub	x13, x13, x14
 c94:	add	x10, x14, x10
 c98:	sub	x11, x11, x14
 c9c:	cbz	x13, cc4 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xdc>
 ca0:	cmp	x9, x10
 ca4:	b.ls	cc4 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xdc>  // b.plast
 ca8:	ldr	w14, [x12], #4
 cac:	subs	x11, x11, #0x1
 cb0:	str	w14, [x8, x10, lsl #2]
 cb4:	sub	x13, x13, #0x1
 cb8:	add	x10, x10, #0x1
 cbc:	b.ne	c9c <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xb4>  // b.any
 cc0:	ret
 cc4:	brk	#0x1
