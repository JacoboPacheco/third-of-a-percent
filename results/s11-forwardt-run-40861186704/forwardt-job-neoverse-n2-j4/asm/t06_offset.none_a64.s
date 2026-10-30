0000000000000c00 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii>:
     c00:	cmp	w2, #0x1
     c04:	b.lt	c90 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x90>  // b.tstop
     c08:	ldr	x8, [x1]
     c0c:	ldr	x9, [x0]
     c10:	sxtw	x11, w3
     c14:	cmp	w2, #0x8
     c18:	mov	w10, w2
     c1c:	b.cc	c34 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x34>  // b.lo, b.ul, b.last
     c20:	lsl	x12, x11, #2
     c24:	add	x14, x12, x9
     c28:	sub	x12, x14, x8
     c2c:	cmp	x12, #0x20
     c30:	b.cs	c94 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x94>  // b.hs, b.nlast
     c34:	mov	x12, xzr
     c38:	lsl	x13, x12, #2
     c3c:	sub	x10, x10, x12
     c40:	add	x11, x13, x11, lsl #2
     c44:	add	x8, x8, x13
     c48:	add	x9, x9, x11
     c4c:	nop
     c50:	nop
     c54:	nop
     c58:	nop
     c5c:	nop
     c60:	nop
     c64:	nop
     c68:	nop
     c6c:	nop
     c70:	nop
     c74:	nop
     c78:	nop
     c7c:	nop
     c80:	ldr	w11, [x8], #4
     c84:	subs	x10, x10, #0x1
     c88:	str	w11, [x9], #4
     c8c:	b.ne	c80 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x80>  // b.any
     c90:	ret
     c94:	and	x12, x10, #0x7ffffff8
     c98:	add	x13, x8, #0x10
     c9c:	add	x14, x14, #0x10
     ca0:	mov	x15, x12
     ca4:	nop
     ca8:	nop
     cac:	nop
     cb0:	nop
     cb4:	nop
     cb8:	nop
     cbc:	nop
     cc0:	ldp	q0, q1, [x13, #-16]
     cc4:	subs	x15, x15, #0x8
     cc8:	add	x13, x13, #0x20
     ccc:	stp	q0, q1, [x14, #-16]
     cd0:	add	x14, x14, #0x20
     cd4:	b.ne	cc0 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xc0>  // b.any
     cd8:	cmp	x12, x10
     cdc:	b.eq	c90 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x90>  // b.none
     ce0:	b	c38 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x38>
