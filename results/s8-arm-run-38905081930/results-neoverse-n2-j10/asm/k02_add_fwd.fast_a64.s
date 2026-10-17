0000000000000e40 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
     e40:	ldp	x8, x9, [x1]
     e44:	subs	x9, x9, x8
     e48:	b.eq	fb0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x170>  // b.none
     e4c:	asr	x11, x9, #2
     e50:	ldp	x9, x12, [x0]
     e54:	ldp	x10, x13, [x2]
     e58:	cmp	x11, #0x1
     e5c:	sub	x12, x12, x9
     e60:	csinc	x11, x11, xzr, hi	// hi = pmore
     e64:	asr	x12, x12, #2
     e68:	sub	x13, x13, x10
     e6c:	sub	x14, x11, #0x1
     e70:	asr	x13, x13, #2
     e74:	cmp	x14, x12
     e78:	csel	x14, x14, x12, cc	// cc = lo, ul, last
     e7c:	cmp	x14, x13
     e80:	csel	x15, x14, x13, cc	// cc = lo, ul, last
     e84:	cmp	x15, #0x7
     e88:	b.hi	e94 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x54>  // b.pmore
     e8c:	mov	x14, xzr
     e90:	b	f28 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xe8>
     e94:	sub	x14, x9, x8
     e98:	cmp	x14, #0x20
     e9c:	mov	x14, xzr
     ea0:	b.cc	f28 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xe8>  // b.lo, b.ul, b.last
     ea4:	sub	x16, x9, x10
     ea8:	cmp	x16, #0x20
     eac:	b.cc	f28 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xe8>  // b.lo, b.ul, b.last
     eb0:	add	x14, x15, #0x1
     eb4:	mov	w16, #0x8                   	// #8
     eb8:	add	x17, x9, #0x10
     ebc:	ands	x15, x14, #0x7
     ec0:	csel	x15, x16, x15, eq	// eq = none
     ec4:	add	x16, x10, #0x10
     ec8:	sub	x14, x14, x15
     ecc:	add	x15, x8, #0x10
     ed0:	mov	x18, x14
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
     f00:	ldp	q0, q3, [x16, #-16]
     f04:	subs	x18, x18, #0x8
     f08:	ldp	q1, q2, [x15, #-16]
     f0c:	add	x15, x15, #0x20
     f10:	add	x16, x16, #0x20
     f14:	add	v0.4s, v0.4s, v1.4s
     f18:	add	v1.4s, v3.4s, v2.4s
     f1c:	stp	q0, q1, [x17, #-16]
     f20:	add	x17, x17, #0x20
     f24:	b.ne	f00 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>  // b.any
     f28:	lsl	x16, x14, #2
     f2c:	mov	x15, xzr
     f30:	sub	x12, x12, x14
     f34:	sub	x13, x13, x14
     f38:	sub	x11, x11, x14
     f3c:	add	x8, x8, x16
     f40:	add	x10, x10, x16
     f44:	add	x9, x9, x16
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
     f80:	cmp	x13, x15
     f84:	b.eq	fb4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x174>  // b.none
     f88:	cmp	x12, x15
     f8c:	b.eq	fb4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x174>  // b.none
     f90:	lsl	x14, x15, #2
     f94:	add	x15, x15, #0x1
     f98:	cmp	x11, x15
     f9c:	ldr	w16, [x8, x14]
     fa0:	ldr	w17, [x10, x14]
     fa4:	add	w16, w17, w16
     fa8:	str	w16, [x9, x14]
     fac:	b.ne	f80 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x140>  // b.any
     fb0:	ret
     fb4:	brk	#0x1
