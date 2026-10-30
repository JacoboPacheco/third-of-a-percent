0000000000000be8 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii>:
 be8:	cmp	w2, #0x1
 bec:	b.lt	c44 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x5c>  // b.tstop
 bf0:	ldr	x8, [x1]
 bf4:	ldr	x9, [x0]
 bf8:	sxtw	x11, w3
 bfc:	cmp	w2, #0x8
 c00:	mov	w10, w2
 c04:	b.cc	c1c <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x34>  // b.lo, b.ul, b.last
 c08:	lsl	x12, x11, #2
 c0c:	add	x14, x12, x9
 c10:	sub	x12, x14, x8
 c14:	cmp	x12, #0x20
 c18:	b.cs	c48 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x60>  // b.hs, b.nlast
 c1c:	mov	x12, xzr
 c20:	lsl	x13, x12, #2
 c24:	sub	x10, x10, x12
 c28:	add	x11, x13, x11, lsl #2
 c2c:	add	x8, x8, x13
 c30:	add	x9, x9, x11
 c34:	ldr	w11, [x8], #4
 c38:	subs	x10, x10, #0x1
 c3c:	str	w11, [x9], #4
 c40:	b.ne	c34 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x4c>  // b.any
 c44:	ret
 c48:	and	x12, x10, #0x7ffffff8
 c4c:	add	x13, x8, #0x10
 c50:	add	x14, x14, #0x10
 c54:	mov	x15, x12
 c58:	ldp	q0, q1, [x13, #-16]
 c5c:	subs	x15, x15, #0x8
 c60:	add	x13, x13, #0x20
 c64:	stp	q0, q1, [x14, #-16]
 c68:	add	x14, x14, #0x20
 c6c:	b.ne	c58 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x70>  // b.any
 c70:	cmp	x12, x10
 c74:	b.eq	c44 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x5c>  // b.none
 c78:	b	c20 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x38>
