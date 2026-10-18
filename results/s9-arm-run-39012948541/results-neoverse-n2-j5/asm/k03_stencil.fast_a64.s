0000000000000e40 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
     e40:	ldp	x8, x9, [x1]
     e44:	sub	x9, x9, x8
     e48:	asr	x9, x9, #2
     e4c:	subs	x13, x9, #0x3
     e50:	b.cc	fb8 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x178>  // b.lo, b.ul, b.last
     e54:	ldp	x10, x11, [x0]
     e58:	sub	x11, x11, x10
     e5c:	asr	x11, x11, #2
     e60:	cmp	x11, #0x1
     e64:	csinc	x12, x11, xzr, hi	// hi = pmore
     e68:	sub	x11, x8, #0x4
     e6c:	sub	x15, x12, #0x1
     e70:	cmp	x15, x13
     e74:	csel	x14, x15, x13, cc	// cc = lo, ul, last
     e78:	cmp	x14, #0x7
     e7c:	b.ls	f3c <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xfc>  // b.plast
     e80:	cmp	x15, x13
     e84:	add	x16, x10, #0x4
     e88:	csel	x13, x15, x13, cc	// cc = lo, ul, last
     e8c:	lsl	x13, x13, #2
     e90:	add	x15, x8, x13
     e94:	add	x13, x10, x13
     e98:	add	x15, x15, #0xc
     e9c:	add	x13, x13, #0x8
     ea0:	cmp	x16, x15
     ea4:	ccmp	x8, x13, #0x2, cc	// cc = lo, ul, last
     ea8:	b.cc	f3c <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xfc>  // b.lo, b.ul, b.last
     eac:	add	x13, x14, #0x1
     eb0:	mov	w14, #0x8                   	// #8
     eb4:	add	x16, x10, #0x14
     eb8:	ands	x15, x13, #0x7
     ebc:	add	x17, x8, #0x10
     ec0:	csel	x14, x14, x15, eq	// eq = none
     ec4:	sub	x15, x13, x14
     ec8:	add	x13, x15, #0x2
     ecc:	add	x14, x15, #0x1
     ed0:	nop
     ed4:	nop
     ed8:	nop
     edc:	nop
     ee0:	nop
     ee4:	nop
     ee8:	nop
     eec:	nop
     ef0:	nop
     ef4:	nop
     ef8:	nop
     efc:	nop
     f00:	ldp	q0, q2, [x17, #-16]
     f04:	subs	x15, x15, #0x8
     f08:	ldur	q1, [x17, #-12]
     f0c:	ldur	q3, [x17, #4]
     f10:	add	v0.4s, v1.4s, v0.4s
     f14:	add	v1.4s, v3.4s, v2.4s
     f18:	ldur	q2, [x17, #-8]
     f1c:	ldur	q3, [x17, #8]
     f20:	add	x17, x17, #0x20
     f24:	add	v0.4s, v0.4s, v2.4s
     f28:	add	v1.4s, v1.4s, v3.4s
     f2c:	stp	q0, q1, [x16, #-16]
     f30:	add	x16, x16, #0x20
     f34:	b.ne	f00 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>  // b.any
     f38:	b	f44 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x104>
     f3c:	mov	w14, #0x1                   	// #1
     f40:	mov	w13, #0x2                   	// #2
     f44:	add	x12, x12, #0x1
     f48:	nop
     f4c:	nop
     f50:	nop
     f54:	nop
     f58:	nop
     f5c:	nop
     f60:	nop
     f64:	nop
     f68:	nop
     f6c:	nop
     f70:	nop
     f74:	nop
     f78:	nop
     f7c:	nop
     f80:	cmp	x12, x13
     f84:	b.eq	fbc <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x17c>  // b.none
     f88:	lsl	x14, x14, #2
     f8c:	ldr	w18, [x8, x13, lsl #2]
     f90:	mov	x15, x13
     f94:	add	x13, x13, #0x1
     f98:	ldr	w16, [x11, x14]
     f9c:	ldr	w17, [x8, x14]
     fa0:	cmp	x9, x13
     fa4:	add	w16, w17, w16
     fa8:	add	w16, w16, w18
     fac:	str	w16, [x10, x14]
     fb0:	mov	x14, x15
     fb4:	b.ne	f80 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x140>  // b.any
     fb8:	ret
     fbc:	brk	#0x1
