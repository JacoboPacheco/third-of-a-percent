0000000000000e28 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
     e28:	ldp	x8, x9, [x1]
     e2c:	subs	x9, x9, x8
     e30:	b.eq	f34 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x10c>  // b.none
     e34:	asr	x11, x9, #2
     e38:	ldp	x9, x12, [x0]
     e3c:	ldp	x10, x13, [x2]
     e40:	cmp	x11, #0x1
     e44:	sub	x12, x12, x9
     e48:	csinc	x11, x11, xzr, hi	// hi = pmore
     e4c:	asr	x12, x12, #2
     e50:	sub	x13, x13, x10
     e54:	sub	x14, x11, #0x1
     e58:	asr	x13, x13, #2
     e5c:	cmp	x14, x12
     e60:	csel	x14, x14, x12, cc	// cc = lo, ul, last
     e64:	cmp	x14, x13
     e68:	csel	x15, x14, x13, cc	// cc = lo, ul, last
     e6c:	cmp	x15, #0x7
     e70:	b.hi	e7c <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x54>  // b.pmore
     e74:	mov	x14, xzr
     e78:	b	ee4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xbc>
     e7c:	sub	x14, x9, x8
     e80:	cmp	x14, #0x20
     e84:	mov	x14, xzr
     e88:	b.cc	ee4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xbc>  // b.lo, b.ul, b.last
     e8c:	sub	x16, x9, x10
     e90:	cmp	x16, #0x20
     e94:	b.cc	ee4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xbc>  // b.lo, b.ul, b.last
     e98:	add	x14, x15, #0x1
     e9c:	mov	w16, #0x8                   	// #8
     ea0:	add	x17, x9, #0x10
     ea4:	ands	x15, x14, #0x7
     ea8:	csel	x15, x16, x15, eq	// eq = none
     eac:	add	x16, x10, #0x10
     eb0:	sub	x14, x14, x15
     eb4:	add	x15, x8, #0x10
     eb8:	mov	x18, x14
     ebc:	ldp	q0, q3, [x16, #-16]
     ec0:	subs	x18, x18, #0x8
     ec4:	ldp	q1, q2, [x15, #-16]
     ec8:	add	x15, x15, #0x20
     ecc:	add	x16, x16, #0x20
     ed0:	add	v0.4s, v0.4s, v1.4s
     ed4:	add	v1.4s, v3.4s, v2.4s
     ed8:	stp	q0, q1, [x17, #-16]
     edc:	add	x17, x17, #0x20
     ee0:	b.ne	ebc <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x94>  // b.any
     ee4:	lsl	x16, x14, #2
     ee8:	mov	x15, xzr
     eec:	sub	x12, x12, x14
     ef0:	sub	x13, x13, x14
     ef4:	sub	x11, x11, x14
     ef8:	add	x8, x8, x16
     efc:	add	x10, x10, x16
     f00:	add	x9, x9, x16
     f04:	cmp	x13, x15
     f08:	b.eq	f38 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x110>  // b.none
     f0c:	cmp	x12, x15
     f10:	b.eq	f38 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x110>  // b.none
     f14:	lsl	x14, x15, #2
     f18:	add	x15, x15, #0x1
     f1c:	cmp	x11, x15
     f20:	ldr	w16, [x8, x14]
     f24:	ldr	w17, [x10, x14]
     f28:	add	w16, w17, w16
     f2c:	str	w16, [x9, x14]
     f30:	b.ne	f04 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xdc>  // b.any
     f34:	ret
     f38:	brk	#0x1
