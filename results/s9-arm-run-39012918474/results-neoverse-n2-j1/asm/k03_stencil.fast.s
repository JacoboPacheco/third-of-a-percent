0000000000000e28 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e28:	ldp	x8, x9, [x1]
     e2c:	sub	x9, x9, x8
     e30:	asr	x9, x9, #2
     e34:	subs	x13, x9, #0x3
     e38:	b.cc	f38 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x110>  // b.lo, b.ul, b.last
     e3c:	ldp	x10, x11, [x0]
     e40:	sub	x11, x11, x10
     e44:	asr	x11, x11, #2
     e48:	cmp	x11, #0x1
     e4c:	csinc	x12, x11, xzr, hi	// hi = pmore
     e50:	sub	x11, x8, #0x4
     e54:	sub	x15, x12, #0x1
     e58:	cmp	x15, x13
     e5c:	csel	x14, x15, x13, cc	// cc = lo, ul, last
     e60:	cmp	x14, #0x7
     e64:	b.ls	ef4 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xcc>  // b.plast
     e68:	cmp	x15, x13
     e6c:	add	x16, x10, #0x4
     e70:	csel	x13, x15, x13, cc	// cc = lo, ul, last
     e74:	lsl	x13, x13, #2
     e78:	add	x15, x8, x13
     e7c:	add	x13, x10, x13
     e80:	add	x15, x15, #0xc
     e84:	add	x13, x13, #0x8
     e88:	cmp	x16, x15
     e8c:	ccmp	x8, x13, #0x2, cc	// cc = lo, ul, last
     e90:	b.cc	ef4 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xcc>  // b.lo, b.ul, b.last
     e94:	add	x13, x14, #0x1
     e98:	mov	w14, #0x8                   	// #8
     e9c:	add	x16, x10, #0x14
     ea0:	ands	x15, x13, #0x7
     ea4:	add	x17, x8, #0x10
     ea8:	csel	x14, x14, x15, eq	// eq = none
     eac:	sub	x15, x13, x14
     eb0:	add	x13, x15, #0x2
     eb4:	add	x14, x15, #0x1
     eb8:	ldp	q0, q2, [x17, #-16]
     ebc:	subs	x15, x15, #0x8
     ec0:	ldur	q1, [x17, #-12]
     ec4:	ldur	q3, [x17, #4]
     ec8:	add	v0.4s, v1.4s, v0.4s
     ecc:	add	v1.4s, v3.4s, v2.4s
     ed0:	ldur	q2, [x17, #-8]
     ed4:	ldur	q3, [x17, #8]
     ed8:	add	x17, x17, #0x20
     edc:	add	v0.4s, v0.4s, v2.4s
     ee0:	add	v1.4s, v1.4s, v3.4s
     ee4:	stp	q0, q1, [x16, #-16]
     ee8:	add	x16, x16, #0x20
     eec:	b.ne	eb8 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x90>  // b.any
     ef0:	b	efc <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd4>
     ef4:	mov	w14, #0x1                   	// #1
     ef8:	mov	w13, #0x2                   	// #2
     efc:	add	x12, x12, #0x1
     f00:	cmp	x12, x13
     f04:	b.eq	f3c <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>  // b.none
     f08:	lsl	x14, x14, #2
     f0c:	ldr	w18, [x8, x13, lsl #2]
     f10:	mov	x15, x13
     f14:	add	x13, x13, #0x1
     f18:	ldr	w16, [x11, x14]
     f1c:	ldr	w17, [x8, x14]
     f20:	cmp	x9, x13
     f24:	add	w16, w17, w16
     f28:	add	w16, w16, w18
     f2c:	str	w16, [x10, x14]
     f30:	mov	x14, x15
     f34:	b.ne	f00 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd8>  // b.any
     f38:	ret
     f3c:	brk	#0x1
